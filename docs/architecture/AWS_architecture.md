# AWS Architecture — Nova Health Tech Clinical GenAI Assistant

## 1. Design goals (from the scenario)

| Requirement | Design response |
|---|---|
| Answer complex medical questions in natural language | Claude Sonnet 4.6 (reasoning) + Claude Haiku 4.5 (latency-critical) on Bedrock, routed by question class |
| Rely on internal trial reports + WHO + PubMed | Three-source RAG with Bedrock Knowledge Bases on OpenSearch Serverless |
| Auditable, regulation-compliant | Bedrock Guardrails + Comprehend Medical PHI detection + CloudTrail + Macie; HIPAA BAA signed with AWS |
| **2-second response for emergency care** | Haiku 4.5 (sub-second first token) + retrieval caching in ElastiCache Redis + hybrid sparse+dense search + streaming responses |
| Consistent tone + phrasing | System prompt library + optional fine-tune on Nova-style answers (Bedrock custom models) |
| Monthly WHO protocol refresh | EventBridge scheduled rule → Step Functions → re-index job (incremental) |
| Legacy PDFs, inconsistent tagging | Textract + Bedrock Data Automation (advanced parsing) → structured chunks; metadata filtering by speciality/date/source |
| Structured WHO API | Direct JSON ingest Lambda, bypassing PDF parsing |

## 2. Component diagram (textual)

```
                           ┌────────────────────────────────────────────────────────┐
                           │                   Hospital / Clinician                 │
                           │      (Web app, EHR iframe, or mobile companion)        │
                           └──────────────────────┬─────────────────────────────────┘
                                  HTTPS + SSO (SAML/OIDC via IAM Identity Center)
                                                  │
                                    ┌─────────────▼─────────────┐
                                    │   CloudFront + WAF        │   ← geo, rate, OWASP rules
                                    └─────────────┬─────────────┘
                                                  │
                                    ┌─────────────▼─────────────┐
                                    │  API Gateway (REST)       │
                                    │  + Cognito authorizer     │   ← per-physician JWT
                                    └─────────────┬─────────────┘
                                                  │
                         ┌────────────────────────▼─────────────────────────┐
                         │        Lambda: /chat  (streaming)                │
                         │        (in private VPC, no egress)               │
                         └───┬──────────┬────────────┬────────────┬─────────┘
                             │          │            │            │
                  1. PHI mask│ 2. Cache │ 3. Retrieve│ 4. Generate│ 5. Audit
                             ▼          ▼            ▼            ▼
            ┌───────────────────┐  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐
            │ Comprehend Medical │  │ElastiCache│  │ Bedrock KB   │  │ Bedrock Models   │
            │  detectPHI + Macie │  │  Redis    │  │ (multi-KB    │  │  Haiku 4.5 / Son │
            │  reversible tokens │  │(semantic  │  │  with meta   │  │  4.6 + Guardrail │
            │                    │  │ cache 10m)│  │  filters)    │  │                  │
            └────────────────────┘  └──────────┘  └──────┬───────┘  └────────┬─────────┘
                                                         │                   │
                                             Hybrid retrieval (BM25+vector)  │
                                                         │                   │
                                 ┌───────────────────────▼───────────┐       │
                                 │  OpenSearch Serverless (vector)   │       │
                                 │  — internal-trials index          │       │
                                 │  — who-guidelines index           │       │
                                 │  — pubmed index                   │       │
                                 │  + knn_vector (1024d, Nova MM)    │       │
                                 └───────────────────────────────────┘       │
                                                                             │
                                                                     ┌───────▼─────────┐
                                                                     │  CloudWatch +   │
                                                                     │  CloudTrail +   │
                                                                     │  S3 audit (OL)  │
                                                                     │  7-yr retention │
                                                                     └─────────────────┘

Ingestion (async, event-driven):

  S3 raw bucket ──► EventBridge ──► Step Functions
                                        │
                                        ├─► Bedrock Data Automation (PDF → structured text + images)
                                        │      (handles inconsistent tagging via LLM-assisted parsing)
                                        │
                                        ├─► Lambda chunker (semantic, 512 tokens, 15% overlap)
                                        │
                                        ├─► Bedrock embed (Nova Multimodal Embeddings — text+image fused)
                                        │
                                        └─► Bedrock Knowledge Base index sync

Monthly WHO refresh:

  EventBridge (cron: day 1 00:00 UTC)
     └─► Step Functions: poll WHO IRIS RSS + ICD-11 API
             └─► download to S3 ──► same ingestion pipeline (incremental, upsert on doc hash)
```

## 3. Data pipeline structure

### 3.1 Sources and ingestion

| Source | Format | Ingest path | Schedule | Chunking strategy |
|---|---|---|---|---|
| Internal clinical trial reports | Legacy PDF, inconsistent tagging | S3 `raw/protocols-pdf/` → Bedrock Data Automation | On upload + initial bulk | Section-aware (Abstract, Methods, Results, AEs); 512 tok, 15% overlap |
| WHO guideline PDFs | PDF (living documents) | S3 `raw/who-guidelines/` → Textract + Data Automation | Monthly cron + RSS webhook | Recommendation-aware; preserve evidence grade; keep page anchor for citation |
| WHO ICD-11 | JSON / FHIR via ICD API | Lambda → S3 `raw/icd/` → direct JSON chunker | Monthly | One chunk per code + description + inclusions/exclusions |
| PubMed abstracts | JSONL (MedRAG mirror) or XML (FTP baseline) | S3 `raw/pubmed/` → Lambda chunker | Daily delta | One chunk per abstract; MeSH tags as metadata |
| FDA drug labels | JSON (openFDA) | Lambda poll → S3 | Weekly | One chunk per section (dosing, contraindications, AEs) |

### 3.2 Parsing legacy PDFs (the hard case in the scenario)

Bedrock Data Automation (BDA) replaces a custom Textract pipeline:

- **BDA advanced parsing** uses a foundation model to handle inconsistent headings and OCR'd tables. No extra charge per the [AWS Bedrock KB parsing docs](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-advanced-parsing.html) beyond the Data Automation cost.
- Output: JSON with `{section_type, text, page, figures[], confidence}`.
- Fallback for low confidence: a Step Functions branch sends the page to a human-in-the-loop queue (Amazon A2I) before indexing.

### 3.3 Embedding choice

**Amazon Nova Multimodal Embeddings** (text + image + video + document) in a single 1024-dim vector space — lets the KB search surface a clinical trial diagram when a clinician asks "what does the TKI resistance pathway look like?". Chosen over Titan v2 because ~30% of the internal PDFs contain critical figures.

## 4. Model orchestration

### 4.1 Model routing

A Lambda router classifies each incoming query (single Haiku 4.5 call, ~150 ms) and chooses:

| Question class | Model | Guardrail | Typical latency |
|---|---|---|---|
| Emergency / acute (sepsis, stroke, MI) | **Claude Haiku 4.5** streaming | Strict PHI + emergency disclaimer | **≤ 2 s to first full answer**, sub-second to first token |
| Complex differential diagnosis | Claude Sonnet 4.6 | Standard | 3–6 s |
| Patient education / phrasing | Fine-tuned Nova Lite (Nova-voice) | Standard + tone | 1–2 s |
| Literature citation lookup | Haiku 4.5 + strict RAG-grounded mode | No-hallucination | 1.5–2 s |

### 4.2 Agent capabilities

Bedrock Agents expose three tools:

1. `retrieve_guideline(topic, latest_only=true)` — knowledge base retrieval with metadata filter `source=WHO` and `date >= NOW-90d`.
2. `lookup_trial(nct_id)` — direct fetch from ClinicalTrials.gov via Lambda.
3. `icd11_code(clinical_term)` — WHO ICD-11 lookup.

The agent cannot write to any PHI store — tools are read-only.

## 5. Security architecture

| Layer | Control |
|---|---|
| Account isolation | Separate AWS account per environment (prod/stage/dev) under AWS Organizations; SCP blocks non-HIPAA-eligible services in prod |
| Network | All Lambdas in private VPC; Bedrock accessed via VPC endpoints (no internet egress); OpenSearch in VPC; security groups deny-by-default |
| Identity | IAM Identity Center federated to hospital IdP; Cognito user pools for physician app; SSM Session Manager only for break-glass |
| Data at rest | S3 + OpenSearch + ElastiCache encrypted with customer-managed KMS keys; Macie scans buckets weekly for PHI leakage |
| Data in transit | TLS 1.3 everywhere; mTLS between Lambda and OpenSearch |
| PHI handling | Comprehend Medical DetectPHI on every inbound message → reversible tokenization (FPE via AWS Payment Cryptography or a KMS-backed custom Lambda). The model never sees raw PHI. |
| Prompt safety | Bedrock Guardrails: denied topics (self-diagnosis without clinician, illegal drug use), PHI filter, contextual grounding filter, prompt-injection filter |
| Audit | CloudTrail → S3 Object Lock (7-year retention per HIPAA §164.316); every model call logged via Bedrock invocation logs with request/response hash |
| Model risk | Guardrail grounding check: reject answers with `grounding_score < 0.7`; fall back to "I need more context from your latest trial report" |
| Secrets | No long-lived keys; IAM roles only. Any third-party API keys in Secrets Manager with rotation. |
| Business-associate agreement | AWS BAA covers Bedrock, S3, Lambda, API Gateway, CloudFront, OpenSearch, Comprehend Medical, etc. — see compliance doc for full list. |

## 6. Deployment approach

### 6.1 RAG first, fine-tune second

1. **Phase 1 — RAG only (weeks 1–6).** Bedrock KB + Claude Haiku/Sonnet. Delivers 80% of clinical accuracy without training. Cited answers only.
2. **Phase 2 — Tone fine-tune (weeks 7–10).** After we collect 5–10k approved Q&A pairs, fine-tune **Amazon Nova Lite** on Bedrock custom models (LoRA-style adapter) for "Nova-voice" — the consistent tone/phrasing the scenario calls out. Keep RAG in the loop so knowledge stays current.
3. **Phase 3 — Domain adapter (quarter 2).** If evaluation shows recurring factual gaps on rare specialities, do a second SFT on a domain-specific dataset (e.g., rare oncology). Never put PHI in training data — synthesize with de-identification first.

Rationale: fine-tuning cannot hit the "monthly WHO updates" requirement alone; only RAG can. Fine-tuning hits the "consistent tone" requirement. Both are needed.

### 6.2 Hybrid or on-prem option for strict hospitals

Core deploy is **public cloud with VPC isolation** (region: `us-east-1` for HIPAA BAA; `eu-central-1` mirror for EU hospitals). For hospital clients that require on-prem:

- **AWS Outposts** rack at the hospital data center — runs the same API Gateway + Lambda + OpenSearch locally, syncs de-identified embeddings back to the central account.
- **Local caching model**: Bedrock is cloud-only, so the Outposts rack calls Bedrock over AWS Direct Connect with a local semantic cache (ElastiCache) that keeps hot guideline chunks < 5 ms away. If cache-hit ratio stays ≥ 70% (achievable for recurring emergency protocols), the p99 latency target is preserved even on intermittent WAN.

### 6.3 Corporate integration

- **EHR (Epic/Cerner) launch** — SMART-on-FHIR iframe launch; the current patient chart context is passed as FHIR resources → Lambda de-identifies → Bedrock agent.
- **SSO** — SAML 2.0 via IAM Identity Center.
- **Audit export** — nightly CSV to hospital's SIEM via AWS Security Hub + S3 replication.

## 7. Performance optimization (hitting the 2-second SLA)

| Technique | Savings | Notes |
|---|---|---|
| Haiku 4.5 for emergency lane | ~3× vs Sonnet | Routed automatically by classifier |
| Streaming response (`invoke_model_with_response_stream`) | Time-to-first-token < 600 ms | Physician starts reading while model finishes |
| Semantic response cache in ElastiCache | 30–45% hit rate expected for common emergency protocols | TTL = 10 min, key = hash(embedding of normalized query) |
| Hybrid BM25 + kNN retrieval | Recall@5 ↑ 8–12% | OpenSearch Serverless supports both in one query |
| Metadata pre-filter (`specialty`, `date`) | Fewer candidates to rerank | Keeps retrieval under 80 ms |
| Smaller chunks (256 vs 512) with richer metadata | Better precision, faster re-rank | 256 for WHO guidelines, 512 for trial reports |
| Provisioned throughput for Bedrock during peak ER hours | Eliminates cold-start | Reserved capacity pays off above ~300 req/min |
| Edge response via CloudFront Functions for cached FAQ | < 50 ms | "What's the latest sepsis bundle?" type questions |
| OpenSearch Serverless auto-scaling OCUs | Consistent retrieval latency | Set min = 4, max = 20 search OCUs |

**Measured target budget (emergency lane):**

```
  200 ms  → API Gateway + Cognito auth
  100 ms  → PHI detect + tokenize
   80 ms  → KB retrieval (hybrid)
  600 ms  → Haiku first token
  900 ms  → Haiku full answer (200 tokens)
  120 ms  → Guardrail grounding + output
-------
 2000 ms  ← target
```

## 8. What gets built vs. bought

| Custom code | Managed services used |
|---|---|
| Router Lambda | Bedrock (models, KB, agents, guardrails) |
| PHI tokenizer helper | Comprehend Medical |
| EHR SMART-on-FHIR adapter | OpenSearch Serverless |
| Evaluation harness (LLM-as-judge) | Bedrock Data Automation |
| Frontend (React + right-panel chat) | CloudFront, API Gateway, Cognito, ElastiCache, KMS, CloudTrail, Macie |

## 9. References

- [AWS Prescriptive Guidance — Creating RAG solutions on AWS for healthcare](https://docs.aws.amazon.com/prescriptive-guidance/latest/rag-healthcare-use-cases/introduction.html)
- [HIPAA compliance for generative AI solutions on AWS](https://aws.amazon.com/blogs/industries/hipaa-compliance-for-generative-ai-solutions-on-aws/)
- [How to safeguard healthcare data privacy using Amazon Bedrock Guardrails](https://aws.amazon.com/blogs/publicsector/how-to-safeguard-healthcare-data-privacy-using-amazon-bedrock-guardrails/)
- [Introducing multimodal retrieval for Amazon Bedrock Knowledge Bases](https://aws.amazon.com/blogs/machine-learning/introducing-multimodal-retrieval-for-amazon-bedrock-knowledge-bases/)
- [Amazon Nova Multimodal Embeddings model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html)
- [Fine-tuning LLMs in healthcare — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/generative-ai-nlp-healthcare/fine-tuning.html)

*Content above is rephrased for compliance with licensing restrictions.*
