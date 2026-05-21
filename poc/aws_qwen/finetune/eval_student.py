"""Evaluate fine-tuned student model against teacher (Qwen3.5-397B-A17B via DeepInfra).

Teacher/judge: Qwen/Qwen3.5-397B-A17B via HuggingFace InferenceClient (DeepInfra provider)
Student: local fine-tuned Qwen3.5-4B

Usage:
    python poc/aws_qwen/finetune/eval_student.py \\
        --student-path models/qwen-student-phase1/merged \\
        --eval-data data/distillation/phase1.jsonl \\
        --n 100 \\
        --output eval_results.json

Requires:
    pip install huggingface_hub>=0.24
    export HF_TOKEN=hf_...
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import re
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

JUDGE_MODEL = "Qwen/Qwen3.5-397B-A17B"
JUDGE_PROVIDER = "deepinfra"

JUDGE_PROMPT = """You are a clinical AI evaluator. Score the following AI-generated clinical answer on a scale of 0-10.

Criteria:
- Accuracy (0-4): Is the answer clinically correct and evidence-based?
- Completeness (0-3): Does it cover the key management steps?
- Format (0-2): Does it follow the required format (citations [N], Recommendation: line)?
- Safety (0-1): Does it avoid dangerous advice or hallucinations?

Question: {question}

Answer to evaluate:
{answer}

Reference answer (from expert teacher model):
{reference}

Output exactly this JSON:
{{"score": <0-10>, "accuracy": <0-4>, "completeness": <0-3>, "format": <0-2>, "safety": <0-1>, "comment": "<one sentence>"}}
"""


def _load_student_pipeline(model_path: str):
    from transformers import pipeline  # noqa: PLC0415
    log.info("Loading student model from %s ...", model_path)
    return pipeline(
        "text-generation",
        model=model_path,
        device_map="auto",
        torch_dtype="auto",
        trust_remote_code=True,
    )


def _student_answer(pipe, question: str, max_new_tokens: int = 512) -> str:
    system = (
        "You are a clinical AI assistant. Answer concisely and cite sources with [N] tags. "
        "End with a Recommendation: line."
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    result = pipe(messages, max_new_tokens=max_new_tokens, temperature=0.1,
                  do_sample=False, return_full_text=False)
    return result[0]["generated_text"] if result else ""


def _judge_score(hf_client, question: str, student_answer: str, reference: str) -> dict:
    prompt = JUDGE_PROMPT.format(
        question=question, answer=student_answer, reference=reference
    )
    try:
        result = hf_client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.0,
            extra_body={
                "top_k": 20,
                # Disable thinking for judge — we want direct JSON output
                "chat_template_kwargs": {"enable_thinking": False},
            },
        )
        raw = result.choices[0].message.content.strip()
        # Strip any leaked <think> blocks
        import re as _re
        raw = _re.sub(r"<think>[\s\S]*?</think>\s*", "", raw).strip()
        fence = re.search(r"\{[\s\S]*\}", raw)
        if fence:
            return json.loads(fence.group(0))
    except Exception as e:
        log.warning("Judge call failed: %s", e)
    return {"score": -1, "comment": "judge_failed"}


def evaluate(
    student_path: str,
    eval_data_path: Path,
    n: int,
    output_path: Path,
) -> None:
    try:
        from huggingface_hub import InferenceClient  # noqa: PLC0415
    except ImportError:
        raise SystemExit("Install: pip install huggingface_hub>=0.24")

    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token:
        raise SystemExit("Set HF_TOKEN environment variable")

    hf_client = InferenceClient(provider=JUDGE_PROVIDER, api_key=hf_token)
    pipe = _load_student_pipeline(student_path)

    # Load eval samples
    records = []
    with open(eval_data_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    sample = random.sample(records, min(n, len(records)))
    log.info("Evaluating %d samples ...", len(sample))

    results = []
    scores = []

    for i, record in enumerate(sample, 1):
        messages = record.get("messages", [])
        question = next((m["content"] for m in messages if m["role"] == "user"), "")
        reference = next((m["content"] for m in messages if m["role"] == "assistant"), "")
        dept = record.get("department", "unknown")

        student_ans = _student_answer(pipe, question)

        # Heuristic metrics
        citation_present = bool(re.search(r"\[\d+\]", student_ans))
        recommendation_present = "recommendation:" in student_ans.lower()
        length_ratio = len(student_ans.split()) / max(1, len(reference.split()))

        # LLM judge
        judge = _judge_score(hf_client, question, student_ans, reference)

        result = {
            "idx": i,
            "department": dept,
            "question": question[:200],
            "student_answer": student_ans[:500],
            "reference_answer": reference[:500],
            "citation_present": citation_present,
            "recommendation_present": recommendation_present,
            "length_ratio": round(length_ratio, 2),
            "judge": judge,
        }
        results.append(result)
        if judge.get("score", -1) >= 0:
            scores.append(judge["score"])

        if i % 10 == 0:
            avg = sum(scores) / len(scores) if scores else 0
            log.info("Progress %d/%d | avg judge score: %.1f/10", i, len(sample), avg)

    # Summary
    avg_score = sum(scores) / len(scores) if scores else 0
    citation_rate = sum(1 for r in results if r["citation_present"]) / len(results)
    rec_rate = sum(1 for r in results if r["recommendation_present"]) / len(results)
    avg_length_ratio = sum(r["length_ratio"] for r in results) / len(results)

    summary = {
        "n_evaluated": len(results),
        "avg_judge_score": round(avg_score, 2),
        "citation_rate": round(citation_rate, 3),
        "recommendation_rate": round(rec_rate, 3),
        "avg_length_ratio": round(avg_length_ratio, 2),
        "student_model": student_path,
        "teacher_model": TEACHER_MODEL,
    }

    output = {"summary": summary, "results": results}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n=== Evaluation Summary ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"\nFull results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate student model vs teacher")
    parser.add_argument("--student-path", required=True, help="Path to merged student model")
    parser.add_argument("--eval-data", required=True, help="JSONL eval data path")
    parser.add_argument("--n", type=int, default=100, help="Number of samples to evaluate")
    parser.add_argument("--output", default="eval_results.json", help="Output JSON path")
    args = parser.parse_args()

    evaluate(
        student_path=args.student_path,
        eval_data_path=Path(args.eval_data),
        n=args.n,
        output_path=Path(args.output),
    )


if __name__ == "__main__":
    main()
