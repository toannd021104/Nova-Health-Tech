# Nova Health Tech — Clinical GenAI Assistant

Production-oriented proposal for Nova Health Tech's clinical decision-support GenAI assistant, with a build-ready AWS plan and a parallel Alibaba Cloud (Qwen) plan.

## Scope

- **AI service** — production: real hundreds-of-documents RAG (WHO guidelines + internal clinical trial reports + WHO ICD-11 API), managed parsing for complex PDFs (tables, figures, flowcharts), fine-tuned small-model student distilled from a large-model teacher to meet the 2-second emergency SLA, full compliance posture (HIPAA / GDPR / MLPS).
- **Web UI** — demo: a lightweight public web page with a right-hand AI assistant panel, good for stakeholder verification. See `aws-demo/`. This is intentionally simple; the AI service behind it is the serious piece.

## Map

```
.
├── README.md                                       ← this file
├── askAli_AI_Assistant.txt                         ← vendor research (kept for reviewers)
│
├── data/                                           ← REAL source data for RAG ingestion
│   ├── who/                                        ← 8 WHO guideline PDFs (100+ pages each, mixed text/tables/figures)
│   ├── icd11/                                      ← ICD-11 MMS entities + search snapshots (live API)
│   │   ├── mms_root.json
│   │   ├── entities/*.json                         ← 28 chapter-level entities, depth-0 walk
│   │   └── search_*.json                           ← sepsis / stroke / MI
│   └── clinical-trials/protocols/                  ← drop internal trial PDFs here (gitignored by size)
│
├── docs/
│   ├── architecture/
│   │   ├── AWS_architecture.md                     ← production AWS design
│   │   ├── Alibaba_architecture.md                 ← parallel Qwen design
│   │   ├── rag_strategy.md                         ← 3 RAG strategies for complex PDFs; one chosen
│   │   ├── fine_tuning_and_distillation.md         ← teacher→student distillation, tone via hyperparams
│   │   └── caching_strategy.md                     ← 3-layer cache: semantic / prompt / reserved
│   ├── compliance/
│   │   └── security_compliance.md                  ← HIPAA / GDPR / FDA SaMD / EU AI Act / MLPS
│   └── pricing/
│       └── cost_analysis.md                        ← AWS vs Ali with caching + batch + distillation
│
├── scripts/
│   ├── download_who_icd.py                         ← run the live WHO ICD-11 API (OAuth2)
│   ├── download_clinicaltrials.py                  ← ClinicalTrials.gov v2 API
│   └── ingest_to_bedrock_kb.py                     ← push /data to S3 + trigger KB sync
│
└── aws-demo/                                       ← simple public web UI + Lambda → Bedrock
    ├── frontend/                                   ← static HTML/JS, deploy to S3+CloudFront
    ├── backend/                                    ← Lambda chat handler
    ├── template.yaml                               ← SAM deploy
    └── README.md
```

## Read order

1. `docs/architecture/AWS_architecture.md` — the build target.
2. `docs/architecture/rag_strategy.md` — how we handle the WHO PDFs and the ICD-11 API.
3. `docs/architecture/fine_tuning_and_distillation.md` — how we hit the 2-second SLA without sacrificing accuracy.
4. `docs/architecture/caching_strategy.md` — the three cache layers.
5. `docs/architecture/Alibaba_architecture.md` — the parallel Qwen plan.
6. `docs/compliance/security_compliance.md` — regulation coverage.
7. `docs/pricing/cost_analysis.md` — cost sheet including caching / batch / distillation.

## Key production decisions (summary)

| Decision | AWS choice | Alibaba choice |
|---|---|---|
| RAG strategy (of 3 candidates) | Managed parse + managed RAG: **Bedrock Data Automation → Bedrock Knowledge Bases on OpenSearch Serverless** | Managed parse + managed RAG: **DocMind + Qwen-VL → Model Studio RAG on OpenSearch Vector Search Edition** |
| Teacher model (complex / distillation source) | Claude Sonnet 4.6 | Qwen3-Max |
| Student model (emergency lane, fine-tuned) | **Nova Lite**, SFT + preference-tuned | **Qwen3-8B**, SFT + LoRA (+ optional DPO) on PAI |
| Text embeddings | Titan Embed Text v2 | text-embedding-v4 |
| Multimodal embeddings (figure-bearing pages) | Amazon Nova Multimodal Embeddings | qwen3-vl-embedding with `enable_fusion=True` |
| Semantic cache (layer 1) | ElastiCache Valkey + RediSearch (LangChain `RedisSemanticCache`) | Tair (Redis-compatible) + TairVector |
| Prompt / context cache (layer 2) | Bedrock Prompt Caching | Qwen Context Cache (implicit + explicit) |
| Reserved capacity (layer 3, peak hours only) | Bedrock Reserved Tier | Qwen PTU |
| Batch for offline teacher + eval | Bedrock Batch (50% off) | Model Studio Batch (50% off) |
| WHO ICD-11 | Ingest + runtime tool call + query expansion | Same, with FC |
| Tone consistency | Distillation on approved answers + `temperature≈0.1, top_p≈0.7, top_k≈40`, fixed system prompt | Same, plus `seed` (Qwen supports it) |

## Running the pieces

Environment variables (never commit):

```bash
# WHO ICD-11 (free OAuth2; register at https://icd.who.int/icdapi)
export WHO_ICD_CLIENT_ID=...
export WHO_ICD_CLIENT_SECRET=...

# AWS or Alibaba cloud creds via the standard SDK env or profile
```

```bash
# 1. Pull real ICD-11 snapshot (the one used for the demo corpus)
python scripts/download_who_icd.py --walk --max-depth 0          # chapters only
python scripts/download_who_icd.py --search sepsis               # keyword search

# 2. Pull clinical trials (public API, no auth)
python scripts/download_clinicaltrials.py --condition sepsis --pages 2

# 3. Upload data to S3 + kick a Bedrock KB sync
python scripts/ingest_to_bedrock_kb.py \
    --bucket nova-rag-raw-dev \
    --kb-id  ABCDEFGHIJ \
    --ds-id  KLMNOPQRST \
    --prefix-map clinical-trials=trials who=who-guidelines icd11=icd11

# 4. Deploy the demo UI
cd aws-demo && sam build && sam deploy --guided
```
