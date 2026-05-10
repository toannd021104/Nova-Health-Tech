# AWS Architecture — Nova Health Tech Clinical GenAI Assistant (Production)

Production design for the AI assistant service deployed in **AWS Singapore (ap-southeast-1)**. The web UI can stay simple and publicly accessible for verification; the AI service itself is sized for real clinical workload.

## 1. Goals mapped to design (from the scenario)

| Requirement | Design response |
|---|---|
| Answer complex medical questions in natural language | Two-lane strategy: **Claude Haiku 4.5** (fast lane) + **Claude Sonnet 4.5** (complex lane). **No fine-tuning of Haiku 4.5 is possible** on Bedrock today — see `docs/architecture/model_customization_research.md`. The fast-lane quality lever is **distillation from Sonnet → Amazon Nova Lite** via Bedrock Model Distillation (managed), trained **before launch** and active from day one. |
| Rely on internal trial reports + treatment protocols + WHO + ICD-11 | Multi-KB RAG (Bedrock Knowledge Bases on OpenSearch Serverless) fed by **scheduled ingestion** + an **internal upload portal** |
| Auditable, compliant | Bedrock Guardrails + Comprehend Medical + Macie + CloudTrail → S3 Object Lock (**6-year retention** per HIPAA §164.530(j)) |
| 2-second emergency response | Fine-tuned Nova Lite student (from Sonnet+RAG distillation) OR plain Haiku 4.5, plus 3-layer caching and streaming |
| Consistent tone | Distillation on approved answers + low-temperature sampling + fixed system prompt (`docs/architecture/fine_tuning_and_distillation.md`) |
| Monthly WHO refresh | EventBridge cron → Step Functions → Bedrock KB incremental sync (see `docs/architecture/ingestion_and_identity.md`) |
| Legacy PDFs, inconsistent tagging | Bedrock Data Automation advanced parsing + Nova Multimodal Embeddings on figure-bearing chunks |
| Structured WHO API | Ingest + runtime tool call + query expansion |
| Corporate integration with hospital systems | **Site-to-Site VPN** between hospital and Nova VPC; **hospital IdP federation** via Cognito (SAML/OIDC) |

## 2. Region and data residency

- **Primary region: `ap-southeast-1` (Singapore).**
- Why Singapore:
  - Low latency to hospital clients in APAC.
  - AWS Singapore is HIPAA-eligible across all services we need (Bedrock, S3, OpenSearch Serverless, Lambda, API Gateway, Cognito, Comprehend Medical, Macie, etc.).
  - Singapore PDPA + HCSA allow cross-border health-data transfer **only when the recipient jurisdiction provides comparable protection**; keeping data **in Singapore** is the simplest compliance posture and avoids the transfer-limitation obligation entirely.
  - Model Studio on Alibaba is also available in Singapore — lets Nova offer both cloud variants without regulatory asymmetry.
- **No cross-border transfer** by default. If Nova ever needs a second region for DR (e.g., Tokyo), PDPA-compliant contracts and patient consent (deemed consent covers most clinical use) must be in place first.
- **No Outposts, no Direct Connect.** Singapore region is close enough; the hospital connects over AWS Site-to-Site VPN.

## 3. Component diagram

```
              ┌──────────────────────────────────────────────────────────────┐
              │   Hospital network (clinician workstations + EHR systems)    │
              └──┬──────────────────────────────────────────────┬────────────┘
                 │                                              │
         AI chat │ HTTPS over                      Internal mgmt │ HTTPS over
                 │ public Internet                               │ Site-to-Site
                 │                                               │ VPN (IPsec/IKEv2)
                 ▼                                               ▼
     ┌──────────────────────┐                      ┌──────────────────────────┐
     │ CloudFront + WAF     │                      │ Customer Gateway on-prem │
     └──────┬───────────────┘                      └──────────┬───────────────┘
            │                                                 │
     ┌──────▼──────────┐   ──────── Site-to-Site VPN ───────► │ VPN GW / TGW
     │ API Gateway     │                                      │  (private side)
     │  (public, REST) │                                      └──────────┬───────────┘
     │  + Cognito JWT  │                                                 │
     │   authorizer    │                                                 │
     └──────┬──────────┘                                                 ▼
            │                                                 ┌──────────────────────┐
            │                                                 │ Private ALB + Cognito│
            │                                                 │ OIDC/SAML ← EntraID  │
            │                                                 │                      │
            │                                                 │ ECS Fargate:         │
            │                                                 │  Upload Portal       │
            │                                                 │  (internal UI)       │
            │                                                 └──────────┬───────────┘
            │                                                            │
            ▼                                                            ▼
   ┌──────────────────────────────┐                        ┌──────────────────────────┐
   │ Lambda /chat (VPC)           │                        │ S3 raw bucket             │
   │  0. authn (Cognito JWT)       │◄──── semantic cache ──┤ /raw/scheduled/...        │
   │  1. PHI mask (Comprehend Med) │     hit returns early │ /raw/manual/...           │
   │  2. if/else router on         │                       │ /raw/icd11/...            │
   │     explicit emergency flag   │                       │ /raw/who/...              │
   │     (no classifier LLM call)  │                       └──────────┬───────────────┘
   │  3. call Bedrock Agent        │                                  │ ObjectCreated
   │  4. ground-check + audit      │                                  ▼
   └─────┬──────────────┬──────────┘                        ┌──────────────────────────┐
         │              │                                   │ Step Functions pipeline  │
 Layer 1 │    Layer 2   │  Generation                       │  BDA parse → chunk →     │
 Elasti- │    Bedrock   │  (Bedrock):                       │  embed → KB sync         │
 Cache   │    Prompt    │    Haiku 4.5 (fast lane)          │                          │
 Valkey  │    Caching   │    Sonnet 4.5 (complex lane,      │                          │
 semantic│              │     teacher of distillation)      │ + GuardDuty Malware scan │
 cache   │              │  + Guardrails                  │ + Macie PHI scan         │
         │              │                                └──────────┬───────────────┘
         │              │                                           ▼
         │              │                             ┌────────────────────────────┐
         │              │                             │ Bedrock Knowledge Bases    │
         │              │                             │  kb-who-guidelines         │
         │              │                             │  kb-internal-trials        │
         │              │                             │  kb-treatment-protocols    │
         │              │                             │  kb-icd11                  │
         │              │                             │  on OpenSearch Serverless  │
         │              │                             │  (hybrid kNN + BM25)       │
         │              │                             │  + Cohere Embed v4         │
         │              │                             │  + Nova Multimodal Emb     │
         │              │                             └────────────────────────────┘
         ▼              ▼
  All traffic logged → CloudTrail → S3 Object Lock (6-yr WORM) → Security Lake
```

### Ingestion triggers (see `docs/architecture/ingestion_and_identity.md`)

- WHO ICD-11 daily delta (EventBridge 02:00 SGT).
- WHO guidelines monthly + RSS webhook for living guidelines.
- Internal clinical trial reports and treatment protocols: **weekly** Sunday pull over Site-to-Site VPN from hospital SharePoint / SMB share.
- Manual overrides via the **Internal Upload Portal** (private ALB, hospital-VPN-only, hospital-IdP auth).

## 4. Data pipeline

See `docs/architecture/rag_strategy.md` for the strategy decision. Summary:

- **Parser**: Bedrock Data Automation with advanced parsing (handles 100+ page PDFs with horizontal / vertical tables and text-based flowcharts out of the box).
- **Chunking**: hierarchical 1500 / 300 tokens with 15% overlap; section-aware.
- **Embeddings**: Cohere Embed v4 (`global.cohere.embed-v4:0`) for text chunks; Amazon Nova Multimodal Embeddings for figure-bearing chunks.
- **Vector store**: OpenSearch Serverless vector collection; BM25 + HNSW hybrid in one index.
- **Metadata on every chunk**: `source`, `document_id`, `revision`, `document_type`, `publication_date`, `review_date`, `specialty`, `evidence_grade`, `page`, `section_heading`, `has_table`, `has_figure`.
- **Retrieval**: hybrid query + metadata pre-filter (default `review_date >= NOW-18m`) → top-20 kNN → Cohere Rerank (Bedrock) → top-5 → Bedrock Agent.

## 5. Model orchestration

### 5.1 Framework choice

See `docs/architecture/framework_choice.md`.

- **Bedrock Agents + Bedrock Knowledge Bases** are the primary runtime (conversational, multi-tool). The Agent exposes retrieval + ICD-11 + trial lookup as tools.
- **LangChain** is used only for the semantic cache (`RedisSemanticCache` against ElastiCache Valkey + RediSearch) and per-session chat memory.

### 5.2 Router and lanes

Routing has two distinct steps driven by different logic:

**Step 1 — Lane selection (pure if/else, no LLM call).** Matches `aws-demo/ec2/app/graph.py` (`_route_next`) and `docs/architecture/workflow_detailed.md` §Step 5.

```python
def _route_lane(state):
    return "emergency" if state["emergency"] else "complex"
```

**Step 2 — Department selection (router agent, complex lane only).** The complex lane runs a lightweight router that reads the clinician's prompt + attachments and picks one of the 40 department agents described in `docs/architecture/technology_options.md` §3b. Emergency lane bypasses this step.

| Question class | Model | Hyperparameters | Guardrail | Latency target |
|---|---|---|---|---|
| Emergency / acute (toggle ON — bypass router) | **Claude Haiku 4.5** (streaming) with optional Nova Lite distillation student behind a feature flag | `temperature=0.1, max_tokens=700, stop=[...]` — Claude rejects sending temperature + top_p together | Strict PHI + emergency disclaimer | **≤ 2 s** |
| Router agent (picks department on complex lane) | **Nova Micro** with structured-output system prompt | `temperature=0, max_tokens=150` (JSON only) | Standard | ~150 ms |
| Complex differential (toggle OFF, department picked) | **Claude Sonnet 4.5** for most specialists; **Sonnet 4.5 vision** if the selected department is Radiology or the user attached an image | `temperature=0.2, max_tokens=1500` | Standard | 3–6 s |
| Literature / citation | Haiku 4.5, grounded-only mode | `temperature=0.1` | No-hallucination | 1.5–2 s |
| Patient-education phrasing | Haiku 4.5 with tone preset | `temperature=0.2` | Standard + tone | 1–2 s |

**Notes on models used:**
- The fast lane serves a **Nova Lite student distilled from Sonnet 4.5** via Bedrock Model Distillation — trained during the pre-launch build and active from day one. Base Haiku 4.5 is the same-API fallback when the custom model endpoint is unavailable. Haiku 4.5 itself cannot be fine-tuned on Bedrock (only Claude 3 Haiku is). See `docs/architecture/model_customization_research.md`.
- **Claude Opus is not used** — priced out for this volume and Sonnet covers the complex lane.
- **Nova Micro / Nova Pro** are available in Singapore and are the cost-sensitive alternative (Version A1+); see `docs/pricing/cost_analysis.md`.
- **Radiology agent needs vision** — uses Claude Sonnet 4.5 which natively accepts images in the Converse API.

### 5.4 Multi-agent department topology (complex lane)

The assistant mirrors a Vietnamese tertiary hospital's clinical structure. Forty specialty agents live behind the router; the clinician sees only the natural-language answer + a route badge ("Cardiology"). Full Vietnamese → English department mapping + KB-namespace assignment in `docs/architecture/technology_options.md` §3b.

- Emergency lane bypasses the router entirely.
- Radiology receives image attachments + DICOMs.
- Clinical Pharmacy is a side-channel auto-invoked on any prescribing question.
- Config-driven enable/disable per hospital tenant — 12-department core for small hospitals, all 40 for teaching hospitals.
- Implementation: Bedrock Agents with per-department action groups; a small Lambda drives the routing.

### 5.3 Agent tools

- `retrieve_guideline(topic, source=WHO, max_age_days=90)` — Bedrock KB retrieval with metadata pre-filter.
- `retrieve_trial(nct_or_doc_id)` — pulls by ID from the internal KB.
- `icd11_lookup(term, mode)` — Lambda hitting the live WHO ICD-11 API (`/mms/search` and `/mms/{id}`).
- `icd11_expand_query(term)` — used silently by the retrieval stage to boost BM25 recall with synonyms.

All tools are read-only; no tool can write to any PHI store.

## 6. Security architecture

Full mapping in `docs/compliance/security_compliance.md`.

| Layer | Control |
|---|---|
| Account isolation | AWS Organizations; one account per environment (prod / stage / dev) in `ap-southeast-1` |
| Network | Lambdas in private VPC; Bedrock + S3 + OpenSearch via VPC endpoints; zero internet egress from the chat Lambda |
| Identity — clinicians | Cognito user pool federated via SAML/OIDC to each hospital's IdP (EntraID / Okta / ADFS); MFA enforced in IdP |
| Identity — Nova staff | IAM Identity Center federated to Nova's EntraID; no long-lived IAM users |
| Hospital ↔ cloud | **Site-to-Site VPN** (IPsec IKEv2, AES-256-GCM, SHA-2), dual-tunnel HA; BGP routing preferred |
| Data at rest | S3, OpenSearch, ElastiCache, Secrets Manager all on customer-managed KMS keys |
| Data in transit | TLS 1.3 everywhere; mTLS internally where supported |
| PHI handling | Comprehend Medical DetectPHI on every inbound message → reversible tokenization (KMS-backed) → model never sees raw PHI. Macie weekly on `raw/` |
| LLM safety | Bedrock Guardrails: denied topics, PHI filter, contextual grounding threshold ≥ 0.7, prompt-injection filter; a fail blocks the response and is logged |
| Audit | CloudTrail → S3 Object Lock (immutable) with **6-year retention** + Security Lake; Bedrock invocation logs capture request/response hashes |
| Ingestion safety | GuardDuty Malware Protection on S3 uploads; Macie PHI scan; quarantine + admin notification on any leak |
| Secrets | Secrets Manager with KMS + rotation Lambda for the WHO ICD-11 OAuth client |
| BAA | AWS BAA signed and scoped to all services used in this design in `ap-southeast-1` |

## 7. Deployment approach

### 7.1 Public cloud in Singapore; optional hybrid via VPN

- **Primary**: all AWS services in `ap-southeast-1`; multi-AZ.
- **Hospital integration**: Site-to-Site VPN only. Outposts and Direct Connect are intentionally out of scope — Singapore latency is acceptable and VPN throughput (1.25 Gbps / tunnel) handles document uploads comfortably.
- **DR**: cross-AZ within ap-southeast-1 for normal DR; a warm-standby in `ap-southeast-3` (Jakarta) or `ap-northeast-1` (Tokyo) is a roadmap item pending PDPA transfer-limitation review.

### 7.2 Launch scope — one production release, all features on

There is **no pilot / PoC / staged rollout**. When we go live, every capability in this document is active on day one: ingestion, retrieval, the 2-second emergency lane, fine-tuned student, multi-agent orchestration, caching, guardrails, and audit trail. Anything listed here that involves training a model is trained **before cut-over** during a pre-launch build phase, not after.

| Capability | State at launch |
|---|---|
| Scheduled ingestion (WHO, ICD-11, SharePoint) + manual Upload Portal over VPN | ✅ on |
| Hybrid retrieval (BM25 + kNN + Cohere Rerank 3.5) on both lanes | ✅ on |
| Emergency toggle + if/else router | ✅ on |
| **Fine-tuned Nova Lite student** distilled from Sonnet 4.5 via Bedrock Model Distillation | ✅ **trained before launch, serving 100% of fast-lane traffic** |
| Multi-agent topology mirroring a Vietnamese tertiary hospital (40 clinical departments, router bypassed on emergency, Radiology uses vision-capable model on image uploads) | ✅ on (configurable set active per hospital tenant) |
| Managed GraphRAG (Bedrock Knowledge Bases GraphRAG on Neptune Analytics) on the WHO + protocol corpus | ✅ on |
| Layer-1 semantic cache + Layer-2 Bedrock Prompt Caching | ✅ on |
| Bedrock Reserved Tier on the emergency lane | ✅ on (sized to peak TPM) |
| Guardrails + Comprehend Medical PHI mask + grounding + citation validator | ✅ on |
| CloudTrail → S3 Object Lock 6-year audit | ✅ on |
| EHR SMART-on-FHIR launch for Epic / Cerner / Allscripts | ✅ on per configured tenant |

### 7.3 Continuous operations (post-launch, not a "phase")

After launch the team runs:

| Cadence | Action |
|---|---|
| Daily 02:00 SGT | WHO ICD-11 delta ingest; semantic-cache invalidation for affected `source:*` tags |
| Monthly day 1 02:30 SGT | WHO guideline PDF refresh + incremental re-index of the Bedrock Knowledge Bases GraphRAG (Neptune Analytics) graph |
| Weekly Sun | SharePoint / trial-report reconciliation pass (safety net for missed webhooks) |
| Monthly | DPO micro-run on the past month's clinician preference pairs (Bedrock Model Distillation has no DPO path; on Version A we use Claude 3 Haiku SFT+DPO fallback or skip DPO for Nova Lite). Short training, same canary evaluation as launch. |
| Quarterly | Full student retrain on accumulated new clinician data + latest WHO releases; re-qualify with eval harness; promote after it matches or beats current student on the holdout. |
| Event-driven | Red-team re-run after any guardrail incident; retrain on new adversarial examples. |

### 7.4 Corporate integration

See `docs/architecture/corporate_integration.md` for the full EHR/FHIR + SharePoint design.

- **EHR launch** via **SMART App Launch v2** against Epic / Cerner (Oracle Health) / Allscripts on FHIR R4; the clinician's EHR session provides the patient context, which Lambda de-identifies before calling Bedrock. Scopes are all `*.rs` (read + search) — the assistant never writes to the EHR.
- **SharePoint / OneDrive** — Microsoft Graph `subscriptions` (webhook or Event Hubs delivery) on `/sites/{site-id}/drives/{drive-id}/root` triggers the same Step Functions ingestion pipeline whenever a document is created / updated / deleted. `Sites.Selected` app permission preferred.
- **Clinician SSO** — Cognito federation per hospital tenant to their EntraID / Okta / ADFS.
- **Admin SSO** — IAM Identity Center → Nova's EntraID.
- **Audit export** — nightly CloudWatch Logs → S3 → hospital SIEM via cross-account role assumption.

## 8. Performance — closing the 2-second budget

See `docs/architecture/caching_strategy.md` for detail. Representative p95 emergency path:

```
     20 ms   Semantic cache hit (Layer 1; 30–45% of emergency queries)
    100 ms   Cognito auth + PHI mask
     60 ms   Hybrid retrieval (metadata pre-filter, top-20 kNN+BM25, rerank to 5)
    400 ms   Haiku 4.5 first-token (with Bedrock Prompt Cache hit on the static prefix)
  1,200 ms   Haiku 4.5 full answer (250 tokens, streaming)
    120 ms   Guardrail + grounding + citation validation
  ────────
   ≤ 1,900 ms  p95
```

Fine-tuned Nova Lite student (live from launch) is already included in this budget; Sonnet falls back on it for about 40% of complex traffic that matches the student's competency rubric, shaving ~300–400 ms and reducing complex-lane cost accordingly.

## 9. References

- [AWS Services in Scope by Compliance Program (HIPAA, etc.)](https://aws.amazon.com/compliance/services-in-scope/)
- [Architecting for HIPAA Security and Compliance on AWS](https://docs.aws.amazon.com/whitepapers/latest/architecting-hipaa-security-and-compliance-on-aws/architecting-hipaa-security-and-compliance-on-aws.html)
- [Amazon Bedrock Knowledge Bases — advanced parsing, chunking](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-advanced-parsing-chunking-and-query-reformulation-giving-greater-control-of-accuracy-in-rag-based-applications/)
- [Cache Prompts Between Requests — Bedrock](https://aws.amazon.com/bedrock/prompt-caching/)
- [AWS Site-to-Site VPN — user guide](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [Cognito SAML / OIDC federation](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-identity-federation.html)
- [Singapore PDPA — cross-border transfers](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers)

*Content above is rephrased for compliance with licensing restrictions.*
