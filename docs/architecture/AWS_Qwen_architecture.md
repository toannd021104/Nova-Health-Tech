# AWS with Qwen — Architecture (Version B, simplified)

All-Qwen on AWS Bedrock. Customization story is pragmatic: use Bedrock's native Qwen family for serving today, use Bedrock's **reinforcement fine-tuning** for Qwen3 32B when we want a custom student, and keep the SageMaker + TRL GRPO path from the AWS builder article as an optional alternative for sub-8B Qwen experiments.

## 1. Major simplification vs the earlier draft

Earlier drafts of Version B pushed SageMaker + Hugging Face TRL as the primary path. That was overbuilt. Bedrock now hosts four Qwen3 models managed-serverless in APAC/US/EU regions, and Bedrock's **reinforcement fine-tuning** endpoint supports Qwen3 32B directly. Keep SageMaker as a side-option; Bedrock alone covers the main deployment and most customization needs.

## 2. Available Qwen models on Bedrock (verified 10 May 2026)

`aws bedrock list-foundation-models` + live smoke test across regions confirmed:

| Model | Total / Active params | Input $/1M (Sydney) | Output $/1M (Sydney) | Role in this design |
|---|---|---|---|---|
| **Qwen3 Next 80B A3B** | 80B / **3B active (MoE)** | **$0.1545** | **$1.2360** | **Emergency fast lane** — fastest Qwen on Bedrock thanks to MoE routing |
| Qwen3 32B dense | 32B dense | $0.1545 | $0.6180 | Alternative fast lane; cheaper output but dense → slower per token |
| **Qwen3 VL 235B A22B** | 235B / 22B active | **$0.5459** | **$2.7398** | **Complex lane + distillation teacher** — includes vision for figure-heavy PDFs |
| Qwen3 235B A22B 2507 | 235B / 22B active | $0.2266 | $0.9064 | Text-only alternative complex lane, cheaper |
| Qwen3 Coder Next | n/a | $0.5150 | $1.2360 | Not used (coding specialist) |

Batch inference: 50% off. Flex tier: 50% off. Priority tier: 75% premium.

### Regional availability

| Region | Qwen3 Next 80B | Qwen3 VL 235B | Qwen3 32B | Price vs Sydney |
|---|---|---|---|---|
| **Sydney (`ap-southeast-2`)** | ✅ | ✅ | ✅ | baseline |
| Singapore (`ap-southeast-1`) | ❌ | ❌ | ❌ | — |
| Tokyo (`ap-northeast-1`) | ✅ ($0.18/$1.45) | ✅ ($0.64/$3.22) | ✅ | higher |
| Mumbai (`ap-south-1`) | ✅ ($0.18/$1.41) | ✅ ($0.62/$3.13) | ✅ | similar |
| us-west-2 / us-east-1 | ✅ ($0.15/$1.20) | ✅ ($0.53/$2.66) | ✅ | cheapest; + fine-tuning endpoint |

**Sydney is the closest APAC Qwen region to Singapore hospitals.** Singapore Bedrock has no Qwen.

## 3. Customization paths

### Path B-1 — Bedrock Reinforcement Fine-Tuning on Qwen3 32B (us-west-2)

Bedrock's native RFT endpoint for Qwen3 32B. From the AWS Bedrock pricing page:

| Item | Price |
|---|---|
| Training hours | **$80 / hr** |
| Post-training inference input | $0.20 / 1M tokens |
| Post-training inference output | $0.78 / 1M tokens |
| Trained-model storage | $1.95 / month |

- Fully managed — you provide prompts + reward function, Bedrock generates responses, scores them, trains the model, exposes the fine-tuned ID via the OpenAI-compatible endpoint.
- Much less moving-parts than SageMaker + TRL.
- Region pin: `us-west-2` only for the training job, but the resulting custom model can be invoked from the mantle endpoint.
- Typical run: 6–12 hours for 10–20k-prompt dataset → **~$500–$1,000 per retrain**.

### Path B-2 — SageMaker + Hugging Face TRL GRPO on Qwen3-1.7B / 4B (from AWS builder article)

Kept as an optional path when you want a smaller, self-served student:

- `ml.g6e.8xlarge` training at ~$5.74/hr × 10–15 hr ≈ **$70–$100 per run**.
- Serve on SageMaker endpoint (e.g. `ml.g5.2xlarge` ~$1.52/hr) **in Singapore** if SG residency for the student is required.
- Choose when (a) you want weights you can eventually pull off AWS, or (b) you want a sub-4B model for the tightest latency.

### When to use which

| Choose... | ...if |
|---|---|
| **No fine-tuning** (Qwen3 Next 80B A3B fast + Qwen3 VL 235B complex) | Launch without customization when RAG + prompt engineering + caching alone clear the clinical-quality rubric. Keeps operational surface small. |
| **Path B-1 (Bedrock RFT on Qwen3 32B)** | You want a clinical-domain-tuned model without managing GPU infrastructure, and are willing to serve from us-west-2. Training runs before cut-over; the custom model ID replaces the base Qwen in the router config on launch day. |
| **Path B-2 (SageMaker GRPO on Qwen3-4B)** | You need the student physically in Singapore for data residency, or want the cheaper quarterly retrain cadence. Same: training runs before launch, endpoint is hot on day one. |

## 4. Component diagram

```
 Clinician browser
      │ HTTPS + Cognito OIDC
      ▼
 CloudFront + WAF + API Gateway
      │
      ▼
 Lambda /chat (VPC)
      ├─ PHI mask (Comprehend Medical)
      ├─ Layer-1 semantic cache (ElastiCache Valkey)
      ├─ LangGraph: retrieve → if/else route
      │
      ├────── retrieval ──────► Bedrock Knowledge Bases on OpenSearch Serverless
      │                          (Cohere Embed v4, hybrid BM25+kNN)
      │
      ├─── emergency=true ────► Bedrock (bedrock-mantle, Sydney)
      │                          qwen.qwen3-next-80b-a3b  (3B active, ~200 tok/s)
      │                          OR custom RFT'd Qwen3-32B from us-west-2
      │
      └─── emergency=false ───► Bedrock (bedrock-mantle, Sydney)
                                  qwen.qwen3-vl-235b-a22b  (vision for figures)
      │
      ▼
 Guardrails (Bedrock Guardrails + citation validator)
      │
      ▼
 Stream response back to client

Ingestion (unchanged from Version A):
 S3 raw → EventBridge → Step Functions → BDA parse → chunk → embed (Cohere v4) → KB sync

Optional customization (quarterly):
 Path B-1: Bedrock RFT endpoint (us-west-2) on Qwen3 32B with grader Lambda
 Path B-2: SageMaker training job (`ml.g6e.8xlarge`) on Qwen3-4B with TRL GRPO
```

## 5. Regulatory caveat (unchanged)

- Bedrock Qwen inference **is not in Singapore today**. Sydney is the nearest APAC region. PDPA transfer-limitation obligation applies → cross-border transfer from SG hospital to Sydney AWS region needs comparable-protection assurance (typically contract clause).
- For PDPA-strict clients: route Version B through the **Bedrock Sydney endpoint**, keep S3 raw storage + OpenSearch Serverless in Singapore, and only ephemeral prompt+response tokens cross the Sydney boundary. The permanent patient data never leaves SG.
- For fine-tuning: Path B-1 requires us-west-2 (US residency). Path B-2 can stay fully in Singapore via SageMaker SG.

## 6. Latency budget (emergency lane)

With **Qwen3 Next 80B A3B** on Bedrock Sydney:

```
  25 ms   ElastiCache semantic cache hit (skip to step 7 if hit)
 100 ms   Cognito auth + PHI mask (Lambda in SG)
  70 ms   Retrieval (OpenSearch Serverless SG)
  90 ms   cross-region call SG → Sydney (Bedrock)
 500 ms   Qwen3 Next first-token (MoE; no prompt cache — full prefix processed each call)
1100 ms   Full answer (250 tokens @ ~250 tok/s via MoE)
 110 ms   Guardrails + citation validation
───────
≤ 1,995 ms  p95 emergency budget

Note: Bedrock Prompt Caching does NOT support Qwen3 models (verified May 2026). The first-token time above assumes no Layer 2 cache. Ver A (Claude) saves ~300–400 ms on TTFT via prompt caching; Ver B cannot replicate this without a future AWS update adding Qwen3 to the supported-models list.
```

The SG→Sydney RTT (~90 ms each way) is the cross-region tax. If we later pick a custom SageMaker endpoint hosted in Singapore, we save the ~180 ms round-trip.

## 7. Monthly cost (600 k calls, 30/70 split, caching on) — updated

| Item | Calc | Cost |
|---|---|---|
| Fast lane — **Qwen3 Next 80B A3B** (Bedrock Sydney) | 180 k × 65 % × (3k in + 350 out) × $0.1545/$1.236 per 1M | ~$105 |
| Complex lane — **Qwen3 VL 235B A22B** (Bedrock Sydney) | 420 k × (3k in + 600 out) × $0.5459/$2.7398 per 1M | ~$1,377 |
| Cohere Embed v4 | ~500 M tokens | ~$60 |
| Cohere Rerank 3.5 (selective) | | ~$85 |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless | baseline | ~$350 |
| Comprehend Medical DetectPHI | | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Valkey | | ~$80 |
| Site-to-Site VPN | dual tunnel | ~$80 |
| **B base — Bedrock-only, no fine-tuning** | | **~$2,767** |

### With customization path B-1 (Bedrock RFT on Qwen3 32B for fast lane)

| Item | Delta |
|---|---|
| RFT training run, amortized (quarterly ~$800) | +$270 |
| Fast lane switches to custom Qwen3 32B (us-west-2): 117k calls × (3k in + 350 out) × $0.20/$0.78 | +$100 (replaces $105) |
| Model storage | +$2 |
| **B total with custom fast-lane model** | **~$3,040** |

Note: the custom model has **cheaper inference than the base Qwen3 Next 80B A3B on output ($0.78 vs $1.24 per 1M)** — so at steady state, switching to the tuned Qwen3-32B actually **saves money** on output-heavy traffic. The payoff depends on traffic volume × answer length.

### With customization path B-2 (SageMaker GRPO on Qwen3-4B, SG endpoint)

| Item | Delta |
|---|---|
| GRPO training run, amortized (quarterly ~$100) | +$35 |
| SageMaker endpoint `ml.g5.2xlarge` 24×7 (serverless option cheaper) | +$1,095 always-on |
| Fast lane replaced by SageMaker endpoint | savings ~$95 |
| **B total with SG-hosted custom student** | **~$3,802** |

Keep Path B-2 for clients who need the emergency-lane model **physically in SG**. Otherwise Path B-1 is cheaper and simpler.

## 8. Why this is attractive now vs. before

- **Bedrock serves both lanes with no self-hosted GPU** — managed `qwen.qwen3-next-80b-a3b` for the fast lane and `qwen.qwen3-vl-235b-a22b` for the complex lane. Pay-per-token, no always-on GPU unless we pick Path B-2.
- **The MoE models are genuinely fast** — Qwen3 Next 80B activates only 3B per token, similar efficiency profile to Qwen3.5-Flash on Model Studio.
- **One IAM, one BAA, one service** — everything under Bedrock. No dual SageMaker-plus-Bedrock ops complexity unless we opt in for Path B-2.
- **Fine-tuning is cheap** — Bedrock RFT $80/hr × ~8 hr = $640 per run, vs the $2,000 custom-model distillation for Claude-family.
- **Built-in vision** — Qwen3 VL 235B handles figures/tables in the WHO PDFs without a separate multimodal embedding pass.

## 9. What makes it less attractive

- **Sydney residency**, not Singapore, for Bedrock inference. Contract-mitigable for PDPA but not ideal.
- **Bedrock RFT** pins the fine-tuning to us-west-2 (one-time US residency for training data).
- **Vision-Language pricing is higher than text-only** — if we don't need figure understanding on every call, split the complex lane to Qwen3 235B A22B 2507 text-only ($0.2266 in / $0.9064 out) and only invoke Qwen3 VL when the retrieved chunks contain figures. Could cut complex-lane cost ~60%.

## 10. References

- [Amazon Bedrock Pricing — Qwen section (verified 10 May 2026)](https://aws.amazon.com/bedrock/pricing/)
- [Qwen3 VL 235B A22B model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-vl-235b-a22b.html)
- [Qwen3 Next 80B A3B model card](https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/model-card-qwen-qwen3-next-80b-a3b.html)
- [Qwen3 32B model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-32b.html)
- [OpenAI-compatible fine-tuning APIs in Amazon Bedrock (Reinforcement Fine-Tuning)](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html)
- [Fine-tune small language models for production-grade tool calling with GRPO using Hugging Face TRL on Amazon SageMaker (AWS Builder)](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai)

*Content above is rephrased for compliance with licensing restrictions.*
