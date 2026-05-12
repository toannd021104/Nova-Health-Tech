import csv

with open("docs/test_questions_800.csv", "r", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

total = len(rows)
general = [r for r in rows if r["type"] == "general"]
emergency = [r for r in rows if r["type"] == "emergency"]
new_general = [r for r in rows if 801 <= int(r["id"]) <= 850]
new_emergency = [r for r in rows if 851 <= int(r["id"]) <= 900]

print(f"Total questions: {total}")
print(f"General: {len(general)}")
print(f"Emergency: {len(emergency)}")
print(f"IDs 801-850 count: {len(new_general)}, types: {set(r['type'] for r in new_general)}")
print(f"IDs 851-900 count: {len(new_emergency)}, types: {set(r['type'] for r in new_emergency)}")
print()
print("Sample new questions:")
for r in rows[800:803]:
    print(f"  {r['id']} [{r['type']}]: {r['question'][:90]}")
for r in rows[850:853]:
    print(f"  {r['id']} [{r['type']}]: {r['question'][:90]}")
