import csv
from collections import Counter
from pathlib import Path

p = Path("docs/eval_results_900.csv")
rows = list(csv.DictReader(p.open(encoding="utf-8")))

total = len(rows)
answered = sum(1 for r in rows if r["answered"] == "True")
refused = sum(1 for r in rows if r["refused"] == "True")

emergency = [r for r in rows if r["type"] == "emergency"]
general = [r for r in rows if r["type"] == "general"]
who_q = [r for r in rows if int(r["id"]) <= 800]
pmc_q = [r for r in rows if int(r["id"]) > 800]

def avg_ms(lst):
    times = [int(r["response_time_ms"]) for r in lst if r["response_time_ms"]]
    return sum(times) / len(times) if times else 0

def sla_pass(lst, threshold):
    return sum(1 for r in lst if int(r["response_time_ms"]) <= threshold)

def ans_pct(lst):
    return sum(1 for r in lst if r["answered"] == "True") / len(lst) * 100 if lst else 0

def ref_pct(lst):
    return sum(1 for r in lst if r["refused"] == "True") / len(lst) * 100 if lst else 0

dept_counter = Counter(r["department"] for r in rows if r["department"])
top_depts = dept_counter.most_common(10)

citations = [int(r["num_citations"]) for r in rows if r["num_citations"]]
avg_citations = sum(citations) / len(citations) if citations else 0
zero_citations = sum(1 for c in citations if c == 0)

times = sorted([int(r["response_time_ms"]) for r in rows if r["response_time_ms"]])
p50 = times[len(times) // 2]
p95 = times[int(len(times) * 0.95)]
p99 = times[int(len(times) * 0.99)]

print(f"total={total}")
print(f"answered={answered} ({answered/total*100:.1f}%)")
print(f"refused={refused} ({refused/total*100:.1f}%)")
print(f"em_total={len(emergency)}")
print(f"em_answered={ans_pct(emergency):.1f}%")
print(f"em_refused={ref_pct(emergency):.1f}%")
print(f"em_avg_ms={avg_ms(emergency):.0f}")
print(f"em_sla_pass={sla_pass(emergency,5000)}/{len(emergency)} ({sla_pass(emergency,5000)/len(emergency)*100:.1f}%)")
print(f"gen_total={len(general)}")
print(f"gen_answered={ans_pct(general):.1f}%")
print(f"gen_refused={ref_pct(general):.1f}%")
print(f"gen_avg_ms={avg_ms(general):.0f}")
print(f"gen_sla_pass={sla_pass(general,15000)}/{len(general)} ({sla_pass(general,15000)/len(general)*100:.1f}%)")
print(f"who_answered={ans_pct(who_q):.1f}%")
print(f"who_refused={ref_pct(who_q):.1f}%")
print(f"pmc_answered={ans_pct(pmc_q):.1f}%")
print(f"pmc_refused={ref_pct(pmc_q):.1f}%")
print(f"avg_citations={avg_citations:.1f}")
print(f"zero_citations={zero_citations} ({zero_citations/total*100:.1f}%)")
print(f"p50={p50}")
print(f"p95={p95}")
print(f"p99={p99}")
print("top_depts:")
for dept, count in top_depts:
    print(f"  {dept}: {count}")
