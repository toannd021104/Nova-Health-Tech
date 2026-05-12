"""
Evaluation script for 900 questions against the live web app.
Reads docs/test_questions_800.csv, POSTs each question to http://47.130.120.152/api/chat,
and records results to docs/eval_results_900.csv.
"""

import csv
import json
import time
import requests
from datetime import datetime

INPUT_CSV = "docs/test_questions_800.csv"
OUTPUT_CSV = "docs/eval_results_900.csv"
API_URL = "http://47.130.120.152/api/chat"

# SLA thresholds
EMERGENCY_SLA_MS = 5000
GENERAL_SLA_MS = 15000

# Phrases that indicate refusal / no data
REFUSE_PHRASES = [
    "cannot answer",
    "not in the context",
    "i don't have",
    "not available in",
    "no information",
    "don't have information",
    "unable to answer",
    "not found in",
    "no relevant information",
]

NO_ANSWER_PHRASES = [
    "cannot answer",
    "not in the context",
    "no information",
]


def classify_answer(answer: str) -> tuple[bool, bool]:
    """Returns (answered, refused)."""
    if not answer or not answer.strip():
        return False, False
    lower = answer.lower()
    refused = any(p in lower for p in REFUSE_PHRASES)
    answered = bool(answer.strip()) and not any(p in lower for p in NO_ANSWER_PHRASES)
    return answered, refused


def query_api(question: str, is_emergency: bool) -> dict:
    """POST to the API and return result dict."""
    payload = {
        "message": question,
        "emergency": is_emergency,
    }
    start = time.time()
    try:
        resp = requests.post(API_URL, json=payload, timeout=60)
        elapsed_ms = int((time.time() - start) * 1000)
        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("answer", "") or data.get("response", "") or data.get("message", "") or ""
            # Try nested structures
            if not answer and isinstance(data, dict):
                for key in ["text", "content", "result", "output"]:
                    if key in data and data[key]:
                        answer = str(data[key])
                        break
            # Citations
            citations = data.get("citations", []) or data.get("sources", []) or []
            num_citations = len(citations) if isinstance(citations, list) else 0
            # Route info
            route = data.get("route", {}) or {}
            lane = route.get("lane", "") if isinstance(route, dict) else ""
            department = route.get("department", "") if isinstance(route, dict) else ""
            return {
                "status": "ok",
                "elapsed_ms": elapsed_ms,
                "answer": answer,
                "num_citations": num_citations,
                "lane": lane,
                "department": department,
                "raw": data,
            }
        else:
            return {
                "status": f"http_{resp.status_code}",
                "elapsed_ms": elapsed_ms,
                "answer": "",
                "num_citations": 0,
                "lane": "",
                "department": "",
                "raw": {},
            }
    except requests.exceptions.Timeout:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "status": "timeout",
            "elapsed_ms": elapsed_ms,
            "answer": "",
            "num_citations": 0,
            "lane": "",
            "department": "",
            "raw": {},
        }
    except Exception as e:
        elapsed_ms = int((time.time() - start) * 1000)
        return {
            "status": f"error: {e}",
            "elapsed_ms": elapsed_ms,
            "answer": "",
            "num_citations": 0,
            "lane": "",
            "department": "",
            "raw": {},
        }


def main():
    # Read questions
    questions = []
    with open(INPUT_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            questions.append(row)

    total = len(questions)
    print(f"Loaded {total} questions from {INPUT_CSV}")
    print(f"Starting evaluation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API: {API_URL}")
    print("-" * 60)

    results = []
    answered_count = 0
    refused_count = 0
    sla_pass_count = 0
    emergency_times = []
    general_times = []

    # Write CSV header
    fieldnames = [
        "id", "type", "question",
        "response_time_ms", "answer", "num_citations",
        "lane", "department", "answered", "refused", "status"
    ]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

    for i, row in enumerate(questions, 1):
        q_id = row["id"]
        q_type = row["type"]
        question = row["question"]
        is_emergency = (q_type == "emergency")

        result = query_api(question, is_emergency)

        answer = result["answer"]
        answered, refused = classify_answer(answer)

        # SLA check
        elapsed = result["elapsed_ms"]
        sla_threshold = EMERGENCY_SLA_MS if is_emergency else GENERAL_SLA_MS
        sla_pass = elapsed <= sla_threshold

        if answered:
            answered_count += 1
        if refused:
            refused_count += 1
        if sla_pass:
            sla_pass_count += 1

        if is_emergency:
            emergency_times.append(elapsed)
        else:
            general_times.append(elapsed)

        out_row = {
            "id": q_id,
            "type": q_type,
            "question": question[:200],
            "response_time_ms": elapsed,
            "answer": answer[:500] if answer else "",
            "num_citations": result["num_citations"],
            "lane": result["lane"],
            "department": result["department"],
            "answered": answered,
            "refused": refused,
            "status": result["status"],
        }
        results.append(out_row)

        # Append to CSV
        with open(OUTPUT_CSV, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(out_row)

        # Progress every 50 questions
        if i % 50 == 0 or i == total:
            pct = i / total * 100
            avg_time = sum(r["response_time_ms"] for r in results) / len(results)
            print(f"Progress: {i}/{total} ({pct:.1f}%) | "
                  f"Answered: {answered_count} | Refused: {refused_count} | "
                  f"Avg time: {avg_time:.0f}ms")

        # 1-second delay between requests
        if i < total:
            time.sleep(1)

    # Summary
    total_times = [r["response_time_ms"] for r in results]
    avg_time = sum(total_times) / len(total_times) if total_times else 0
    avg_emergency = sum(emergency_times) / len(emergency_times) if emergency_times else 0
    avg_general = sum(general_times) / len(general_times) if general_times else 0
    sla_pct = sla_pass_count / total * 100

    print("\n" + "=" * 60)
    print("EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Total questions:          {total}")
    print(f"Answered:                 {answered_count} ({answered_count/total*100:.1f}%)")
    print(f"Refused/no data:          {refused_count} ({refused_count/total*100:.1f}%)")
    print(f"Average response time:    {avg_time:.0f} ms")
    print(f"Emergency avg time:       {avg_emergency:.0f} ms")
    print(f"General avg time:         {avg_general:.0f} ms")
    print(f"SLA pass rate:            {sla_pass_count}/{total} ({sla_pct:.1f}%)")
    print(f"  (Emergency ≤{EMERGENCY_SLA_MS}ms, General ≤{GENERAL_SLA_MS}ms)")
    print("=" * 60)
    print(f"\nResults saved to: {OUTPUT_CSV}")

    # Save summary to markdown
    summary_md = f"""# Evaluation Summary — 900 Questions

**Run date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**API endpoint:** {API_URL}

## Results

| Metric | Value |
|--------|-------|
| Total questions | {total} |
| Answered | {answered_count} ({answered_count/total*100:.1f}%) |
| Refused / no data | {refused_count} ({refused_count/total*100:.1f}%) |
| Average response time | {avg_time:.0f} ms |
| Emergency avg time | {avg_emergency:.0f} ms |
| General avg time | {avg_general:.0f} ms |
| SLA pass rate | {sla_pass_count}/{total} ({sla_pct:.1f}%) |

## SLA Thresholds

| Type | Threshold | Avg Time | Pass Rate |
|------|-----------|----------|-----------|
| Emergency | ≤{EMERGENCY_SLA_MS} ms | {avg_emergency:.0f} ms | {sum(1 for r in results if r['type']=='emergency' and r['response_time_ms']<=EMERGENCY_SLA_MS)}/{len(emergency_times)} ({sum(1 for r in results if r['type']=='emergency' and r['response_time_ms']<=EMERGENCY_SLA_MS)/len(emergency_times)*100:.1f}% if emergency_times else 'N/A') |
| General | ≤{GENERAL_SLA_MS} ms | {avg_general:.0f} ms | {sum(1 for r in results if r['type']=='general' and r['response_time_ms']<=GENERAL_SLA_MS)}/{len(general_times)} ({sum(1 for r in results if r['type']=='general' and r['response_time_ms']<=GENERAL_SLA_MS)/len(general_times)*100:.1f}% if general_times else 'N/A') |

## Notes

- Questions 1–800: WHO COVID-19 guidelines (source: WHO)
- Questions 801–900: Clinical trial papers (PMC IDs embedded in question text)
- Sequential evaluation with 1-second delay between requests
- SLA: Emergency ≤5,000 ms, General ≤15,000 ms
"""

    with open("docs/eval_summary_900.md", "w", encoding="utf-8") as f:
        f.write(summary_md)
    print("Summary saved to: docs/eval_summary_900.md")


if __name__ == "__main__":
    main()
