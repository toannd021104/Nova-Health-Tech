# POC — Nova Health Tech Clinical AI · AWS, 10-day demo

Two sibling POCs, both running the **same 12-department multi-agent topology** with RAG + managed GraphRAG + ElastiCache Redis OSS + PHI mask + emergency bypass. Reviewers pick one or run both side-by-side.

| Variant | Folder | LLM family | Fine-tuning | 10-day cost (100 q) |
|---|---|---|---|---|
| **AWS + Claude** (Version A, non-fine-tuned) | [`aws_claude/`](aws_claude/README.md) | Claude Haiku 4.5 + Sonnet 4.5 on Bedrock Singapore | **none** (base models + prompt caching) | **~$165** |
| **AWS + Qwen** (Version B, with SFT) | [`aws_qwen/`](aws_qwen/README.md) | Qwen3 Next 80B A3B + Qwen3 VL 235B A22B + Qwen3 32B on Bedrock Sydney | **SFT on Qwen3-4B** via SageMaker TRL (Scenario A) or RFT on Qwen3-32B (Scenario C) | **~$197** (A) · ~$516 (B-ss) · ~$804 (C) |

## Shared design

Both POCs use the same building blocks so the reviewer can compare apples to apples:

- **Amazon-only AI stack** — no Cohere; Amazon Titan Embed Text v2 for embeddings, Amazon Rerank 1.0 for reranking
- **Multi-agent topology** — router picks from 12 demo departments; emergency toggle is pure if/else and bypasses the router
- **Managed GraphRAG** — Amazon Bedrock Knowledge Bases GraphRAG on Amazon Neptune Analytics
- **Layer-1 cache** — Amazon ElastiCache for Redis OSS (`cache.t4g.micro`), explicitly Redis not Valkey
- **OpenSearch Serverless** — 2 OCUs minimum for the vector index
- **Light-theme UI** with emergency toggle, route badge, image attachment for Radiology, live citations

## Why two POCs?

- The **Claude POC** is the "no-training baseline" — production Version A will ship with a Nova Lite student distilled from Sonnet, but the POC shows how far prompt engineering + RAG + GraphRAG + caching alone get on Anthropic's quality bar. Every LLM call stays in Singapore (PDPA-native).
- The **Qwen POC** is the "fine-tuning showcase" — it bundles a live SFT run (~6 hr on `ml.g6e.8xlarge`, ~$34) plus serves/displays the fine-tuned artifact. Best for demonstrating the GRPO+SFT recipe from the AWS builder article. Qwen inference lives in Sydney (~90 ms cross-region from SG Lambda).

Both POCs share the corpus in `data/clinical-trials/departments/` (36 PDFs / 413 pages / ~500 k tokens).

## Running both at once

Each POC deploys to its own tag set (`Owner=nova-health-poc-claude` vs `Owner=nova-health-poc-qwen`) with separate CloudFront distributions, so there's no resource clash. Running in parallel for 10 days costs ~$362 total (~$165 + ~$197) minus the shared corpus ingestion cost duplication (~$5 × 2 = $10). Realistically **~$350 combined** for a side-by-side demo.

## Cost summary

| Line item | aws_claude | aws_qwen (Scenario A) |
|---|---:|---:|
| Ingestion (one-time) | $5.64 | $4.43 |
| SFT training | $0 | $34 |
| Always-on infra (10 d) | $158 | $158 |
| Per-query inference (100 q) | $1.33 | $0.37 |
| **Total** | **~$165** | **~$197** |

Per-query cost is where the two diverge most: **Claude Sonnet 4.5 is ~3.6× more expensive per complex-lane call than Qwen3 VL 235B A22B**, but Bedrock Prompt Caching (enabled by default for Claude 4.x) brings it down to $1.33 for the 100-question demo. Extrapolated to production (600 k queries / month), Qwen is dramatically cheaper — see `docs/pricing/cost_analysis.md`.

## Folder layout

```
poc/
├── README.md                       ← this file
├── aws_claude/                     ← Version A POC (non-fine-tuned)
│   ├── README.md                    ← cost breakdown + deploy instructions
│   ├── deploy.py
│   ├── teardown.py
│   ├── requirements.txt
│   └── app/
│       ├── agents/__init__.py       ← 12 departments bound to Haiku/Sonnet/Nova Micro
│       ├── router.py                ← Nova Micro department classifier
│       ├── graph.py                 ← LangGraph with Redis cache, GraphRAG, vision
│       ├── rag.py                   ← Titan Embed v2 + FAISS + Amazon Rerank
│       ├── graphrag.py              ← Bedrock KB GraphRAG tool
│       ├── cache.py                 ← ElastiCache Redis OSS
│       ├── server.py                ← FastAPI + Mangum
│       └── static/                  ← light-theme chat UI
└── aws_qwen/                       ← Version B POC (with SFT)
    └── (same structure, different models)
```
