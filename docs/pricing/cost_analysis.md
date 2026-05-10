# Cost Analysis — AWS vs Alibaba Cloud (Singapore, with caching + distillation)

All figures are list prices as of **early 2026** in USD, rounded. Confirm with the account team before committing — cloud pricing moves.

## 1. Three cost levers both clouds offer

| Lever | AWS | Alibaba Cloud | Savings |
|---|---|---|---|
| **Prompt / context caching** on repeated prefix | Bedrock Prompt Caching (`<cachePoint/>` in Converse) | Qwen Context Cache — implicit + explicit | Up to **90% off** on cached input tokens, up to **85% lower** time-to-first-token |
| **Batch inference** for offline jobs | Bedrock Batch (50% off) | Model Studio Batch (50% off) | **50% off** tokens for any non-realtime workload |
| **Reserved / provisioned throughput** | Bedrock Reserved Tier ($/1k TPM monthly) | Qwen PTU | Flat rate, removes queueing, consistent latency |

### Options chosen for Nova's main deploy

- **Realtime traffic** (both lanes) → on-demand + **prompt caching** on the static system prompt + tone template + top retrieved chunks.
- **Teacher batch** (distillation dataset, nightly LLM-as-judge eval) → **Batch** at 50% off.
- **Peak-hour emergency lane only** → **Reserved Tier / PTU** once traffic is steady and predictable (phase 3).

The most impactful optimization is prompt caching: the Nova system prompt + tone template + the emergency-disclaimer preamble run ~2–3 KB and are identical across calls, so they become near-free after the first hit.

## 2. Free-tier / trial credits

| Item | AWS | Alibaba |
|---|---|---|
| LLM free tokens | None on Bedrock; AWS Activate credits possible for startups | **1M free tokens per Qwen model** at activation |
| Fine-tuning free quota | None | PAI workspace activation is free; pay per compute job |
| OpenSearch trial | None (OCU billed from minute 1) | Trial banners apply periodically |
| Object storage | 5 GB free first year | OSS regional free tier |
| Compute | 1M Lambda req/mo free | ~1M FC req/mo free |

Ali's 1M-token-per-model quota enables a near-zero-cost prototype. AWS prototype is typically $100–300 in Bedrock charges.

## 3. LLM inference pricing (per 1M tokens)

### AWS Bedrock (Singapore, `ap-southeast-1`, via `global.*` inference profiles)

| Model | Input | Output | Role in this design |
|---|---|---|---|
| Claude Haiku 4.5 | ~$1.00 | ~$5.00 | **Emergency lane (primary)** |
| Claude Sonnet 4.5 | ~$3.00 | ~$15.00 | **Complex lane + distillation teacher** |
| Amazon Nova Lite | ~$0.06 | ~$0.24 | Fine-tuned student from phase 3 (replaces Haiku for emergency) |
| Cohere Embed v4 | ~$0.12 per 1M tokens | — | Text embeddings (Titan v2 not in Singapore today) |
| Amazon Nova Multimodal Embeddings | ~$0.06 per 1M + image fees | — | Figure-bearing chunks |

- **Batch**: 50% off.
- **Prompt caching**: cache writes at a small premium, cache hits discount input tokens up to 90%.
- **Claude Opus is not used** in this design.

### Alibaba Cloud Model Studio (Singapore, per 1M tokens)

| Model | Input | Output | Role |
|---|---|---|---|
| Qwen3.5-Flash | $0.10 | $0.40 | Emergency lane fallback |
| Qwen-Plus | $0.40 | $1.20 | Mid-tier, optional second teacher |
| Qwen-Max (Qwen3-Max) | $1.20 | $6.00 | Complex lane + distillation teacher |
| Qwen3-8B on PAI-EAS | ~$1–2/hr small GPU | — | Fine-tuned student (phase 3) |
| text-embedding-v4 | per-token | — | Text embeddings |
| qwen3-vl-embedding | per-token + per-image | — | Figure-bearing chunks |

- Batch: 50% off.
- Implicit context cache hits bill at **20% of normal input price**; explicit cache same discount with guaranteed hit.

## 4. Per-request budget (the 2-second emergency case, post-phase-3)

This matches the workflow in `docs/architecture/workflow_detailed.md`.

| Step | Cost driver | Approx per call |
|---|---|---|
| 1 | Browser → edge | free (CloudFront) |
| 2 | API Gateway + Cognito auth | ~$0.0000035 / call |
| 3 | PHI mask (Comprehend Medical) + semantic cache lookup | $0.00010 per 100 chars ≈ $0.00015 |
| 4 | OpenSearch Serverless hybrid retrieval + Cohere embedding of the query | ~$0.00002 query embedding + included in OCU-hour |
| 5a | **Haiku 4.5** — 3k input (cached 70%) + 350 out = ~$0.00091 + $0.00175 | **≈ $0.0027** |
| 5b | Sonnet 4.5 — 3k input (cached 70%) + 600 out = ~$0.00273 + $0.0090 | ≈ $0.012 |
| 6 | Bedrock Guardrails | ~$0.00010 per 1k text units ≈ $0.00030 |
| 7 | Response streaming | included |
| 8 | Audit log write (CloudWatch + S3) | ~$0.000005 |

**Total per emergency call:** ~$0.003 (post-caching, Haiku).
**Total per complex call:** ~$0.013 (post-caching, Sonnet).

## 5. Distillation cost (quarterly retrain)

### AWS — distill Claude Sonnet 4.5 → Nova Lite

- Teacher batch generation of 20k answers with RAG context (avg 4k input + 300 output): ~80M in + 6M out tokens.
  - Sonnet batch: `(80 × $1.50) + (6 × $7.50)` ≈ **$165**.
- Bedrock Nova Lite custom-model SFT: typically **$1,500–2,500** per run.
- Hosted Nova Lite custom-model inference via Provisioned Throughput: ~$10–30/hr when the endpoint is active.
- **Total retrain**: ~**$2,000 per quarter**.

### Alibaba — distill Qwen-Max → Qwen3-8B (LoRA)

- Teacher batch: 80M in + 6M out on Qwen-Max batch: `(80 × $0.60) + (6 × $3.00)` ≈ **$66**.
- PAI Model Gallery Qwen3-8B LoRA SFT on A10 GPU: 2–4 GPU-hrs × ~$1–2/hr ≈ **$5–30**.
- PAI-EAS hosting: ~$1–2/hr for A10 serving the 8B model; ~$720–1,500/mo if kept warm.
- **Total retrain**: under **$100 per quarter** for training.

## 6. Vector store

| | AWS — OpenSearch Serverless | Alibaba — OpenSearch Vector Search |
|---|---|---|
| Unit | OCU-hour (search + indexing) | CU-hour + storage |
| Entry monthly | ~$170–350/mo (min OCU floor) | ~$80–200/mo (small single-node) |

## 7. Indicative monthly cost — 500-physician production pilot, all optimizations on

Assumptions:

- 500 physicians × 40 queries/day = 20k/day → ~600k/month.
- Average 3,000 input + 350 output tokens.
- Lane split driven by the clinician's **emergency toggle** — no classifier call.
- Observed split: 30% emergency (Haiku), 70% complex (Sonnet).
- **Semantic cache** hit 35% of emergency queries (shared emergency protocols repeat across shifts).
- **Prompt cache** hit 70% of the remaining calls → ~50% effective input-token discount.
- Vector store ~20 GB indexed.
- Distillation retrain quarterly, amortized.

### AWS (production, Singapore)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Haiku 4.5 | 180k × 65% = 117k calls × $0.003/call (with caching) | ~**$350** |
| Complex lane — Sonnet 4.5 | 420k × $0.013/call | ~**$5,460** |
| Cohere Embed v4 (ingest + queries) | ~500M tokens amortized | ~**$60** |
| Nova Multimodal embeddings (figure chunks) | ~50M tokens + images | ~**$40** |
| Bedrock Guardrails | per call | ~**$180** |
| OpenSearch Serverless (baseline + 20 GB) | min 1+1 OCU × 720 hr × ~$0.24 | ~**$350** |
| Comprehend Medical DetectPHI | per 100-char unit | ~**$180** |
| Lambda + API Gateway + CloudFront + WAF | serverless | ~**$150** |
| S3 + CloudTrail Object Lock + Macie | low | ~**$120** |
| ElastiCache Valkey (cache.t4g.small × 2 AZ, RediSearch) | | ~**$80** |
| Distillation retrain, amortized | $2k / 3 | ~**$700** |
| Site-to-Site VPN (dual tunnel) | 2 × ~$36 + data out | ~**$80** |
| **AWS total** | | **≈ $7,750 / month** |

Dropping to Haiku for more of the traffic (say 60/40 by training clinicians to use the toggle) would pull this down to ~$4.5k.

Without any caching this would be ~$11–13k. With all three cache layers + Sonnet as the default we're at ~$7.8k. If the 60/40 split holds, it's ~$4.5k. After phase-3 distillation (Nova Lite replacing Haiku), the fast lane drops from $350/mo to well under $50, and the total settles near **$3.5–4k**.

### Alibaba Cloud (production, Singapore)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3.5-Flash / Qwen3-8B student | 117k calls × ~$0.0015 | ~**$175** |
| Complex lane — Qwen-Max | 420k × ~$0.005 (with cache) | ~**$2,100** |
| text-embedding-v4 | ~500M tokens | ~**$50** |
| qwen3-vl-embedding (figures) | ~50M + images | ~**$60** |
| Content Moderation 2.0 | per call | ~**$50** |
| OpenSearch Vector Search Edition (small cluster) | | ~**$180** |
| DataWorks SDDP PHI masking | | ~**$120** |
| FC + API Gateway + CDN + WAF | | ~**$90** |
| OSS + ActionTrail + SLS WORM | | ~**$70** |
| Tair (Redis-compatible) | | ~**$60** |
| Distillation retrain, amortized | $100/3 | ~**$35** |
| IPsec-VPN Gateway | | ~**$60** |
| **Alibaba total** | | **≈ $3,050 / month** |

Serving the Qwen3-8B student on PAI-EAS full-time adds ~$720–1,500/mo — not included above because it only becomes relevant in phase 3, and can be replaced with Qwen-Flash API calls if utilization is low.

## 8. When AWS is the right call

- US hospital clients requiring BAA + US-eligible services in US regions (then deploy `us-east-1` tenant separately).
- Clinical leadership wants Claude-class reasoning as the teacher's quality ceiling.
- Existing EDP / Activate credits on AWS absorb much of the bill.
- Strong compliance-team familiarity with AWS HIPAA posture.

## 9. When Alibaba is the right call

- International / APAC rollout outside the US; mainland-China expansion likely.
- Cost ceiling is a hard constraint.
- Open weights for Qwen let Nova also ship on-prem when a hospital requires it.
- Heavy distillation / fine-tune cadence planned.

## 10. References

- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Amazon Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/)
- [Amazon Nova Pricing](https://aws.amazon.com/nova/pricing/)
- [Alibaba Model Studio Pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [Qwen Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache)
- [PTU and token-based billing for Model Studio](https://www.alibabacloud.com/help/en/model-studio/model-training-and-deployment-billing)

*Content above is rephrased for compliance with licensing restrictions.*
