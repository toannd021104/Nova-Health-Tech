# Fine-tuning & model customization — per version

Every technique here is part of the **launch build**. The student model, tone fine-tune, and guardrail-adversarial retrain all complete before cut-over and serve 100% of their respective lanes on day one. Post-launch runs continuous retraining (monthly DPO, quarterly SFT), not a "phase 2".

## 1. Techniques — plain definitions

| Technique | Goal | Input data | Output |
|---|---|---|---|
| **SFT** (supervised fine-tuning) | Teach the model to imitate good answers | `(prompt → target_answer)` pairs | Updated weights |
| **DPO** ([direct preference optimization](https://arxiv.org/abs/2305.18290)) | Teach the model one answer is preferred over another | `(prompt, chosen, rejected)` triples | Updated weights |
| **RLHF** ([classical RL with human feedback](https://arxiv.org/abs/2203.02155)) | DPO's ancestor — train a reward model then PPO against it | Preference labels + RL infra | Updated weights. Heavier than DPO with no clinical-accuracy upside — **not chosen**. |
| **Knowledge distillation** | Transfer a big model's behavior into a smaller, faster one | Big teacher + small student + prompts | Teacher-generated SFT/DPO dataset + fine-tuned student |
| **GRPO** ([reinforcement fine-tuning with verifiable reward](https://arxiv.org/abs/2402.03300)) | RL against a computable reward; no separate reward model | Prompts + grader function | Updated weights |

Distillation is **not** a fourth technique — it's a way to generate the SFT training data without paying human labelers.

## 2. What Nova actually needs

| Scenario need | Best technique |
|---|---|
| Answer complex medical questions in natural language | Base foundation model + RAG. No fine-tune needed. |
| Rely on internal trial reports + WHO + ICD-11 | RAG. Fine-tuning can't replace this — WHO updates monthly. |
| Consistent tone and phrasing | SFT on Nova-approved answers; DPO if preference pairs exist. |
| 2-second emergency SLA | Smaller, faster student. Distilled (teacher → student) with SFT. |
| Patient-sensitive internal trials | **Never put PHI in training data.** De-identify via [Comprehend Medical](https://aws.amazon.com/comprehend/medical/) / [DataWorks SDDP](https://www.alibabacloud.com/product/sddp) first. |

## 3. What's actually fine-tunable per cloud

### AWS Bedrock — custom model fine-tuning ([official list](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-supported.html))

| Provider | Model | Fine-tune region |
|---|---|---|
| Amazon | Nova 2 Lite / Nova Lite / Nova Micro / Nova Pro / Nova Canvas | us-east-1 |
| Amazon | Titan Image Generator G1 v2 / Titan Multimodal Embeddings | us-east-1, us-west-2 |
| **Anthropic** | **Claude 3 Haiku (2024-03-07 v1)** | **us-west-2 only** |
| Meta | Llama 3.1 / 3.2 / 3.3 | us-west-2 |

**Key constraint: Claude Haiku 4.5 is NOT fine-tunable.** Only Claude 3 Haiku (2024-03-07 snapshot) is. SFT only — no DPO, no RLHF for Claude on Bedrock. Hyperparameters:

```
epochCount:             2     (default, range 1–10)
batchSize:              32    (default, range 4–256)
learningRateMultiplier: 1.0   (default, range 0.1–2.0)
earlyStoppingThreshold: 0.001 (default, range 0–0.1)
earlyStoppingPatience:  2     (default, range 1–10)
```

### AWS Bedrock — Model Distillation ([docs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html))

Managed end-to-end: give it prompts, it asks the teacher, trains the student, exposes a custom-model endpoint.

- Two data sources: prompts you provide, or invocation logs from production traffic (recommended for clinical — clinician questions become the seed set)
- You can supply "golden examples" as prompt-response pairs to steer teacher generations
- Available teacher/student pairs include Nova Premier → Nova Pro/Lite/Micro; Llama 3.1 70B → Llama 3.1 8B, etc. Confirm current list before committing.

### AWS Bedrock — Reinforcement Fine-Tuning ([docs](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html))

The new `bedrock-mantle` endpoint. Two models as of May 2026:

- **[`qwen.qwen3-32b`](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-32b.html)**, us-west-2 — **$80/hr** training, then $0.20 in / $0.78 out per 1 M on custom-model inference
- **`openai.gpt-oss-20b`**, us-west-2

Lambda-defined grader function. Closest to GRPO in spirit. Fully managed — no GPU cluster to run.

### SageMaker path — all open weights, all techniques

Via [Hugging Face TRL](https://huggingface.co/docs/trl/index) on SageMaker:

- **SFT** on Qwen3-8B / Qwen3-32B / any HF open-weight
- **DPO** with TRL's `DPOTrainer`
- **GRPO** via [TRL's `GRPOTrainer`](https://huggingface.co/docs/trl/main/en/grpo_trainer) — this is what the [AWS Builder GRPO article](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai) uses

Serve on SageMaker endpoint in SG (residency-compliant) or drop onto PAI-EAS on Alibaba.

### Alibaba PAI — Qwen open weights ([PAI Model Gallery](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models))

| Model family | Techniques supported |
|---|---|
| Qwen3 0.6B / 1.7B / 4B / 8B / 14B / 32B | **SFT** (full / LoRA / QLoRA), **DPO**, **GRPO** |
| Qwen2.5 (7B-Instruct, 32B-Coder, etc.) | SFT + DPO |
| Qwen1.5 Base / Chat | SFT + DPO |

Plus Model Studio HTTP API offers token-billed fine-tuning for Qwen-Plus / Qwen-Turbo — click-and-train, no weights exposed.

## 4. Per-version launch-day plan

### Version A — AWS with Claude

| Role | Model | Customization |
|---|---|---|
| Complex-lane / teacher | [Claude Sonnet 4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html) | — (used as-is) |
| Emergency-lane base fallback | Claude Haiku 4.5 | — (cannot be fine-tuned) |
| **Fast-lane student, serves production on day one** | **Amazon Nova Lite** | **Bedrock Model Distillation** — Sonnet 4.5 as teacher → Nova Lite as student. Managed end-to-end; training completes pre-launch. |
| Backup (if client demands Claude-family student) | Claude 3 Haiku (2024-03-07) | Bedrock custom SFT on us-west-2. Trade-off: lose Haiku 4.5 quality gains. |

### Version B — AWS with Qwen

| Role | Model | Customization |
|---|---|---|
| Complex-lane / teacher | **Qwen3 VL 235B A22B** on Bedrock Sydney ([model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-vl-235b-a22b.html)); text-only alternative: Qwen3 235B A22B 2507 | — |
| Fast-lane base | **Qwen3 Next 80B A3B** on Bedrock Sydney ([model card](https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/model-card-qwen-qwen3-next-80b-a3b.html)) — MoE, 3B active | — |
| Fast-lane student (path B-1, preferred) | **Qwen3 32B** | [Bedrock RFT](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html) on us-west-2 with Lambda grader. Fully managed. |
| Fast-lane student (path B-2, optional) | Qwen3-1.7B or Qwen3-4B on SageMaker | SFT + LoRA + GRPO via [TRL on `ml.g6e.8xlarge`](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai). Matches AWS builder article. |

Path B-1 default: simpler ops, and the $0.78/1M output on the custom model is **cheaper** than the base $1.24/1M — cost win as well as quality win. Path B-2 only beats B-1 when SG residency for the student is mandatory.

### Version C — Alibaba Cloud

| Role | Model | Customization |
|---|---|---|
| Complex-lane / teacher | **Qwen3.5-Plus** on Model Studio SG ([pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)) | — |
| Emergency-lane base | Qwen3.5-Flash | — |
| **Student, serves production on day one** | **Qwen3-8B on PAI Model Gallery → PAI-EAS** | SFT + LoRA (or QLoRA), optional DPO, optional GRPO. Most flexible of the three versions. |

## 5. SFT dataset pipeline (shared across all three versions)

```
Step 1 — Seed prompts
  (a) de-identified clinician questions from historical invocation logs
  (b) paraphrases + edge cases generated by the teacher from WHO / protocol chunks
      → target: 10k–30k prompts

Step 2 — Teacher generation (batch, 50% off)
  For each prompt:
    retrieve RAG context
    ask teacher with Nova-style system prompt
    record (question, context, teacher_answer)

Step 3 — Clinician review
  Amazon A2I (Version A) or Alibaba Human Verification (Version C)
  Sample 10–20%. Approved rows → SFT. Clinician choices → DPO pairs.

Step 4 — Train
  Version A → Bedrock Model Distillation (managed)
  Version B → Bedrock RFT on Qwen3-32B (us-west-2) OR SageMaker TRL GRPO on Qwen3-4B
  Version C → PAI Model Gallery Qwen3-8B SFT + LoRA

Step 5 — Evaluation harness
  LLM-as-judge (teacher grades student) on accuracy, citation coverage,
  PHI leakage, tone, emergency-appropriateness.

Step 6 — Promote to production
  Gate: student ≥ 95% of teacher on holdout + no regression on safety suite
    (PHI leak, ungrounded answer, prompt injection).
  Launch-day: 100% on fast lane. Post-launch retrains: 5% canary for 72 hours.
```

**Never put raw PHI in training data.** De-identify before step 2.

## 6. Hyperparameters (for Version B path B-2 / Version C — the open-weight paths)

For **Qwen3-8B LoRA on SageMaker TRL or PAI Model Gallery** (matches the [AWS Builder GRPO recipe](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai)):

- LoRA rank 16, alpha 32, dropout 0.05
- `learning_rate 2e-4`, 3 epochs, warmup ratio 0.03, `bf16` precision
- Batch size per device 4, gradient accumulation 4 on a `ml.g5.2xlarge` or PAI A10

For **Claude 3 Haiku fallback path**, the hyperparameters in §3 (AWS Bedrock custom fine-tuning) apply.

## 7. Tone consistency — sampling first, training second

Before any fine-tune: `temperature=0.1`, narrow `max_tokens`, stop sequences, fixed system prompt (see [`aws-demo/ec2/app/graph.py`](../aws-demo/ec2/app/graph.py)). These alone deliver ~80% of "consistent tone" for clinicians.

Fine-tuning adds on top:
- Clinical-citation rubric the model follows without re-prompting
- Tone mimicking Nova's approved-answer corpus
- Lower cost and latency (smaller student on fast lane)
- Tool-calling reliability (GRPO on Versions B and C only)

## 8. Per-run cost ([full cost breakdown in each proposal doc](overview.md))

| | Version A | Version B | Version C |
|---|---|---|---|
| Technique | SFT via Bedrock Model Distillation (Sonnet → Nova Lite) | GRPO + RLVR on SageMaker TRL (Qwen3-1.7B/4B) OR Bedrock RFT on Qwen3-32B | SFT + LoRA on PAI Model Gallery (Qwen3-8B); optional DPO/GRPO |
| Teacher data generation | 80 M in + 6 M out on Sonnet batch ≈ **$165** | Synthetic prompts + verifiable reward; no teacher call → **~$0** | 80 M in + 6 M out on Qwen3.5-Plus batch ≈ **$66** |
| Training job | Bedrock Model Distillation: **$1,500–2,500** | `ml.g6e.8xlarge` × 10–15 hr × $5.74 = **$60–90** (SageMaker) OR $640 (Bedrock RFT) | 2–4 GPU-hr × $1–2/hr = **$5–30** on PAI |
| Clinician review (~15% sample) | low five-figure if outsourced; in-house free | same | same |
| **Total run cost** | **~$1,700–2,700** | **~$70–100** (SageMaker) OR **~$640** (Bedrock RFT) | **~$15–40** |
| Run cadence | Quarterly | Monthly if wanted (cheap) | Monthly if wanted |

**GRPO on open-weight Qwen is the cheapest to iterate.** Frequent retraining → best student over time.

## 9. References

- [Customize a model with fine-tuning in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-fine-tuning.html)
- [Amazon Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html)
- [OpenAI-compatible fine-tuning APIs in Amazon Bedrock (Reinforcement Fine-Tuning)](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html)
- [Supported models and Regions for fine-tuning](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-supported.html)
- [AWS Builder — GRPO tool-calling fine-tune on Hugging Face TRL + SageMaker](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai)
- [Fine-tune Qwen — Alibaba Model Studio](https://www.alibabacloud.com/help/en/model-studio/text-generation-model-tuning)
- [PAI Qwen3 deploy / fine-tune / evaluate](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models)
- [TRL GRPO Trainer — Hugging Face](https://huggingface.co/docs/trl/main/en/grpo_trainer)

*Content above is rephrased for compliance with licensing restrictions.*
