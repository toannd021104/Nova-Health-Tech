# Cost Analysis — Three Versions (AWS+Claude / AWS+Qwen / Alibaba+Qwen)

All figures are list prices as of **early 2026**, USD, rounded. Confirm with the account team — cloud pricing moves. Main sources cited at the bottom.

## 0. Critical regional-availability caveat (updated 10 May 2026)

Verified against AWS profile `gapv50k` using `aws bedrock list-foundation-models`:

- **Qwen is NOT available in Singapore Bedrock (`ap-southeast-1`).** Nearest APAC region with Qwen is Sydney (`ap-southeast-2`).
- **Nova Micro / Lite / Pro ARE available in Singapore** via `apac.amazon.nova-*` inference profiles.
- **Claude Haiku 4.5 / Sonnet 4.5 ARE available in Singapore** via `global.anthropic.*` inference profiles.

This changes the verdict: **Version A with Nova Micro on the fast lane is the cheapest SG-native option.** See `docs/architecture/regional_availability.md` for the full verification and §1 below for the re-ranked totals.

## 1. Quick verdict (re-ranked for SG residency, updated for Qwen3.5-Plus)

| | **Version A — AWS + Claude** (Singapore) | **Version B — AWS + Qwen** (Sydney Bedrock + SageMaker SG) | **Version C — Alibaba + Qwen** (Singapore) |
|---|---|---|---|
| **Fast-lane model options** | **Nova Micro (cheapest, SG)** OR Haiku 4.5 (quality, SG) | Qwen3-32B Sydney (no SG residency) OR fine-tuned Qwen3-4B on SageMaker SG endpoint | **Qwen3.5-Flash** OR fine-tuned Qwen3-8B |
| **Complex-lane model options** | Sonnet 4.5 OR Nova Pro | Qwen3-235B Sydney | **Qwen3.5-Plus** (newer Feb-2026 release, replaces Qwen-Max) |
| **Singapore data residency** | ✅ | ⚠️ only if SageMaker endpoint hosts the model; Bedrock Qwen is Sydney | ✅ |
| **Monthly pilot total (500 physicians, base)** | **~$2,755 / mo (A1+: Nova Micro + Nova Pro)** or ~$7,095 / mo (A2: Haiku 4.5 + Sonnet 4.5) | ~$2,300 / mo (Sydney Bedrock) + ~$1,095 / mo if SG-hosted student required | **~$1,880 / mo (Qwen3.5-Flash + Qwen3.5-Plus)** |
| **Post-customization total** | ~$2,000 / mo (Nova Micro unchanged — customization may not be needed) | ~$2,000 / mo (after GRPO on SageMaker SG with serverless inference) | ~$1,940 / mo (after SFT+LoRA on PAI) |
| **Customization cost per run** | ~$2,000 (Bedrock Model Distillation, optional) | **~$70–100** (SageMaker TRL GRPO on ml.g6e.8xlarge) | **~$15–40** (PAI Model Gallery Qwen3 LoRA) |
| **Data-residency posture** | Singapore, PDPA-native | Sydney Bedrock or SG SageMaker (split) | Singapore, PDPA-native |

**Headline (re-ranked)**: Version C is now the cheapest SG-native option at ~$1,880/mo base thanks to Qwen3.5-Plus pricing. Version A1+ (Nova Micro + Nova Pro) is a close second at ~$2,755/mo and wins on "one AWS BAA covers everything." Version B loses once SG residency is required.

**About Qwen3.6-27B** (released 22 Apr 2026): coding-agent specialist. Nova should not use it — lower general-knowledge scores than Qwen3.5-Plus/Qwen3.5-397B, and it's not yet exposed as a Model Studio API endpoint. Revisit if Alibaba adds it to Model Studio with medical benchmarks.

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

### Version A — AWS Bedrock (Singapore `ap-southeast-1` via `apac.*` / `global.*` inference profiles)

Verified available in Singapore as of 10 May 2026.

| Model | Input | Output | Role |
|---|---|---|---|
| **Nova Micro** | **~$0.035** | **~$0.14** | **Cheapest fast-lane option (SG ✅)** |
| Nova Lite | ~$0.06 | ~$0.24 | Mid-tier fast-lane option (SG ✅) |
| Claude Haiku 4.5 | ~$1.00 | ~$5.00 | Fast-lane option, higher quality (SG ✅) |
| Claude Sonnet 4.5 | ~$3.00 | ~$15.00 | Complex lane + distillation teacher (SG ✅) |
| Nova Pro | ~$0.80 | ~$3.20 | Alternate complex-lane option (SG ✅) |
| Cohere Embed v4 | ~$0.12 per 1 M | — | Text embeddings (SG ✅) |
| Cohere Rerank 3.5 | $2.00 per 1,000 queries | — | Optional reranking (SG ✅) |
| Bedrock Guardrails | ~$0.15 per 1,000 text units | — | PHI + grounding (SG ✅) |

Nova Micro is roughly **30× cheaper than Haiku 4.5 on input, 35× cheaper on output**. If it clears the clinical quality rubric, it's the obvious fast-lane choice.

Batch at 50 % off. Prompt-cache read at ~10 % of standard input; cache write at a small premium.

### Version B — AWS Bedrock (Sydney `ap-southeast-2`) + SageMaker

Qwen is **not available in Singapore Bedrock**. Nearest APAC region is Sydney. Fine-tuning via Bedrock's OpenAI-compatible endpoint is `us-west-2` only; GRPO via SageMaker TRL can run in Singapore.

**Bedrock inference** (Sydney pricing from the AWS Bedrock pricing page, Qwen section):

| Model | Input | Output | Batch input | Batch output | Role |
|---|---|---|---|---|---|
| **Qwen3 32B** | **$0.1545** | **$0.6180** | $0.0773 | $0.3090 | Fast-lane base (Sydney — not SG-native) |
| **Qwen3 235B A22B (2507)** | **$0.2266** | **$0.9064** | $0.1133 | $0.4532 | Complex lane + distillation teacher (Sydney) |
| Qwen3 Coder 30B A3B | $0.1545 | $0.6180 | $0.0773 | $0.3090 | Not used here |

**SageMaker (for GRPO+RLVR fine-tuning per the AWS builder article), Singapore `ap-southeast-1`:**

| Resource | Price | Role |
|---|---|---|
| `ml.g6e.8xlarge` training job | ~$5.74/hr (L40S GPU) | GRPO+RLVR training, 10–15 hrs per run |
| `ml.g5.2xlarge` inference endpoint | ~$1.52/hr | Serve Qwen3-4B fine-tuned student (SG-native) |
| SageMaker Serverless Inference | pay per inference-ms + memory | Lower idle cost if traffic is bursty |

**SG-residency variant of Version B:** train on SageMaker SG + host student on SageMaker SG endpoint. The Bedrock-managed Qwen3 models in Sydney can only be used if the client accepts Sydney residency, or for batch training-data generation that's subsequently scrubbed.

### Version C — Alibaba Model Studio (Singapore region, per 1 M tokens)

**Updated 10 May 2026**: switch the complex lane from `Qwen-Max` to `Qwen3.5-Plus` (released Feb 2026 — newer, cheaper, better benchmarks). `Qwen-Max` retired as the default.

| Model | Input | Output | Role |
|---|---|---|---|
| **Qwen3.5-Flash** | **$0.10** (0–128K) | **$0.40** (0–128K) | **Emergency fast-lane base** (1M context, same as Qwen-Plus level quality) |
| **Qwen3.5-Plus** | **$0.40** (0–256K) | **$2.40** (0–256K) | **Complex lane + distillation teacher** (newer than Qwen-Max, ~3× cheaper input, ~2.5× cheaper output, 1M context, multimodal) |
| Qwen3-Max | $1.20 | $6.00 | Older — kept as fallback for visual-reasoning-heavy questions |
| Qwen3-8B on PAI-EAS | $1.0–$2.0/hr (A10 small GPU) | — | Fine-tuned student, serve full-time |
| text-embedding-v4 | ~$0.07 per 1 M | — | Text embeddings |
| qwen3-vl-embedding | token+image metered | — | Figure-bearing chunks |

**Qwen3.6-27B (released 22 Apr 2026) — NOT chosen for Nova.** It's a coding-specialized dense model; SWE-bench leader but **lower general-knowledge scores than Qwen3.5-27B** (MMLU-Pro 86.2 vs 86.1 similar, but knowledge tasks favor Qwen3.5-397B's 87.8). Clinical triage needs knowledge + reasoning, not code synthesis. Also not yet listed in Model Studio pricing — open weights on HuggingFace only. Re-evaluate when Alibaba publishes an API endpoint.

Batch 50 % off. Implicit context-cache hits bill at 20 % of normal input price.

## 5. Per-call cost (emergency vs complex, with all caching on)

Shows what one `/chat` request costs on each version after Layer-2 prompt caching kicks in.

### Version A (Claude / Nova)

| Step | Cost |
|---|---|
| API Gateway + Cognito | $3.5 × 10⁻⁶ |
| Comprehend Medical DetectPHI | ~$1.5 × 10⁻⁴ |
| Hybrid retrieval + Cohere embed query | ~$2 × 10⁻⁵ + OpenSearch OCU-amortized |
| **Nova Micro** (3 k in @ 50 % cache + 350 out) | **~$0.000102** |
| **Haiku 4.5** (3 k in @ 50 % cache + 350 out) | ~$0.0027 |
| **Sonnet 4.5** (3 k in @ 50 % cache + 600 out) | ~$0.012 |
| **Nova Pro** (3 k in @ 50 % cache + 600 out) | ~$0.003 |
| Guardrails | ~$3 × 10⁻⁴ |
| Audit + streaming | ~$5 × 10⁻⁶ |

**With Nova Micro**: emergency call ≈ **$0.0006**, complex call (Sonnet) ≈ $0.013.
**With Haiku 4.5**: emergency call ≈ $0.003, complex call ≈ $0.013.
**Nova Micro + Nova Pro combo**: emergency ≈ $0.0006, complex ≈ $0.0035 — the absolute cheapest SG-native Bedrock combo.

### Version B (AWS Qwen, Sydney Bedrock on-demand)

| Step | Cost |
|---|---|
| Same infra as A | ~$5 × 10⁻⁴ combined |
| **Qwen3 32B** (3 k in + 350 out) | `(3 × $0.1545 / 1,000) + (0.35 × $0.6180 / 1,000)` = **$6.8 × 10⁻⁴** |
| **Qwen3 235B** (3 k in + 600 out) | `(3 × $0.2266 / 1,000) + (0.6 × $0.9064 / 1,000)` = **$1.2 × 10⁻³** |
| Guardrails + audit | ~$3 × 10⁻⁴ |

**Emergency call ≈ $0.0015 · Complex call ≈ $0.002** (plus $1,095/mo amortized SageMaker SG endpoint if we need SG residency, see row below).

### Version C (Alibaba Qwen — Qwen3.5-Plus for complex, Qwen3.5-Flash for fast)

| Step | Cost |
|---|---|
| Same infra as A/B, FC/API GW/etc | ~$4 × 10⁻⁴ combined |
| **Qwen3.5-Flash** (3 k in + 350 out, cache 50 % off) | `(3 × $0.10/1 M × 0.5) + (0.35 × $0.40 / 1 M)` ≈ **$3.5 × 10⁻⁴** |
| **Qwen3.5-Plus** (3 k in + 600 out, cache 50 % off) | `(3 × $0.40/1 M × 0.5) + (0.6 × $2.40/1 M)` ≈ **$2.0 × 10⁻³** |
| Content Moderation + audit | ~$2 × 10⁻⁴ |

**Emergency call ≈ $0.0008 · Complex call ≈ $0.0026** (Qwen3.5-Plus roughly 2.5× cheaper per complex call than the earlier Qwen-Max choice at $0.006)

## 6. Monthly pilot cost (600 k calls, 30/70 emergency/complex)

### Version A — AWS + Claude / Nova (Singapore) — TWO sub-variants

#### A1 — Nova Micro (fast) + Sonnet 4.5 (complex) · cheapest SG-native

| Item | Calc | Cost |
|---|---|---|
| Fast lane — **Nova Micro** | 180 k × 65 % (post-sem-cache) × $0.0006 | ~$70 |
| Complex lane — Sonnet 4.5 | 420 k × $0.013 | ~$5,460 |
| Cohere Embed v4 | ~500 M tokens amortized | ~$60 |
| Cohere Rerank 3.5 (selective) | 10 % of complex calls | ~$85 |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless | 1+1 OCU × 720 hr × $0.24 | ~$350 |
| Comprehend Medical | per 100-char unit | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Valkey (2 AZ cache.t4g.small) | | ~$80 |
| Site-to-Site VPN | dual tunnel | ~$80 |
| **A1 subtotal** | | **~$6,815** |

#### A1+ — Nova Micro (fast) + **Nova Pro** (complex) · all-Nova, SG-native

| Item | Cost vs A1 |
|---|---|
| Complex lane — Nova Pro instead of Sonnet 4.5 (420 k × $0.0035) | ~$1,470 (vs Sonnet's $5,460) |
| Everything else same as A1 | ~$1,285 |
| **A1+ subtotal** | **~$2,755** |

Nova Pro can't match Sonnet 4.5 on complex clinical reasoning depth, but if it clears the benchmark it's the cheapest SG-native option in the entire comparison. **This becomes the new baseline to beat.**

#### A2 — Haiku 4.5 (fast) + Sonnet 4.5 (complex) · currently-deployed variant

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Haiku 4.5 | 180 k × 65 % × $0.003 | ~$350 |
| Complex lane — Sonnet 4.5 | 420 k × $0.013 | ~$5,460 |
| All other items same as A1 | | ~$1,285 |
| **A2 subtotal** | | **~$7,095** |
| Phase-3 distillation (Sonnet → Nova Lite) amortized | $2,000 / 3 | ~$670 |
| Post-distill Nova Lite replaces Sonnet on ~40 % of complex traffic | savings | −$2,200 |
| **A2 post-customization** | | **~$5,565** |

### Version B — AWS + Qwen (Sydney Bedrock + optional SageMaker SG)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3 32B (Bedrock Sydney on-demand) | 180 k × 65 % × $0.0015 | ~$175 |
| Complex lane — Qwen3 235B (Bedrock Sydney on-demand) | 420 k × $0.002 | ~$840 |
| Cohere Embed v4 | ~500 M tokens | ~$60 |
| Cohere Rerank 3.5 (selective) | | ~$85 |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless | baseline | ~$350 |
| Comprehend Medical DetectPHI | | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Valkey | | ~$80 |
| Site-to-Site VPN | dual tunnel | ~$80 |
| **B base (accepting Sydney residency)** | | **~$2,300** |
| Phase-3 GRPO+RLVR training (Qwen3-4B, 15 epochs) | ~12 hr × $5.74 + teacher-gen batch | ~$80–100 per run |
| SageMaker SG endpoint for fine-tuned student (`ml.g5.2xlarge` always-on) | 720 hr × $1.52 | ~$1,095 |
| Savings — student replaces Qwen3 32B on ~85 % of emergency lane | | **−$150** |
| **B with custom student always-on (SG-residency variant)** | | **~$3,245** |
| **B with serverless inference (scale-to-zero off-peak)** | ~300 hr × $1.52 | **~$1,950** |

Important: "B base" at $2,300 only applies if the client accepts **Sydney** residency for Qwen calls. Strictly-SG clients are on the $3,245 variant (SageMaker SG endpoint) unless we serve the fast lane from Nova Micro as a hybrid — which defeats the purpose of Version B.

### Version C — Alibaba + Qwen (Singapore)

Post-Qwen3.5 update: complex lane now uses **Qwen3.5-Plus** (Feb 2026 release) instead of Qwen-Max. 3× cheaper input / 2.5× cheaper output for equivalent or better benchmarks.

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3.5-Flash | 180 k × 65 % × $0.0004 (3k in + 350 out @ tier 1) | ~$47 |
| Complex lane — **Qwen3.5-Plus** (vs Qwen-Max) | 420 k × $0.0026 (3k in + 600 out @ tier 1) | **~$1,105** (was $2,520 on Qwen-Max) |
| text-embedding-v4 | ~500 M tokens | ~$35 |
| qwen3-vl-embedding (figures) | metered | ~$60 |
| Content Moderation 2.0 | per call | ~$50 |
| OpenSearch Vector Search (small cluster) | | ~$180 |
| DataWorks SDDP PHI masking | | ~$120 |
| FC + API GW + CDN + WAF | | ~$90 |
| OSS + ActionTrail + SLS WORM | | ~$70 |
| Tair (Redis-compatible) | | ~$60 |
| IPsec VPN Gateway | | ~$60 |
| **Base monthly (Qwen3.5-Plus)** | | **~$1,880** |
| Phase-3 SFT+LoRA training (Qwen3-8B) | 2–4 GPU-hr × $1–2 on PAI | ~$15–40 per run |
| PAI-EAS hosting fine-tuned Qwen3-8B (A10 GPU, always-on) | | ~$720–1,500 |
| Replace Qwen3.5-Plus with student on 60 % of complex lane | | **−$660** |
| **With custom student always-on** | | **~$1,940–2,720** |

Alibaba's advantage is now even stronger: Qwen3-8B on PAI-EAS fits on a single A10 **and** Qwen3.5-Plus complex-lane pricing is cheaper than the Bedrock Qwen3-235B in Sydney.

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

**Version A1+ — AWS + Nova Micro + Nova Pro (Singapore)** — cost-sensitive, PDPA-required clients. Pending clinical-quality benchmark. Simplest compliance story (all one AWS BAA, all in SG).

**Version A2 — AWS + Haiku 4.5 + Sonnet 4.5 (Singapore)** — current default. Clinical leadership trusts Anthropic; Nova Micro hasn't yet proven sufficient for emergency-care quality.

**Version B — AWS + Qwen** — hospital needs open weights under AWS BAA; willing to accept Sydney residency, or willing to run SageMaker SG endpoints at ~$1k/mo floor. GRPO+RLVR recipe is compelling for fast retrain cadence.

**Version C — Alibaba + Qwen** — APAC / mainland-China expansion; hard cost ceiling; hospitals that may later require on-prem; most flexible fine-tuning toolbox; Singapore residency native.

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
