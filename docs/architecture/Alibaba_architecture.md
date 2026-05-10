# Alibaba Cloud Architecture — Nova Health Tech Clinical GenAI (Production)

Parallel production design using Qwen and Alibaba Cloud managed services in the **Singapore region**. Same production scope as the AWS plan: real hundreds-of-documents RAG, scheduled ingestion + internal upload portal, fine-tuned student for the 2-second emergency lane, full compliance posture.

## 1. Why Qwen on Alibaba in Singapore

- Qwen3 / Qwen3.5 / Qwen3.6 models are open-weight and natively fine-tunable on PAI (SFT + LoRA + QLoRA + DPO + GRPO — confirmed in `askAli_AI_Assistant.txt`).
- Qwen is available natively in the **Singapore** Model Studio region.
- `qwen3-vl-embedding` (multimodal, fused) is the recommended embedding for the WHO PDFs mixing text, tables, and figures — per `askAli_AI_Assistant.txt`.
- Qwen pricing is 5–10× cheaper per token than Claude; at Nova's volume the monthly inference bill is materially smaller.
- Alibaba Singapore holds ISO 27001 / 27017 / 27018 / 27701, SOC 1/2/3, and aligns with PDPA obligations for a data-intermediary role.

## 2. Region and data residency

- **Primary region: Singapore.** Model Studio, PAI, OpenSearch Vector Search, OSS, Tair, FC, ActionTrail all present.
- **Keep data in Singapore.** Avoids the PDPA transfer-limitation obligation; matches the AWS plan for regulatory symmetry.
- **No on-prem (Apsara Stack) in scope.** Hospital connects over Site-to-Site IPsec VPN; Alibaba Singapore region is close enough.

## 3. Component diagram

```
              ┌──────────────────────────────────────────────────────────────┐
              │   Hospital network (clinician workstations + EHR)            │
              └──┬──────────────────────────────────────────────┬────────────┘
                 │                                              │
         AI chat │                                Internal mgmt │ HTTPS over
                 │ HTTPS                                         │ IPsec VPN
                 ▼                                               ▼
     ┌──────────────────────┐                      ┌──────────────────────────┐
     │ Anti-DDoS + WAF +    │                      │ Customer Gateway on-prem │
     │ Alibaba CDN          │                      └──────────┬───────────────┘
     └──────┬───────────────┘                                 │
            │                                                 │
     ┌──────▼──────────┐   ───── Site-to-Site IPsec VPN ─────►│ VPN Gateway
     │ API Gateway     │                                      │ (private side)
     │  + RAM / IDaaS  │                                      └──────────┬───────────┘
     │    authorizer   │                                                 │
     └──────┬──────────┘                                                 ▼
            │                                                 ┌──────────────────────┐
            │                                                 │ Private SLB + IDaaS  │
            │                                                 │ OIDC/SAML ← EntraID  │
            │                                                 │                      │
            │                                                 │ SAE container:       │
            │                                                 │  Upload Portal       │
            │                                                 │  (internal UI)       │
            │                                                 └──────────┬───────────┘
            │                                                            │
            ▼                                                            ▼
   ┌──────────────────────────────┐                        ┌──────────────────────────┐
   │ Function Compute /chat (VPC) │                        │ OSS raw bucket            │
   │  0. authn (RAM/IDaaS token)  │◄──── semantic cache ──┤ /raw/scheduled/...        │
   │  1. PHI mask (DataWorks SDDP) │     hit returns early │ /raw/manual/...           │
   │  2. router (Qwen-Flash)       │                       │ /raw/icd11/...            │
   │  3. route to Agent / Workflow │                       │ /raw/who/...              │
   │     (Model Studio Application)│                       └──────────┬───────────────┘
   │  4. ground-check + audit      │                                  │ ObjectCreated
   └─────┬──────────────┬──────────┘                                  ▼
         │              │                                ┌──────────────────────────┐
 Layer 1 │    Layer 2   │  Generation                    │ Function Workflow        │
 Tair    │    Qwen      │  (Model Studio / PAI-EAS):     │  DocMind parse → chunk → │
 +Tair   │    Context   │    Qwen-Flash (fast lane)      │  embed → KB sync         │
 Vector  │    Cache     │    Qwen-Max (complex + teacher)│                          │
 semantic│              │    Qwen3-8B student (phase 3)  │ + Security Center scan   │
 cache   │              │  + Content Moderation          │ + SDDP PHI scan          │
         │              │                                └──────────┬───────────────┘
         │              │                                           ▼
         │              │                             ┌────────────────────────────┐
         │              │                             │ Model Studio Knowledge Base│
         │              │                             │  kb-who-guidelines         │
         │              │                             │  kb-internal-trials        │
         │              │                             │  kb-treatment-protocols    │
         │              │                             │  kb-icd11                  │
         │              │                             │  on OpenSearch Vector      │
         │              │                             │  Search Edition            │
         │              │                             │  + text-embedding-v4       │
         │              │                             │  + qwen3-vl-embedding      │
         │              │                             └────────────────────────────┘
         ▼              ▼
  All traffic logged → ActionTrail → SLS → OSS (WORM, 6-yr retention)
```

## 4. Data pipeline

See `docs/architecture/rag_strategy.md`. Summary for Alibaba:

- **Parser**: DocMind handles general PDFs; PAI pipeline invokes **Qwen-VL-Max** on pages flagged as complex (multi-page tables, flowcharts).
- **Chunking**: hierarchical 1500/300 tokens, 15% overlap, section-aware — same as AWS side.
- **Embeddings**: `text-embedding-v4` for text chunks; `qwen3-vl-embedding` with `enable_fusion=True` (2560-dim) for figure-bearing chunks.
- **Vector store**: **OpenSearch Vector Search Edition**; Model Studio embedding plugin handles re-vectorization on upload.
- **Retrieval**: hybrid kNN + BM25, metadata pre-filter, `gte-rerank` for reranking before generation.

## 5. Model orchestration

### 5.1 Framework — Model Studio Application

See `docs/architecture/framework_choice.md`. Two application types per Alibaba's own docs:

- **Agent application** — conversational; LLM decides which tools / RAG to call. Used for the general clinical chat.
- **Workflow application** — deterministic DAG (retrieve → prompt → generate → moderation). Used for the emergency lane, where the path is fixed and auditability matters most.

**LangChain** is used only for the semantic cache (against Tair + TairVector) and chat memory, same as the AWS side.

### 5.2 Router and lanes

A small FC classifier (Qwen3.5-Flash, ~200 ms) picks the lane:

| Question class | Model | Hyperparameters | Guardrail | Latency target |
|---|---|---|---|---|
| Emergency / acute | **Qwen3.5-Flash** (streaming) with optional Qwen3-8B distillation student behind a feature flag | `temperature=0.1, top_p=0.7, top_k=40, seed=42` | Strict PHI + emergency disclaimer | **≤ 2 s** |
| Complex differential | **Qwen-Max (Qwen3-Max)** (streaming) | `temperature=0.2, top_p=0.9` | Standard | 3–6 s |
| Literature / citation | Qwen3.5-Flash, grounded-only mode | `temperature=0.1, top_p=0.7, top_k=40` | No-hallucination | 1.5–2 s |
| Patient-education phrasing | Qwen3.5-Flash with tone preset | `temperature=0.2, top_p=0.9` | Standard + tone | 1–2 s |

Qwen APIs are OpenAI-compatible, so the same router code works against Model Studio's Singapore endpoint (`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`). Qwen supports `seed`, which we pin per deployment to maximize determinism.

### 5.3 Agent tools (Model Studio plug-ins)

- `retrieve_guideline(topic, source=WHO, max_age_days=90)` — KB retrieval.
- `retrieve_trial(doc_id)` — internal KB.
- `icd11_lookup(term, mode)` — FC calling the live WHO ICD-11 API.
- `icd11_expand_query(term)` — silent query expansion for retrieval.

All tools are read-only.

## 6. Security architecture

| Layer | Control |
|---|---|
| Account isolation | Resource Directory + Control Policy Service; one account per env in Singapore |
| Network | FC in VPC; Model Studio + PAI-EAS via PrivateLink; OpenSearch Vector in VPC; no public egress from the chat FC |
| Identity — clinicians | **Alibaba IDaaS (Cloud Identity)** user pool federated via SAML/OIDC to each hospital's IdP (EntraID / Okta / ADFS); MFA enforced in IdP |
| Identity — Nova staff | **Cloud SSO + RAM** federated to Nova's EntraID; short-lived SSO credentials |
| Hospital ↔ cloud | **Site-to-Site IPsec VPN** on VPN Gateway (IKEv2 + AES-256-GCM + SHA-2), dual-tunnel HA |
| Data at rest | OSS, OpenSearch, Tair, Credentials Manager all on KMS BYOK |
| Data in transit | TLS 1.3; ASM for mTLS |
| PHI handling | DataWorks Data Security Guard + SDDP classify → reversible tokenization in FC (KMS-backed) |
| LLM safety | Content Moderation 2.0 for generative AI — medical misinformation, jailbreak, PII, bias filters |
| Audit | ActionTrail → SLS → OSS WORM with **6-year retention** (HIPAA §164.530(j)); Model Studio observability captures every call |
| Ingestion safety | Security Center scan on uploaded PDFs; SDDP PHI scan; quarantine + notify on leak |
| Secrets | Credentials Manager with KMS + rotation FC for WHO ICD-11 OAuth client |
| Compliance | ISO 27001/17/18/27701, SOC 1/2/3, PDPA alignment in Singapore region |

## 7. Deployment approach

### 7.1 Public cloud in Singapore; VPN for the hospital

- All Alibaba services in Singapore; multi-AZ where applicable.
- Hospital integration over Site-to-Site IPsec VPN — no dedicated line unless a customer specifically requests one.
- DR via cross-AZ within Singapore; a warm-standby region is a roadmap item with PDPA review.

### 7.2 Phased rollout

| Phase | Weeks | Deliverable | Typical cost |
|---|---|---|---|
| 1 | 1–6 | Scheduled WHO + ICD-11 ingestion live, upload portal live, RAG with Qwen-Flash (fast) + Qwen-Max (complex) | Low hundreds of USD/mo |
| 2 | 7–10 | Distill Qwen3-8B student from Qwen-Max outputs; LoRA on PAI Model Gallery | ~$30–100 per retrain |
| 3 | 11–14 | Student at 100% via PAI-EAS; enable Qwen Context Cache (implicit + explicit); PTU on emergency lane | Marginal; PTU only when sustained TPM high |
| 4 | quarterly | Retrain with new WHO + clinician data | < $100 per retrain |

### 7.3 Corporate integration

See `docs/architecture/corporate_integration.md` for the full EHR/FHIR + SharePoint design.

- **EHR launch** via **SMART App Launch v2** against Epic / Cerner (Oracle Health) / Allscripts on FHIR R4; Function Compute de-identifies the patient slice (DataWorks SDDP) before calling Model Studio. Read-only scopes only.
- **SharePoint / OneDrive** — Microsoft Graph webhooks → Function Compute → OSS → ingestion pipeline.
- **Clinician SSO** — IDaaS federation per hospital tenant.
- **Admin SSO** — Cloud SSO → Nova's EntraID.
- **Audit export** — SLS → OSS nightly → hospital SIEM.

## 8. Performance — closing the 2-second budget

See `docs/architecture/caching_strategy.md`. Representative p95 emergency path:

```
     25 ms   Tair semantic cache hit (Layer 1; 30–45% of emergency queries)
    100 ms   IDaaS auth + PHI mask
     70 ms   OpenSearch Vector hybrid retrieval + rerank
    300 ms   Qwen3.5-Flash first-token (with Qwen Context Cache hit)
  1,100 ms   Qwen3.5-Flash full answer (250 tokens, streaming)
    110 ms   Moderation + citation check
  ────────
   ≤ 1,700 ms  p95
```

## 9. References

- [Text generation — Alibaba Cloud Model Studio (service regions include Singapore)](https://www.alibabacloud.com/help/en/model-studio/text-generation)
- [Agent vs Workflow Applications in Model Studio](https://www.alibabacloud.com/help/en/model-studio/application-introduction)
- [AI Agent Architecture with LLM and Tools — Alibaba](https://www.alibabacloud.com/help/en/model-studio/getting-started/application-building-instructions)
- [Context Cache for Qwen models](https://www.alibabacloud.com/help/en/model-studio/context-cache)
- [Multimodal embeddings — Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings)
- [Alibaba Cloud VPN Gateway — IPsec-VPN](https://www.alibabacloud.com/help/en/vpn/)
- [Alibaba IDaaS — overview](https://www.alibabacloud.com/help/en/idaas/)
- [Singapore PDPA — cross-border transfers](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers)

*Content above is rephrased for compliance with licensing restrictions.*
