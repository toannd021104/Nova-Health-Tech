# AWS with Qwen — Architecture (Version B)

All-Qwen on AWS. Combines Bedrock's new OpenAI-compatible endpoint (hosts `qwen.qwen3-32b` with reinforcement fine-tuning) with SageMaker for flexible SFT / DPO / GRPO on smaller Qwen variants. Useful when Nova wants open-weight models + AWS compliance posture in one bundle.

## 1. Why a Qwen-on-AWS variant exists

- Some Nova clients (or Nova's own compliance team) require **open weights** to eliminate vendor lock on model behavior, but also want AWS's HIPAA posture + BAA.
- Cost: Qwen3-32B fine-tuned and served on SageMaker can beat Claude Sonnet token pricing 3–5×.
- Data residency: AWS GovCloud / us-east-1 / us-west-2 gives fixed-region guarantees the Alibaba-hosted Qwen path cannot currently offer for US clients.

## 2. Regulatory caveat

- **Bedrock OpenAI-compatible fine-tuning is `us-west-2` only** today. Inference for `qwen.qwen3-32b` and `qwen.qwen3-vl-235b-a22b` is also us-west-2 in the current model cards.
- This means **data residency is US** for the AWS-Qwen version — not Singapore. If the hospital client requires PDPA/Singapore-only, Version A (AWS Claude in ap-southeast-1) or Version C (Alibaba in Singapore) is correct.
- Otherwise: fine-tuning + inference both in `us-west-2` under an AWS BAA.

## 3. Model selection

| Role | Model | Where | Customization technique |
|---|---|---|---|
| Teacher (complex lane) | **Qwen3-VL 235B A22B** via Bedrock `bedrock-mantle` endpoint (`qwen.qwen3-vl-235b-a22b`) | us-west-2 inference | — (not fine-tuned; used as-is) |
| Student / fast lane (option A) | **Qwen3 32B** via Bedrock OpenAI-compatible endpoint (`qwen.qwen3-32b`) | us-west-2, fine-tuned | **Reinforcement fine-tuning** on Bedrock with a Lambda grader (verifiable reward, e.g., "is the answer grounded in retrieved context?") |
| Student / fast lane (option B) | **Qwen3-8B** on SageMaker JumpStart | us-west-2, fine-tuned | **SFT + LoRA** via Hugging Face TRL on a SageMaker training job; optional **DPO** round |
| Embeddings | Cohere Embed v4 on Bedrock | us-west-2 | — |

We recommend **Option B (Qwen3-8B on SageMaker)** as the primary student, because:
- It's 4x smaller than Qwen3-32B → cheaper and faster to serve.
- SageMaker TRL gives us the full SFT + DPO + GRPO toolbox per the AWS builder article on tool-calling with GRPO.
- Qwen3-32B remains a fallback if the 8B student can't hit the quality bar.

## 4. Component diagram (text)

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
      │                          (Cohere Embed v4 · hybrid BM25+kNN)
      │
      ├─── emergency=true ────► SageMaker real-time endpoint
      │                          Qwen3-8B fine-tuned student (g5.2xlarge)
      │
      └─── emergency=false ───► Bedrock `bedrock-mantle` endpoint
                                  qwen.qwen3-vl-235b-a22b teacher
      │
      ▼
 Guardrails (Bedrock Guardrails + citation validator)
      │
      ▼
 Stream response back to client

Ingestion (unchanged from Version A):
 S3 raw → EventBridge → Step Functions → BDA parse → chunk → embed (Cohere v4) → KB sync

Training lane (quarterly):
 Clinician Q logs → SageMaker training (TRL SFT + LoRA on Qwen3-8B) → DPO round
                                  → eval (LLM-as-judge on Qwen3-VL-235B) → promote to endpoint
```

## 5. Fine-tuning workflow (detailed)

1. **Harvest prompts**: 10k–30k de-identified clinician questions from invocation logs, plus paraphrases generated from the WHO / protocol corpus.
2. **Teacher generation (distillation)**: run the Qwen3-VL 235B teacher on Bedrock in batch mode against each `(question, RAG-context)` to produce target answers. 50% batch discount applies.
3. **Clinician review**: Amazon Ground Truth or a custom UI; 10–20% of pairs get human review. Corrections become higher-weight SFT rows or DPO pairs.
4. **SFT**: SageMaker training job running `trl sft` on Qwen3-8B, with LoRA. Typical 20k-sample run: 2–4 GPU-hours on `ml.g5.2xlarge`.
5. **DPO** (optional): `trl dpo` on the pairs collected in step 3.
6. **Evaluation**: LLM-as-judge using the Qwen3-VL teacher to grade student answers on accuracy, citation coverage, tone, safety.
7. **Deploy**: SageMaker endpoint (g5.2xlarge) with the fine-tuned 8B model. Alternatively, if Qwen3-32B reinforcement fine-tuning on Bedrock goes better, deploy on `bedrock-mantle` instead.

## 6. Latency budget (emergency lane, post-fine-tune)

```
  20 ms   Semantic cache hit (Layer 1; skip to step 7 if hit)
 100 ms   Cognito auth + PHI mask
  70 ms   Hybrid retrieval
 400 ms   SageMaker endpoint first-token (Qwen3-8B on g5.2xlarge)
1000 ms   full answer (250 tokens, streaming)
 110 ms   Guardrails + citation validation
───────
≤ 1,700 ms  p95
```

Cohere Embed v4 for the query embedding is ~20 ms extra; Bedrock Prompt Caching (if available for the mantle endpoint — not yet confirmed) would shave more.

## 7. Cost (quick order-of-magnitude)

| Item | Cost |
|---|---|
| Qwen3-VL 235B teacher inference (complex lane) | Confirm on Bedrock pricing; expect low-to-mid-single-digit $/1M tokens |
| Qwen3-8B student on SageMaker endpoint (g5.2xlarge, always-on) | ~$1.20–$1.80/hr → ~$900–$1,300/mo per replica |
| Training: 20k samples SFT + LoRA | $5–$30 per run |
| Training: Qwen3-32B reinforcement fine-tuning on Bedrock | billed by tokens + grader executions; estimate on a small pilot first |
| OpenSearch Serverless | ~$350/mo baseline |
| Everything else (Lambda, S3, ElastiCache, Guardrails, Comprehend Medical, CloudTrail) | ~$700/mo |

Single-replica Qwen3-8B always-on is the expensive line — similar to the Alibaba PAI-EAS case. A small team can get away with auto-scaled inference (scale to zero when idle) using SageMaker Serverless Inference for non-peak traffic.

## 8. What makes this version attractive

- Full open-weight ownership (Qwen3-8B weights + LoRA adapter) — portable to on-prem / other clouds later.
- Three real fine-tuning techniques available on the same platform (SFT, DPO, GRPO) — most flexible AWS path.
- Under the AWS BAA + HIPAA posture for US clients.

## 9. What makes it less attractive

- `us-west-2` pin for both training and inference of Qwen models.
- More moving parts than Version A (SageMaker + Bedrock + OpenSearch, not just Bedrock).
- Qwen3 model card availability on Bedrock is newer than Claude's, so fewer battle-tested production deployments to reference.

## 10. References

- [OpenAI-compatible fine-tuning APIs in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html)
- [Qwen3-VL 235B A22B model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-vl-235b-a22b.html)
- [Fine-tune small language models for production-grade tool calling with GRPO using Hugging Face TRL on Amazon SageMaker](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai)
- [SageMaker JumpStart — fine-tune pretrained models](https://docs.aws.amazon.com/sagemaker/latest/dg/jumpstart-fine-tune.html)
- [Fine-Tuning LLMs with TRL CLI on SageMaker (Hugging Face)](https://huggingface.co/docs/sagemaker/examples/sagemaker-sdk-fine-tune-trl-cli)

*Content above is rephrased for compliance with licensing restrictions.*
