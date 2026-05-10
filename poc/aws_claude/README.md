# POC — Nova Health Tech Clinical AI · AWS + Claude (Version A), 10-day demo

Single-user, single-tenant, **AWS Version A (Claude on Bedrock Singapore)**. This is the **non-fine-tuning variant** — we ship base Claude Haiku 4.5 + Claude Sonnet 4.5 and let prompt engineering, RAG, GraphRAG, and caching do the work. Good for clients who want the Anthropic quality bar on day one without a training run in the critical path.

- ✅ Multi-agent topology (12-department demo subset of the full 40)
- ✅ **No fine-tuning / no SFT / no RFT** — base models only (that's the point of this POC)
- ✅ RAG + **managed GraphRAG** (Amazon Bedrock Knowledge Bases on Amazon Neptune Analytics)
- ✅ **Amazon-only AI stack** — no Cohere; Titan Embed Text v2 for embeddings, Amazon Rerank 1.0 for reranking
- ✅ **Amazon ElastiCache for Redis OSS** — explicitly Redis, not Valkey
- ✅ Emergency bypass, PHI regex mask, Bedrock Guardrails, citations
- ✅ **Bedrock Prompt Caching** (works out of the box with Claude 4.x, unlike Qwen)

Demo parameters: **1 user × 10 questions / day × 10 days = 100 questions**, availability 24/7 for the 10 days.

## 1. Region layout

Everything Singapore-native except Amazon Rerank:

| Service | Region | Reason |
|---|---|---|
| Lambda, API Gateway, CloudFront, S3, OpenSearch Serverless, Neptune Analytics, ElastiCache Redis | `ap-southeast-1` Singapore | main tenant region |
| Claude Haiku 4.5 / Sonnet 4.5 | `ap-southeast-1` via `global.anthropic.*` inference profiles | PDPA-native |
| Amazon Rerank 1.0 | `ap-northeast-1` Tokyo | Rerank is Tokyo or Oregon only |
| Titan Embed Text v2 | Singapore | available in-region |
| Bedrock Data Automation | Singapore | available in-region |

**No Sydney, no us-west-2.** Only the Rerank call crosses a region boundary (~70 ms RTT to Tokyo).

```
  Reviewer's browser
        │
        │ HTTPS via CloudFront (ap-southeast-1 edge)
        ▼
  API Gateway → Lambda (Singapore)
        │
        ├─ ElastiCache Redis OSS (SG)              Layer-1 semantic cache
        │
        ├─ OpenSearch Serverless (SG)              vector KB per department
        │
        ├─ Neptune Analytics (SG) via Bedrock KB   managed GraphRAG
        │
        ├─ Bedrock Singapore                        Claude Haiku 4.5 (emergency, router)
        │                                            Claude Sonnet 4.5 (complex + vision)
        │
        └─ cross-region → Tokyo Bedrock            Amazon Rerank 1.0
```

## 2. Feature → technology mapping

| Capability | POC implementation |
|---|---|
| Multi-agent topology | 12 department agents (Emergency, Cardiology-Internal, Pulmonology, Gastroenterology, Nephrology, Endocrinology, Neurology, Infectious Disease, Oncology, Obstetrics, Pediatrics, Radiology) |
| Router | **Amazon Nova Micro** on Bedrock Singapore — structured JSON output, temperature 0, ~150 ms. Nova Micro is ~30× cheaper than Haiku 4.5 on input and fine for a deterministic classifier. |
| Emergency lane | Pure if/else bypasses router → **Claude Haiku 4.5** (`global.anthropic.claude-haiku-4-5-20251001-v1:0`) |
| Complex-lane specialist | **Claude Sonnet 4.5** (`global.anthropic.claude-sonnet-4-5-20250929-v1:0`) — handles Radiology image attachments natively via the Converse API |
| **Fine-tuning** | **NONE.** No SFT, no distillation, no RFT. Production Version A ships with Nova Lite distilled from Sonnet, but this POC is the "no-training baseline" so judges can compare against the fine-tuned Qwen POC. |
| RAG embeddings | **Amazon Titan Embed Text v2** ($0.02 / 1M tokens, 1024-dim, Singapore) |
| Reranker | **Amazon Rerank 1.0** on Bedrock Tokyo (`amazon.rerank-v1:0`) |
| Vector store | **OpenSearch Serverless** vector collection (hybrid kNN + BM25) — minimum 2 OCU |
| GraphRAG | **Amazon Bedrock Knowledge Bases GraphRAG on Amazon Neptune Analytics** — managed. Graph entity extraction runs on Claude Haiku 4.5 at ingest time (cheap + handles the clinical vocabulary). |
| Layer-1 semantic cache | **Amazon ElastiCache for Redis OSS** — `cache.t4g.micro` single node. Exact-match key in the POC; production uses RediSearch vector index. |
| **Layer-2 prompt cache** | **Bedrock Prompt Caching** — free for Claude 4.x, enabled from day one. Up to 90 % off on cached input tokens and ~85 % latency cut for the cached prefix. Qwen POC doesn't get this (Bedrock doesn't support prompt caching for Qwen3). |
| Guardrails | Bedrock Guardrails (PHI filter, grounding ≥ 0.7, prompt-injection) |
| Audit | CloudWatch Logs, 1-day retention (POC only) |
| Auth | Shared access token via query string |

## 3. Cost breakdown — 10-day POC, 100 questions

All prices are list prices (verified 10 May 2026).

### 3.1 One-time ingestion (pre-launch, runs once)

Corpus is 36 PDFs / 413 pages / ~500 k tokens — same corpus as the Qwen POC.

| Item | Calc | Cost |
|---|---|---|
| Bedrock Data Automation (standard tier, PDF parse) | 413 pages × $0.010 / page | **$4.13** |
| Amazon Titan Embed Text v2 | ~500 k tokens × $0.02 / 1M | **$0.01** |
| Bedrock KB GraphRAG entity extraction — Claude Haiku 4.5 | ~500 k in × $1.00 / 1M + ~200 k out × $5.00 / 1M | **$1.50** |
| Graph import into Neptune Analytics | free with Bedrock KB GraphRAG integration | **$0** |
| **Ingestion subtotal (one-time)** | | **~$5.64** |

Haiku-based entity extraction is ~5× pricier than Qwen3 235B A22B 2507 for the same job, but we're staying in-region and keeping the model family consistent with the runtime choice.

### 3.2 Always-on infrastructure (10 days = 240 hours)

| Service | Instance / tier | Rate | 240 hr |
|---|---|---|---|
| OpenSearch Serverless (SG) — 2 OCUs minimum | — | 2 × $0.24 / hr | **$115.20** |
| Neptune Analytics (SG) — 1 m-NCU minimum | m-NCU | $0.16 / hr | **$38.40** |
| ElastiCache for Redis OSS (SG) — single-node | `cache.t4g.micro` | $0.017 / hr | **$4.08** |
| Lambda | 1024 MB arm64 | ~200 × 2 s × $0.0000167 / GB-s | **< $0.01** |
| API Gateway REST | 100 calls | $3.50 / 1 M | **< $0.01** |
| CloudFront | 100 requests | free tier | **$0** |
| S3 | ~100 MB | $0.023 / GB-mo | **$0.01** |
| CloudWatch Logs | ~10 MB | $0.50 / GB ingest | **$0.01** |
| **Always-on subtotal (10 days)** | | | **~$157.72** |

Same managed-service floor as the Qwen POC. OpenSearch + Neptune + Redis are the three line items that matter.

### 3.3 Per-query inference (100 questions, 30 emergency / 70 complex)

| Item | Calc | Cost |
|---|---|---|
| Router — Nova Micro (70 complex-lane calls only) | 70 × (500 in × $0.035/1M + 40 out × $0.14/1M) | **$0.001** |
| Fast lane — Haiku 4.5 with **Bedrock Prompt Caching 90 % hit after warmup** | 30 × (3 k in × 0.5 blended × $1.00/1M + 350 out × $5.00/1M) | **$0.098** |
| Complex lane — Sonnet 4.5 with **prompt caching 70 % hit** | 70 × (3 k in × 0.65 blended × $3.00/1M + 600 out × $15.00/1M) | **$1.039** |
| GraphRAG graph-traversal LLM calls (~10 % of complex on Sonnet) | 7 × ~$0.015 | **$0.105** |
| Amazon Rerank 1.0 (70 complex calls, 20 docs each) | 70 × $0.001 / query | **$0.070** |
| Titan Embed query vector | 100 × ~80 tok × $0.02/1M | **< $0.01** |
| Bedrock Guardrails | 100 × $0.15 / 1000 units | **$0.015** |
| **Per-query subtotal (100 questions)** | | **~$1.33** |

The prompt-cache hit is a real number here — the system prompt + tone template + static RAG prefix share ~2 kB across every call, so the cached portion bills at 10 % of list price. Without the cache, per-query would be ~$3.50 instead of $1.33.

### 3.4 Grand total

| Scenario | Ingest | Always-on 10 d | Per-query | **TOTAL** |
|---|---:|---:|---:|---:|
| **AWS + Claude POC (no fine-tuning)** | $5.64 | $158 | $1.33 | **~$165** |

That's **~$32 cheaper** than the Qwen POC Scenario A (~$197) because we skip the $34 SFT training run. All other line items are the same or very close.

### 3.5 Side-by-side with the Qwen POC

| Line item | AWS + Claude POC | AWS + Qwen POC (Scenario A) |
|---|---:|---:|
| Ingestion | $5.64 | $4.43 |
| SFT training | **$0 (no fine-tuning)** | $34 |
| Always-on infra | $158 | $158 |
| Student inference endpoint | $0 | $0 |
| Per-query LLM + rerank | $1.33 | $0.37 |
| **TOTAL (10 days, 100 q)** | **~$165** | **~$197** |

Claude POC is cheaper **only because it skips training**. Per-query Claude costs ~3.6× more than per-query Qwen (Claude Sonnet 4.5 vs Qwen3 VL 235B A22B). If the reviewer extrapolates to production volume (600 k queries/month), the Qwen POC is dramatically cheaper long-term — which is exactly the cost argument in `docs/pricing/cost_analysis.md`.

## 4. Why there's no SFT in this POC

Two real reasons:

1. **Claude 4.5 itself is not fine-tunable on Bedrock.** Only Claude 3 Haiku (2024-03-07) is, and using it would regress us to an older model family. See `docs/architecture/model_customization_research.md` §3.
2. **The production Version A ships with a distilled Nova Lite student** (Sonnet → Nova Lite via Bedrock Model Distillation, $1.5–2.5k per run). The POC deliberately doesn't include it so the reviewer sees the "pure prompt-engineering + RAG + caching" baseline. The Qwen POC is where they see live fine-tuning.

If the reviewer specifically asks for distillation here, adding it is a ~$670 line item (Bedrock Model Distillation Sonnet → Nova Lite), pushing the POC to ~$835 for the 10 days — still cheaper than the Qwen Scenario C at $804 only by accident.

## 5. What the reviewer can test

- **Emergency toggle** → Haiku 4.5 in < 2 s, no router, served in Singapore (no cross-region tax)
- **Complex case** → Nova Micro router picks a department → Sonnet 4.5 specialist answers, citations as `[1][2]`
- **Radiology image attach** → router forces Radiology → Sonnet 4.5 vision describes findings, defers to human radiologist
- **GraphRAG query** → Bedrock KB GraphRAG traverses Neptune + vector
- **Redis semantic-cache hit** → same question twice; second time < 50 ms
- **Bedrock Prompt Caching hit** → same question's prefix is cached; see the "input_tokens_cached" count in the response metadata
- **Amazon Rerank visibility** → rerank scores show on top-5 citations
- **No fine-tuned artifact** — this is the Claude baseline POC; the Qwen POC is where you see SFT

## 6. Deploy / teardown

```bash
# deploy
python poc/aws-claude/deploy.py --profile gapv50k --region ap-southeast-1

# teardown after the interview
python poc/aws-claude/teardown.py --profile gapv50k --region ap-southeast-1
```

Runs completely independently from the Qwen POC — different stack, different tags (`Owner=nova-health-poc-claude`), different CloudFront distribution. You can run both POCs in parallel for a side-by-side demo.

## 7. Files in this folder

| File | Purpose |
|---|---|
| `README.md` | This doc |
| `deploy.py` | Boto3 deployer — build FAISS indexes + Lambda zip |
| `teardown.py` | Single-command cleanup of tagged resources |
| `app/server.py` | FastAPI entry (Mangum-wrapped for Lambda) |
| `app/graph.py` | LangGraph: PHI → cache → lane → router → retrieve+rerank+graph → generate → cache-write |
| `app/router.py` | **Nova Micro** department classifier |
| `app/rag.py` | **Titan Embed v2** + FAISS + **Amazon Rerank** |
| `app/graphrag.py` | Bedrock KB GraphRAG retrieval tool |
| `app/cache.py` | **ElastiCache Redis OSS** Layer-1 semantic cache |
| `app/agents/__init__.py` | 12 department system prompts bound to Haiku/Sonnet/Nova Micro |
| `app/static/` | Light-theme chat UI (shared styling with the Qwen POC) |
| `requirements.txt` | Python deps |
