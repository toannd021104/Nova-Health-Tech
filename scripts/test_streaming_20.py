"""Test 20 questions (10 emergency + 10 general) via streaming endpoint.
Measures actual TTFT (time to first token) and total time."""
import csv
import json
import random
import time
import requests
from pathlib import Path

API_URL = "http://47.130.120.152/api/chat/stream"
INPUT_CSV = "docs/test_questions_800.csv"

random.seed(2026)
questions = list(csv.DictReader(open(INPUT_CSV, encoding="utf-8")))
emergency_qs = [q for q in questions if q["type"] == "emergency"]
general_qs = [q for q in questions if q["type"] == "general"]

sample = random.sample(emergency_qs, 10) + random.sample(general_qs, 10)
random.shuffle(sample)

print("Testing 20 questions via /api/chat/stream (SSE)")
print("Measuring TTFT (time to first token) + total time")
print("-" * 70)

results = []

for i, row in enumerate(sample, 1):
    q_id = row["id"]
    q_type = row["type"]
    question = row["question"]
    is_emergency = q_type == "emergency"

    payload = json.dumps({"message": question, "emergency": is_emergency})

    t_start = time.time()
    t_first_token = None
    full_text = ""
    citations = []
    route_info = {}

    try:
        resp = requests.post(API_URL, data=payload, headers={"Content-Type": "application/json"}, stream=True, timeout=60)

        if resp.status_code != 200:
            results.append({"id": q_id, "type": q_type, "ttft_ms": 0, "total_ms": 0, "error": f"HTTP {resp.status_code}"})
            print(f"  [{i}] ERROR HTTP {resp.status_code}")
            continue

        event_type = ""
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            if line.startswith("event: "):
                event_type = line[7:].strip()
            elif line.startswith("data: "):
                data = json.loads(line[6:])
                now = time.time()

                if event_type == "route":
                    route_info = data
                elif event_type == "token":
                    if t_first_token is None:
                        t_first_token = now
                    full_text += data.get("text", "")
                elif event_type == "done":
                    citations = data.get("citations", [])
                elif event_type == "error":
                    full_text = f"ERROR: {data.get('error', 'unknown')}"

        t_end = time.time()
        ttft_ms = int((t_first_token - t_start) * 1000) if t_first_token else 0
        total_ms = int((t_end - t_start) * 1000)

        results.append({
            "id": q_id,
            "type": q_type,
            "ttft_ms": ttft_ms,
            "total_ms": total_ms,
            "citations": len(citations),
            "answer_len": len(full_text),
            "lane": route_info.get("lane", ""),
            "dept": route_info.get("department", ""),
        })

        sla_ttft = 2000 if is_emergency else 4000
        sla_status = "PASS" if ttft_ms <= sla_ttft else "FAIL"
        print(f"  [{i:2}] {q_type:9} TTFT={ttft_ms:5}ms total={total_ms:5}ms {sla_status} | {question[:55]}...")

    except Exception as e:
        total_ms = int((time.time() - t_start) * 1000)
        results.append({"id": q_id, "type": q_type, "ttft_ms": 0, "total_ms": total_ms, "error": str(e)})
        print(f"  [{i:2}] ERROR: {e}")

    time.sleep(1)

# Summary
print("\n" + "=" * 70)
print("STREAMING TEST RESULTS")
print("=" * 70)

em_results = [r for r in results if r["type"] == "emergency" and "error" not in r]
gen_results = [r for r in results if r["type"] == "general" and "error" not in r]

if em_results:
    em_ttft = [r["ttft_ms"] for r in em_results]
    em_total = [r["total_ms"] for r in em_results]
    em_sla = sum(1 for t in em_ttft if t <= 2000)
    print(f"\nEmergency (n={len(em_results)}):")
    print(f"  TTFT avg:  {sum(em_ttft)//len(em_ttft)} ms")
    print(f"  TTFT min:  {min(em_ttft)} ms")
    print(f"  TTFT max:  {max(em_ttft)} ms")
    print(f"  TTFT SLA (<=2s): {em_sla}/{len(em_results)} ({em_sla/len(em_results)*100:.0f}%)")
    print(f"  Total avg: {sum(em_total)//len(em_total)} ms")
    print(f"  Total SLA (<=5s): {sum(1 for t in em_total if t<=5000)}/{len(em_results)}")

if gen_results:
    gen_ttft = [r["ttft_ms"] for r in gen_results]
    gen_total = [r["total_ms"] for r in gen_results]
    gen_sla = sum(1 for t in gen_ttft if t <= 4000)
    print(f"\nGeneral (n={len(gen_results)}):")
    print(f"  TTFT avg:  {sum(gen_ttft)//len(gen_ttft)} ms")
    print(f"  TTFT min:  {min(gen_ttft)} ms")
    print(f"  TTFT max:  {max(gen_ttft)} ms")
    print(f"  TTFT SLA (<=4s): {gen_sla}/{len(gen_results)} ({gen_sla/len(gen_results)*100:.0f}%)")
    print(f"  Total avg: {sum(gen_total)//len(gen_total)} ms")
    print(f"  Total SLA (<=15s): {sum(1 for t in gen_total if t<=15000)}/{len(gen_results)}")

all_ttft = [r["ttft_ms"] for r in results if "error" not in r]
all_total = [r["total_ms"] for r in results if "error" not in r]
if all_ttft:
    print(f"\nOverall (n={len(all_ttft)}):")
    print(f"  TTFT avg: {sum(all_ttft)//len(all_ttft)} ms")
    print(f"  Total avg: {sum(all_total)//len(all_total)} ms")

print("\nDone.")
