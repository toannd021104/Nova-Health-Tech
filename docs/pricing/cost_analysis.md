# Cost Analysis — AWS vs Alibaba Cloud for Nova Health Tech Clinical GenAI

All figures are list prices as of **early 2026**, in USD, rounded. Confirm current rates with your account team before committing — cloud pricing moves weekly.

## 1. Free-tier / trial credits at start

| Item | AWS | Alibaba Cloud |
|---|---|---|
| LLM free tokens | AWS Free Tier does not include Bedrock tokens; sign up may include marketing credits | **1,000,000 free tokens per Qwen model** (one-time, at account activation) |
| Fine-tuning free quota | None; pay per token trained | PAI workspace activation is free; pay per compute job |
| Embedding free quota | None; pay per token | Model Studio embedding model gets a share of the 1M-token quota |
| OpenSearch trial | OpenSearch Serverless charges per OCU hour from minute 1 (no free tier) | OpenSearch Vector Search Edition — check current free trial banner; historically 1-month trial on small instance |
| Object storage | 5 GB S3 Standard free (first 12 months) | OSS has per-region free tier; ~5 GB standard storage typically free in trial |
| CDN | 1 TB out/month (first 12 months) | CDN has regional trial quotas |
| Compute | 1M Lambda requests + 400k GB-s free monthly | FC has ~1M free invocations monthly, free tier |

**Bottom line for Ali free trial**: the 1M token quota per Qwen model plus PAI's free activation lets Nova prototype RAG + a small Qwen3-8B fine-tune for roughly **$0–50** in out-of-pocket spend. AWS Bedrock has no comparable token free tier, so prototype cost is closer to **$100–300**.

## 2. LLM inference pricing (per 1M tokens)

### AWS Bedrock (on-demand, us-east-1)

| Model | Input | Output | Best fit |
|---|---|---|---|
| Claude Haiku 4.5 | ~$1.00 | ~$5.00 | Emergency lane (fast) |
| Claude Sonnet 4.6 | ~$3.00 | ~$15.00 | Complex reasoning |
| Claude Opus 4.6 | ~$15.00 | ~$75.00 | Rarely — only complex consults |
| Amazon Nova Lite | ~$0.06 | ~$0.24 | Tone fine-tune target; low-latency answers |
| Amazon Nova Pro | ~$0.80 | ~$3.20 | Mid-tier reasoning |
| Amazon Nova Premier | ~$2.50 | ~$12.50 | Top-tier reasoning |
| Titan Text Express (embeddings/legacy) | ~$0.20 | ~$0.60 | Legacy |
| Nova Multimodal Embeddings | ~$0.06 per 1M tokens + image pricing | — | Embedding |

Batch: 50% off. Reserved tier: fixed price per 1k tokens-per-minute, monthly invoice.

### Alibaba Cloud Model Studio (global pricing, per 1M tokens)

| Model | Input | Output | Best fit |
|---|---|---|---|
| Qwen3.5-Flash | $0.10 | $0.40 | Emergency lane (fast) |
| Qwen-Plus / Qwen3-Plus | $0.40 | $1.20 | Balanced primary model |
| Qwen3.5-Plus | $0.40 | $2.40 | Balanced, long-context |
| Qwen3.6-Plus | $0.50–$2.00 | $3.00–$6.00 | Multimodal, 1M context |
| Qwen3-Max | $1.20 | $6.00 | Complex reasoning |
| qwen3-vl-embedding | per token + per image | — | Multimodal embedding |

Batch: 50% off. Context caching: further discount on repeated input (useful for repeated system prompts + retrieved chunks).

**Ali is roughly 5–10× cheaper per token than AWS Bedrock for a comparable-quality model.** That changes the shape of the architecture: you can afford a larger retrieved-context window on Qwen, which can partially substitute for aggressive reranking.

## 3. Fine-tuning cost

### AWS

- **Bedrock custom models** — charged per training token and per hour of training job; a 10k-sample Nova Lite SFT run is typically **low four figures** USD.
- **SageMaker training for Llama 3.2/3.3 LoRA** — 1× ml.g5.12xlarge for a few hours ≈ **$50–150** per run; much cheaper than Bedrock custom, but you manage the GPU cluster.
- Hosted custom model inference requires Provisioned Throughput — commit fees can run **$20–80/hour** depending on model.

### Alibaba Cloud

- **PAI Model Gallery Qwen3-8B LoRA** on A10 GPU: typical 10k-sample SFT job ~1–3 GPU-hours → **$5–30** total.
- **PAI-EAS serving** fine-tuned Qwen3-8B: starts around ~$0.8–$2/hour for a small GPU instance; A10 for a 7–8B model runs around $1–2/hour.
- **Model Studio token-based tuning** for Qwen-Plus/Turbo — you pay by training tokens at a published rate (visible in the training console before the job starts); no GPU-hour billing.

Fine-tuning on Ali is decisively cheaper for Qwen — that's the main reason the Ali proposal is attractive for phase-2 work.

## 4. Vector store pricing

| | AWS — OpenSearch Serverless (vector) | Alibaba — OpenSearch Vector Search Edition |
|---|---|---|
| Unit | OCU-hour (search OCU + indexing OCU) | Compute unit hour (CU) + storage |
| Entry monthly cost | ~$170–350/month for small workloads (minimum 2 OCUs each) | Entry single-node ~$80–200/month |
| Scaling | Auto-scale OCUs | Scale CU count |

AWS minimum-OCU floor (was 2 each; now 1 in most regions) is the thing that can surprise small teams — you pay that floor even with zero traffic. For a pilot, consider **Aurora PostgreSQL + pgvector** on AWS (cheaper) if Bedrock KB flexibility isn't needed day-one.

## 5. Storage, logs, networking

Roughly comparable; both providers charge cents per GB-month for object storage and per-GB egress. Budget ~$20–50/month for a pilot footprint of a few GB of PDFs + logs.

## 6. Indicative monthly cost — 500-physician pilot

Assumptions:

- 500 physicians, 40 queries/day average per physician → 20,000 queries/day, ~600,000/month.
- Average query: 3k input tokens (context + RAG chunks), 400 output tokens.
- 60% on fast model (emergency lane), 35% on balanced model, 5% on top-tier.
- Vector store: ~10 GB index, moderate search volume.
- Fine-tune: one Qwen3-8B / Nova Lite SFT per quarter.

### AWS monthly estimate

| Item | Units | Cost |
|---|---|---|
| Haiku 4.5: 360k queries × (3k input + 400 out) × $1/$5 per M | 1.08B input + 144M out | ~$1,080 + $720 = **$1,800** |
| Sonnet 4.6: 210k queries × same × $3/$15 per M | 630M in + 84M out | ~$1,890 + $1,260 = **$3,150** |
| Opus 4.6: 30k queries × same × $15/$75 | 90M in + 12M out | ~$1,350 + $900 = **$2,250** |
| Nova Multimodal Embeddings (ingest) | ~200M tokens | ~$12 |
| Bedrock Guardrails | included per call (few cents per 1k calls) | ~$60 |
| OpenSearch Serverless (min 2+2 OCUs) | 720 hr × ~$0.24/OCU | ~**$350** |
| Comprehend Medical (DetectPHI on inputs) | ~$0.0001 per 100 chars | ~**$180** |
| Lambda + API Gateway + CloudFront | serverless | ~**$120** |
| S3 + CloudTrail + Macie | | ~**$80** |
| ElastiCache Redis (cache.t4g.small × 2 AZ) | | ~**$50** |
| **AWS subtotal** | | **~$8,050 / month** |

Fine-tune quarterly ≈ **$2,000–3,000** per run, amortized ~$700/month.

### Alibaba Cloud monthly estimate

| Item | Cost |
|---|---|
| Qwen3.5-Flash: 360k queries × (3k in + 400 out) × $0.10/$0.40 per M | ~$108 + $58 = **$166** |
| Qwen-Plus: 210k × same × $0.40/$1.20 | ~$252 + $101 = **$353** |
| Qwen3-Max: 30k × same × $1.20/$6.00 | ~$108 + $72 = **$180** |
| qwen3-vl-embedding (ingest + queries) | ~**$30** |
| Content Moderation 2.0 for Qwen | ~**$50** |
| OpenSearch Vector Search Edition (small cluster) | ~**$180** |
| SDDP / DataWorks PHI masking | ~**$120** |
| FC + API Gateway + CDN | ~**$80** |
| OSS + ActionTrail + SLS | ~**$60** |
| Tair (Redis-compatible) | ~**$40** |
| **Alibaba subtotal** | **~$1,260 / month** |

Fine-tune quarterly on Qwen3-8B ≈ **$30–100** per run, amortized < $50/month.

### Cost comparison

For this workload **Alibaba is ~6× cheaper on token spend**, driven by Qwen's aggressive pricing. AWS costs flip if:

- Your clients require US HIPAA + US data-residency (Ali's HIPAA posture is weaker; BAA is region-specific).
- You need deep Claude-class reasoning for a majority of queries.
- You already have committed AWS EDP spend and can apply credits.

## 7. Credit / savings levers

| | AWS | Alibaba |
|---|---|---|
| Volume commit | Enterprise Discount Program (EDP), Private Pricing Agreement | Enterprise Discount Agreement |
| Batch inference | 50% off on Bedrock | 50% off on Model Studio |
| Reserved | Bedrock Reserved Tier (fixed $/kTPM monthly) | Qwen PTU (Provisioned Throughput Units) |
| Caching | Semantic cache in ElastiCache | Context caching + Tair |
| Model right-sizing | Route to Haiku/Nova Lite when possible | Route to Qwen3.5-Flash when possible |
| Self-host | SageMaker + Llama if latency/cost tips that way | PAI-EAS with fine-tuned Qwen on A10 — from ~$1/hr |

## 8. What to verify with the account team before committing

- **AWS Bedrock BAA scope** for Comprehend Medical + Guardrails + your specific model IDs.
- **Bedrock model availability** in `us-east-1` and `eu-central-1` (model availability varies by region).
- **Alibaba HIPAA BAA** availability in your target region.
- **Alibaba China regions** — only needed if you serve mainland hospitals; triggers MLPS L3 + PIPL scope.
- **Current free trial** pages — AWS credits sometimes available via AWS Activate / AWS for Healthcare; Alibaba runs periodic credit campaigns.

## References

- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [Amazon Nova Pricing](https://aws.amazon.com/nova/pricing/)
- [Alibaba Cloud Model Studio model pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [Understand PTU and Token-Based Billing for Model Studio](https://www.alibabacloud.com/help/en/model-studio/model-training-and-deployment-billing)
- [Alibaba Model Studio free quota](https://www.alibabacloud.com/help/en/model-studio/new-free-quota)
- [PAI product purchase guidelines](https://www.alibabacloud.com/help/en/pai/pai-product-purchase-guidelines)

*Content above is rephrased for compliance with licensing restrictions.*
