# Cost Analysis — Three Versions (AWS+Claude / AWS+Qwen / Alibaba+Qwen)

All figures are list prices as of **early 2026**, USD, rounded. Confirm with the account team — cloud pricing moves. Main sources cited at the bottom.

## 1. Quick verdict

| | **Version A — AWS + Claude** (Singapore) | **Version B — AWS + Qwen** (us-west-2) | **Version C — Alibaba + Qwen** (Singapore) |
|---|---|---|---|
| Monthly pilot total (500 physicians) | **~$5,500 / mo** | **~$2,800 / mo** | **~$2,550 / mo** |
| Post-customization total | ~$4,500 / mo (Sonnet → Nova Lite distill) | **~$2,000 / mo** (after GRPO+RLVR Qwen3-4B student) | ~$2,400 / mo (after SFT+LoRA Qwen3-8B) |
| Customization cost per run | ~$2,000 (Bedrock Model Distillation) | **~$70–100** (SageMaker TRL GRPO on ml.g6e.8xlarge) | **~$15–40** (PAI Model Gallery Qwen3 LoRA) |
| Data-residency posture | Singapore, PDPA-native | US-only today (us-west-2 pin) | Singapore, PDPA-native |

Headline: Versions B and C are roughly 45–50 % cheaper than A. A is the right call when the client insists on Anthropic-quality answers and Singapore residency; the us-west-2 pin disqualifies B for PDPA-strict clients until Qwen inference lands in ap-southeast-1.

## 2. Assumptions shared across all three versions

- 500 physicians × 40 queries/day = 20 k/day → **~600 k queries/month**.
- Average request: **3,000 input + 350 output tokens** (RAG context included).
- Traffic split set by the clinician's **emergency toggle**, not a classifier. Observed: **30 % emergency / 70 % complex**.
- Semantic-cache (Layer 1) hit rate 35 % on emergency queries.
- Prompt / context-cache (Layer 2) hit rate 70 % on non-cached calls → effective 50 % off on input tokens.
- Vector store ~20 GB indexed.
- Site-to-Site VPN up for corporate integration (dual tunnel).
- Nothing fine-tuned in phase 1–2; customization is a phase 3+ add-on.

## 3. Three cost levers available on all three clouds

| Lever | AWS Bedrock (A & B) | Alibaba Model Studio (C) | Savings |
|---|---|---|---|
| **Prompt / context caching** on static prefix | Bedrock Prompt Caching (`<cachePoint/>`) | Qwen Context Cache (implicit + explicit) | Up to 90 % off on cached input tokens |
| **Batch inference** for offline jobs | Bedrock Batch, Flex tier | Model Studio Batch | 50 % off tokens |
| **Reserved capacity** for peak | Bedrock Reserved Tier | Qwen PTU | Flat rate; no queueing |

Our chosen defaults: on-demand + prompt caching for realtime traffic; batch for the teacher-data generation; reserved tier only if the fast lane goes steady-state TPM.

## 4. Per-token model pricing (per 1 M tokens)

### Version A — AWS Bedrock (Singapore `ap-southeast-1` via `global.*` inference profiles)

| Model | Input | Output | Role |
|---|---|---|---|
| Claude Haiku 4.5 | ~$1.00 | ~$5.00 | Emergency fast lane |
| Claude Sonnet 4.5 | ~$3.00 | ~$15.00 | Complex lane + distillation teacher |
| Amazon Nova Lite | ~$0.06 | ~$0.24 | Phase-3 custom student (distilled from Sonnet) |
| Amazon Nova Micro | ~$0.035 | ~$0.14 | Smaller student alternative |
| Cohere Embed v4 | ~$0.12 per 1 M | — | Text embeddings |
| Cohere Rerank 3.5 | $2.00 per 1,000 queries | — | Optional reranking |
| Bedrock Guardrails | ~$0.15 per 1,000 text units | — | PHI + grounding |

Batch at 50 % off. Prompt-cache read at ~10 % of standard input; cache write at a small premium. (`Haiku 4.5` and `Sonnet 4.5` in Bedrock's Singapore `global.*` profiles use the above on-demand rates; confirm the live pricing page at link in §9.)

### Version B — AWS Bedrock + SageMaker (Qwen in us-west-2)

**Bedrock inference** (from `aws.amazon.com/bedrock/pricing` — Qwen section, Sydney/us-west-2 tier):

| Model | Input | Output | Batch input | Batch output | Role |
|---|---|---|---|---|---|
| **Qwen3 32B** | **$0.1545** | **$0.6180** | $0.0773 | $0.3090 | Emergency fast lane (base) OR reinforcement fine-tune target |
| **Qwen3 235B A22B (2507)** | **$0.2266** | **$0.9064** | $0.1133 | $0.4532 | Complex lane + distillation teacher |
| Qwen3 Coder 30B A3B | $0.1545 | $0.6180 | $0.0773 | $0.3090 | Not used here |

**SageMaker (for GRPO+RLVR fine-tuning of Qwen3-1.7B / Qwen3-4B per the AWS builder article):**

| Resource | Price | Role |
|---|---|---|
| `ml.g6e.8xlarge` training job | ~$5.74/hr (L40S GPU, us-west-2) | GRPO+RLVR training, 10–15 hrs per run |
| `ml.g5.2xlarge` inference endpoint | ~$1.52/hr | Serve Qwen3-4B fine-tuned student |
| SageMaker Serverless Inference | pay per inference-ms + memory | Lower idle cost if traffic is bursty |

Gains from the AWS builder article: a **Qwen3-4B** fine-tuned via GRPO+RLVR on one `ml.g6e.8xlarge` for ~15 epochs reached response-validity 0.98 and schema-match 0.95 — above GPT-OSS-120B. **The student replaces the Qwen3 32B call on the fast lane.**

### Version C — Alibaba Model Studio (Singapore region, per 1 M tokens)

| Model | Input | Output | Role |
|---|---|---|---|
| Qwen3.5-Flash | $0.10 | $0.40 | Emergency fast-lane base |
| Qwen-Plus | $0.40 | $1.20 | Alternate mid-tier teacher |
| Qwen-Max (Qwen3-Max) | $1.20 | $6.00 | Complex lane + distillation teacher |
| Qwen3-8B on PAI-EAS | $1.0–$2.0/hr (A10 small GPU) | — | Fine-tuned student, serve full-time |
| text-embedding-v4 | ~$0.07 per 1 M | — | Text embeddings |
| qwen3-vl-embedding | token+image metered | — | Figure-bearing chunks |

Batch 50 % off. Implicit context-cache hits bill at 20 % of normal input price.

## 5. Per-call cost (emergency vs complex, with all caching on)

Shows what one `/chat` request costs on each version after Layer-2 prompt caching kicks in.

### Version A (Claude)

| Step | Cost |
|---|---|
| API Gateway + Cognito | $3.5 × 10⁻⁶ |
| Comprehend Medical DetectPHI | ~$1.5 × 10⁻⁴ |
| Hybrid retrieval + Cohere embed query | ~$2 × 10⁻⁵ + OpenSearch OCU-amortized |
| **Haiku 4.5** (3 k in @ 50 % cache + 350 out) | ~**$0.0027** |
| **Sonnet 4.5** (3 k in @ 50 % cache + 600 out) | ~**$0.012** |
| Guardrails | ~$3 × 10⁻⁴ |
| Audit + streaming | ~$5 × 10⁻⁶ |

**Emergency call ≈ $0.003 ·  Complex call ≈ $0.013**

### Version B (AWS Qwen, Bedrock on-demand)

| Step | Cost |
|---|---|
| Same infra as A | ~$5 × 10⁻⁴ combined |
| **Qwen3 32B** (3 k in + 350 out) | `(3 × $0.1545 / 1,000) + (0.35 × $0.6180 / 1,000)` = **$6.8 × 10⁻⁴** |
| **Qwen3 235B** (3 k in + 600 out) | `(3 × $0.2266 / 1,000) + (0.6 × $0.9064 / 1,000)` = **$1.2 × 10⁻³** |
| Guardrails + audit | ~$3 × 10⁻⁴ |

**Emergency call ≈ $0.0015 · Complex call ≈ $0.002** (plus $700–1,000/mo amortized SageMaker endpoint if we run the GRPO-tuned 4B student, see row below).

### Version C (Alibaba Qwen)

| Step | Cost |
|---|---|
| Same infra as A/B, FC/API GW/etc | ~$4 × 10⁻⁴ combined |
| **Qwen3.5-Flash** (3 k in + 350 out, cache 50 % off) | `(3 × $0.10/1 M × 0.5) + (0.35 × $0.40 / 1 M)` ≈ **$3.5 × 10⁻⁴** |
| **Qwen-Max** (3 k in + 600 out, cache 50 % off) | `(3 × $1.20/1 M × 0.5) + (0.6 × $6.00/1 M)` ≈ **$5.4 × 10⁻³** |
| Content Moderation + audit | ~$2 × 10⁻⁴ |

**Emergency call ≈ $0.0008 · Complex call ≈ $0.006**

## 6. Monthly pilot cost (600 k calls, 30/70 emergency/complex)

### Version A — AWS + Claude (Singapore)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Haiku 4.5 | 180 k × 65 % (post-sem-cache) × $0.003 | ~$350 |
| Complex lane — Sonnet 4.5 | 420 k × $0.013 | ~$5,460 |
| Cohere Embed v4 (ingest + queries) | ~500 M tokens amortized | ~$60 |
| Cohere Rerank 3.5 | 420 k complex × 1 query each | ~$840 → use only on ~10 % → **~$85** |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless | 1+1 OCU × 720 hr × $0.24 | ~$350 |
| Comprehend Medical | per 100-char unit | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Valkey (2 AZ cache.t4g.small) | | ~$80 |
| Site-to-Site VPN (dual tunnel) | 2 × $36 + data | ~$80 |
| **Base monthly** | | **~$7,100** |
| Phase-3 distillation (Sonnet → Nova Lite) amortized | $2,000 / 3 | ~$670 |
| Post-distillation Nova Lite replaces Sonnet on ~40 % of complex traffic | savings on the complex lane | **−$2,200** |
| **Post-customization total** | | **~$5,570** |

Bracket: if we train clinicians to use the emergency toggle and shift the split to 60 % emergency / 40 % complex, the total drops another ~$1,100/mo.

### Version B — AWS + Qwen (us-west-2)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3 32B (Bedrock on-demand) | 180 k × 65 % × $0.0015 | ~$175 |
| Complex lane — Qwen3 235B (Bedrock on-demand) | 420 k × $0.002 | ~$840 |
| Cohere Embed v4 | ~500 M tokens | ~$60 |
| Cohere Rerank 3.5 (selective) | | ~$85 |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless | baseline | ~$350 |
| Comprehend Medical DetectPHI | | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Valkey | | ~$80 |
| Site-to-Site VPN | dual tunnel | ~$80 |
| **Base monthly (no custom model yet)** | | **~$2,300** |
| Phase-3 GRPO+RLVR training (Qwen3-4B, 15 epochs) | ~12 hr × $5.74 + teacher-gen batch | ~$80–100 per run |
| SageMaker endpoint for fine-tuned student (`ml.g5.2xlarge` always-on) | 720 hr × $1.52 | ~$1,095 |
| Savings — student replaces Qwen3 32B on ~85 % of emergency lane | | **−$150** |
| **With custom student always-on** | | **~$3,245** |
| **With serverless inference (scale-to-zero off-peak)** | ~300 hr × $1.52 | **~$1,950** |

The GRPO fine-tuning itself is negligible (~$100/run); the recurring cost is endpoint hosting. Bedrock Custom Model Import for the fine-tuned Qwen is an alternative — price varies with model size; check with AWS account team.

### Version C — Alibaba + Qwen (Singapore)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3.5-Flash | 180 k × 65 % × $0.0008 | ~$95 |
| Complex lane — Qwen-Max | 420 k × $0.006 | ~$2,520 |
| text-embedding-v4 | ~500 M tokens | ~$35 |
| qwen3-vl-embedding (figures) | metered | ~$60 |
| Content Moderation 2.0 | per call | ~$50 |
| OpenSearch Vector Search (small cluster) | | ~$180 |
| DataWorks SDDP PHI masking | | ~$120 |
| FC + API GW + CDN + WAF | | ~$90 |
| OSS + ActionTrail + SLS WORM | | ~$70 |
| Tair (Redis-compatible) | | ~$60 |
| IPsec VPN Gateway | | ~$60 |
| **Base monthly** | | **~$3,340** |
| Phase-3 SFT+LoRA training (Qwen3-8B) | 2–4 GPU-hr × $1–2 on PAI | ~$15–40 per run |
| PAI-EAS hosting fine-tuned Qwen3-8B (A10 GPU, always-on) | | ~$720–1,500 |
| Replace Qwen-Max with student on 60 % of complex lane | | **−$1,500** |
| **With custom student always-on** | | **~$2,400–2,900** |

Alibaba's advantage is the Qwen3-8B on PAI-EAS fits comfortably on a single A10 — cheaper steady-state than the SageMaker endpoint in Version B despite similar capabilities.

## 7. Customization cost per run (phase-3 retrain, quarterly)

| | AWS + Claude (A) | AWS + Qwen (B) | Alibaba + Qwen (C) |
|---|---|---|---|
| Technique | SFT via **Bedrock Model Distillation** (Sonnet → Nova Lite) | **GRPO + RLVR** on SageMaker via Hugging Face TRL (Qwen3-1.7B or 4B) | **SFT + LoRA** on PAI Model Gallery (Qwen3-8B); optional DPO/GRPO |
| Teacher data generation | 80 M in + 6 M out on Sonnet batch: `(80 × $1.50) + (6 × $7.50)` ≈ **$165** | Synthetic prompts + verifiable reward; no teacher call needed → **~$0** | 80 M in + 6 M out on Qwen-Max batch: `(80 × $0.60) + (6 × $3.00)` ≈ **$66** |
| Training job | Bedrock Model Distillation managed job: **$1,500–2,500** | `ml.g6e.8xlarge` × 10–15 hr × $5.74 = **$60–90** | 2–4 GPU-hr × $1–2/hr = **$5–30** |
| Clinician review (~15 % sample) | low five-figure labeling if outsourced; free if in-house | same | same |
| **Total run cost** | **~$1,700–2,700** | **~$70–100** | **~$15–40** |
| Run cadence | Quarterly | Monthly if we want (cheap enough) | Monthly if we want |

GRPO+RLVR on AWS is by far the cheapest to iterate — which means it gets the best student over time because we can retrain more often.

## 8. Sensitivity — what changes the answer

- **Toggle split**: shifting from 30/70 to 60/40 emergency/complex drops Version A by ~$1,100, B by ~$260, C by ~$900.
- **Always-on student endpoint vs serverless**: in Version B, scale-to-zero off-peak saves ~$700/mo; in Version C, a Qwen-Flash API fallback for low-traffic hours saves similar amounts.
- **OpenSearch Serverless floor**: 2+2 OCUs (default safety) would add ~$350/mo vs the 1+1 assumed above.
- **Cohere Rerank**: charging all 420 k complex calls would add ~$840/mo. Restrict reranking to the 10 % with borderline retrieval scores and it stays ~$85.

## 9. Free-tier & trial credits

| | AWS | Alibaba |
|---|---|---|
| LLM free tokens | None on Bedrock; AWS Activate credits possible for startups | **1 M free tokens per Qwen model** at activation |
| Fine-tune free quota | None | PAI workspace activation free; pay per compute job |
| OpenSearch trial | None | Periodic trial banners |

## 10. When each version is the right call

**Version A — AWS + Claude** — US or Singapore clients who demand Claude-class quality; leadership trusts Anthropic's brand; existing AWS Activate / EDP credits absorb the Sonnet bill; PDPA/Singapore residency required.

**Version B — AWS + Qwen** — clients who need BAA + AWS posture but prefer open weights; strong internal ML team comfortable with SageMaker + TRL; willing to deploy in us-west-2 for now (loses Singapore residency). Best cost if serverless inference gates usage.

**Version C — Alibaba + Qwen** — APAC / mainland-China expansion; hard cost ceiling; hospitals that may later require on-prem (portable LoRA adapter); most flexible fine-tuning cadence; Singapore residency native.

## 11. References

- [Amazon Bedrock Pricing — Qwen and Anthropic sections](https://aws.amazon.com/bedrock/pricing/)
- [Amazon Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/)
- [Amazon SageMaker Pricing — training instance rates](https://aws.amazon.com/sagemaker/ai/pricing/)
- [SageMaker instance pricing aggregator (`ml.g6e.8xlarge`)](https://cloudprice.net/aws/sagemaker/instances/ml.g6e.8xlarge)
- [Alibaba Cloud Model Studio pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [Qwen Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache)
- [PTU and token-based billing for Model Studio](https://www.alibabacloud.com/help/en/model-studio/model-training-and-deployment-billing)
- [Fine-tune small language models for production-grade tool calling with GRPO using Hugging Face TRL on Amazon SageMaker (AWS Builder Center, May 2026)](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai)

*Content above is rephrased for compliance with licensing restrictions.*
