# Fine-tuning vs. RAG Strategy for Nova Health Tech

## Do we need RAG? Do we need fine-tuning? Both?

**Both — but in this order.** They solve different problems. Any clinical assistant that skips RAG cannot satisfy the "monthly WHO updates" requirement, and any assistant that skips tone/phrasing fine-tuning tends to feel inconsistent across physicians.

| Requirement from the scenario | Satisfied by |
|---|---|
| Answer complex medical questions in natural language | Foundation model (no training needed for Claude 4.x / Qwen3.5) |
| Rely on internal trial reports + WHO + PubMed | **RAG** — must be fresh, traceable, citable |
| Monthly WHO protocol updates | **RAG** — fine-tune can't be retrained monthly at acceptable cost or time |
| 2-second emergency response | Small/fast model (Haiku 4.5 / Qwen3.5-Flash) + streaming — no fine-tune needed |
| Patient-sensitive trial data | RAG with PHI masking; never in training data |
| Consistent tone and phrasing | **SFT + optionally DPO** on Nova-approved answer style |

## RAG design (same pattern both clouds)

1. **Ingest** — S3/OSS raw bucket receives PDFs and JSON.
2. **Parse** — Bedrock Data Automation (AWS) / DocMind + Qwen-VL (Ali) to turn inconsistent legacy PDFs into structured text + figures + metadata.
3. **Chunk** — section-aware; 256 tokens for WHO (recommendation-dense), 512 for trials, 300 for PubMed abstracts; 15% overlap.
4. **Embed** — multimodal: Amazon Nova Multimodal Embeddings (AWS) / qwen3-vl-embedding fused (Ali). A single vector covers text and figure in the same chunk.
5. **Index** — OpenSearch with HNSW and `knn_vector` mapping, plus BM25 in the same index for hybrid retrieval.
6. **Retrieve** — hybrid (BM25 + kNN) with metadata pre-filter (`source`, `speciality`, `date`, `evidence_grade`). Rerank top-20 with a cross-encoder if latency budget allows.
7. **Generate** — grounded prompt template forces citation (`{"claim": "...", "source": "WHO Malaria 2025-08, p.42"}`). Output fails guardrail if no citation is present.
8. **Cache** — semantic cache on Redis/Tair keyed by the query embedding; 10-minute TTL; invalidated on any WHO/internal doc reindex.

## Fine-tuning strategy

### When fine-tuning is justified

- After 5–10k approved Q&A pairs from Nova clinicians are curated.
- After RAG evaluation shows recurring *tone* or *phrasing* complaints (not factual gaps — those are fixed with better retrieval).
- When you want to embed company-specific conventions ("always mention contraindications before dosage", "use SBAR format") that are tedious to enforce via system prompt.

### When to avoid fine-tuning

- Keeping the model current on literature — use RAG.
- Reducing hallucination — use RAG + grounding checks; fine-tuning on too-small datasets often makes hallucination worse.
- Short deadlines — fine-tuning + eval typically adds 2–4 weeks to a release.

### AWS fine-tuning choices

| Model | Method | When | Approx cost |
|---|---|---|---|
| Amazon Nova Lite | SFT via Bedrock custom models (managed) | Tone fine-tune — fast & cheap | $ low-four-figures for 10k samples |
| Amazon Nova Pro | SFT | Deeper specialty adapter | $ mid-four-figures |
| Meta Llama 3.2 / 3.3 | SFT / LoRA via Bedrock or SageMaker | When you want open weights you can also run on-prem | $ depends on GPU hours |

Do not fine-tune Claude — Anthropic does not expose Claude weights on Bedrock for SFT; rely on system prompts + Guardrails for Claude tone.

### Alibaba Cloud fine-tuning choices (confirmed via askAli_AI_Assistant.txt)

| Model | Method | When |
|---|---|---|
| **Qwen3-8B** | LoRA (recommended first step) or SFT (full-parameter) | Tone fine-tune for Nova-voice; 1–2 A10 GPUs enough |
| Qwen3-14B / 32B | LoRA / QLoRA (4-bit or 8-bit) | Specialty domain adapter |
| Qwen2.5-7B-Instruct | SFT + **DPO** (Direct Preference Optimization) | Align on clinician-preferred safer answers |
| Qwen3 | **GRPO** (reinforcement-learning-style) | Advanced reasoning alignment, last resort |
| Qwen3-VL (if multimodal outputs needed) | SFT via PAI | If Nova wants the model to also interpret image inputs |

Fine-tuning is available in:

- **PAI Model Gallery** — click-to-train UI, best for teams that want a managed flow.
- **PAI-DSW notebooks** — full code control.
- **Model Studio HTTP API** — token-billed tuning for Qwen-Turbo/Plus variants.
- **Arena CLI on ACK** — if you need to drive training with Kubernetes.

### Do not fine-tune on PHI

Both clouds' guidance — and every medical-AI compliance framework — says the same thing: **de-identify training data first**. Use Comprehend Medical (AWS) or DataWorks + custom masking (Ali) to strip PHI, then optionally synthesize realistic replacement data with the same foundation model you'll serve, so the distribution stays close.

## Evaluation harness (required before production)

- **LLM-as-judge** pattern with a stronger model grading the answers (Claude Sonnet 4.6 / Qwen3-Max), using a clinician-authored rubric: factual accuracy, citation coverage, PHI leakage, emergency-appropriateness, tone.
- **Retrieval eval**: Recall@5, MRR against a held-out Q→passage dataset.
- **Latency eval**: p50, p95, p99 on the emergency lane.
- **Safety eval**: Bedrock Guardrails / Alibaba Content Moderation both need red-team prompt sets — build 200+ adversarial prompts before launch (self-diagnosis, dosing override, PII exfiltration, jailbreak).
- **Drift eval** after each monthly WHO refresh: re-run eval suite automatically; alert if any metric drops > 3%.

## References

- [Evaluate healthcare generative AI applications using LLM-as-a-judge on AWS](https://aws.amazon.com/blogs/machine-learning/evaluate-healthcare-generative-ai-applications-using-llm-as-a-judge-on-aws/)
- [Fine-tune Qwen — Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/text-generation-model-tuning)

*Content above is rephrased for compliance with licensing restrictions.*
