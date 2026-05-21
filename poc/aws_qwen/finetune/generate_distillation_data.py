"""Generate distillation dataset using Qwen3.5-397B-A17B (teacher) via HuggingFace Inference Providers.

Teacher: Qwen/Qwen3.5-397B-A17B (397B total, 17B active MoE)
Provider: DeepInfra (cheapest, $0.54/1M in, $3.40/1M out) via HuggingFace InferenceClient
Fallback: Together.ai ($0.60/1M in, $3.60/1M out)

This uses the HuggingFace `huggingface_hub` InferenceClient which routes to
the provider transparently — OpenAI-compatible, no separate API key needed
beyond a HuggingFace token with billing enabled.

Usage:
    # Phase 1 — 4000 Q&A, ~30 min fine-tune
    python poc/aws_qwen/finetune/generate_distillation_data.py \\
        --phase 1 --output data/distillation/phase1.jsonl

    # Phase 2 — 10000 Q&A, full fine-tune
    python poc/aws_qwen/finetune/generate_distillation_data.py \\
        --phase 2 --output data/distillation/phase2.jsonl

Requires:
    pip install huggingface_hub>=0.24
    export HF_TOKEN=hf_...   (HuggingFace token with billing enabled)

Cost estimate:
    4000 Q&A x ~800 tokens avg x $0.54/1M input + $3.40/1M output ~ $1.73
    10000 Q&A ~ $4.33

Each output line is JSONL in ChatML / TRL SFTTrainer format:
    {"messages": [{"role": "system", ...}, {"role": "user", ...}, {"role": "assistant", ...}]}
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import time
from pathlib import Path

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Teacher: Qwen3.5-397B-A17B via DeepInfra (cheapest provider, live on HF)
TEACHER_MODEL = "Qwen/Qwen3.5-397B-A17B"
TEACHER_PROVIDER = "deepinfra"   # fallback: "together" or "novita"

SYSTEM_PROMPT = """You are an AI clinical assistant for internal use by licensed clinicians at Nova Health Tech's partner hospitals.

Rules:
- Ground every clinical claim in evidence; cite sources with [1], [2] tags when referencing guidelines.
- If you don't know, say so plainly and do not guess.
- Never include raw patient identifiers. Refer to patients as "the patient".
- Write for a clinician: precise, concise, plain English, no bedside softeners.
- When prescribing information is requested, include: drug, dose, route, frequency, duration, key contraindications, and one sentence on monitoring.
- Always end with a clear "Recommendation:" line and, when relevant, a "Caveat:" line.
"""

# ── Seed question templates per department ────────────────────────────────────
# Each entry: (department_label, question_template)
# Templates use {X} placeholders that get filled with random values.

_SEED_QUESTIONS: list[tuple[str, str]] = [
    # Emergency
    ("emergency", "Patient presents with SpO2 {spo2}% on room air and severe {condition}. What is the immediate management?"),
    ("emergency", "Adult patient with suspected sepsis: HR {hr}, BP {bp}, temp {temp}C. What is the sepsis bundle?"),
    ("emergency", "Patient with anaphylaxis after {allergen} exposure. What is the first-line treatment and dose?"),
    ("emergency", "Trauma patient: GCS {gcs}, BP {bp}, HR {hr}. What is the primary survey priority?"),
    ("emergency", "Patient with STEMI on ECG. Door-to-balloon time target and immediate steps?"),
    ("emergency", "Child {age} years old with febrile seizure lasting {duration} minutes. Management?"),
    ("emergency", "Patient with acute stroke symptoms onset {hours} hours ago. tPA eligibility criteria?"),
    ("emergency", "Diabetic patient with blood glucose {glucose} mmol/L, altered consciousness. Management?"),
    ("emergency", "Patient with suspected pulmonary embolism: HR {hr}, SpO2 {spo2}%. Immediate workup?"),
    ("emergency", "Overdose with {drug}. What are the antidote and supportive measures?"),

    # Cardiology
    ("cardiology-internal", "Patient with HFrEF EF {ef}%. What is the evidence-based quadruple therapy?"),
    ("cardiology-internal", "NSTEMI patient: troponin rising, no ST elevation. Anticoagulation strategy?"),
    ("cardiology-internal", "Patient with new-onset AF with RVR HR {hr}. Rate control vs rhythm control decision?"),
    ("cardiology-internal", "Patient on warfarin INR {inr}. What is the reversal strategy for urgent surgery?"),
    ("cardiology-internal", "Hypertensive emergency BP {bp}. Target BP reduction in first hour?"),
    ("cardiology-internal", "Patient with complete heart block. Temporary pacing indications?"),
    ("cardiology-internal", "Post-MI patient: when to start beta-blocker and ACE inhibitor?"),
    ("cardiology-internal", "Patient with aortic stenosis AVA {ava} cm2. TAVR vs SAVR decision criteria?"),

    # Pulmonology
    ("pulmonology", "COPD exacerbation: FEV1 {fev1}% predicted. Steroid dose and duration?"),
    ("pulmonology", "Severe asthma attack not responding to salbutamol. Next step?"),
    ("pulmonology", "Community-acquired pneumonia CURB-65 score {score}. Inpatient vs outpatient decision?"),
    ("pulmonology", "Patient with suspected PE: Wells score {wells}. D-dimer vs CTPA decision?"),
    ("pulmonology", "Patient on {fio2}% FiO2 with PaO2 {pao2} mmHg. ARDS Berlin criteria?"),
    ("pulmonology", "Lung cancer screening criteria: age {age}, pack-year history {packs}?"),
    ("pulmonology", "Patient with pleural effusion: Light's criteria for exudate vs transudate?"),
    ("pulmonology", "OSA patient: AHI {ahi}. CPAP titration starting pressure?"),

    # Gastroenterology
    ("gastroenterology", "Upper GI bleed: Rockall score {score}. Endoscopy timing?"),
    ("gastroenterology", "Crohn's disease flare: CRP {crp}, albumin {alb}. Steroid vs biologic decision?"),
    ("gastroenterology", "Acute pancreatitis: Ranson score {score}. ICU admission criteria?"),
    ("gastroenterology", "H. pylori positive: first-line eradication regimen in high-clarithromycin-resistance area?"),
    ("gastroenterology", "Cirrhosis patient with ascites: SBP prophylaxis criteria?"),
    ("gastroenterology", "Hepatic encephalopathy grade {grade}. Lactulose dosing and precipitant workup?"),
    ("gastroenterology", "Ulcerative colitis: Mayo score {score}. Step-up therapy decision?"),

    # Nephrology
    ("nephrology", "AKI stage {stage} post-contrast. Fluid resuscitation and monitoring?"),
    ("nephrology", "CKD stage {stage}: eGFR {egfr} mL/min. Metformin dose adjustment?"),
    ("nephrology", "Hyperkalemia K+ {k} mmol/L with ECG changes. Emergency management?"),
    ("nephrology", "Hyponatremia Na+ {na} mmol/L, symptomatic. Correction rate and target?"),
    ("nephrology", "Dialysis patient with missed session: fluid overload management?"),
    ("nephrology", "Vancomycin dosing in patient with eGFR {egfr} mL/min?"),
    ("nephrology", "Contrast nephropathy prevention in patient with eGFR {egfr}?"),

    # Endocrinology
    ("endocrinology", "Type 2 diabetes HbA1c {hba1c}%. Add-on therapy after metformin failure?"),
    ("endocrinology", "DKA: pH {ph}, glucose {glucose} mmol/L. Insulin infusion protocol?"),
    ("endocrinology", "Hypothyroidism TSH {tsh}. Levothyroxine starting dose by weight?"),
    ("endocrinology", "Adrenal crisis: cortisol {cortisol}. Hydrocortisone dose and route?"),
    ("endocrinology", "Hypercalcemia Ca2+ {ca} mmol/L. Bisphosphonate vs calcitonin decision?"),
    ("endocrinology", "Gestational diabetes: fasting glucose {glucose}. Insulin vs metformin?"),
    ("endocrinology", "Thyroid storm: Burch-Wartofsky score {score}. Management protocol?"),

    # Neurology
    ("neurology", "Acute ischemic stroke: NIHSS {nihss}, onset {hours} hours. tPA eligibility?"),
    ("neurology", "Status epilepticus: benzodiazepine failed. Second-line agent and dose?"),
    ("neurology", "Thunderclap headache: LP xanthochromia positive. Next step?"),
    ("neurology", "Guillain-Barre: FVC {fvc}% predicted. Intubation threshold?"),
    ("neurology", "Parkinson's disease: motor fluctuations on levodopa. Adjunct therapy?"),
    ("neurology", "Meningitis: CSF WBC {wbc}, protein {protein}. Empiric antibiotic choice?"),
    ("neurology", "Myasthenic crisis: bulbar symptoms. Plasmapheresis vs IVIG decision?"),

    # Infectious Disease
    ("infectious-disease", "Septic shock: source unknown. Empiric antibiotic coverage?"),
    ("infectious-disease", "HIV patient CD4 {cd4}: opportunistic infection prophylaxis?"),
    ("infectious-disease", "MDR-TB: rifampicin resistant. Second-line regimen?"),
    ("infectious-disease", "Neutropenic fever: ANC {anc}. Empiric antifungal threshold?"),
    ("infectious-disease", "COVID-19 severe: SpO2 {spo2}%. Dexamethasone and remdesivir criteria?"),
    ("infectious-disease", "Clostridium difficile: WBC {wbc}, creatinine {cr}. Fidaxomicin vs vancomycin?"),
    ("infectious-disease", "Endocarditis: Duke criteria {major} major, {minor} minor. Antibiotic duration?"),

    # Oncology
    ("oncology-chemo", "NSCLC stage {stage}: PD-L1 {pdl1}%. First-line immunotherapy decision?"),
    ("oncology-chemo", "Febrile neutropenia: ANC {anc}, temp {temp}C. MASCC score and management?"),
    ("oncology-chemo", "Cisplatin-based regimen: creatinine {cr}. Dose reduction threshold?"),
    ("oncology-chemo", "Immune checkpoint inhibitor: grade {grade} colitis. Steroid protocol?"),
    ("oncology-chemo", "Breast cancer ER+/HER2-: adjuvant endocrine therapy duration?"),
    ("oncology-chemo", "Tumor lysis syndrome: uric acid {ua}, creatinine {cr}. Rasburicase criteria?"),

    # Obstetrics
    ("obstetrics", "Pre-eclampsia: BP {bp}, proteinuria {protein}g/24h. Delivery decision?"),
    ("obstetrics", "PPH: blood loss {loss}mL. Oxytocin vs carboprost decision?"),
    ("obstetrics", "Gestational diabetes: fasting {fasting}, 2h {twoh} mmol/L. Insulin threshold?"),
    ("obstetrics", "Preterm labor at {weeks} weeks: tocolysis and steroid protocol?"),
    ("obstetrics", "HELLP syndrome: platelets {plt}. Delivery timing?"),
    ("obstetrics", "Eclampsia: magnesium sulfate loading dose and maintenance?"),

    # Pediatrics
    ("pediatrics", "Pediatric sepsis: weight {weight}kg, HR {hr}, BP {bp}. Fluid bolus protocol?"),
    ("pediatrics", "Neonatal jaundice: bilirubin {bili} at {hours} hours of life. Phototherapy threshold?"),
    ("pediatrics", "Pediatric DKA: pH {ph}, glucose {glucose}. Fluid and insulin protocol?"),
    ("pediatrics", "Febrile infant {age} days old: lumbar puncture decision criteria?"),
    ("pediatrics", "Bronchiolitis: SpO2 {spo2}%, age {age} months. Admission criteria?"),
    ("pediatrics", "Pediatric status epilepticus: weight {weight}kg. Diazepam dose?"),

    # Radiology
    ("radiology", "Chest X-ray: bilateral infiltrates, fever, SpO2 {spo2}%. Differential diagnosis?"),
    ("radiology", "CT head: hyperdense lesion in {location}. Hemorrhage vs calcification?"),
    ("radiology", "Abdominal CT: free air under diaphragm. Surgical emergency criteria?"),
    ("radiology", "MRI brain: DWI restriction in {territory}. Stroke vs mimics?"),
    ("radiology", "Chest CT: pulmonary nodule {size}mm. Fleischner Society follow-up?"),
    ("radiology", "Ultrasound: gallbladder wall {thickness}mm, pericholecystic fluid. Cholecystitis criteria?"),
]

# Random value pools for template filling
_POOLS: dict[str, list] = {
    "spo2": [72, 78, 82, 85, 88, 90, 92],
    "condition": ["COVID-19", "pneumonia", "ARDS", "pulmonary edema", "asthma"],
    "hr": [45, 55, 110, 120, 130, 140, 150],
    "bp": ["80/50", "90/60", "180/110", "200/120", "220/130"],
    "temp": [36.0, 38.5, 39.0, 39.5, 40.0, 40.5],
    "allergen": ["penicillin", "shellfish", "latex", "bee sting", "peanuts"],
    "gcs": [6, 8, 10, 12, 14],
    "duration": [5, 10, 15, 20, 30],
    "hours": [1, 2, 3, 4, 5, 6, 8, 12, 24],
    "glucose": [2.5, 3.0, 18.0, 22.0, 28.0, 35.0, 45.0],
    "drug": ["paracetamol", "tricyclic antidepressant", "opioid", "benzodiazepine", "aspirin"],
    "ef": [15, 20, 25, 30, 35, 40],
    "inr": [3.5, 4.0, 5.0, 6.0, 8.0, 10.0],
    "ava": [0.6, 0.7, 0.8, 0.9, 1.0],
    "fev1": [25, 30, 40, 50, 60],
    "score": [0, 1, 2, 3, 4, 5, 6],
    "wells": [1, 2, 3, 4, 5, 6],
    "fio2": [40, 60, 80, 100],
    "pao2": [45, 55, 60, 70, 80],
    "ahi": [15, 20, 30, 40, 50],
    "crp": [50, 100, 150, 200],
    "alb": [25, 28, 30, 32, 35],
    "grade": [1, 2, 3, 4],
    "stage": [1, 2, 3, 4],
    "egfr": [10, 15, 20, 30, 45, 60],
    "k": [5.5, 6.0, 6.5, 7.0, 7.5],
    "na": [115, 118, 120, 122, 125],
    "hba1c": [7.5, 8.0, 8.5, 9.0, 10.0, 11.0],
    "ph": [6.9, 7.0, 7.1, 7.2, 7.3],
    "tsh": [0.01, 0.05, 8.0, 15.0, 50.0],
    "cortisol": [50, 100, 150, 200],
    "ca": [2.8, 3.0, 3.2, 3.5, 3.8],
    "nihss": [4, 8, 12, 16, 20],
    "fvc": [40, 50, 60, 70],
    "wbc": [2000, 5000, 10000, 20000, 30000],
    "protein": [0.5, 1.0, 2.0, 3.0, 5.0],
    "cd4": [50, 100, 150, 200, 350],
    "anc": [100, 200, 500, 1000],
    "cr": [100, 150, 200, 250, 300],
    "pdl1": [0, 1, 10, 50, 80],
    "ua": [600, 700, 800, 900, 1000],
    "loss": [500, 800, 1000, 1500, 2000],
    "fasting": [5.1, 5.5, 6.0, 6.5, 7.0],
    "twoh": [8.0, 8.5, 9.0, 10.0, 11.0],
    "weeks": [24, 26, 28, 30, 32, 34],
    "plt": [20000, 50000, 80000, 100000],
    "weight": [3, 5, 10, 15, 20, 30, 40],
    "bili": [150, 200, 250, 300, 350],
    "age": [1, 2, 3, 5, 7, 10, 14, 28, 60, 90],
    "location": ["basal ganglia", "thalamus", "cerebellum", "frontal lobe", "temporal lobe"],
    "territory": ["MCA", "PCA", "PICA", "ACA", "basilar"],
    "size": [4, 6, 8, 10, 12, 15, 20],
    "thickness": [3, 4, 5, 6, 7, 8],
    "packs": [20, 30, 40, 50],
    "minor": [0, 1, 2],
    "major": [1, 2],
    "minor_count": [1, 2, 3],
    "pao2": [45, 55, 60, 70],
}


def _fill_template(template: str) -> str:
    """Fill a question template with random values from the pools."""
    import re
    placeholders = re.findall(r"\{(\w+)\}", template)
    result = template
    for ph in placeholders:
        pool = _POOLS.get(ph, [ph])
        result = result.replace(f"{{{ph}}}", str(random.choice(pool)), 1)
    return result


def _generate_questions(n: int) -> list[tuple[str, str]]:
    """Generate n (department, question) pairs by sampling and filling templates."""
    questions = []
    # Ensure coverage across all departments
    per_dept = max(1, n // len(set(d for d, _ in _SEED_QUESTIONS)))
    dept_counts: dict[str, int] = {}

    while len(questions) < n:
        dept, template = random.choice(_SEED_QUESTIONS)
        count = dept_counts.get(dept, 0)
        if count >= per_dept * 3 and len(questions) < n * 0.9:
            continue  # avoid over-sampling one dept early
        q = _fill_template(template)
        questions.append((dept, q))
        dept_counts[dept] = count + 1

    return questions[:n]


def _call_teacher(client, question: str, department: str) -> str:
    """Call Qwen3.5-397B-A17B via HuggingFace InferenceClient (DeepInfra provider).

    Key notes from the model card:
    - Qwen3.5 thinks by default (<think>...</think> prefix)
    - We disable thinking for clean distillation data (instruct mode)
    - Recommended non-thinking params: temp=0.7, top_p=0.8, top_k=20, presence_penalty=1.5
    """
    dept_context = {
        "emergency": "You are an emergency medicine specialist.",
        "cardiology-internal": "You are a cardiologist.",
        "pulmonology": "You are a pulmonologist.",
        "gastroenterology": "You are a gastroenterologist.",
        "nephrology": "You are a nephrologist.",
        "endocrinology": "You are an endocrinologist.",
        "neurology": "You are a neurologist.",
        "infectious-disease": "You are an infectious disease specialist.",
        "oncology-chemo": "You are a medical oncologist.",
        "obstetrics": "You are an obstetrician.",
        "pediatrics": "You are a pediatrician.",
        "radiology": "You are a radiologist.",
    }.get(department, "You are a clinical specialist.")

    system = SYSTEM_PROMPT + f"\n{dept_context}"

    result = client.chat.completions.create(
        model=TEACHER_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": question},
        ],
        max_tokens=800,
        temperature=0.7,    # non-thinking mode recommended params
        top_p=0.8,
        extra_body={
            "top_k": 20,
            "presence_penalty": 1.5,
            # Disable thinking mode — we want clean answers, not <think> blocks
            "chat_template_kwargs": {"enable_thinking": False},
        },
    )
    answer = result.choices[0].message.content.strip()

    # Safety strip: remove any <think>...</think> block if thinking leaked through
    import re as _re
    answer = _re.sub(r"<think>[\s\S]*?</think>\s*", "", answer).strip()

    return answer


def generate(n: int, output_path: Path, resume: bool = True) -> None:
    """Generate n Q&A pairs using Qwen3.5-397B-A17B (DeepInfra) and write to output_path."""
    try:
        from huggingface_hub import InferenceClient  # noqa: PLC0415
    except ImportError:
        raise SystemExit("Install: pip install huggingface_hub>=0.24")

    hf_token = os.environ.get("HF_TOKEN", "")
    if not hf_token:
        raise SystemExit(
            "Set HF_TOKEN environment variable.\n"
            "Get one at https://huggingface.co/settings/tokens\n"
            "Requires billing enabled on your HF account for DeepInfra provider."
        )

    client = InferenceClient(
        provider=TEACHER_PROVIDER,
        api_key=hf_token,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Resume support
    existing = 0
    if resume and output_path.exists():
        with open(output_path, encoding="utf-8") as f:
            existing = sum(1 for _ in f)
        log.info("Resuming from %d existing records", existing)

    questions = _generate_questions(n)
    to_generate = questions[existing:]
    log.info("Generating %d Q&A pairs via %s/%s (skipping %d done)",
             len(to_generate), TEACHER_PROVIDER, TEACHER_MODEL, existing)

    errors = 0
    with open(output_path, "a", encoding="utf-8") as f:
        for i, (dept, question) in enumerate(to_generate, start=existing + 1):
            try:
                answer = _call_teacher(client, question, dept)
                record = {
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": question},
                        {"role": "assistant", "content": answer},
                    ],
                    "department": dept,
                }
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()

                if i % 50 == 0:
                    log.info("Progress: %d/%d (errors: %d)", i, n, errors)

                # Small delay — DeepInfra has generous rate limits but be polite
                time.sleep(0.2)

            except Exception as exc:
                log.warning("Error on question %d (%s): %s", i, dept, exc)
                errors += 1
                time.sleep(5)
                if errors > 50:
                    log.error("Too many errors (%d), stopping", errors)
                    break

    total = existing + (len(to_generate) - errors)
    log.info("Done. Total records: %d, errors: %d, output: %s", total, errors, output_path)


def main():
    parser = argparse.ArgumentParser(description="Generate distillation dataset from teacher model")
    parser.add_argument("--phase", type=int, choices=[1, 2], default=1,
                        help="Phase 1 = 4000 Q&A (~30 min fine-tune), Phase 2 = 10000 Q&A")
    parser.add_argument("--n", type=int, default=0,
                        help="Override number of Q&A pairs (0 = use phase default)")
    parser.add_argument("--output", type=str, default="",
                        help="Output JSONL path (default: data/distillation/phaseN.jsonl)")
    parser.add_argument("--no-resume", action="store_true",
                        help="Start fresh even if output file exists")
    args = parser.parse_args()

    n = args.n or (4000 if args.phase == 1 else 10000)
    output = Path(args.output) if args.output else Path(f"data/distillation/phase{args.phase}.jsonl")

    log.info("Phase %d: generating %d Q&A pairs -> %s", args.phase, n, output)
    generate(n, output, resume=not args.no_resume)


if __name__ == "__main__":
    main()
