"""Per-department agent prompts for the POC (Version B — AWS + Nova/Qwen).

Model reality in ap-southeast-1 Singapore (verified May 2026):
- NO Qwen models on Bedrock Singapore.
- Available: Claude (Anthropic), Amazon Nova, Cohere Embed.

This PoC uses Amazon Nova models (Singapore-native, no cross-region):
  - Nova Micro  — router (cheapest, structured JSON)
  - Nova Lite   — emergency lane (fast, low cost)
  - Nova Pro    — complex lane specialist (best quality available in SG)

Fine-tuning:
  - Teacher: Nova Pro (generates distillation Q&A, Singapore, no external API)
  - Student: Qwen/Qwen3.5-4B from HuggingFace, SFT+LoRA locally,
             served via /api/student/chat on the same FastAPI server.
             Apache 2.0 license. 4B params, fits in 8GB VRAM (bfloat16)
             or 4GB VRAM (QLoRA 4-bit). ChatML format, natively multimodal.

The student is open-source Qwen running locally — NOT on Bedrock, NOT via
DashScope. HuggingFace download only.

RAG: reuses the same Bedrock KBs as aws_claude:
  - Vector KB:   MUEEBGPRSJ (OpenSearch Serverless, Cohere Embed Multilingual v3)
  - GraphRAG KB: FU6SXD0B8B (Neptune Analytics)
Both are in ap-southeast-1 Singapore.
"""
from __future__ import annotations

from dataclasses import dataclass

# Amazon Nova model IDs — all available in ap-southeast-1 Singapore.
NOVA_MICRO = "apac.amazon.nova-micro-v1:0"    # router: cheapest, structured JSON
NOVA_LITE  = "apac.amazon.nova-lite-v1:0"     # emergency lane: fast
NOVA_PRO   = "apac.amazon.nova-pro-v1:0"      # complex lane: best quality in SG
NOVA_PRO_TEACHER = NOVA_PRO                   # teacher for distillation dataset


@dataclass(frozen=True)
class Department:
    label: str
    vietnamese: str
    english: str
    kb_namespace: str      # kept for compatibility; not used with Bedrock KB
    model: str             # Bedrock model ID
    system_prompt: str


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
        model=NOVA_LITE,
        system_prompt="""You are an emergency clinical AI assistant. Ground claims in retrieved context with [1],[2] citations. If context lacks the answer, say so. Write for clinicians: precise, concise. Put the action first. End with "Recommendation:" line.""",
    ),
    "cardiology-internal": Department(
        label="cardiology-internal",
        vietnamese="Khoa Nội Tim mạch",
        english="Internal Cardiology",
        kb_namespace="departments/cardiology-internal",
        model=NOVA_PRO,
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
        model=NOVA_PRO,
        system_prompt=_COMMON_STYLE + """
Scope: COPD (GOLD), asthma, pneumonia, pulmonary embolism workup, lung cancer screening, sleep-disordered breathing.
""",
    ),
    "gastroenterology": Department(
        label="gastroenterology",
        vietnamese="Khoa Tiêu hoá",
        english="Gastroenterology",
        kb_namespace="departments/gastroenterology",
        model=NOVA_PRO,
        system_prompt=_COMMON_STYLE + """
Scope: IBD, GI bleeding, liver disease (including cirrhosis complications), pancreatitis, H. pylori.
""",
    ),
    "nephrology": Department(
        label="nephrology",
        vietnamese="Khoa Nội thận - Thận nhân tạo",
        english="Nephrology & Dialysis",
        kb_namespace="departments/nephrology",
        model=NOVA_PRO,
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
        model=NOVA_PRO,
        system_prompt=_COMMON_STYLE + """
Scope: T1/T2 diabetes (ADA), thyroid, adrenal, osteoporosis.
""",
    ),
    "neurology": Department(
        label="neurology",
        vietnamese="Khoa Thần kinh",
        english="Neurology",
        kb_namespace="departments/neurology",
        model=NOVA_PRO,
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
        model=NOVA_PRO,
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
        model=NOVA_PRO,
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
        model=NOVA_PRO,
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
        model=NOVA_PRO,
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
        model=NOVA_PRO,   # Nova Pro supports image input via Converse API
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

