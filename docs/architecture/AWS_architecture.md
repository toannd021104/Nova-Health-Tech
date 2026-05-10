# AWS Architecture — Nova Health Tech Clinical GenAI Assistant (Production)

Production design for the AI assistant service deployed in **AWS Singapore (ap-southeast-1)**. The web UI can stay simple and publicly accessible for verification; the AI service itself is sized for real clinical workload.

## 1. Goals mapped to design (from the scenario)

| Requirement | Design response |
|---|---|
| Answer complex medical questions in natural language | Two-lane strategy: **Claude Haiku 4.5** (fast lane, student-enhanced) + **Claude Sonnet 4.6** (complex lane, teacher of distillation) |
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
   │  2. router (Haiku classifier) │                       │ /raw/icd11/...            │
   │  3. route to Agent / Workflow │                       │ /raw/who/...              │
   │     (Bedrock Agents)          │                       └──────────┬───────────────┘
   │  4. ground-check + audit      │                                  │ ObjectCreated
   └─────┬──────────────┬──────────┘                                  ▼
         │              │                                ┌──────────────────────────┐
 Layer 1 │    Layer 2   │  Generation                    │ Step Functions pipeline  │
 Elasti- │    Bedrock   │  (Bedrock):                    │  BDA parse → chunk →     │
 Cache   │    Prompt    │    Haiku 4.5 (fast, student)   │  embed → KB sync         │
 Valkey  │    Caching   │    Sonnet 4.6 (complex,        │                          │
 semantic│              │     teacher of distillation)   │ + GuardDuty Malware scan │
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
         │              │                             │  + Titan Embed Text v2     │
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
- **Embeddings**: Titan Embed Text v2 for text; Nova Multimodal Embeddings for figure-bearing chunks.
- **Vector store**: OpenSearch Serverless vector collection; BM25 + HNSW hybrid in one index.
- **Metadata on every chunk**: `source`, `document_id`, `revision`, `document_type`, `publication_date`, `review_date`, `specialty`, `evidence_grade`, `page`, `section_heading`, `has_table`, `has_figure`.
- **Retrieval**: hybrid query + metadata pre-filter (default `review_date >= NOW-18m`) → top-20 kNN → Cohere Rerank (Bedrock) → top-5 → Bedrock Agent.

## 5. Model orchestration

### 5.1 Framework choice

See `docs/architecture/framework_choice.md`.

- **Bedrock Agents + Bedrock Knowledge Bases** are the primary runtime (conversational, multi-tool). The Agent exposes retrieval + ICD-11 + trial lookup as tools.
- **LangChain** is used only for the semantic cache (`RedisSemanticCache` against ElastiCache Valkey + RediSearch) and per-session chat memory.

### 5.2 Router and lanes

A small Lambda classifier (Nova Micro, ~150 ms) picks the lane for each query:

| Question class | Model | Hyperparameters | Guardrail | Latency target |
|---|---|---|---|---|
| Emergency / acute | **Claude Haiku 4.5** (streaming) with optional Nova Lite distillation student behind a feature flag | `temperature=0.1, top_p=0.7, max_tokens=700, stop=[...]` | Strict PHI + emergency disclaimer | **≤ 2 s** |
| Complex differential | **Claude Sonnet 4.6** (streaming) | `temperature=0.2, top_p=0.9, max_tokens=1500` | Standard | 3–6 s |
| Literature / citation | Haiku 4.5, grounded-only mode | `temperature=0.1, top_p=0.7` | No-hallucination | 1.5–2 s |
| Patient-education phrasing | Haiku 4.5 with tone preset | `temperature=0.2, top_p=0.9` | Standard + tone | 1–2 s |

**Claude Opus is not used** — it's overkill for clinical QA at this token volume and its price is hard to justify next to Sonnet. If a query truly needs Opus-level reasoning (rare), it goes to a human specialist instead.

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

### 7.2 Phased rollout

| Phase | Weeks | Deliverable |
|---|---|---|
| 1 | 1–6 | Scheduled WHO + ICD-11 ingestion live, upload portal live, RAG with Haiku (fast) + Sonnet (complex); eval baseline |
| 2 | 7–10 | Distillation round 1: Sonnet generates Qs+answers from curated seed → clinician review → Nova Lite SFT → ship behind feature flag at 5% canary |
| 3 | 11–14 | Student at 100%; enable Bedrock Prompt Caching; add DPO preference-tuning; Reserved Tier on the emergency lane |
| 4 | quarterly | Retrain student on accumulated new clinician data + new WHO / ICD-11 |

### 7.3 Corporate integration

- **EHR launch** via SMART-on-FHIR iframe; the FHIR slice passed to Lambda is de-identified before it reaches the model.
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

Fine-tuned Nova Lite student (phase 3) shaves ~300–400 ms off that.

## 9. References

- [AWS Services in Scope by Compliance Program (HIPAA, etc.)](https://aws.amazon.com/compliance/services-in-scope/)
- [Architecting for HIPAA Security and Compliance on AWS](https://docs.aws.amazon.com/whitepapers/latest/architecting-hipaa-security-and-compliance-on-aws/architecting-hipaa-security-and-compliance-on-aws.html)
- [Amazon Bedrock Knowledge Bases — advanced parsing, chunking](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-advanced-parsing-chunking-and-query-reformulation-giving-greater-control-of-accuracy-in-rag-based-applications/)
- [Cache Prompts Between Requests — Bedrock](https://aws.amazon.com/bedrock/prompt-caching/)
- [AWS Site-to-Site VPN — user guide](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [Cognito SAML / OIDC federation](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-identity-federation.html)
- [Singapore PDPA — cross-border transfers](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers)

*Content above is rephrased for compliance with licensing restrictions.*
