# Cost Analysis — Three Versions (AWS+Claude / AWS+Qwen / Alibaba+Qwen)

All figures are list prices as of **early 2026**, USD, rounded. Confirm with the account team — cloud pricing moves. Main sources cited at the bottom.

## 0. Critical regional-availability caveat (updated 10 May 2026)

Verified against AWS profile `gapv50k` using `aws bedrock list-foundation-models`:

- **Qwen is NOT available in Singapore Bedrock (`ap-southeast-1`).** Nearest APAC region with Qwen is Sydney (`ap-southeast-2`).
- **Nova Micro / Lite / Pro ARE available in Singapore** via `apac.amazon.nova-*` inference profiles.
- **Claude Haiku 4.5 / Sonnet 4.5 ARE available in Singapore** via `global.anthropic.*` inference profiles.

This changes the verdict: **Version A with Nova Micro on the fast lane is the cheapest SG-native option.** See `docs/architecture/regional_availability.md` for the full verification and §1 below for the re-ranked totals.

## 1. Quick verdict (re-ranked for SG residency, updated for Qwen3.5-Plus + Bedrock Qwen3 Next)

| | **Version A — AWS + Claude** (Singapore) | **Version B — AWS + Qwen** (Sydney Bedrock) | **Version C — Alibaba + Qwen** (Singapore) |
|---|---|---|---|
| **Fast-lane model options** | **Nova Micro (cheapest, SG)** OR Haiku 4.5 (quality, SG) | **Qwen3 Next 80B A3B** (Sydney; MoE, 3B active) OR Qwen3 32B dense OR custom RFT'd Qwen3-32B | **Qwen3.5-Flash** OR fine-tuned Qwen3-8B |
| **Complex-lane model options** | Sonnet 4.5 OR Nova Pro | **Qwen3 VL 235B A22B** (Sydney; with vision) OR Qwen3 235B A22B 2507 (text-only, cheaper) | **Qwen3.5-Plus** (newer Feb-2026 release, replaces Qwen-Max) |
| **Customization** | Bedrock Model Distillation (Sonnet → Nova Lite, ~$2k/run) | **Bedrock Reinforcement Fine-Tuning on Qwen3 32B** (us-west-2, $80/hr ≈ $640/run) OR SageMaker GRPO on Qwen3-4B (~$100/run) | PAI SFT+LoRA on Qwen3-8B (~$15–40/run) |
| **Singapore data residency** | ✅ | ⚠️ Bedrock Qwen is Sydney; PDPA contract-mitigable | ✅ |
| **Monthly pilot total (500 physicians, base)** | **~$2,755 / mo (A1+: Nova Micro + Nova Pro)** or ~$7,095 / mo (A2: Haiku 4.5 + Sonnet 4.5) | **~$2,767 / mo** (Bedrock-only, no SageMaker) | **~$1,920 / mo (Qwen3.5-Flash + Qwen3.5-Plus, SG-native embed/rerank)** |
| **Post-customization total** | ~$5,570 / mo (A2 after Nova Lite distillation) | **~$3,040 / mo** (after Bedrock RFT on Qwen3 32B) | ~$1,980 / mo (after SFT+LoRA on PAI) |
| **Data-residency posture** | Singapore, PDPA-native | Sydney Bedrock (PDPA-mitigable); SG only if SageMaker path | Singapore, PDPA-native |

**Headline (re-ranked)**:
1. **Version C (~$1,920/mo)** — cheapest SG-native, Qwen3.5-Plus replaced Qwen-Max for 3× savings on complex lane. Embeddings use `text-embedding-v4` + `tongyi-embedding-vision-plus` (SG International); reranker is `qwen3-rerank`.
2. **Version A1+ (~$2,755/mo)** — cheapest fully AWS-BAA-covered SG-native, pending Nova Micro/Pro clinical quality benchmark.
3. **Version B (~$2,767/mo)** — pure Bedrock, no SageMaker required. Qwen3 Next 80B A3B + Qwen3 VL 235B. Sydney residency.
4. **Version A2 (~$7,095/mo)** — running demo today (Haiku 4.5 + Sonnet 4.5). Quality-first baseline.

**About Qwen3.6-27B** (released 22 Apr 2026): coding-agent specialist. Nova should not use it — lower general-knowledge scores than Qwen3.5-Plus/Qwen3.5-397B, not on Model Studio API, not on Bedrock. Re-evaluate when it gets hosted with medical benchmarks.

## 2. Assumptions shared across all three versions

- 500 physicians × 40 queries/day = 20 k/day → **~600 k queries/month**.
- Average request: **3,000 input + 350 output tokens** (RAG context included).
- Traffic split set by the clinician's **emergency toggle**, not a classifier. Observed: **30 % emergency / 70 % complex**.
- Semantic-cache (Layer 1) hit rate 35 % on emergency queries.
- Prompt / context-cache (Layer 2) hit rate 70 % on non-cached calls → effective 50 % off on input tokens.
- Vector store ~20 GB indexed.
- Site-to-Site VPN up for corporate integration (dual tunnel).
- Nothing below is "phase 2" or "phase 3" — everything is live at launch. Customization costs are amortized per retrain cadence (monthly DPO, quarterly SFT). Optional toggles (multi-agent specialist, LazyGraphRAG, PubMed tool) add usage to the numbers below; see line items.

## 3. Three cost levers available on all three clouds

| Lever | AWS Bedrock — Version A (Claude/Nova) | AWS Bedrock — Version B (Qwen, Sydney) | Alibaba Model Studio (C) | Savings |
|---|---|---|---|---|
| **Prefix / prompt caching** on static prefix | ✅ Bedrock Prompt Caching (`<cachePoint/>`) — Claude 4.x + Nova | ❌ Not supported for Qwen3 on Bedrock (verified May 2026). Self-hosted path uses vLLM APC / SGLang RadixAttention instead. | ✅ Qwen Context Cache (implicit from day 1 + explicit) | Up to 90% off on cached input tokens |
| **Batch inference** for offline jobs | Bedrock Batch, Flex tier | Bedrock Batch, Flex tier | Model Studio Batch | 50% off tokens |
| **Reserved capacity** for peak | Bedrock Reserved Tier | Bedrock Reserved Tier | Qwen PTU | Flat rate; no queueing |

Our chosen defaults: on-demand + prefix caching (where supported) for realtime traffic; batch for the teacher-data generation; reserved tier only if the fast lane goes steady-state TPM. See `docs/architecture/caching_strategy.md` for the full Layer 1 / Layer 2 / Layer 3 breakdown and the LangChain-vs-inference-engine split.

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

### Version B — AWS Bedrock (Sydney `ap-southeast-2`) — all Qwen served via Bedrock

Qwen is **not in Singapore Bedrock**; nearest APAC region is Sydney. Bedrock hosts four Qwen3 models managed-serverless, so Version B needs no SageMaker for its base inference. SageMaker is an optional path only when data residency forces an SG-hosted custom student.

**Bedrock inference (Sydney pricing from the AWS Bedrock pricing page, verified 10 May 2026):**

| Model | Input | Output | Batch input | Batch output | Role |
|---|---|---|---|---|---|
| **Qwen3 Next 80B A3B** | **$0.1545** | **$1.2360** | $0.0773 | $0.6180 | **Fast lane** — MoE, 3B active per token, fastest Qwen on Bedrock |
| Qwen3 32B dense | $0.1545 | $0.6180 | $0.0773 | $0.3090 | Alternative fast lane; cheaper output but dense |
| **Qwen3 VL 235B A22B** | **$0.5459** | **$2.7398** | $0.2730 | $1.3699 | **Complex lane + distillation teacher** — with vision, 22B active |
| Qwen3 235B A22B 2507 | $0.2266 | $0.9064 | $0.1133 | $0.4532 | Alternative complex lane (text-only, cheaper) |
| Qwen3 Coder Next | $0.5150 | $1.2360 | — | — | Not used (coding specialist) |

**Bedrock Reinforcement Fine-Tuning (us-west-2 only, for Qwen3 32B):**

| Item | Price | Role |
|---|---|---|
| Training hours | **$80/hr** | Fine-tune a clinical-domain student |
| Post-training inference input | $0.20 per 1M tokens | Custom model invocation |
| Post-training inference output | $0.78 per 1M tokens | Custom model invocation |
| Trained-model storage | $1.95 / month | Per model |

**SageMaker (optional alternative path for Qwen3-1.7B/4B GRPO per the AWS builder article):**

| Resource | Price | Role |
|---|---|---|
| `ml.g6e.8xlarge` training job (L40S GPU) | ~$5.74/hr | GRPO+RLVR on smaller Qwen; 10–15 hr per run |
| `ml.g5.2xlarge` SageMaker endpoint in SG | ~$1.52/hr | Serve the student in-region (PDPA-native) |
| SageMaker Serverless Inference | per inference-ms | Scale-to-zero off-peak |

Choose SageMaker only when (a) the student must physically live in Singapore for PDPA, or (b) a sub-4B model is needed for tightest latency.

### Version C — Alibaba Model Studio (Singapore region, per 1 M tokens)

**Updated 10 May 2026**: switch the complex lane from `Qwen-Max` to `Qwen3.5-Plus` (released Feb 2026 — newer, cheaper, better benchmarks). `Qwen-Max` retired as the default.

| Model | Input | Output | Role |
|---|---|---|---|
| **Qwen3.5-Flash** | **$0.10** (0–128K) | **$0.40** (0–128K) | **Emergency fast-lane base** (1M context, same as Qwen-Plus level quality) |
| **Qwen3.5-Plus** | **$0.40** (0–256K) | **$2.40** (0–256K) | **Complex lane + distillation teacher** (newer than Qwen-Max, ~3× cheaper input, ~2.5× cheaper output, 1M context, multimodal) |
| Qwen3-Max | $1.20 | $6.00 | Older — kept as fallback for visual-reasoning-heavy questions |
| Qwen3-8B on PAI-EAS | $1.0–$2.0/hr (A10 small GPU) | — | Fine-tuned student, serve full-time |
| text-embedding-v4 | $0.07 per 1M | — | Text embeddings (Qwen3-Embedding series; dims 64–2048; 8192-token context) |
| tongyi-embedding-vision-plus | $0.09 per 1M text · metered per image/video | — | Multimodal embeddings for figure-bearing chunks (SG International; 1152-dim). `qwen3-vl-embedding` is **Chinese Mainland only**, not SG. |
| qwen3-rerank | $0.10 per 1M | — | Reranker (500-doc cap). `qwen3-vl-rerank` and `gte-rerank-v2` are not on SG International. |

**Qwen3.6-27B (released 22 Apr 2026) — NOT chosen for Nova.** It's a coding-specialized dense model; SWE-bench leader but **lower general-knowledge scores than Qwen3.5-27B** (MMLU-Pro 86.2 vs 86.1 similar, but knowledge tasks favor Qwen3.5-397B's 87.8). Clinical triage needs knowledge + reasoning, not code synthesis. Also not yet listed in Model Studio pricing — open weights on HuggingFace only. Re-evaluate when Alibaba publishes an API endpoint.

Batch 50 % off. Implicit context-cache hits bill at 20 % of normal input price.

## 5. Per-call cost (emergency vs complex, with all caching on)

Shows what one `/chat` request costs on each version after Layer-1 semantic cache miss + Layer-2 prefix cache where available (Version A on Bedrock Prompt Caching; Version C on Qwen Context Cache implicit). Version B on Bedrock has no Layer-2; the "50% cache" assumption below for B represents partial reuse via batched RAG context reordering, not Bedrock prompt caching — it would only apply literally if Ver B pivots to a self-hosted vLLM/SGLang endpoint (see `docs/architecture/caching_strategy.md`).

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
| **Qwen3 Next 80B A3B** (3 k in + 350 out) | `(3 × $0.1545 / 1,000) + (0.35 × $1.2360 / 1,000)` = **$8.9 × 10⁻⁴** |
| **Qwen3 VL 235B A22B** (3 k in + 600 out) | `(3 × $0.5459 / 1,000) + (0.6 × $2.7398 / 1,000)` = **$3.3 × 10⁻³** |
| Qwen3 235B A22B 2507 text-only (3 k + 600) | `(3 × $0.2266 / 1,000) + (0.6 × $0.9064 / 1,000)` = **$1.2 × 10⁻³** |
| Custom RFT Qwen3-32B (3 k + 350) | `(3 × $0.20 / 1,000) + (0.35 × $0.78 / 1,000)` = **$8.7 × 10⁻⁴** |
| Guardrails + audit | ~$3 × 10⁻⁴ |

**Emergency call ≈ $0.0009 · Complex call (VL) ≈ $0.0033, (text) ≈ $0.0012**

If we split the complex lane so that only figure-bearing retrieval hits Qwen3-VL and the rest goes to Qwen3 235B text-only, complex-call cost drops to ~$0.0015.

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
| Distillation (Sonnet → Nova Lite) amortized, trained once pre-launch + re-qualified quarterly | $2,000 per run / 3 months | ~$670 |
| Post-distill Nova Lite replaces Sonnet on ~40 % of complex traffic | savings | −$2,200 |
| **A2 with trained Nova Lite student (baseline at launch)** | | **~$5,565** |

### Version B — AWS + Qwen (Sydney Bedrock only, no SageMaker)

Bedrock hosts four Qwen3 models in Sydney, so Version B is fully Bedrock-hosted for base inference. SageMaker is only needed if a client requires the custom student physically in Singapore.

| Item | Calc | Cost |
|---|---|---|
| Fast lane — **Qwen3 Next 80B A3B** (Bedrock Sydney) | 180 k × 65 % × $0.0009 | ~$105 |
| Complex lane — **Qwen3 VL 235B A22B** (Bedrock Sydney) | 420 k × $0.0033 | ~$1,377 |
| Cohere Embed v4 | ~500 M tokens | ~$60 |
| Cohere Rerank 3.5 (selective) | | ~$85 |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless | baseline | ~$350 |
| Comprehend Medical DetectPHI | | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Valkey | | ~$80 |
| Site-to-Site VPN | dual tunnel | ~$80 |
| **B base (Bedrock-only, no custom model — same-API fallback)** | | **~$2,767** |
| Bedrock RFT training (Qwen3-32B, ~8 hr × $80/hr), trained pre-launch, amortized quarterly | ~$640 per run | +~$215 |
| Fast lane switches to custom Qwen3-32B (us-west-2) with cheaper output | | ~neutral or saves ~$20 |
| Model storage | | +~$2 |
| **B at launch with trained Qwen3-32B custom model (path B-1)** | | **~$2,985–$3,040** |

**Splitting the complex lane:** Most RAG retrievals don't involve figures. If we route only figure-bearing queries to Qwen3 VL and the rest to Qwen3 235B A22B 2507 (text-only at $0.2266/$0.9064), the complex lane cost drops:

| Split variant | Complex-lane cost |
|---|---|
| 100 % Qwen3 VL 235B | ~$1,377 |
| 80 % text-only / 20 % VL | ~$400 (text) + ~$275 (VL) = **~$675** |

**Using the split, B base drops to ~$2,065/mo — below Version C base.**

### Optional SG-residency variant (path B-2, SageMaker)

Same launch-day custom student, but hosted in Singapore on SageMaker:

| Item | Cost |
|---|---|
| GRPO training on `ml.g6e.8xlarge` (quarterly retrain ~$100) | amortized +$35 |
| SageMaker SG endpoint `ml.g5.2xlarge` always-on (`720 hr × $1.52`) | +$1,095 |
| Savings on fast lane (replaces Bedrock Qwen3 Next calls) | −$95 |
| **B path B-2 total** | **~$3,800** |

Use path B-2 only when the client mandates SG residency for the student model.

### Version C — Alibaba + Qwen (Singapore)

Post-Qwen3.5 update: complex lane now uses **Qwen3.5-Plus** (Feb 2026 release) instead of Qwen-Max. 3× cheaper input / 2.5× cheaper output for equivalent or better benchmarks.

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3.5-Flash | 180 k × 65 % × $0.0004 (3k in + 350 out @ tier 1) | ~$47 |
| Complex lane — **Qwen3.5-Plus** (vs Qwen-Max) | 420 k × $0.0026 (3k in + 600 out @ tier 1) | **~$1,105** (was $2,520 on Qwen-Max) |
| text-embedding-v4 | ~500 M tokens × $0.07 / 1M | ~$35 |
| tongyi-embedding-vision-plus (figure-bearing chunks) | ~5 M text tokens × $0.09 + ~50 k image inputs metered | ~$50 |
| qwen3-rerank (top-20 set, 10% of complex calls) | ~500 M tokens amortized | ~$50 |
| Content Moderation 2.0 | per call | ~$50 |
| OpenSearch Vector Search (small cluster) | | ~$180 |
| DataWorks SDDP PHI masking | | ~$120 |
| FC + API GW + CDN + WAF | | ~$90 |
| OSS + ActionTrail + SLS WORM | | ~$70 |
| Tair (Redis-compatible) | | ~$60 |
| IPsec VPN Gateway | | ~$60 |
| **Base monthly (Qwen3.5-Plus, no student)** | | **~$1,920** |
| SFT+LoRA training run (Qwen3-8B), trained once pre-launch + quarterly retrain | 2–4 GPU-hr × $1–2 on PAI | ~$15–40 per run |
| PAI-EAS hosting fine-tuned Qwen3-8B (A10 GPU, always-on) | | ~$720–1,500 |
| Student replaces Qwen3.5-Plus on ~60 % of complex-lane traffic | | **−$660** |
| **C at launch with Qwen3-8B student active** | | **~$1,980–2,760** |

Alibaba's advantage is now even stronger: Qwen3-8B on PAI-EAS fits on a single A10 **and** Qwen3.5-Plus complex-lane pricing is cheaper than the Bedrock Qwen3-235B in Sydney.

## 7. Customization cost per run (pre-launch training + post-launch retrain cadence)

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
