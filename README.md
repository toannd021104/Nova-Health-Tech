# Nova Health Tech — Clinical GenAI Assistant

Production proposal for Nova Health Tech's clinical decision-support GenAI assistant. Three architecture versions, all **primary region Singapore**: Version A (AWS + Claude), Version B (AWS + Qwen), Version C (Alibaba + Qwen).

## Scope

- **AI service — production.** Hundreds-of-documents RAG (WHO guidelines + internal clinical trial reports + treatment protocols + WHO ICD-11 API), managed parsing for complex PDFs (horizontal/vertical tables, text-based flowcharts, figures), fine-tuned small-model student distilled from a large-model teacher for the 2-second emergency SLA, scheduled ingestion + internal upload portal over Site-to-Site VPN, hospital-IdP federation, full compliance posture (Singapore PDPA + HCSA; HIPAA when US clients are onboarded).
- **Web UI — demo.** A lightweight publicly-accessible web page with a right-hand AI assistant panel for stakeholder verification. See `aws-demo/`.

## Map

```
.
├── README.md                                          ← this file
├── SESSION_HANDOFF.md                                 ← context for continuing in a new Kiro session
├── askAli_AI_Assistant.txt                            ← vendor research (kept for reviewers)
│
├── docs/                                              ← proposal docs (consolidated to 8)
│   ├── overview.md                                     ← 3-version big picture + decision tree
│   ├── rag_and_pipelines.md                            ← shared RAG + ingestion + multi-agent + framework + caching + EHR
│   ├── customization.md                                ← SFT / DPO / GRPO / distillation per version
│   ├── regional_services.md                            ← live-verified AWS + Alibaba service availability matrix
│   ├── compliance.md                                   ← PDPA / HIPAA / HCSA / FDA / EU AI Act / audit 6-yr
│   ├── proposals/
│   │   ├── version_a_aws_claude.md                     ← Version A — AWS + Claude (SG)
│   │   ├── version_b_aws_qwen.md                       ← Version B — AWS + Qwen (Bedrock Sydney)
│   │   └── version_c_alibaba_qwen.md                   ← Version C — Alibaba + Qwen (SG) [recommended default]
│   └── architecture/
│       └── diagrams/
│           └── aws_workflow.svg                        ← numbered workflow diagram
│
├── poc/                                               ← 10-day interview POC
│   ├── README.md                                       ← scope + cost math for 100 questions
│   ├── aws_claude/                                     ← Version A POC (~$165, no fine-tuning)
│   └── aws_qwen/                                       ← Version B POC (~$197, includes SFT on Qwen3-4B)
│
├── data/                                              ← REAL source data for RAG
│   ├── README.md
│   ├── who/                                            ← 8 WHO guideline PDFs
│   ├── icd11/                                          ← 316 live entity JSONs via WHO ICD-11 API
│   └── clinical-trials/
│       ├── protocols/                                  ← drop internal trial PDFs here
│       └── departments/                                ← 36 open-access PMC papers for 12 demo departments
│
├── scripts/
│   ├── download_who_icd.py                             ← live WHO ICD-11 API (OAuth2)
│   ├── download_clinicaltrials.py                      ← ClinicalTrials.gov v2 API
│   ├── download_department_refs.py                     ← PMC open-access PDFs per department
│   └── ingest_to_bedrock_kb.py                         ← push /data to S3 + trigger KB sync
│
└── aws-demo/                                          ← simple public web UI + Lambda → Bedrock
    ├── frontend/
    ├── backend/
    ├── template.yaml
    ├── README.md
    └── ec2/                                            ← DEPLOYED demo on t4g.small SG (LangGraph + FAISS)
        ├── deploy.py
        ├── setup_instance.py
        ├── user_data.sh
        ├── NAMING.md                                   ← HA-<b64> resource map
        ├── README.md
        └── app/                                        ← FastAPI + LangChain + LangGraph
            ├── graph.py                                ← classify → retrieve → answer
            ├── rag.py                                  ← FAISS + Cohere Embed v4 on Bedrock
            ├── server.py                               ← /api/chat + optional EntraID OIDC
            └── static/
```

## Read order

1. [`docs/overview.md`](docs/overview.md) — 3-version big picture + decision tree + common design
2. [`docs/proposals/version_c_alibaba_qwen.md`](docs/proposals/version_c_alibaba_qwen.md) — recommended default (SG-native, cheapest, zero cross-region)
3. [`docs/proposals/version_a_aws_claude.md`](docs/proposals/version_a_aws_claude.md) — AWS + Claude/Nova
4. [`docs/proposals/version_b_aws_qwen.md`](docs/proposals/version_b_aws_qwen.md) — AWS + Qwen (Sydney)
5. [`docs/rag_and_pipelines.md`](docs/rag_and_pipelines.md) — shared RAG, ingestion, multi-agent, framework, caching, EHR integration
6. [`docs/customization.md`](docs/customization.md) — SFT / DPO / GRPO / distillation per version
7. [`docs/regional_services.md`](docs/regional_services.md) — live-verified service availability matrix
8. [`docs/compliance.md`](docs/compliance.md) — PDPA / HIPAA / HCSA / FDA / EU AI Act / audit retention

## Key production decisions (summary)

| Decision | AWS (Versions A + B) | Alibaba (Version C) |
|---|---|---|
| **Region** | `ap-southeast-1` (Singapore); Qwen falls back to Sydney `ap-southeast-2` | Singapore International (SG-native) |
| **Cross-region hops at query time** | 2 (Tokyo embed+rerank) for A · 2–3 (Sydney chat + Tokyo) for B | **0** |
| **Hospital integration** | AWS Site-to-Site VPN (IKEv2) — no Outposts / Direct Connect | Alibaba VPN Gateway IPsec — no Apsara Stack |
| **AI framework** | Bedrock Agents + Knowledge Bases | Model Studio Agent + Workflow Applications |
| **Fast-lane model** | Claude Haiku 4.5 or Amazon Nova Micro (A) · Qwen3 Next 80B A3B MoE (B) | Qwen3.5-Flash |
| **Complex-lane model** | Claude Sonnet 4.5 or Amazon Nova Pro (A) · Qwen3 VL 235B A22B (B) | Qwen3.5-Plus |
| **Claude Opus** | Not used | N/A |
| **Text embeddings** | Amazon Titan Embed Text v2 (Tokyo) | text-embedding-v4 |
| **Multimodal embeddings (figures)** | Amazon Nova Multimodal Embeddings (us-east-1) | tongyi-embedding-vision-plus (SG Intl) |
| **Reranker** | Amazon Rerank 1.0 (Tokyo) | qwen3-rerank |
| **Vector store** | OpenSearch Serverless | OpenSearch Vector Search Edition |
| **Managed GraphRAG** | Bedrock KB GraphRAG on Neptune Analytics | AnalyticDB PG GraphRAG service |
| **PDF parsing** | Bedrock Data Automation (Sydney) | DocMind + Qwen-VL-Max |
| **Cache Layer 1 (semantic)** | ElastiCache Redis OSS + RediSearch (LangChain RedisSemanticCache) | Tair (Redis-compatible, NOT Valkey) + TairVector |
| **Cache Layer 2 (prefix)** | Bedrock Prompt Caching (Claude + Nova; NOT Qwen3) | Qwen Context Cache (implicit + explicit) |
| **Customization** | Bedrock Model Distillation (Sonnet → Nova Lite, A) · Bedrock RFT on Qwen3-32B (B) | PAI Model Gallery Qwen3-8B SFT + LoRA + GRPO |
| **Tone consistency** | Fixed system prompt + `temperature=0.1` | Same + `seed=42` |
| **Identity — clinicians** | Cognito federated to hospital IdP (SAML/OIDC) | IDaaS EIAM 2.0 federated to hospital IdP |
| **Identity — Nova staff** | IAM Identity Center ↔ Nova EntraID | Cloud SSO + RAM ↔ Nova EntraID |
| **Audit log retention** | CloudTrail → S3 Object Lock **6 years** (HIPAA §164.530(j)) | ActionTrail → SLS → OSS WORM **6 years** |
| **WHO ICD-11 API** | Monthly ingest + runtime tool + query expansion | Same pattern |
| **Emergency routing** | Pure if/else on explicit UI toggle — no classifier LLM call | Same |
| **Launch scope** | One product, all features on day one; no phases | Same |

## Verdict (ranked by total monthly cost, SG residency — launch-day with all features on)

| Rank | Version | ~$/mo (launch-day) | SG-native for query path |
|---|---|---|---|
| 1 | Version C (Alibaba) | ~$2,280–3,060 | ✅ zero cross-region hops |
| 2 | Version B (Qwen Sydney, with custom Qwen3-32B) | ~$3,240 | ⚠️ Sydney chat |
| 3 | Version A1+ (Nova Micro + Nova Pro, with Nova Lite student) | ~$4,655–5,655 | ✅ chat; Tokyo embed+rerank |
| 4 | Version A2 (Haiku 4.5 + Sonnet 4.5, with Nova Lite student) | ~$5,765 | ✅ chat; Tokyo embed+rerank |

All four numbers include the version's respective fine-tuned student / custom-model cost — apples-to-apples.

## Running the pieces

Environment variables (never commit secrets):

```bash
# WHO ICD-11 (free OAuth2; register at https://icd.who.int/icdapi)
export WHO_ICD_CLIENT_ID=...
export WHO_ICD_CLIENT_SECRET=...

# AWS or Alibaba cloud creds via the standard SDK env/profile
```

```bash
# 1. Pull real ICD-11 data (demo corpus in this repo)
python scripts/download_who_icd.py --walk --max-depth 0          # chapters only
python scripts/download_who_icd.py --search sepsis               # keyword search

# 2. Pull public clinical trials (for a test corpus only)
python scripts/download_clinicaltrials.py --condition sepsis --pages 2

# 3. Upload data + kick a Bedrock KB sync
python scripts/ingest_to_bedrock_kb.py \
    --bucket nova-rag-raw-sg \
    --kb-id  ABCDEFGHIJ \
    --ds-id  KLMNOPQRST \
    --prefix-map who=who-guidelines icd11=icd11 clinical-trials=trials \
    --region ap-southeast-1

# 4. Deploy the demo UI (verification only; not production)
cd aws-demo && sam build && sam deploy --guided
```
