"""Test 50 random questions against the updated stack (streaming + multi-strategy chunking + top-15)."""
import csv
import json
import random
import time
import urllib.request
from datetime import datetime
from pathlib import Path

API_URL = "http://47.130.120.152/api/chat"
INPUT_CSV = "docs/test_questions_800.csv"
OUTPUT_FILE = "docs/eval_50_random_v2.md"

random.seed(2026)

# Load questions
questions = list(csv.DictReader(open(INPUT_CSV, encoding="utf-8")))
sample = random.sample(questions, 50)

print(f"Testing 50 random questions at {datetime.now()}")
print(f"API: {API_URL}")
print("-" * 60)

results = []
for i, row in enumerate(sample, 1):
    q_id = row["id"]
    q_type = row["type"]
    question = row["question"]
    is_emergency = q_type == "emergency"

    payload = json.dumps({"message": question, "emergency": is_emergency}).encode()
    req = urllib.request.Request(API_URL, data=payload, headers={"Content-Type": "application/json"})

    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            elapsed_ms = int((time.time() - t0) * 1000)
            answer = data.get("answer", "")
            citations = data.get("citations", [])
            lane = data.get("route", {}).get("lane", "")
            dept = data.get("route", {}).get("department", "")
            refused = "cannot answer" in answer.lower() or "not in the context" in answer.lower()
            results.append({
                "id": q_id, "type": q_type, "question": question[:100],
                "ms": elapsed_ms, "answered": not refused, "refused": refused,
                "citations": len(citations), "lane": lane, "dept": dept,
                "answer_preview": answer[:200],
            })
    except Exception as e:
        elapsed_ms = int((time.time() - t0) * 1000)
        results.append({
            "id": q_id, "type": q_type, "question": question[:100],
            "ms": elapsed_ms, "answered": False, "refused": False,
            "citations": 0, "lane": "", "dept": "", "answer_preview": f"ERROR: {e}",
        })

    if i % 10 == 0:
        avg = sum(r["ms"] for r in results) / len(results)
        answered = sum(1 for r in results if r["answered"])
        print(f"  {i}/50 | avg={avg:.0f}ms | answered={answered}/{len(results)}")

    time.sleep(1)

# Summary
total = len(results)
answered = sum(1 for r in results if r["answered"])
refused = sum(1 for r in results if r["refused"])
errors = sum(1 for r in results if "ERROR" in r["answer_preview"])
times = [r["ms"] for r in results]
avg_ms = sum(times) / len(times)
em_times = [r["ms"] for r in results if r["type"] == "emergency"]
gen_times = [r["ms"] for r in results if r["type"] == "general"]
em_avg = sum(em_times) / len(em_times) if em_times else 0
gen_avg = sum(gen_times) / len(gen_times) if gen_times else 0
em_sla = sum(1 for t in em_times if t <= 5000)
gen_sla = sum(1 for t in gen_times if t <= 15000)
avg_citations = sum(r["citations"] for r in results) / total

times.sort()
p50 = times[len(times)//2]
p95 = times[int(len(times)*0.95)]

print(f"\n{'='*60}")
print(f"RESULTS (50 random, multi-strategy chunking + top-15)")
print(f"{'='*60}")
print(f"Answered:     {answered}/{total} ({answered/total*100:.1f}%)")
print(f"Refused:      {refused}/{total} ({refused/total*100:.1f}%)")
print(f"Errors:       {errors}/{total}")
print(f"Avg time:     {avg_ms:.0f} ms")
print(f"Emergency:    avg={em_avg:.0f}ms, SLA pass={em_sla}/{len(em_times)}")
print(f"General:      avg={gen_avg:.0f}ms, SLA pass={gen_sla}/{len(gen_times)}")
print(f"Avg citations: {avg_citations:.1f}")
print(f"p50={p50}ms  p95={p95}ms")

# Write report
report = f"""# Evaluation v2 — 50 Random Questions
## Multi-strategy chunking + numberOfResults=15 + streaming

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Changes from v1:**
- Chunking: WHO=hierarchical (parent 1500, child 300), Clinical trials=semantic (max 512), ICD-11=no chunking
- numberOfResults: 5 -> 15
- Emergency lane: Vector KB only (no GraphRAG)
- Streaming endpoint: /api/chat/stream (SSE)
- Removed metadata filter

## Results

| Metric | v2 (this run) | v1 (900-question baseline) |
|---|---|---|
| Answered | {answered}/{total} ({answered/total*100:.1f}%) | 813/900 (90.3%) |
| Refused | {refused}/{total} ({refused/total*100:.1f}%) | 89/900 (9.9%) |
| Avg response time | {avg_ms:.0f} ms | 7,811 ms |
| Emergency avg | {em_avg:.0f} ms | 5,825 ms |
| General avg | {gen_avg:.0f} ms | 9,761 ms |
| Emergency SLA (<=5s) | {em_sla}/{len(em_times)} ({em_sla/len(em_times)*100:.1f}% if em_times else 'N/A') | 74/446 (16.6%) |
| General SLA (<=15s) | {gen_sla}/{len(gen_times)} ({gen_sla/len(gen_times)*100:.1f}% if gen_times else 'N/A') | 454/454 (100%) |
| Avg citations | {avg_citations:.1f} | 5.2 |
| p50 | {p50} ms | 7,490 ms |
| p95 | {p95} ms | 11,380 ms |

## Sample Answers

"""

for r in results[:10]:
    status = "ANSWERED" if r["answered"] else ("REFUSED" if r["refused"] else "ERROR")
    report += f"**[{r['id']}] {r['type']}** ({r['ms']}ms, {status})\n"
    report += f"> {r['question']}\n\n"
    report += f"{r['answer_preview'][:300]}...\n\n---\n\n"

Path(OUTPUT_FILE).write_text(report, encoding="utf-8")
print(f"\nReport saved to {OUTPUT_FILE}")
