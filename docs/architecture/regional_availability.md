# Model Regional Availability — Singapore vs. Nearest-APAC vs. us-west-2

Verified **10 May 2026** against the AWS profile `gapv50k` using `aws bedrock list-foundation-models` / `list-inference-profiles` + a live Converse smoke test. Prices from the public Bedrock / Nova pricing pages; confirm with AWS account team before committing.

## 1. Singapore (`ap-southeast-1`) — what's actually hosted

### Claude (Anthropic)

| Profile ID | Model | Verified |
|---|---|---|
| `global.anthropic.claude-haiku-4-5-20251001-v1:0` | Claude Haiku 4.5 | ✅ used by the running demo |
| `global.anthropic.claude-sonnet-4-5-20250929-v1:0` | Claude Sonnet 4.5 | ✅ used by the running demo |
| `apac.anthropic.claude-3-haiku-20240307-v1:0` | Claude 3 Haiku | ✅ (this is the one that supports Bedrock SFT, in us-west-2 only) |

### Amazon Nova

| Profile ID | Model | Verified |
|---|---|---|
| `apac.amazon.nova-micro-v1:0` | **Nova Micro** | ✅ smoke-tested — replied "Nova works efficiently..." |
| `apac.amazon.nova-lite-v1:0` | Nova Lite | ✅ |
| `apac.amazon.nova-pro-v1:0` | Nova Pro | ✅ |
| `global.amazon.nova-2-lite-v1:0` | Nova 2 Lite | ✅ |

### Cohere (embeddings & rerank)

| Profile ID | Model | Verified |
|---|---|---|
| `global.cohere.embed-v4:0` | Cohere Embed v4 | ✅ used by the running demo |
| Cohere Rerank 3.5 | | ❌ **not in Singapore** — Tokyo + Oregon only. Running demo uses it via cross-region fallback. |

### Amazon embeddings, rerank, and parsing — what's actually in SG

Verified via `aws bedrock list-foundation-models --region ap-southeast-1`:

| Model / Service | In Singapore? | Nearest APAC if not in SG |
|---|---|---|
| Titan Embed Text v2 (`amazon.titan-embed-text-v2:0`) | ❌ | Sydney, Tokyo, Mumbai — we use **Tokyo** in the POCs so it co-locates with Amazon Rerank |
| Titan Embed Image v1 (`amazon.titan-embed-image-v1`) | ❌ | Sydney |
| **Nova Multimodal Embeddings** (`amazon.nova-2-multimodal-embeddings-v1:0`) | ❌ | **us-east-1 ONLY** — single-region model. Using it from a Singapore tenant means cross-border PDPA transfer. |
| Amazon Rerank 1.0 (`amazon.rerank-v1:0`) | ❌ | Tokyo + Oregon only — single-region model |
| Cohere Rerank 3.5 | ❌ | Tokyo |
| **Amazon Bedrock Data Automation** (PDF / image / video parsing) | ❌ | Sydney, Tokyo, Mumbai (per the BDA cross-region inference profiles table) |
| Bedrock Knowledge Bases + GraphRAG on Neptune Analytics | ✅ (via `us-east-1` backbone with SG endpoints — KB data plane is in SG; control plane varies) | — |
| OpenSearch Serverless (vector) | ✅ | — |

**Implication for Singapore-first deployments:**
- Ingestion pipeline does BDA parse → Titan embed via **cross-region to Tokyo or Sydney**. Corpus bytes transit out of SG during the one-time ingest, then stay in SG (vector store is OpenSearch Serverless in SG, graph store is Neptune Analytics in SG).
- Query-time calls cross-region to Tokyo for **embed-query + rerank** (combined ~120 ms on the complex lane; emergency lane skips both).
- If the client mandates **zero cross-border transfer, including transient embedding calls**, the only option is **Cohere Embed v4 in SG** — but that breaks the Amazon-only rule. The trade-off has to be surfaced in the commercial conversation.
- **Nova Multimodal Embeddings** is a US-only service. Production Version A can use it when the client accepts a specific BAA + cross-border clause for the ingest step.

### Qwen (Alibaba)

**Not available in Singapore Bedrock.** Programmatic list returned zero matches for `qwen` in `ap-southeast-1`.

## 2. Where Qwen actually lives on Bedrock

`aws bedrock list-foundation-models --query "modelSummaries[?contains(modelId,'qwen')].modelId"`:

| Region | Qwen models present | Distance from Singapore |
|---|---|---|
| `ap-southeast-2` (Sydney) | qwen3-32b, qwen3-235b-a22b-2507, qwen3-vl-235b-a22b, **qwen3-next-80b-a3b**, qwen3-coder-30b-a3b, qwen3-coder-480b-a35b, qwen3-coder-next | ~6,300 km · ~90–110 ms round-trip |
| `ap-northeast-1` (Tokyo) | Same set (minus coder-next) | ~5,300 km · ~80–100 ms |
| `ap-south-1` (Mumbai) | Same set | ~3,900 km · ~75–90 ms |
| `us-west-2` (Oregon) | Same set; **+ Reinforcement Fine-Tuning endpoint for Qwen3-32B** ($80/hr training) | ~13,000 km · ~180–220 ms |
| `us-east-1` (Virginia) | Reduced set (no 235B variant) | ~15,500 km · ~230 ms |

**Sydney is the nearest APAC region with Qwen.** All four key models (Qwen3 Next 80B, Qwen3 VL 235B, Qwen3 32B, Qwen3 235B text-only) verified working there via live Converse calls.

### Sydney Qwen pricing (from AWS Bedrock pricing page, verified 10 May 2026)

| Model | Input $/1M | Output $/1M | Batch input | Batch output |
|---|---|---|---|---|
| Qwen3 Next 80B A3B | $0.1545 | $1.2360 | $0.0773 | $0.6180 |
| Qwen3 32B dense | $0.1545 | $0.6180 | $0.0773 | $0.3090 |
| Qwen3 VL 235B A22B | $0.5459 | $2.7398 | $0.2730 | $1.3699 |
| Qwen3 235B A22B 2507 | $0.2266 | $0.9064 | $0.1133 | $0.4532 |

Flex tier 50 % off. Priority tier 75 % premium.

## 3. SageMaker (for GRPO+RLVR fine-tuning per the AWS builder article)

SageMaker training + inference are available everywhere including `ap-southeast-1`. The GPU instance type used by the builder article (`ml.g6e.8xlarge`, 1× NVIDIA L40S) is offered in Singapore; confirm the service quota before launching.

However, **fine-tuning `qwen.qwen3-32b` on Bedrock's OpenAI-compatible endpoint is `us-west-2` only** per AWS docs. If we want fine-tuned Qwen3 and data-residency in SG, SageMaker is the path — deploy the fine-tuned model onto a SageMaker endpoint in `ap-southeast-1`.

## 4. Impact on the three versions

| | **Version A — AWS + Claude** | **Version B — AWS + Qwen** | **Version C — Alibaba + Qwen** |
|---|---|---|---|
| Singapore (PDPA-native)? | ✅ | ❌ Bedrock Qwen is Sydney (closest APAC). SageMaker training is in SG but inference would pull from Bedrock Sydney. | ✅ Alibaba Model Studio natively in Singapore |
| Nearest APAC fallback | — | Sydney | — |
| us-west-2 pin | — | Only if GRPO+RLVR on Bedrock OpenAI-compatible API; SageMaker path avoids this. | — |
| Recommended emergency-lane model | **Nova Micro** (cheaper than Haiku 4.5, available in SG) or Haiku 4.5 (quality) | Qwen3-32B in Sydney (no fine-tune) or fine-tuned Qwen3-4B on SageMaker SG | Qwen3.5-Flash or fine-tuned Qwen3-8B on PAI-EAS |

## 5. Nova Micro vs Qwen3-1.7B / 4B / 32B — honest comparison

User observation: **Nova Micro is cheaper than Qwen3-1.7B.** Let me validate.

### Pure inference cost (1 M tokens)

| Model | Input | Output | Hosting model | Region |
|---|---|---|---|---|
| **Nova Micro** | **$0.035** | **$0.14** | Bedrock managed, on-demand | SG ✅ |
| Nova Lite | $0.06 | $0.24 | Bedrock managed, on-demand | SG ✅ |
| Qwen3 32B | $0.1545 | $0.6180 | Bedrock managed, on-demand | Sydney (not SG) |
| Qwen3-1.7B fine-tuned | — (GPU-hour) | — (GPU-hour) | SageMaker endpoint, e.g. `ml.g5.xlarge` | SG if we host in SG |
| Qwen3-4B fine-tuned | — (GPU-hour) | — (GPU-hour) | SageMaker endpoint, e.g. `ml.g5.2xlarge` | SG if we host in SG |

### Steady-state reality (600k calls/month)

**Nova Micro** on Bedrock: 3k in + 350 out per call → `(3 × $0.035 + 0.35 × $0.14) / 1000` = **$0.00015 per call**. For 600 k calls: **~$90/month**.

**Qwen3-1.7B** fine-tuned on SageMaker endpoint `ml.g5.xlarge` (24×7): **~$1,095/month** fixed.

**Qwen3-4B** fine-tuned on SageMaker endpoint `ml.g5.2xlarge` (24×7): **~$1,095/month** fixed.

Break-even math: Nova Micro stays cheaper than a 24×7 Qwen endpoint until we exceed **~7.3 million calls/month** (12× the pilot). With SageMaker Serverless Inference (scale-to-zero), Qwen endpoint cost can drop to ~$200–400/mo but still loses on token-price-per-call at Nova Micro's tier.

### Quality caveat

Nova Micro is a small model and hasn't been benchmarked on clinical tool-calling the way Qwen3-4B GRPO-tuned was in the AWS builder article (0.96 exact match, 0.95 schema match vs GPT-OSS-120B). Nova Micro's published strength is general instruction-following. **For the emergency lane specifically**, we'd want to benchmark both:
- Nova Micro with prompt engineering + RAG
- GRPO-tuned Qwen3-4B

If Nova Micro (no fine-tune) clears our rubric (citation coverage, grounding, tone), it wins on cost and SG-residency. If it doesn't, we pay the Qwen3-4B endpoint premium for quality.

## 6. Revised recommendation per version

### Version A (AWS + Claude) — primary emergency-lane model options, SG-native

| Option | Notes |
|---|---|
| **Nova Micro** — `apac.amazon.nova-micro-v1:0` | Cheapest Bedrock-managed option in SG. Use without fine-tuning first. |
| **Haiku 4.5** — `global.anthropic.claude-haiku-4-5-20251001-v1:0` | Currently running in the demo. Higher quality, higher price. |

Switch cost analysis: replacing Haiku 4.5 with Nova Micro on the fast lane drops emergency-call cost from ~$0.003 to ~$0.00015 (20× cheaper) while keeping the SG data-residency posture. Quality delta has to be measured on the clinical benchmark before we commit.

### Version B (AWS + Qwen) — Sydney Bedrock + SageMaker SG

| Option | Notes |
|---|---|
| Qwen3-32B base (Bedrock Sydney) | Not SG-native. PDPA-review required. |
| **GRPO-tuned Qwen3-4B on SageMaker SG endpoint** | Data stays in SG; highest-quality student per the AWS builder article. Fixed endpoint cost (~$1,095/mo 24×7 or less with serverless). |
| Qwen3-235B (Bedrock Sydney) | Complex lane only. |

**The value of Version B is the GRPO+RLVR recipe** — training is cheap, quality is great. But if data residency in SG is required, the Bedrock-hosted Qwen base models can't serve your clinical traffic; you must train on SageMaker and host on a SageMaker SG endpoint. This means **Version B's cost floor is ~$1k/mo higher than Version A with Nova Micro**.

### Version C (Alibaba + Qwen) — SG-native

Unchanged. Qwen3.5-Flash or fine-tuned Qwen3-8B on PAI-EAS in the Singapore region.

## 7. What this means for the cost sheet

The **cheapest SG-native option is actually Version A with Nova Micro** for the fast lane, not Version B or C. Let me update `docs/pricing/cost_analysis.md` to reflect this properly:

- Add a "Version A (Nova Micro variant)" column showing ~$90/month fast lane cost.
- Demote "Version B is 45% cheaper" — that was true only if we let the data-residency constraint slide.
- Re-rank the verdict table: A (Nova Micro) < C < A (Haiku 4.5) < B.

Done in the cost doc update following this file.

## 8. Alibaba Model Studio (Singapore International) — embedding & reranker availability

Verified against the Alibaba Cloud Model Studio pricing page (Singapore International endpoint `https://dashscope-intl.aliyuncs.com`) on 10 May 2026. "Chinese Mainland only" entries are listed on the pricing page's mainland tab but do not appear on the International tab.

### Text embeddings — available in Singapore International

| Model | Price (per 1M tokens) | Dims | Max input | Batch size | Notes |
|---|---|---|---|---|---|
| `text-embedding-v4` | $0.07 | 64–2048 | 8,192 tokens | 10 | Qwen3-Embedding series — our primary choice |
| `text-embedding-v3` | $0.07 | 512–1024 | — | — | Older; no reason to prefer v3 over v4 |

### Multimodal embeddings — what the SG International endpoint actually exposes

| Model | Availability | Text price | Image / Video price | Dim | Note |
|---|---|---|---|---|---|
| `tongyi-embedding-vision-plus` | ✅ SG International | $0.09 / 1M | metered per input | 1152 | **Chosen for Version C figure-bearing chunks.** Generates separate text / image / video vectors; no single-vector fusion. |
| `tongyi-embedding-vision-flash` | ✅ SG International | $0.09 / 1M text · $0.03 image-video | metered | 768 | Cheaper faster option; lower dim. |
| `qwen3-vl-embedding` | ❌ Chinese Mainland only | $0.10 / 1M text | $0.258 image/video | 256–2560, fused | Supports `enable_fusion=True` (a single combined vector). **Not available in Singapore International.** The vendor chatbot recommended it in `askAli_AI_Assistant.txt`, but that recommendation implicitly assumed Chinese Mainland deployment. |
| `multimodal-embedding-v1` | Chinese Mainland only | — | — | — | Legacy. |

### Rerankers — what the SG International endpoint actually exposes

| Model | Availability | Price | Doc cap | Note |
|---|---|---|---|---|
| `qwen3-rerank` | ✅ SG International | $0.10 / 1M tokens | 500 docs | **Chosen for Version C reranking.** Text-only. |
| `qwen3-vl-rerank` | ❌ Chinese Mainland only | $0.10 text · $0.258 image | — | Cross-modal reranker (rerank by both text and image). Not available in Singapore International. |
| `gte-rerank-v2` | ❌ Chinese Mainland only | $0.115 / 1M | — | Alibaba's general-purpose reranker. Not in International. |

### Trade-off

Picking `tongyi-embedding-vision-plus` instead of `qwen3-vl-embedding` means text and images embed into **separate** vectors rather than a single fused one. Retrieval still works — the RAG application performs two parallel searches (text-vector kNN + image-vector kNN) and merges results — but for queries that deeply depend on text-image semantic fusion (e.g. "find the page where the flowchart arrow goes from the 'sepsis+' node to the 'vasopressor' node"), we lose some recall versus a fused multimodal index.

To get fused-vector retrieval on Qwen, Nova would need to:

- deploy Version C in **Chinese Mainland** (loses Singapore residency — PDPA-prohibitive for SG hospital data), or
- self-host Qwen3-VL-Embedding on PAI-EAS in Singapore (open weights on HuggingFace) — adds ~$700–1,000/mo of A10 GPU hosting and operational burden.

For the Nova pilot we keep `tongyi-embedding-vision-plus` + `qwen3-rerank` and re-evaluate only if retrieval evaluation shows the fused-vector gap is meaningful for our corpus.

## 9. Next actions

1. **Benchmark Nova Micro + RAG** against Haiku 4.5 + RAG on the isolated AWS-with-Claude environment — same corpus, same 30–50 clinical questions. Measure p50/p95 latency, citation coverage, tone consistency.
2. If Nova Micro passes, switch the running demo's fast lane from Haiku 4.5 to Nova Micro. One-line change in `graph.py`.
3. Only pursue Version B GRPO training if the benchmark shows Nova Micro + RAG can't close the quality gap.
