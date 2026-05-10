# Nova Health Tech — Clinical GenAI Assistant

Production proposal for Nova Health Tech's clinical decision-support GenAI assistant, with a build-ready AWS plan and a parallel Alibaba Cloud (Qwen) plan. **Primary region: Singapore on both clouds.**

## Scope

- **AI service — production.** Real hundreds-of-documents RAG (WHO guidelines + internal clinical trial reports + treatment protocols + WHO ICD-11 API), managed parsing for complex PDFs (horizontal/vertical tables, text-based flowcharts, figures), fine-tuned small-model student distilled from a large-model teacher for the 2-second emergency SLA, scheduled ingestion + internal upload portal over Site-to-Site VPN, hospital-IdP federation, full compliance posture (Singapore PDPA + HCSA; HIPAA when US clients are onboarded).
- **Web UI — demo.** A lightweight publicly-accessible web page with a right-hand AI assistant panel, good for stakeholder verification. See `aws-demo/`.

## Map

```
.
├── README.md                                           ← this file
├── askAli_AI_Assistant.txt                             ← vendor research (kept for reviewers)
│
├── data/                                               ← REAL source data for RAG ingestion
│   ├── README.md
│   ├── who/                                            ← 8 WHO guideline PDFs (100+ pages, text + tables + figures)
│   ├── icd11/                                          ← LIVE WHO ICD-11 data (via the API)
│   │   ├── mms_root.json
│   │   ├── entities/*.json                             ← 316 real entities (chapter-level walk)
│   │   └── search_*.json                               ← sepsis / stroke / MI
│   └── clinical-trials/protocols/                      ← drop internal trial PDFs here
│
├── docs/
│   ├── architecture/
│   │   ├── AWS_architecture.md                         ← production AWS design (Singapore, no Opus, no Outposts)
│   │   ├── Alibaba_architecture.md                     ← parallel Qwen design (Singapore)
│   │   ├── workflow_detailed.md                        ← step-by-step runtime + ingestion walkthrough
│   │   ├── rag_strategy.md                             ← 3 RAG strategies for complex PDFs; one chosen
│   │   ├── fine_tuning_and_distillation.md             ← teacher→student distillation + tone via hyperparams
│   │   ├── caching_strategy.md                         ← 3-layer cache (semantic / prompt-context / reserved)
│   │   ├── framework_choice.md                         ← Bedrock Agents + Model Studio Application (chosen) vs LangGraph/LlamaIndex
│   │   ├── regional_availability.md                    ← which models actually work in Singapore (verified 10 May 2026)
│   │   ├── corporate_integration.md                    ← EHR (SMART on FHIR) + SharePoint (Graph webhooks) + upload portal
│   │   ├── ingestion_and_identity.md                   ← scheduled ingestion, upload portal, Site-to-Site VPN, IdP federation
│   │   └── diagrams/
│   │       └── aws_workflow.svg                        ← the numbered workflow diagram
│   ├── compliance/
│   │   └── security_compliance.md                      ← PDPA / HCSA / HIPAA(6-yr) / FDA / ISO / EU AI Act
│   └── pricing/
│       └── cost_analysis.md                            ← cost sheet with caching + batch + distillation
│
├── scripts/
│   ├── download_who_icd.py                             ← live WHO ICD-11 API (OAuth2)
│   ├── download_clinicaltrials.py                      ← ClinicalTrials.gov v2 API
│   └── ingest_to_bedrock_kb.py                         ← push /data to S3 + trigger KB sync
│
└── aws-demo/                                           ← simple public web UI + Lambda → Bedrock (verification demo)
    ├── frontend/
    ├── backend/
    ├── template.yaml
    ├── README.md
    └── ec2/                                            ← DEPLOYED demo on t4g.small in Singapore (LangGraph + FAISS)
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

1. `docs/architecture/AWS_architecture.md` — the build target (Singapore, Haiku-first, Site-to-Site VPN).
2. `docs/architecture/workflow_detailed.md` — the numbered end-to-end flow (matches the SVG).
3. `docs/architecture/diagrams/aws_workflow.svg` — one-page visual architecture.
4. `docs/architecture/corporate_integration.md` — EHR / SMART on FHIR, SharePoint / Microsoft Graph, upload portal.
5. `docs/architecture/ingestion_and_identity.md` — scheduled ingestion, hospital IdP federation, VPN details.
6. `docs/architecture/rag_strategy.md` — handling the WHO PDFs and the ICD-11 API.
7. `docs/architecture/fine_tuning_and_distillation.md` — 2-second SLA without losing accuracy.
8. `docs/architecture/caching_strategy.md` — three cache layers.
9. `docs/architecture/framework_choice.md` — why Bedrock Agents + Model Studio Application are primary.
10. `docs/architecture/Alibaba_architecture.md` — parallel Qwen plan.
11. `docs/compliance/security_compliance.md` — regulation coverage, 6-year retention.
12. `docs/pricing/cost_analysis.md` — cost sheet with caching / batch / distillation applied.

## Key production decisions (summary)

| Decision | AWS choice | Alibaba choice |
|---|---|---|
| **Region** | `ap-southeast-1` (Singapore) — HIPAA-eligible, PDPA-native | Singapore Model Studio + PAI + OpenSearch Vector |
| **Cross-border transfer** | None by default; stays in Singapore | None by default; stays in Singapore |
| **Hospital integration** | Site-to-Site VPN (IPsec IKEv2). No Outposts, no Direct Connect | Site-to-Site VPN on VPN Gateway. No Apsara Stack unless requested |
| **AI framework** | Bedrock Agents + Knowledge Bases (primary); LangChain only for semantic cache + memory | Model Studio **Agent application** for chat, **Workflow application** for emergency lane; LangChain only for cache + memory |
| **Fast-lane model (emergency, ≤ 2 s)** | Claude Haiku 4.5 (+ Nova Lite fine-tuned student from phase 3) | Qwen3.5-Flash (+ Qwen3-8B PAI-EAS student from phase 3) |
| **Complex-lane / teacher model** | Claude Sonnet 4.6 | Qwen-Max (Qwen3-Max) |
| **Claude Opus** | Not used (overkill, price hard to justify) | N/A |
| **Text embeddings** | Titan Embed Text v2 | text-embedding-v4 |
| **Multimodal embeddings (figures)** | Amazon Nova Multimodal Embeddings | qwen3-vl-embedding with `enable_fusion=True` |
| **Vector store** | OpenSearch Serverless (hybrid kNN + BM25) | OpenSearch Vector Search Edition |
| **PDF parsing** | Bedrock Data Automation (advanced parsing) | DocMind + Qwen-VL-Max for complex pages |
| **Semantic cache (Layer 1)** | ElastiCache Valkey + RediSearch, LangChain `RedisSemanticCache` | Tair + TairVector, same LangChain pattern |
| **Prompt/context cache (Layer 2)** | Bedrock Prompt Caching | Qwen Context Cache (implicit + explicit) |
| **Reserved capacity (Layer 3, peak only)** | Bedrock Reserved Tier | Qwen PTU |
| **Batch (offline teacher + eval)** | Bedrock Batch (50% off) | Model Studio Batch (50% off) |
| **Tone consistency** | Distillation + `temperature=0.1, top_p=0.7, top_k=40`, fixed system prompt | Same + `seed=42` (Qwen supports seed) |
| **Identity — clinicians** | Cognito federated (SAML/OIDC) to each hospital's IdP (EntraID / Okta / ADFS) | Alibaba IDaaS federated to hospital IdP |
| **Identity — Nova staff** | IAM Identity Center ↔ Nova EntraID | Cloud SSO + RAM ↔ Nova EntraID |
| **Audit log retention** | CloudTrail → S3 Object Lock, **6 years** (HIPAA §164.530(j)) | ActionTrail → SLS → OSS WORM, **6 years** |
| **WHO ICD-11 API** | Monthly ingest + runtime tool call + query expansion | Same pattern |

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
