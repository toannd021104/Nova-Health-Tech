"""Create a minimal synthetic distillation dataset to test the SageMaker pipeline.
20 records — enough to validate upload + training job submission without needing HF_TOKEN.
"""
import json, random, pathlib

SYSTEM = """You are an AI clinical assistant for internal use by licensed clinicians at Nova Health Tech's partner hospitals.

Rules that apply to every answer:
- Ground every clinical claim in the retrieved context; cite sources with [1], [2] tags.
- If the retrieved context does not contain the answer, say so plainly and do not guess.
- Write for a clinician: precise, concise, plain English.
- Always end with a clear "Recommendation:" line and, when relevant, a "Caveat:" line.
"""

SAMPLES = [
    ("emergency", "Patient SpO2 82% on room air with severe COVID-19. What treatment does WHO recommend immediately?",
     "Based on WHO guidelines [1], for severe COVID-19 with SpO2 <90%, immediate supplemental oxygen is indicated targeting SpO2 ≥94%. Prone positioning should be initiated if available. Dexamethasone 6mg/day for up to 10 days is recommended for patients requiring oxygen [2].\n\nRecommendation: Start supplemental oxygen immediately, initiate prone positioning, administer dexamethasone 6mg IV/PO daily.\nCaveat: Remdesivir may be considered if within 10 days of symptom onset and no renal impairment."),
    ("cardiology-internal", "Patient with HFrEF EF 25%. What is the evidence-based quadruple therapy?",
     "For HFrEF with EF 25%, guideline-directed medical therapy (GDMT) includes four pillars [1][2]: (1) ACE inhibitor or ARNi (sacubitril/valsartan preferred if tolerated), (2) beta-blocker (carvedilol, metoprolol succinate, or bisoprolol), (3) MRA (spironolactone or eplerenone), (4) SGLT2 inhibitor (dapagliflozin or empagliflozin).\n\nRecommendation: Initiate all four drug classes at low doses and uptitrate to target doses as tolerated. Monitor renal function and potassium.\nCaveat: Sacubitril/valsartan requires 36-hour washout from ACE inhibitor before initiation."),
    ("nephrology", "AKI stage 2 post-contrast. Fluid resuscitation and monitoring?",
     "For contrast-induced AKI stage 2 [1], isotonic saline (0.9% NaCl) at 1-1.5 mL/kg/hr for 6-12 hours pre- and post-procedure is the primary prevention. For established AKI, avoid nephrotoxins, hold NSAIDs and ACE inhibitors, and monitor urine output hourly [2].\n\nRecommendation: IV isotonic saline 1 mL/kg/hr, strict fluid balance, daily creatinine and electrolytes, nephrology consult if no improvement in 48 hours.\nCaveat: N-acetylcysteine is no longer routinely recommended per current guidelines."),
    ("endocrinology", "Type 2 diabetes HbA1c 9.5% on metformin. Add-on therapy options?",
     "For HbA1c 9.5% on metformin monotherapy [1], add-on therapy should be guided by comorbidities: (1) SGLT2 inhibitor if established CVD or CKD (eGFR >30), (2) GLP-1 RA if obesity or CVD risk, (3) DPP-4 inhibitor if tolerability is a concern, (4) insulin if symptomatic hyperglycemia [2].\n\nRecommendation: Add SGLT2 inhibitor (empagliflozin 10mg or dapagliflozin 10mg) as first choice given cardiovascular and renal benefits.\nCaveat: Check eGFR before initiating SGLT2 inhibitor; avoid if eGFR <30."),
    ("neurology", "Acute ischemic stroke NIHSS 12, onset 3 hours ago. tPA eligibility?",
     "For acute ischemic stroke with NIHSS 12 and onset 3 hours ago [1], IV alteplase (tPA) 0.9 mg/kg (max 90 mg) is indicated within 4.5 hours of onset if no contraindications. Key exclusions: recent surgery, active bleeding, BP >185/110 mmHg uncontrolled, INR >1.7, platelet <100k [2].\n\nRecommendation: Administer IV alteplase 0.9 mg/kg (10% bolus, 90% over 60 min) after ruling out contraindications. Activate stroke team and consider mechanical thrombectomy if large vessel occlusion.\nCaveat: BP must be <185/110 mmHg before and during tPA administration."),
]

# Expand to 20 records by repeating with slight variation
records = []
for dept, q, a in SAMPLES * 4:
    records.append({
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": q},
            {"role": "assistant", "content": a},
        ],
        "department": dept,
    })

out = pathlib.Path("data/distillation/phase1.jsonl")
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"Created {out} with {len(records)} records (synthetic test data)")
print("NOTE: Replace with real data by running generate_distillation_data.py with HF_TOKEN set")
