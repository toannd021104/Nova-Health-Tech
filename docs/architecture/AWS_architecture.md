# AWS Architecture — Nova Health Tech Clinical GenAI Assistant (Production Plan)

Production design for the AI assistant service. The web UI can stay simple and publicly accessible for verification, but the AI service itself (model serving, RAG, data pipeline, security) is sized for the real clinical workload: hundreds of source documents, hundreds of physicians, and monthly WHO refreshes.

## 1. Design goals (from the scenario)

| Requirement | Design response |
|---|---|
| Answer complex medical questions in natural language | Two-lane model strategy: **Claude Sonnet 4.6** (teacher, complex) + a **fine-tuned Nova Lite student** distilled from Sonnet+RAG outputs for the fast lane |
| Rely on internal trial reports + WHO + ICD-11 | Hierarchical RAG in Bedrock Knowledge Bases on OpenSearch Serverless; BDA advanced parsing for complex PDFs; ICD-11 API used three ways (see `docs/architecture/rag_strategy.md`) |
| Auditable, regulation-compliant | Bedrock Guardrails + Comprehend Medical + Macie + CloudTrail to S3 Object Lock (7-yr); HIPAA BAA with AWS |
| **2-second emergency response** | Fine-tuned small student + semantic cache + Bedrock prompt caching + streaming (see `docs/architecture/caching_strategy.md`) |
| Consistent tone | Distillation corpus from Sonnet; low-temperature sampling; fixed system-prompt template (see `docs/architecture/fine_tuning_and_distillation.md` §hyperparameters) |
| Monthly WHO refresh | EventBridge → Step Functions → incremental KB sync |
| Legacy PDFs, inconsistent tagging | Bedrock Data Automation (advanced parsing) with figure extraction; multimodal embeddings on figure-bearing chunks |
| Structured WHO API | Direct JSON ingest via Function + runtime tool call via Bedrock Agents |

## 2. Component diagram

```
                           ┌────────────────────────────────────────────────────────┐
                           │                   Clinician / Hospital                 │
                           │   (Web app, EHR SMART-on-FHIR iframe, mobile)          │
                           └──────────────────────┬─────────────────────────────────┘
                                  HTTPS + SSO (SAML/OIDC via Cognito + IAM IdC)
                                                  │
                                    ┌─────────────▼─────────────┐
                                    │   CloudFront + WAF        │
                                    └─────────────┬─────────────┘
                                                  │
                                    ┌─────────────▼─────────────┐
                                    │  API Gateway (REST + WS)  │
                                    │  + Cognito authorizer     │
                                    └─────────────┬─────────────┘
                                                  │
                         ┌────────────────────────▼─────────────────────────┐
                         │        Lambda /chat (in private VPC)             │
                         │   0. authn/z, 1. PHI mask, 2. classify,          │
                         │   3. cache check, 4. retrieve, 5. generate,      │
                         │   6. ground check, 7. audit                      │
                         └─┬─────────┬─────────────┬────────────┬─────┬─────┘
                           │         │             │            │     │
               Comprehend  │ Layer 1 │   Layer 2   │   Gen      │ Log │
                 Medical   │ Redis   │   Bedrock   │ (students, │     │
                 DetectPHI │ semantic│   Prompt    │  teacher)  │     │
                           │ cache   │   Cache     │            │     │
                           ▼         ▼             ▼            ▼     ▼
            ┌──────────────────┐ ┌──────────┐ ┌─────────────────┐ ┌──────────────┐
            │ de-id/tokenize   │ │ElastiCache│ │  Bedrock        │ │ CloudWatch   │
            │ via KMS          │ │ Valkey/   │ │  ┌────────────┐ │ │ CloudTrail   │
            │                  │ │ RediSearch│ │  │ Sonnet 4.6 │ │ │ → S3 WORM    │
            └──────────────────┘ └──────────┘ │  │ (teacher)  │ │ │ 7-yr retn    │
                                              │  │ Nova Lite  │ │ └──────────────┘
                                              │  │ (student,  │ │
                                              │  │ fine-tuned)│ │
                                              │  └────────────┘ │
                                              │  + Guardrails   │
                                              └────────┬────────┘
                                                       │
                                         ┌─────────────▼─────────────┐
                                         │ Bedrock Knowledge Bases   │
                                         │  - kb-who-guidelines      │
                                         │  - kb-internal-trials     │
                                         │  - kb-icd11               │
                                         │ on OpenSearch Serverless  │
                                         │ (hybrid kNN + BM25)       │
                                         │  + Titan Embed Text v2    │
                                         │  + Nova Multimodal Emb    │
                                         └─────────────┬─────────────┘
                                                       │
                                         metadata index + chunk store

Ingestion (async, event-driven):

  S3 raw bucket ──► EventBridge ──► Step Functions
      ├── Bedrock Data Automation (advanced parsing: text + tables + figures)
      ├── Lambda chunker (hierarchical 1500/300 tok, 15% overlap)
      ├── Bedrock embed (Titan v2 for text; Nova Multimodal for figure chunks)
      ├── Macie scan for PHI leakage (quarantine if found)
      └── Bedrock Knowledge Base sync (incremental, upsert on doc-hash)

Monthly refresh:

  EventBridge cron (day 1, 00:00 UTC)
   └── Step Functions workflow
         ├── GET WHO guidelines index (RSS)   → diff → download changed PDFs
         ├── GET WHO ICD-11 /mms delta        → diff → upsert JSON
         └── trigger ingestion pipeline for changed docs

Distillation (quarterly):

  S3 training-data bucket ◄── Bedrock Batch (Sonnet, 50% off, generates answers)
        └── clinician review via A2I ── DPO pair builder
              └── Bedrock custom model job ── Nova Lite student (SFT + pref tune)
                    └── eval harness (LLM-as-judge) ── promote to prod if pass
```

## 3. Data pipeline structure

See `docs/architecture/rag_strategy.md` for the three candidate strategies and the recommendation (managed parse + managed RAG, with multimodal-embedding fallback for figure-heavy pages).

### 3.1 Sources

| Source | Format | Ingest path | Schedule | Chunking |
|---|---|---|---|---|
| Internal clinical trial reports | Legacy PDF, inconsistent tagging | S3 → Bedrock Data Automation | On upload + bulk backfill | Hierarchical 1500/300 tokens, 15% overlap; section-aware |
| WHO guideline PDFs | PDF (100+ pages, tables + figures + flowcharts) | S3 → Bedrock Data Automation (advanced parsing) | Monthly cron + RSS watcher | Same hierarchical + figure extraction |
| WHO ICD-11 | JSON via ICD-11 API | Lambda → S3 → Lambda chunker | Monthly full walk + daily delta | One chunk per entity |
| (Future) External literature | JSONL / XML | Lambda → S3 | Daily delta | One chunk per abstract |

### 3.2 Parsing and embedding

- **Bedrock Data Automation** with advanced parsing handles text, tables (preserves 2-D structure), figures (extracts and captions), and layout metadata.
- **Text chunks** → Titan Embed Text v2 (1024-dim).
- **Figure-bearing chunks** → Amazon Nova Multimodal Embeddings (fuses the page text + cropped figure into one vector), enabling "show me the dosing flowchart" queries.
- **OpenSearch Serverless** holds both indexes; a single retrieval call does hybrid kNN + BM25 over both.

### 3.3 ICD-11 API as a first-class source

Three integration points; see `docs/architecture/rag_strategy.md` §"ICD-11 API is a first-class source".

- Credentials live in **AWS Secrets Manager** (`nova/who-icd/client_id`, `nova/who-icd/client_secret`), rotated via Lambda; Secrets Manager KMS-encrypted.
- Access is via a short-lived Bearer token that the Lambda fetches on cold start and refreshes before expiry.

## 4. Model orchestration

### 4.1 Router

A small Lambda classifier (optionally Nova Micro) picks the lane for each query:

| Question class | Model | Temperature / top_p / top_k | Guardrail | Latency target |
|---|---|---|---|---|
| Emergency / acute | **Fine-tuned Nova Lite student** (streaming) | 0.1 / 0.7 / 40 | Strict PHI + emergency disclaimer injector | **≤ 2 s** |
| Complex differential | **Claude Sonnet 4.6** (streaming) | 0.2 / 0.9 / — | Standard | 3–6 s |
| Literature / citation lookup | Student, grounded-only mode | 0.1 / 0.7 / 40 | No-hallucination | 1.5–2 s |
| Patient-education phrasing | Student with tone-preset system prompt | 0.2 / 0.9 / 40 | Standard + tone | 1–2 s |

Until the student is trained and evaluated, the emergency lane uses **Claude Haiku 4.5** unmodified as a fallback — still hits the SLA, just without the tone/accuracy gains distillation brings.

### 4.2 Agent tools (Bedrock Agents)

- `retrieve_guideline(topic, source=WHO, max_age_days=90)` — KB retrieval with metadata pre-filter.
- `lookup_trial(nct_id)` — Lambda fetching ClinicalTrials.gov at request time.
- `icd11_lookup(term, mode)` — Lambda hitting the WHO ICD-11 API (`/mms/search` or `/mms/{id}`) for live authoritative codes and synonyms.
- `icd11_expand_query(term)` — used silently by the retrieval stage to expand the hybrid BM25 query with ICD-11 synonyms.

All tools are read-only; no tool can write to any PHI store.

## 5. Security architecture

Summary below; full mapping in `docs/compliance/security_compliance.md`.

| Layer | Control |
|---|---|
| Account isolation | AWS Organizations; one account per env; SCP bans non-HIPAA-eligible services in prod |
| Network | Lambdas in private VPC; Bedrock via VPC endpoints; OpenSearch Serverless in VPC; no Internet egress |
| Identity | IAM Identity Center → hospital IdP; Cognito user pools for the app; MFA enforced |
| Data at rest | S3, OpenSearch, ElastiCache, Secrets Manager all on customer-managed KMS keys |
| Data in transit | TLS 1.3; mTLS internally |
| PHI handling | Comprehend Medical DetectPHI on inbound → reversible tokenization → model never sees raw PHI. Macie weekly on raw S3. |
| LLM safety | Bedrock Guardrails: denied topics, PHI filter, contextual grounding ≥ 0.7, prompt-injection filter. A guardrail fail blocks response and is logged. |
| Audit | CloudTrail → S3 Object Lock 7 yr; Bedrock invocation logging captures request/response hashes |
| Model risk | Evaluation harness gates every student retrain; production pins a specific model version |
| Secrets | Secrets Manager with KMS + automatic rotation for the ICD-11 API credential |
| BAA | AWS BAA covers all services in this design — verify current list before launch |

## 6. Deployment approach

### 6.1 Public cloud by default, hybrid available

- **Primary**: Bedrock + OpenSearch Serverless in `us-east-1`; mirror in `eu-central-1` for EU hospitals.
- **Hybrid on request**: AWS Outposts rack at the hospital data center runs the frontend + API + ElastiCache + an OpenSearch cache locally; Bedrock calls go over AWS Direct Connect. Keeps sub-ms local cache hits for the hottest protocols.

### 6.2 Phased rollout

| Phase | Weeks | Deliverable |
|---|---|---|
| 1 | 1–6 | RAG-only with Claude Haiku on the fast lane; Sonnet on the slow lane; evaluation harness baseline |
| 2 | 7–10 | Distillation round 1: Sonnet generates Qs+answers → clinician review → Nova Lite SFT → ship student behind a feature flag with canary 5% |
| 3 | 11–14 | Student at 100%; add DPO from clinician preferences; enable Bedrock prompt caching and reserved-tier on peak hours |
| 4 | quarterly | Retrain student on accumulated new clinician data + new WHO guidelines |

### 6.3 Corporate integration

- **EHR launch** via SMART-on-FHIR iframe; patient-chart slice passed to Lambda as FHIR resources, de-identified, then attached to the prompt.
- **SSO** — SAML 2.0 via IAM Identity Center.
- **Audit export** — nightly CSV to hospital SIEM via S3 Cross-Region Replication.

## 7. Performance optimization — how the 2-second budget closes

See `docs/architecture/caching_strategy.md` for full details; summary:

```
     20 ms   Semantic cache hit (30–45% of emergency queries)        ← return fast
    100 ms   Authn + PHI mask
     60 ms   Hybrid retrieval (metadata-filtered, top-20 kNN+BM25)
    400 ms   Student model first-token (with prompt cache hit)
  1,200 ms   Student full answer (250 tokens, streaming)
    120 ms   Guardrail + grounding + citation validation
  ────────
  ≤ 1,900 ms  p95 emergency budget
```

The combination matters: fine-tuned small model alone isn't enough; caching alone isn't enough; hybrid retrieval alone isn't enough. The three together, plus streaming, give the SLA.

## 8. References

- [AWS Prescriptive Guidance — Creating RAG solutions on AWS for healthcare](https://docs.aws.amazon.com/prescriptive-guidance/latest/rag-healthcare-use-cases/introduction.html)
- [HIPAA compliance for generative AI solutions on AWS](https://aws.amazon.com/blogs/industries/hipaa-compliance-for-generative-ai-solutions-on-aws/)
- [Amazon Bedrock Knowledge Bases — advanced parsing & chunking](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-advanced-parsing-chunking-and-query-reformulation-giving-greater-control-of-accuracy-in-rag-based-applications/)
- [Cache Prompts Between Requests — Bedrock](https://aws.amazon.com/bedrock/prompt-caching/)
- [Fine-tuning LLMs in healthcare — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/generative-ai-nlp-healthcare/fine-tuning.html)
- [WHO ICD-11 API Swagger](https://id.who.int/swagger/index.html)

*Content above is rephrased for compliance with licensing restrictions.*
