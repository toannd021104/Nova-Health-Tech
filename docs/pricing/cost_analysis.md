# Cost Analysis — AWS vs Alibaba Cloud (Production, with Caching + Distillation)

All figures are list prices as of **early 2026** in USD, rounded. Confirm current rates with your account team before committing.

## 1. Three cost levers both clouds offer

| Lever | AWS | Alibaba Cloud | Typical savings |
|---|---|---|---|
| **Prompt / context caching** on repeated prefix | Bedrock Prompt Caching (`<cachePoint/>` in Converse API) | Qwen Context Cache — implicit (auto) + explicit | Up to **90% off input tokens** on cache hits; up to **85% lower time-to-first-token** |
| **Batch inference** for offline work | Bedrock Batch (50% off) | Model Studio Batch (50% off) | **50% off input+output tokens** for any non-realtime job |
| **Reserved / provisioned throughput** for peaks | Bedrock Reserved Tier ($/1k TPM monthly) | Qwen Provisioned Throughput Units (PTU) | Flat-rate, removes queueing, consistent latency |

### Options chosen for Nova's main deploy

- **Realtime traffic (emergency + complex lanes)** → on-demand + **prompt/context caching**. Caching shines because our system prompt + tone template + top retrieved chunks repeat across many calls.
- **Teacher batch (distillation dataset, nightly eval)** → **Batch** inference at 50% off.
- **Peak-hours emergency lane only** → **Reserved Tier / PTU**, turned on once traffic is steady and predictable (phase 3).

Prompt caching is the single most impactful optimization — the RAG system prompt and tone template together are ~2–3k tokens and are effectively identical across calls, so they become free after the first hit window.

## 2. Free-tier / trial credits

| Item | AWS | Alibaba Cloud |
|---|---|---|
| LLM free tokens | None for Bedrock; AWS Activate credits possible for startups | **1,000,000 free tokens per Qwen model** at account activation |
| Fine-tuning free quota | None; pay per token trained | PAI workspace activation free; pay per compute job |
| OpenSearch trial | None (OCU billed from minute 1) | Trial banners apply periodically |
| Object storage | 5 GB S3 free first year | OSS small free tier |
| Compute | 1M Lambda invocations/mo free | ~1M FC invocations/mo free |

Ali's 1M-token-per-model quota gives Nova a near-zero-cost RAG+light-finetune prototype. AWS prototype is typically $100–300 in Bedrock charges.

## 3. LLM inference pricing (per 1M tokens)

### AWS Bedrock (on-demand, ap-southeast-1 Singapore)

| Model | Input | Output | Best fit |
|---|---|---|---|
| Claude Haiku 4.5 | ~$1.00 | ~$5.00 | Emergency/fast lane (primary) |
| Claude Sonnet 4.6 | ~$3.00 | ~$15.00 | Complex reasoning + teacher (distillation) |
| Amazon Nova Lite | ~$0.06 | ~$0.24 | **Student (fine-tuned)** for emergency lane (phase 3) |
| Amazon Nova Pro | ~$0.80 | ~$3.20 | Larger student if Lite under-fits |
| Titan Embed Text v2 | ~$0.02 per 1M | — | Text embeddings |
| Nova Multimodal Embeddings | ~$0.06 per 1M + image pricing | — | Figure-bearing chunks |

Batch: 50% off. Prompt-caching: cache writes at a small premium, cache hits discount input tokens up to 90%.

### Alibaba Cloud Model Studio (global pricing, per 1M tokens)

| Model | Input | Output | Best fit |
|---|---|---|---|
| Qwen3.5-Flash | $0.10 | $0.40 | Emergency lane fallback (before student ships) |
| Qwen-Plus / Qwen3-Plus | $0.40 | $1.20 | Mid-tier; optional second teacher |
| Qwen3-Max | $1.20 | $6.00 | Teacher (distillation) + complex reasoning |
| Qwen3-8B (self-host on PAI-EAS, GPU-hour billed) | ~$1–2/hr small GPU | — | **Student (fine-tuned)** for emergency lane |
| text-embedding-v4 | per token | — | Text embeddings |
| qwen3-vl-embedding | per token + per image | — | Figure-bearing chunks |

Batch: 50% off. Implicit context cache hits bill at **20% of standard input price**; explicit cache same discount with guaranteed hit.

## 4. Fine-tuning / distillation cost

### AWS — distill Claude Sonnet → Nova Lite

- Teacher batch generation of ~20k answers with RAG context (avg ~4k input + ~300 output tokens): ~80M input + ~6M output tokens.
  - Batch Sonnet: (80 × $1.50) + (6 × $7.50) ≈ **$165**.
- Bedrock Nova Lite custom-model SFT: typically **$1,500–2,500** end-to-end on a 20k-sample job.
- Hosted custom-model inference via Provisioned Throughput: ~$10–30/hr depending on model and region (only billed when the reserved endpoint is active).
- **Total retrain (quarterly)**: roughly **$2,000 per cycle**.

Note: Claude weights are not available for SFT on Bedrock; distillation targets Nova Lite (Bedrock-native) or an open-weight model on SageMaker.

### Alibaba — distill Qwen3-Max → Qwen3-8B (LoRA)

- Teacher batch generation: 80M + 6M tokens on Qwen3-Max batch pricing (50% off): (80 × $0.60) + (6 × $3.00) ≈ **$66**.
- PAI Model Gallery Qwen3-8B LoRA SFT on A10 GPU: 2–4 GPU-hours × ~$1–2/hr ≈ **$5–30**.
- PAI-EAS hosting: ~$1–2/hr for an A10 serving the 8B model; budget ~$720–1,500/mo if kept warm 24×7 (or lower if scaled on demand).
- **Total retrain (quarterly)**: under **$100 per cycle** for training; hosting is the larger recurring cost.

Ali wins the distillation TCO decisively.

## 5. Vector store

| | AWS — OpenSearch Serverless | Alibaba — OpenSearch Vector Search Edition |
|---|---|---|
| Unit | OCU-hour (search + indexing) | CU-hour + storage |
| Entry monthly cost | ~$170–350/mo (minimum OCU floor) | ~$80–200/mo (small single-node) |
| Scaling | Auto-scale OCUs | Add CUs |
| Notes | Minimum-OCU floor billed even at zero traffic; consider Aurora + pgvector for tiny pilots | Native Model Studio embedding plugin handles re-vectorization |

## 6. Indicative monthly cost — 500-physician production pilot, with all optimizations on

Assumptions:

- 500 physicians × 40 queries/day = 20,000/day → ~600,000/month.
- Average request: 3,000 input + 350 output tokens (with RAG context and the tone template).
- Traffic split: 60% emergency (fast lane), 35% complex, 5% top-tier.
- **Semantic cache** hit 35% on the fast lane (no LLM call).
- **Prompt / context cache** hit 70% of remaining calls (those calls pay ~10% of normal input token cost for the cached prefix; we conservatively apply a 50% effective discount on input tokens overall).
- Vector store: ~20 GB indexed, moderate search.
- Distillation retrain: one per quarter, amortized.

### AWS (production, optimized)

| Item | Unit calc | Cost |
|---|---|---|
| Fast lane — Claude Haiku 4.5 | 360k × 65% (after sem cache) = 234k calls × (3k in + 350 out); input effective price ~$0.50 after prompt cache | ~**$800** |
| Complex lane — Sonnet 4.6 | 210k × (3k in + 350 out); input effective price ~$1.50 after prompt cache | ~**$1,700** |
| Top-tier escalation | 30k × same (stays on Sonnet; Opus not used) | ~**$250** |
| Titan text embeddings (ingest + queries) | ~500M tokens amortized | ~**$10** |
| Nova Multimodal embeddings (figure chunks) | ~50M tokens + images | ~**$20** |
| Bedrock Guardrails | per call | ~**$60** |
| OpenSearch Serverless (baseline + 20 GB) | min 1+1 OCU × 720 hr × ~$0.24 | ~**$350** |
| Comprehend Medical DetectPHI | per 100-char unit on input | ~**$180** |
| Lambda + API Gateway + CloudFront + WAF | serverless | ~**$150** |
| S3 + CloudTrail (Object Lock) + Macie | low | ~**$120** |
| ElastiCache Valkey/Redis (cache.t4g.small × 2 AZ with RediSearch) | | ~**$80** |
| Distillation retrain, amortized | $2k / 3 | ~**$700** |
| **AWS total** | | **≈ $4,540 / month** |

Without the caching layers, the same workload would run ~$7–8k/month. With prompt caching + semantic cache + router biasing traffic to Haiku, roughly **30–40% savings** is realistic. When the Nova Lite student ships in phase 3, the fast-lane cost drops further by 80–90% — typical post-distillation AWS total settles around **$3,000–3,500 / month**.

### Alibaba Cloud (production, optimized)

| Item | Unit calc | Cost |
|---|---|---|
| Fast lane — Qwen3-8B student on PAI-EAS | 234k calls routed to PAI-EAS; serve on 1× A10 always-on | ~**$1,200** (GPU-hour) |
| Slow lane — Qwen3-Max | 210k × (3k in + 350 out); input effective price ~$0.60 after context cache | ~**$580** |
| Top-tier path — Qwen3-Max with longer context | 30k × same | ~**$90** |
| text-embedding-v4 (ingest + queries) | ~500M tokens | ~**$25** |
| qwen3-vl-embedding (figure chunks) | ~50M + images | ~**$30** |
| Content Moderation 2.0 | per call | ~**$50** |
| OpenSearch Vector Search Edition (small cluster) | | ~**$180** |
| DataWorks SDDP PHI masking | | ~**$120** |
| FC + API Gateway + CDN + WAF | | ~**$90** |
| OSS + ActionTrail + SLS WORM | | ~**$70** |
| Tair (Redis-compatible) + TairVector | | ~**$60** |
| Distillation retrain, amortized | $100 / 3 | ~**$35** |
| **Alibaba total** | | **≈ $2,530 / month** |

Note: you can trade GPU-hour for token-cost by serving the student via a Qwen Plus/Flash API instead of PAI-EAS. That brings the fast-lane cost to ~$50–$100/mo at the expense of less control over latency and tone. Most Nova-class deployments justify the dedicated endpoint on the emergency lane.

## 7. When AWS is the right call despite higher cost

- US hospital clients require a signed BAA + US HIPAA-eligible services in US regions.
- Compliance team prefers AWS's well-mapped HIPAA posture.
- Nova already has EDP / Activate credits that absorb much of the bill.
- Clinical leadership wants Claude Sonnet as the teacher's quality ceiling.

## 8. When Alibaba is the right call

- International rollout outside the US, especially APAC or mainland China.
- Cost ceiling is a hard constraint.
- Nova wants open weights (Qwen3-8B) so they can also serve on-prem when a hospital requires it.
- Heavy distillation / fine-tune cadence planned.

## 9. References

- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Amazon Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/)
- [Amazon Nova Pricing](https://aws.amazon.com/nova/pricing/)
- [Alibaba Cloud Model Studio model pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [Qwen Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache)
- [PTU and token-based billing for Model Studio](https://www.alibabacloud.com/help/en/model-studio/model-training-and-deployment-billing)

*Content above is rephrased for compliance with licensing restrictions.*
