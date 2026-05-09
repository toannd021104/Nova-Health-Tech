# Nova Health Tech — Clinical GenAI Assistant

Proposal package for Nova Health Tech's clinical decision-support GenAI assistant, covering both **AWS (primary build)** and **Alibaba Cloud (proposed)** architectures.

## What's in this repo

```
.
├── README.md                          ← this file
├── Nova Health Tech's challenge.txt   ← original scenario
├── askAli_AI_Assistant.txt            ← Ali assistant answers (Qwen fine-tune + multimodal embeddings)
├── Task List - Task list.csv          ← task tracker
│
├── data/                              ← sample input data for RAG
│   ├── DATA_SOURCES.md                ← how to download each corpus
│   ├── clinical-trials/               ← ClinicalTrials.gov API samples + sample medical PDF
│   ├── pubmed/                        ← MedRAG PubMed abstracts chunk (~15k records)
│   ├── who/                           ← WHO guideline PDFs (manual download links)
│   └── treatment-protocols/           ← FDA drug labels (openFDA)
│
├── docs/
│   ├── architecture/
│   │   ├── AWS_architecture.md
│   │   ├── Alibaba_architecture.md
│   │   └── fine_tuning_vs_rag.md
│   ├── compliance/
│   │   └── security_compliance.md     ← HIPAA, GDPR, China MLPS, DSL, medical AI regs
│   └── pricing/
│       └── cost_analysis.md           ← AWS vs Alibaba cost sheet + free-tier notes
│
├── scripts/
│   ├── download_clinicaltrials.py     ← pull additional CT.gov records
│   ├── download_pubmed.py             ← pull PubMed abstracts via E-utilities
│   ├── download_who_icd.py            ← pull WHO ICD-11 via API (requires free OAuth key)
│   └── ingest_to_bedrock_kb.py        ← upload processed chunks to S3 for Bedrock KB
│
└── aws-demo/                          ← minimal web app: clinical portal + right-panel AI chat
    ├── frontend/                      ← static HTML/JS (deploy to S3 + CloudFront)
    ├── backend/                       ← Lambda handler calling Bedrock
    ├── template.yaml                  ← SAM template (API Gateway + Lambda + Bedrock)
    └── README.md
```

## Quick start

1. Read `Nova Health Tech's challenge.txt` for the scenario.
2. Read `docs/architecture/AWS_architecture.md` for the build-ready AWS design.
3. Read `docs/architecture/Alibaba_architecture.md` for the Alibaba Cloud proposal (Qwen + Model Studio + PAI + OpenSearch Vector Search Edition).
4. Check `data/DATA_SOURCES.md` for data that was downloaded vs. needs manual download (WHO IRIS + PubMed are rate-limited from automation IPs).
5. Deploy the demo: `cd aws-demo && sam build && sam deploy --guided`.

## Cloud strategy summary

| Dimension | AWS (build) | Alibaba Cloud (proposal) |
|---|---|---|
| Foundation model | Claude Haiku 4.5 (speed) + Claude Sonnet 4.6 (depth) on Bedrock | Qwen3-Plus + Qwen3-Max on Model Studio |
| Multimodal embedding | Amazon Nova Multimodal Embeddings | qwen3-vl-embedding (fused) |
| Vector store | OpenSearch Serverless (vector) | OpenSearch Vector Search Edition |
| RAG orchestration | Bedrock Knowledge Bases + Agents | Model Studio Application (RAG) + PAI-EAS |
| Fine-tuning | Bedrock custom models (Nova / Llama 3.2) | PAI Model Gallery — Qwen3 SFT + LoRA + DPO |
| PHI guardrails | Bedrock Guardrails + Comprehend Medical + Macie | Content Moderation + DataWorks masking + PAI-ACP |
| Region for data residency | us-east-1 with HIPAA BAA; eu-central-1 for GDPR | Singapore / Frankfurt for intl; Shanghai for mainland (MLPS L3) |
| Deploy model | Serverless public cloud (VPC-isolated) + on-prem hybrid via Outposts if hospital requires | Hybrid: Alibaba Cloud + on-prem via ACK-Edge / Apsara Stack |

## Build status (what's done vs. pending)

| Task | Status | Artifact |
|---|---|---|
| Find English-language inputs for RAG (trials, protocols, PubMed, WHO) | ✅ Done (partial — see DATA_SOURCES.md) | `data/` + download scripts |
| Simple AWS web page with right-panel AI assistant | ✅ Done (demo) | `aws-demo/` |
| Fine-tuning research (SFT / RLHF) on AWS + Alibaba, feasibility for emergency-care + budget | ✅ Done | `docs/architecture/fine_tuning_vs_rag.md` + cost analysis |
| Pricing & free-trial check for Ali (OpenSearch, Model Studio, PAI) | ✅ Done | `docs/pricing/cost_analysis.md` |
| Choose vector DB | ✅ Done (recommendation + rationale) | AWS: OpenSearch Serverless vector; Ali: OpenSearch Vector Search Edition (see architecture docs) |
| AWS fine-tune cost + Bedrock multimodal embedding Nova credit check | ✅ Done (pricing + model choice) | `docs/pricing/cost_analysis.md` + `docs/architecture/AWS_architecture.md` |

### Remaining manual steps (see `data/DATA_SOURCES.md`)

1. Download a handful of WHO guideline PDFs from `https://www.who.int/publications/who-guidelines` (IRIS now serves via JS SPA — curl/Invoke-WebRequest don't work).
2. Register a free NCBI API key at https://account.ncbi.nlm.nih.gov/ if you want to run `scripts/download_pubmed.py`. My local IP got blocked during testing; NCBI explicitly recommends using an API key for any automated pipeline.
3. Register free WHO ICD-11 API credentials at https://icd.who.int/icdapi to run `scripts/download_who_icd.py`.

### Data already downloaded (ready to feed the RAG pipeline)

- `data/clinical-trials/sample_diabetes_studies.json` (368 KB)
- `data/clinical-trials/sample_sepsis_studies.json` (88 KB) — emergency-care relevant
- `data/clinical-trials/sample_stroke_studies.json` (104 KB) — emergency-care relevant
- `data/clinical-trials/fda_sepsis_drugs.json` (123 KB) — openFDA drug labels
- `data/clinical-trials/arxiv_radiology_rag.pdf` (773 KB) — real PDF stand-in for "legacy clinical trial report with inconsistent tagging"
- `data/pubmed/pubmed_medrag_sample.jsonl` (34 MB, 15,377 abstracts) — MedRAG PubMed mirror
