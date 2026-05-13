"""Test streaming TTFT for both emergency and general lanes.

Measures:
- Pre-generate time (from route event)
- TTFT (time to first token from request start)
- Total time
- Token counts

Usage:
    python scripts/test_streaming_ttft.py
"""
import json
import time
import requests

BASE_URL = "http://47.130.120.152"

EMERGENCY_QUESTIONS = [
    "Patient presenting with acute chest pain, diaphoresis, ST elevation in leads II, III, aVF. What is the immediate management?",
    "Severe anaphylaxis after penicillin injection, BP 60/40, airway swelling. What do I do?",
    "Child 3yo, febrile seizure lasting 8 minutes, still seizing. Protocol?",
    "COVID-19 patient SpO2 78% on room air, respiratory rate 36. Immediate steps?",
    "Suspected septic shock, lactate 6.2, MAP 55 despite 2L crystalloid. Next actions?",
    "Massive upper GI bleed, hematemesis 500ml, HR 130, BP 80/50. Emergency protocol?",
    "Acute stroke symptoms onset 45 minutes ago, NIHSS 18. What is the protocol?",
    "Severe COVID pneumonia requiring intubation. What ventilator settings and medications?",
    "Patient with COVID-19 developing acute kidney injury, creatinine rising rapidly. Emergency management?",
    "Pregnant patient 34 weeks with severe pre-eclampsia, BP 180/110, headache. Immediate management?",
]

GENERAL_QUESTIONS = [
    "What are the WHO recommendations for corticosteroid use in severe COVID-19?",
    "Summarize the evidence for baricitinib in hospitalized COVID-19 patients.",
    "What is the recommended anticoagulation strategy for COVID-19 patients?",
    "What does the WHO guideline say about remdesivir for COVID-19 treatment?",
    "Explain the GRADE evidence assessment for IL-6 receptor blockers in COVID-19.",
    "What are the WHO recommendations for oxygen therapy in COVID-19?",
    "How should COVID-19 be managed in immunocompromised patients according to WHO?",
    "What is the role of convalescent plasma in COVID-19 treatment per WHO guidelines?",
    "Describe the WHO severity classification for COVID-19.",
    "What are the drug interactions to consider when treating COVID-19 with antivirals?",
]


def test_stream(question: str, emergency: bool) -> dict:
    """Send a streaming request and measure timing."""
    t0 = time.time()
    ttft = None
    full_text = ""
    route_data = {}
    usage = {}
    citations = []

    resp = requests.post(
        f"{BASE_URL}/api/chat/stream",
        json={"message": question, "emergency": emergency},
        stream=True,
        timeout=30,
    )
    resp.raise_for_status()

    event_type = ""
    for line in resp.iter_lines(decode_unicode=True):
        if not line:
            continue
        if line.startswith("event: "):
            event_type = line[7:].strip()
        elif line.startswith("data: ") and event_type:
            data = json.loads(line[6:])
            if event_type == "route":
                route_data = data
            elif event_type == "token":
                if ttft is None:
                    ttft = time.time() - t0
                full_text += data.get("text", "")
            elif event_type == "done":
                usage = data.get("usage", {})
                citations = data.get("citations", [])
            elif event_type == "error":
                print(f"  ERROR: {data.get('error')}")
            event_type = ""

    total = time.time() - t0
    return {
        "question": question[:60] + "...",
        "emergency": emergency,
        "lane": route_data.get("lane", "?"),
        "department": route_data.get("badge", "?"),
        "pre_gen_ms": route_data.get("preGenMs", 0),
        "retrieve_ms": route_data.get("retrieveMs", 0),
        "ttft_ms": int(ttft * 1000) if ttft else None,
        "total_ms": int(total * 1000),
        "input_tokens": usage.get("inputTokens", 0),
        "output_tokens": usage.get("outputTokens", 0),
        "answer_len": len(full_text),
        "num_citations": len(citations),
        "sla_pass": (ttft * 1000 <= 5000 if emergency else total * 1000 <= 15000) if ttft else False,
    }


def main():
    print("=" * 80)
    print("STREAMING TTFT TEST")
    print(f"Endpoint: {BASE_URL}/api/chat/stream")
    print("=" * 80)

    results = []

    print("\n--- EMERGENCY LANE (SLA: TTFT <= 5s) ---\n")
    for q in EMERGENCY_QUESTIONS:
        r = test_stream(q, emergency=True)
        results.append(r)
        sla = "PASS" if r["sla_pass"] else "FAIL"
        print(f"  [{sla}] TTFT={r['ttft_ms']}ms | Total={r['total_ms']}ms | "
              f"PreGen={r['pre_gen_ms']}ms | Retrieve={r['retrieve_ms']}ms | "
              f"Tokens: {r['input_tokens']}in/{r['output_tokens']}out")
        time.sleep(1)

    print("\n--- GENERAL LANE (SLA: Total <= 15s) ---\n")
    for q in GENERAL_QUESTIONS:
        r = test_stream(q, emergency=False)
        results.append(r)
        sla = "PASS" if r["sla_pass"] else "FAIL"
        print(f"  [{sla}] TTFT={r['ttft_ms']}ms | Total={r['total_ms']}ms | "
              f"PreGen={r['pre_gen_ms']}ms | Retrieve={r['retrieve_ms']}ms | "
              f"Tokens: {r['input_tokens']}in/{r['output_tokens']}out")
        time.sleep(1)

    # Summary
    emerg = [r for r in results if r["emergency"]]
    general = [r for r in results if not r["emergency"]]

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    if emerg:
        avg_ttft = sum(r["ttft_ms"] for r in emerg if r["ttft_ms"]) / len(emerg)
        avg_total = sum(r["total_ms"] for r in emerg) / len(emerg)
        sla_pass = sum(1 for r in emerg if r["sla_pass"])
        print(f"  Emergency: avg TTFT={avg_ttft:.0f}ms, avg Total={avg_total:.0f}ms, SLA pass={sla_pass}/{len(emerg)}")
    if general:
        avg_ttft = sum(r["ttft_ms"] for r in general if r["ttft_ms"]) / len(general)
        avg_total = sum(r["total_ms"] for r in general) / len(general)
        sla_pass = sum(1 for r in general if r["sla_pass"])
        print(f"  General:   avg TTFT={avg_ttft:.0f}ms, avg Total={avg_total:.0f}ms, SLA pass={sla_pass}/{len(general)}")


if __name__ == "__main__":
    main()
