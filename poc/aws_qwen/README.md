# POC — Nova Health Tech Clinical AI · AWS + Qwen (Version B), 10-day demo

Single-user, single-tenant, **AWS Version B (Qwen on Bedrock Sydney)**, with every production feature wired in:

- ✅ Multi-agent topology (12-department demo subset of the full 40)
- ✅ Fine-tuning — **SFT via SageMaker TRL on Qwen3-4B** (cheapest honest path) or **RLHF-equivalent via Bedrock Reinforcement Fine-Tuning on Qwen3-32B** (single-service, pricier)
- ✅ RAG + **managed GraphRAG** (Amazon Bedrock Knowledge Bases on Amazon Neptune Analytics)
- ✅ **Amazon-only AI stack** — no Cohere; Titan Embed Text v2 for embeddings, Amazon Rerank 1.0 for reranking
- ✅ **Amazon ElastiCache for Redis OSS** — explicitly Redis, not Valkey
- ✅ Emergency bypass, PHI regex mask, Bedrock Guardrails, citations

Demo parameters: **1 user × 10 questions / day × 10 days = 100 questions**, availability 24/7 for the 10 days.

## 1. Region layout

| Service | Region | Reason |
|---|---|---|
| Lambda, API Gateway, CloudFront, S3, OpenSearch Serverless, Neptune Analytics, ElastiCache Redis | `ap-southeast-1` Singapore | main tenant region |
| Qwen inference (Qwen3 Next 80B A3B, Qwen3 VL 235B A22B, Qwen3 32B, Qwen3 235B A22B 2507) | `ap-southeast-2` Sydney | nearest APAC Qwen region |
| Amazon Rerank 1.0 | `ap-northeast-1` Tokyo | only two Rerank regions exist (Tokyo + Oregon); Tokyo is closer |
| Bedrock RFT training (if Path β chosen) | `us-west-2` Oregon | only RFT region for Qwen3-32B |
| Titan Embed Text v2 | `ap-northeast-1` Tokyo (cross-region from SG Lambda) | **NOT in Singapore.** Nearest with Titan Text v2 + Rerank co-located is Tokyo. |
| Bedrock Data Automation (one-time ingest) | `ap-southeast-2` Sydney (cross-region) | **NOT in Singapore.** Nearest APAC is Sydney or Mumbai. |

Cross-region latency: SG→Sydney ~90 ms, SG→Tokyo ~70 ms. Both are comfortable for the 2-s emergency SLA (still under 1.8 s p95).

```
  Reviewer's browser
        │
        │ HTTPS via CloudFront (ap-southeast-1 edge)
        ▼
  API Gateway → Lambda (Singapore)
        │
        ├─ ElastiCache Redis OSS (SG)              Layer-1 semantic cache
        │
        ├─ OpenSearch Serverless (SG) + FAISS      vector KB per department
        │
        ├─ Neptune Analytics (SG) via Bedrock KB   managed GraphRAG
        │
        ├─ cross-region → Sydney Bedrock           Qwen3 router / emergency / complex
        │
        ├─ cross-region → Tokyo Bedrock            Amazon Rerank 1.0
        │
        └─ cross-region → us-west-2 (optional)     Bedrock RFT'd Qwen3-32B custom endpoint
```

## 2. Feature → technology mapping

| Capability | POC implementation |
|---|---|
| Multi-agent topology | 12 department agents (Emergency, Cardiology-Internal, Pulmonology, Gastroenterology, Nephrology, Endocrinology, Neurology, Infectious Disease, Oncology, Obstetrics, Pediatrics, Radiology). Full Vietnamese → English mapping in `docs/architecture/technology_options.md` §3b. |
| Router | **Qwen3 32B dense** on Bedrock Sydney — structured JSON output, temperature 0, ~150 ms |
| Emergency lane | Pure if/else bypasses router → **Qwen3 Next 80B A3B** (MoE, 3B active, fastest Qwen on Bedrock) |
| Complex-lane specialist | **Qwen3 VL 235B A22B** for all specialists (handles Radiology image attachments natively — no separate vision model needed) |
| SFT / RLHF | Two supported paths, pick one at deploy time — see §4 |
| RAG embeddings | **Amazon Titan Embed Text v2** on Bedrock **Tokyo** (`ap-northeast-1`) — cross-region call from SG Lambda. $0.02 / 1M tokens, 1024-dim. **Not available in Singapore** (verified via `aws bedrock list-foundation-models`). |
| Reranker | **Amazon Rerank 1.0** on Bedrock Tokyo (`amazon.rerank-v1:0`) — same Tokyo region as embeddings |
| Vector store | **OpenSearch Serverless** vector collection (hybrid kNN + BM25) — minimum 2 OCU (1 index + 1 search), Singapore |
| GraphRAG | **Amazon Bedrock Knowledge Bases GraphRAG on Amazon Neptune Analytics** — managed, GA March 2025. Graph entity extraction runs on Qwen3 235B A22B 2507 (text-only, cheap) at ingest time. |
| PDF parsing | **Amazon Bedrock Data Automation** on **Sydney** (`ap-southeast-2`) — one-time at pre-deploy. **Not available in Singapore.** |
| Layer-1 semantic cache | **Amazon ElastiCache for Redis OSS** — `cache.t4g.micro` single node (explicitly Redis, not Valkey). Exact-match lookup in the POC; production uses RediSearch vector index for fuzzy semantic matching. |
| Guardrails | Bedrock Guardrails (PHI filter, grounding ≥ 0.7, prompt-injection) |
| Audit | CloudWatch Logs, 1-day retention (POC only; production = CloudTrail → S3 Object Lock 6 yr) |
| Auth | Shared access token via query string (one-reviewer demo) |

## 3. Cost breakdown — 10-day POC, 100 questions total

All prices are list prices from the AWS Bedrock / SageMaker / ElastiCache / Neptune Analytics / OpenSearch Serverless pricing pages (verified 10 May 2026). Reconfirm with the account team before deployment.

### 3.1 One-time ingestion (pre-launch, runs once)

Corpus is 36 PDFs / 413 pages / ~500 k tokens (measured — see `data/clinical-trials/departments/README.md`).

| Item | Calc | Cost |
|---|---|---|
| **Bedrock Data Automation — Sydney** (not in Singapore; cross-region PDF parse) | 413 pages × $0.010 / page | **$4.13** |
| S3 cross-region transfer SG → Sydney (~36 MB corpus) | $0.02 / GB | **< $0.01** |
| **Amazon Titan Embed Text v2 — Tokyo** (not in Singapore) | ~500 k tokens × $0.02 / 1M | **$0.01** |
| Bedrock KB GraphRAG entity extraction — Qwen3 235B A22B 2507 (text-only, cheapest 235B tier) | ~500 k in × $0.2266 / 1M + ~200 k out × $0.9064 / 1M | **$0.29** |
| Graph import into Neptune Analytics | free with Bedrock KB GraphRAG integration | **$0** |
| **Ingestion subtotal (one-time)** | | **~$4.44** |

### 3.2 SFT / RLHF training (one-time, pre-launch) — pick ONE path

**Path α — SageMaker TRL SFT on Qwen3-4B (CHEAPEST)**

Runs the AWS builder-article GRPO+SFT recipe on Hugging Face TRL. Produces a fine-tuned Qwen3-4B student specialized on the Nova tone + citation style. Lives in S3 after training; served separately if you want live inference.

| Item | Calc | Cost |
|---|---|---|
| Training job `ml.g6e.8xlarge` (L40S × 1) | ~6 hr × $5.74 / hr | **$34** |
| Model artifact storage in S3 | ~8 GB × $0.023 / GB-mo × (10 / 30 day) | **$0.06** |
| **Path α subtotal** | | **~$34** |

**Path β — Bedrock Reinforcement Fine-Tuning on Qwen3-32B (AWS-native, pricier)**

Fully managed — upload prompts + reward function, Bedrock trains and exposes a custom-model endpoint. RFT is Bedrock's RLHF-equivalent (reinforcement learning with a verifiable reward; the AWS term is "reinforcement fine-tuning").

| Item | Calc | Cost |
|---|---|---|
| RFT training (us-west-2 only) | ~8 hr × $80 / hr | **$640** |
| Trained-model storage | $1.95 / mo × (10 / 30 day) | **$0.65** |
| **Path β subtotal** | | **~$641** |

### 3.3 Always-on infrastructure (10 days = 240 hours)

| Service | Instance / tier | Rate | 240 hr |
|---|---|---|---|
| OpenSearch Serverless (SG) — 2 OCUs minimum (1 index + 1 search) | — | 2 × $0.24 / hr | **$115.20** |
| Neptune Analytics (SG) — 1 m-NCU minimum | m-NCU | $0.16 / hr | **$38.40** |
| **ElastiCache for Redis OSS (SG)** — single-node, cheapest | `cache.t4g.micro` | $0.017 / hr | **$4.08** |
| Lambda (POC traffic) | 1024 MB arm64 | ~200 × 2 s × $0.0000167 / GB-s | **< $0.01** |
| API Gateway REST | 100 calls | $3.50 / 1 M | **< $0.01** |
| CloudFront | 100 requests | 50 GB + 2 M req free tier | **$0** |
| S3 (corpus + FAISS + logs) | ~100 MB | $0.023 / GB-mo | **$0.01** |
| CloudWatch Logs (1-day retention) | ~10 MB | $0.50 / GB ingest | **$0.01** |
| **Always-on subtotal (10 days)** | | | **~$157.72** |

### 3.4 Serving the fine-tuned student

Three sub-options depending on the training path:

**Path α-serve A — Don't host the student; reviewer inspects artifact + eval numbers**

| Item | Cost |
|---|---|
| S3 holds the student weights; eval harness results in a side panel of the UI | **$0** |

**Path α-serve B — Always-on SageMaker endpoint for Qwen3-4B student**

| Item | Calc | Cost |
|---|---|---|
| SageMaker endpoint `ml.g5.2xlarge` (24×7 in SG) | 240 hr × $1.52 / hr | **$364.80** |
| Alternative: SageMaker Serverless Inference | ~100 × 2 s × 8 GB × $0.20 / GB-s | **~$320** |

**Path β-serve — Bedrock custom-model endpoint (for RFT'd Qwen3-32B)**

| Item | Calc | Cost |
|---|---|---|
| Custom-model inference (us-west-2) | 100 calls × ~$0.0008 / call | **$0.08** |
| No idle cost (pay-per-token) | | |

### 3.5 Per-query inference (100 questions, 30 emergency / 70 complex)

| Item | Calc | Cost |
|---|---|---|
| Router — Qwen3 32B (70 complex-lane calls only) | 70 × (500 in × $0.1545/1M + 40 out × $0.6180/1M) | **$0.007** |
| Fast lane — Qwen3 Next 80B A3B (30 emergency calls) | 30 × (3 k in × $0.1545/1M + 350 out × $1.2360/1M) | **$0.027** |
| Complex lane — Qwen3 VL 235B A22B (70 complex calls) | 70 × (3 k in × $0.5459/1M + 600 out × $2.7398/1M) | **$0.230** |
| GraphRAG graph-traversal LLM calls (~10 % of complex) | 7 × ~$0.002 | **$0.014** |
| **Amazon Rerank 1.0** (70 complex calls, 20 docs each) | 70 × $0.001 / query (standard Bedrock rerank billing) | **$0.070** |
| Per-query Titan Embed (query vector) | 100 × ~80 tok × $0.02/1M | **< $0.01** |
| Bedrock Guardrails | 100 × $0.15 / 1000 units | **$0.015** |
| **Per-query subtotal (100 questions)** | | **~$0.37** |

### 3.6 Grand totals (10-day POC)

| Scenario | Ingest | Train | Always-on 10 d | Student inference | Per-query | **TOTAL** |
|---|---:|---:|---:|---:|---:|---:|
| **A. Cheapest** — SageMaker SFT (Path α), don't host student | $4.43 | $34 | $158 | $0 | $0.37 | **~$197** |
| **B. Realistic** — SageMaker SFT + always-on SG endpoint | $4.43 | $34 | $158 | $365 | $0.37 | **~$561** |
| **B-ss. Realistic serverless** — SageMaker SFT + Serverless Inference | $4.43 | $34 | $158 | $320 | $0.37 | **~$516** |
| **C. AWS-native RFT** — Bedrock RFT on Qwen3-32B, served via Bedrock custom endpoint | $4.43 | $641 | $158 | $0.08 | $0.37 | **~$804** |

**Recommendation for the interview demo: Scenario A at ~$197.** The reviewer gets every capability (multi-agent Qwen stack, RAG with Titan + Amazon Rerank, managed GraphRAG, Redis semantic cache, emergency bypass), plus a fine-tuning artifact to inspect and eval-harness numbers showing the student beats base Qwen by X% on the holdout — all without paying $365 for an always-on GPU endpoint that only has to answer 100 questions.

If the reviewer specifically asks to see the fine-tuned model **answering live**, jump to **Scenario B-ss at ~$516** (Serverless Inference is cheaper than always-on for this traffic and cold-start is tolerable). **Scenario C** is for a demo where the single-service simplicity of Bedrock RFT outweighs the training cost.

### Diffs vs the earlier Claude-based POC

| | Claude POC (~$1.50) | **Qwen POC Scenario A (~$197)** |
|---|---|---|
| Why the jump | FAISS in Lambda, no managed services | adds managed **OpenSearch Serverless ($115)**, **Neptune Analytics GraphRAG ($38)**, **Redis cache ($4)**, **Titan/Amazon Rerank ($0.07)**, **Qwen cross-region Sydney inference ($0.23)**, and the **SFT training run ($34)** |
| LLMs | Haiku 4.5 / Sonnet 4.5 in SG | Qwen3 Next 80B A3B (emergency), Qwen3 32B (router), Qwen3 VL 235B A22B (specialists), all in Sydney |
| Embeddings | Cohere Embed v4 | **Amazon Titan Embed Text v2** |
| Reranker | Cohere Rerank 3.5 | **Amazon Rerank 1.0** |
| Cache | none | **ElastiCache Redis OSS** |
| GraphRAG | stubbed | **real Bedrock KB GraphRAG on Neptune Analytics** |
| Fine-tuning | skipped | **SFT on Qwen3-4B via SageMaker TRL** |

The Qwen POC is ~130× more expensive than the Claude POC because the Claude POC deliberately cut every managed service. Once we turn on OpenSearch, Neptune, Redis, and a real training run — which the reviewer explicitly asked for — the floor is around $200.

## 4. SFT / RLHF path detail

### Path α — SageMaker TRL SFT on Qwen3-4B

Data prep (pre-training):
- Seed prompts: de-identified historical clinical questions + paraphrases from WHO / PMC corpus (~3 k prompts total).
- **Teacher** = Qwen3 VL 235B A22B on Bedrock Sydney, generates target answers with Nova's system prompt applied.
- Clinician review on 10 % sample — approved rows become SFT training data.

Training config (matches `docs/architecture/fine_tuning_and_distillation.md` §4):
- LoRA rank 16, alpha 32, dropout 0.05
- `learning_rate 2e-4`, 3 epochs, warmup ratio 0.03, bf16
- Batch size per device 4, gradient accumulation 4
- `ml.g6e.8xlarge` × 1 instance, ~6 hr per run

### Path β — Bedrock Reinforcement Fine-Tuning on Qwen3-32B

- Upload prompts + a grader Lambda that returns a verifiable reward (e.g. "does the answer cite a real chunk?", "does the dose match the WHO guideline?").
- Bedrock RFT trains and exposes the custom model at an OpenAI-compatible endpoint in us-west-2.
- Cost: $80 / hr training × ~8 hr = $640, then post-training inference at $0.20 in / $0.78 out per 1M tokens.

## 5. What the reviewer can test

- **Emergency toggle** → Qwen3 Next 80B A3B in < 2 s, no router
- **Complex case** → Qwen3 32B router picks a department → Qwen3 VL 235B A22B specialist answers, citations rendered as `[1][2]`
- **Radiology image attach** → router forces Radiology → Qwen3 VL native vision describes findings, defers to a human radiologist
- **GraphRAG query** ("what are the common themes across our internal cardiology trials?") → Bedrock KB GraphRAG traverses Neptune + vector, composes a corpus-wide summary
- **Redis semantic-cache hit** → ask the same question twice; second time returns from Redis in < 50 ms with a "cached" badge
- **Amazon Rerank visibility** → top-5 citations show the rerank score alongside the FAISS vector score
- **Fine-tuning artifact** → side panel shows the SageMaker training logs + eval harness numbers (Scenario A) or live answers from the RFT'd model (Scenario C)

## 6. Teardown

```bash
python poc/teardown.py --profile gapv50k --region ap-southeast-1
```

Deletes all resources tagged `Owner=nova-health-poc`. Always-on resources (OpenSearch Serverless OCUs, Neptune Analytics m-NCU, ElastiCache node, SageMaker endpoint if present) stop billing the moment they're deleted.

## 7. Files in this folder

| File | Purpose |
|---|---|
| `README.md` | This doc |
| `deploy.py` | Boto3 deployer — build FAISS indexes + Lambda zip; full infra stage |
| `teardown.py` | Single-command cleanup of tagged resources |
| `app/server.py` | FastAPI entry (Mangum-wrapped for Lambda) |
| `app/graph.py` | LangGraph state machine: PHI → cache → lane → router → retrieve+rerank+graph → generate → cache-write |
| `app/router.py` | **Qwen3 32B** department classifier |
| `app/rag.py` | **Titan Embed v2** + FAISS + **Amazon Rerank** |
| `app/graphrag.py` | Bedrock KB GraphRAG retrieval tool |
| `app/cache.py` | **ElastiCache Redis OSS** Layer-1 semantic cache |
| `app/agents/__init__.py` | 12 department system prompts with Qwen model bindings |
| `app/static/` | Light-theme chat UI |
| `requirements.txt` | Python deps (includes `redis>=5.0`) |
