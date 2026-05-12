"""Quick smoke test of the deployed web app."""
import json
import time
import urllib.request

BASE = "http://47.130.120.152"

def test(label, message, emergency=False):
    url = f"{BASE}/api/chat"
    body = json.dumps({"message": message, "emergency": emergency}).encode()
    req = urllib.request.Request(
        url, data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
        elapsed = time.time() - t0

    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"  Time: {elapsed:.2f}s  |  Lane: {data['route']['lane']}  |  Dept: {data['route']['department']}")
    print(f"  Citations: {len(data['citations'])}")
    print(f"  Answer:")
    for line in data["answer"][:800].split("\n"):
        print(f"    {line}")
    if data["citations"]:
        print(f"  Top citation: {data['citations'][0]['source'][:80]}")

# Healthz
with urllib.request.urlopen(f"{BASE}/healthz", timeout=5) as r:
    print("Healthz:", json.loads(r.read()))

# Case 1: Emergency
test(
    "CASE 1 — Emergency (COVID-19 oxygen)",
    "Patient with severe COVID-19, SpO2 88% on room air. What oxygen target and treatment does WHO recommend?",
    emergency=True
)

# Case 2: Complex
test(
    "CASE 2 — Complex (COVID-19 treatment protocol)",
    "According to WHO guidelines, what is the recommended treatment for hospitalised adult with severe COVID-19 requiring supplemental oxygen? Include drug names and evidence grading.",
    emergency=False
)
