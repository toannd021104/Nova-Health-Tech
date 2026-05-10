# Fine-tuning, Distillation, and the 2-Second Emergency SLA

## The core tension

Emergency care needs an answer in ≤ 2 seconds. The models that answer medical questions well (Claude Sonnet 4.6, Qwen3-Max) are slow — typical p95 around 5–8 seconds for a 300-token answer with RAG context. The models that are fast enough (Claude Haiku 4.5, Qwen3.5-Flash) answer in 1–2 seconds but miss clinically important nuance on rarer conditions.

## The plan (agreed with user)

**Use a small model for serving, make it smart via distillation + fine-tuning from a big model's outputs.**

1. The big model (teacher) — Claude Sonnet 4.6 on AWS, Qwen3-Max on Ali — answers a curated set of representative clinical questions, with the full RAG context attached.
2. Clinicians review and approve those answers. This builds a **synthetic instruction dataset** of ~10–30k `(question, RAG-context, approved-answer)` tuples.
3. The small model (student) — Haiku 4.5 on AWS (via Nova Micro/Lite custom fine-tune since Claude weights aren't trainable on Bedrock), Qwen3-8B on Ali — is fine-tuned on that dataset with SFT + LoRA.
4. At serving time, the student is called with the RAG context; it produces answers that are close to the teacher's quality but at the small model's latency.

This is exactly the distillation pattern that Clinical Knowledge Distillation for EHRs and the SynthVision medical dataset both validate. It turns a latency problem into a one-time training investment.

### Model choices per cloud

| Role | AWS | Alibaba Cloud |
|---|---|---|
| Teacher (slow, high quality, used during training and live escalation for complex questions) | **Claude Sonnet 4.6** on Bedrock | **Qwen-Max (Qwen3-Max)** on Model Studio |
| Student (fast, serves emergency traffic) | **Claude Haiku 4.5** in phases 1–2; **Nova Lite fine-tuned on Sonnet+RAG outputs** once the distillation dataset is ready (phase 3) | **Qwen3.5-Flash** in phases 1–2; **Qwen3-8B SFT + LoRA on PAI** (served on PAI-EAS) from phase 3 |
| Why not Opus / why not fine-tune Claude | Opus 4.6 is deliberately excluded — price is hard to justify for clinical QA at this volume, and Sonnet is already the teacher. Claude weights aren't exposed for SFT on Bedrock, so the fine-tunable target is Nova Lite. | Qwen is open weights; fine-tune the student directly |

### Data pipeline for fine-tune

```
Step 1 — Seed queries
  ├── scrape de-identified historical clinician questions from Nova's existing tool
  └── generate synthetic variations using the teacher (paraphrases, edge cases)
         → ~10k seed questions

Step 2 — Teacher generation (batched, 50% off on both clouds)
  for each question:
      retrieve RAG context
      ask teacher: "Answer in Nova's standard tone, cite every claim, ≤ 250 words"
      store (question, context, teacher_answer)

Step 3 — Clinician review (Amazon A2I / Alibaba Human Verification)
  sample 10–20% for clinician review; fix what they flag; feed corrections
  back into the dataset with higher weight

Step 4 — DPO pair dataset (optional but recommended)
  for each reviewed example, build (chosen=clinician-approved,
                                    rejected=earlier model draft)
  → Qwen supports DPO natively; Nova Lite supports preference tuning

Step 5 — Fine-tune
  AWS: Bedrock custom model (Nova Lite SFT)
  Ali: PAI Model Gallery (Qwen3-8B SFT + LoRA, then optional DPO)

Step 6 — Evaluation gate
  LLM-as-judge eval (teacher grades student answers) + clinician spot-check
  If student accuracy ≥ 95% of teacher on the holdout, ship; else iterate.
```

### Deployment in the two lanes

The router Lambda / Function Compute picks the model per query:

```
emergency classifier (200–300 ms, Nova Micro / Qwen-Flash)
   ├── emergency → AWS: Haiku 4.5 (phase 1–2) → Nova Lite student (phase 3+). Cached + streaming.     → ≤ 2 s
   │              Ali: Qwen3.5-Flash (phase 1–2) → Qwen3-8B student on PAI-EAS (phase 3+).            → ≤ 2 s
   ├── complex   → Teacher (Sonnet 4.6 / Qwen-Max), streaming                                          → 4–7 s
   └── citation-heavy → fast-lane model with strict grounded-only mode                                 → ≤ 3 s
```

Before the student ships, Haiku 4.5 and Qwen3.5-Flash already meet the 2-second SLA on their own. Distillation is the quality lift, not the latency lift.

### Costs

Distillation is a one-time cost (periodic retraining, ~quarterly).

- **AWS** — Nova Lite SFT on 20k samples: about $1–2k per run on Bedrock custom models; teacher calls to generate the dataset at batch-50%-off rates, roughly $300–600 for 20k teacher answers with RAG context. Total retrain: ~**$2k per quarter**.
- **Alibaba** — Qwen3-8B LoRA on 20k samples: 2–4 GPU-hours on A10, about $10–30; teacher (Qwen3-Max) batch calls for 20k answers, roughly $30–60. Total retrain: under **$100 per quarter**.

The savings on inference far outweigh this — routing emergency traffic to a small student model (instead of the teacher) is the single largest cost-and-latency lever in the whole system.

## Consistent tone and phrasing via hyperparameters

The scenario asks for "consistent tone and phrasing." Fine-tuning on Nova-approved answers bakes in the style, but the inference-time levers matter too:

| Parameter | Default (creative) | Recommended (clinical) | Rationale |
|---|---|---|---|
| `temperature` | 0.7 | **0.1–0.2** | Low temperature makes token selection near-deterministic. Same prompt + same context produces nearly the same answer every time. |
| `top_p` (nucleus) | 1.0 | **0.7–0.9** | Narrows the sampling pool to high-probability tokens. Cuts stylistic drift without going fully deterministic. |
| `top_k` | unset | **40** (when the model supports it, e.g. Qwen / Nova) | Hard cap on candidate tokens per step; avoids rare tokens that bloat style variance. |
| `max_tokens` | 4096 | **700** for emergency, **1500** for complex | Limits runaway answers; pairs with system prompt "be concise". |
| `stop_sequences` | none | `["\n\nDisclaimer:", "\n\nEND"]` | Cuts off at a predictable stopping point for cleaner formatting. |
| `frequency_penalty` | 0 | **0.2** | Gently discourages repeating the same phrasing across turns. |
| `presence_penalty` | 0 | **0** for clinical | Keep 0 — we want repeated use of the correct terminology. |
| `seed` (if supported) | none | **Pin per deployment** (e.g. 42) | Maximal determinism when the provider supports it. Nova/Qwen OpenAI-compatible endpoints support `seed`; Claude on Bedrock does not. |

Trade-off: pure `temperature=0` is not actually fully deterministic on most hosted APIs because of mixed-precision GPU batching, and it can make the model brittle (refusing to answer when uncertain). `temperature=0.1–0.2` with a fine-tuned student gives the best combination of consistency and resilience in our testing plan.

**System prompt template** (same shape on both clouds) also enforces tone:

```
You are Nova's clinical decision-support assistant.
Voice: precise, neutral, professional. No filler phrases.
Structure every answer as:
  1. Immediate action (one sentence, only for emergency questions)
  2. Key details (3–5 bullets, each with a citation token like [1], [2])
  3. Cautions / contraindications
  4. References (the citation list)
Never include advice for patients directly. If stakes are high, remind the
clinician that this is decision support, not a diagnosis.
```

## When to avoid fine-tuning

- **Knowledge freshness** — always via RAG. WHO publishes monthly updates; a fine-tune cycle can't keep up and would encode stale facts.
- **Hallucination control** — RAG + grounding check + citation validator; fine-tuning on too-small datasets often makes hallucination worse.
- **Short deadlines** — fine-tuning + eval typically adds 3–4 weeks. Start with RAG only.
- **On PHI** — never. De-identify or synthesize before any training job, on either cloud.

## Evaluation harness (required before production)

- **LLM-as-judge** using the teacher model with a clinician-authored rubric: factual accuracy, citation coverage, PHI leakage, tone consistency, emergency-appropriateness.
- **Latency eval** — p50, p95, p99 under production load; reject a new model version if p95 emergency latency exceeds 1800 ms.
- **Safety eval** — 200+ red-team prompts (prompt injection, self-diagnosis, dosage override, jailbreak) before go-live.
- **Drift eval** after each monthly WHO refresh and every student retrain — rerun the full suite, alert if any metric drops > 3%.

## References

- [Clinical Knowledge Distillation for EHRs (arXiv)](https://arxiv.org/html/2506.15118)
- [Synthetic data distillation enables extraction of clinical information at scale — Nature](https://www.nature.com/articles/s41746-025-01681-4)
- [When Compressing a Frontier Model Actually Pays Off](https://tianpan.co/blog/2026-04-09-knowledge-distillation-economics-production-ai)
- [Fine-tune Qwen — Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/text-generation-model-tuning)
- [Fine-tuning LLMs in healthcare — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/generative-ai-nlp-healthcare/fine-tuning.html)
- [The Tuning Decisions Nobody Explains — temperature / top-p / top-k in production](https://tianpan.co/blog/2026-04-18-sampling-parameters-production-temperature-top-p-tuning)

*Content above is rephrased for compliance with licensing restrictions.*
