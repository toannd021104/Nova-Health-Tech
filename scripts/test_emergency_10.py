import json, time, urllib.request, random, csv

random.seed(99)
questions = list(csv.DictReader(open("docs/test_questions_800.csv", encoding="utf-8")))
emergency_qs = [q for q in questions if q["type"] == "emergency"]
sample = random.sample(emergency_qs, 10)

print("Testing 10 emergency questions (top-5 retrieval):")
times = []
for i, row in enumerate(sample, 1):
    payload = json.dumps({"message": row["question"], "emergency": True}).encode()
    req = urllib.request.Request("http://47.130.120.152/api/chat", data=payload, headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    ms = int((time.time() - t0) * 1000)
    times.append(ms)
    sla = "PASS" if ms <= 5000 else "FAIL"
    q_short = row["question"][:70]
    print(f"  [{i}] {ms}ms {sla} | {q_short}")
    time.sleep(1)

avg = sum(times) / len(times)
sla_pass = sum(1 for t in times if t <= 5000)
print(f"\nAvg: {avg:.0f}ms | SLA pass: {sla_pass}/10 ({sla_pass*10}%)")
print(f"Min: {min(times)}ms | Max: {max(times)}ms")
