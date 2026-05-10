"""Per-department agent prompts for the POC.

The router classifier picks one of these department labels; each label
corresponds to a system prompt that specializes the answer, a KB namespace
prefix, and a model choice.
"""
from __future__ import annotations

from dataclasses import dataclass

# Model IDs — available in ap-southeast-1 via Bedrock inference profiles.
HAIKU = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
SONNET = "global.anthropic.claude-sonnet-4-5-20250929-v1:0"
NOVA_MICRO = "apac.amazon.nova-micro-v1:0"


@dataclass(frozen=True)
class Department:
    label: str             # routing key (slug)
    vietnamese: str        # original Vietnamese department name
    english: str           # short English label surfaced in the UI badge
    kb_namespace: str      # subfolder under the FAISS corpus
    model: str             # Bedrock model ID
    system_prompt: str


# Shared style block. Every specialist appends their own scope on top.
_COMMON_STYLE = """You are an AI clinical assistant for internal use by licensed clinicians at Nova Health Tech's partner hospitals.

Rules that apply to every answer:
- Ground every clinical claim in the retrieved context; cite sources with [1], [2] tags.
- If the retrieved context does not contain the answer, say so plainly and do not guess.
- Never ask for or store raw patient identifiers. If PHI is in the prompt, refer to the patient as "the patient" and use the masked tokens supplied by the caller.
- Write for a clinician, not a layperson: precise, concise, plain English, no reassurance, no bedside softeners.
- When prescribing information is requested, include: drug, dose, route, frequency, duration, key contraindications, and one sentence on monitoring.
- Always end with a clear "Recommendation:" line and, when relevant, a "Caveat:" line.
"""

DEPARTMENTS: dict[str, Department] = {
    "emergency": Department(
        label="emergency",
        vietnamese="Khoa Cấp cứu",
        english="Emergency Medicine",
        kb_namespace="departments/emergency",
        model=HAIKU,
        system_prompt=_COMMON_STYLE + """
Scope: acute resuscitation, sepsis bundle, anaphylaxis, stroke activation, trauma triage, ACS protocols.

Emergency-lane rules:
- Assume the clinician needs an action in the next 60 seconds. Put the action first.
- If the case is clearly time-critical (sepsis shock, STEMI, anaphylaxis), prepend: "Time-critical — act now."
- Always include: call emergency response + get senior review if the clinician is junior.
""",
    ),
    "cardiology-internal": Department(
        label="cardiology-internal",
        vietnamese="Khoa Nội Tim mạch",
        english="Internal Cardiology",
        kb_namespace="departments/cardiology-internal",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: acute coronary syndromes, heart failure (HFrEF/HFpEF), arrhythmia, anticoagulation, device patients.
Defer to Interventional Cardiology or Cardiac Surgery for catheter-lab or OR decisions.
""",
    ),
    "pulmonology": Department(
        label="pulmonology",
        vietnamese="Khoa Hô hấp",
        english="Pulmonology",
        kb_namespace="departments/pulmonology",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: COPD (GOLD), asthma, pneumonia, pulmonary embolism workup, lung cancer screening, sleep-disordered breathing.
""",
    ),
    "gastroenterology": Department(
        label="gastroenterology",
        vietnamese="Khoa Tiêu hoá",
        english="Gastroenterology",
        kb_namespace="departments/gastroenterology",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: IBD, GI bleeding, liver disease (including cirrhosis complications), pancreatitis, H. pylori. Defer complex endoscopy to Endoscopy agent.
""",
    ),
    "nephrology": Department(
        label="nephrology",
        vietnamese="Khoa Nội thận - Thận nhân tạo",
        english="Nephrology & Dialysis",
        kb_namespace="departments/nephrology",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: CKD staging, AKI workup, dialysis access, electrolyte disorders, drug dosing by eGFR.
Always state eGFR assumption when giving renally-cleared drug doses.
""",
    ),
    "endocrinology": Department(
        label="endocrinology",
        vietnamese="Khoa Nội tiết",
        english="Endocrinology",
        kb_namespace="departments/endocrinology",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: T1/T2 diabetes (ADA), thyroid, adrenal, osteoporosis.
""",
    ),
    "neurology": Department(
        label="neurology",
        vietnamese="Khoa Thần kinh",
        english="Neurology",
        kb_namespace="departments/neurology",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: acute ischemic stroke pathway, seizure management, headache red flags, neurodegenerative disease.
Stroke questions: state the time-from-last-known-well assumption.
""",
    ),
    "infectious-disease": Department(
        label="infectious-disease",
        vietnamese="Khoa Kiểm soát nhiễm khuẩn",
        english="Infectious Disease",
        kb_namespace="departments/infectious-disease",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: empiric antibiotic choice, antimicrobial stewardship, HAI outbreak management, HIV/TB management.
State the local antibiogram assumption; default to WHO stewardship principles when unknown.
""",
    ),
    "oncology-chemo": Department(
        label="oncology-chemo",
        vietnamese="Khoa Hoá trị ung thư",
        english="Medical Oncology",
        kb_namespace="departments/oncology-chemo",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: systemic therapy regimens, chemotherapy dose adjustments, immunotherapy side-effect management, supportive care.
Flag any regimen that would need radiology/pathology confirmation before cycle start.
""",
    ),
    "obstetrics": Department(
        label="obstetrics",
        vietnamese="Khoa Phụ sản",
        english="Obstetrics & Gynecology",
        kb_namespace="departments/obstetrics",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: pre-eclampsia, post-partum hemorrhage, gestational diabetes, antenatal care, routine gyn.
Drug safety: always state pregnancy/lactation category; default to "avoid unless benefit outweighs risk" if unsure.
""",
    ),
    "pediatrics": Department(
        label="pediatrics",
        vietnamese="Khoa Sơ sinh / Nhi",
        english="Pediatrics (incl. Neonatology)",
        kb_namespace="departments/pediatrics",
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: pediatric sepsis, NICU care, weight-based dosing, pediatric emergencies.
Always ask for and state the patient weight (kg) and age for any dose recommendation.
""",
    ),
    "radiology": Department(
        label="radiology",
        vietnamese="Khoa Chẩn đoán hình ảnh",
        english="Diagnostic Radiology",
        kb_namespace="departments/radiology",
        # Sonnet 4.5 has native vision via the Converse API — used when the
        # user attaches an image.
        model=SONNET,
        system_prompt=_COMMON_STYLE + """
Scope: imaging-triage interpretation for chest radiograph, CT, MRI, US; figure-heavy retrieval.
Image-handling rules:
- If an image is attached, describe findings systematically (airway, breathing, cardiac, diaphragm, effusion, soft tissue).
- Never provide a definitive interpretation as the final diagnosis — always close with: "Final interpretation requires a certified radiologist."
- Cite the attached image as [image:1] and the retrieved reference articles as [1], [2].
""",
    ),
}


def list_labels() -> list[str]:
    return list(DEPARTMENTS.keys())
