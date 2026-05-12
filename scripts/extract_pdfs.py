"""Extract text from all 12 clinical trial PDFs for question generation."""
import pypdf
import os

pdfs = {
    "PMC1236923": "data/clinical-trials/departments/cardiology-internal/PMC1236923.pdf",
    "PMC11846407": "data/clinical-trials/departments/emergency/PMC11846407.pdf",
    "PMC2898118": "data/clinical-trials/departments/endocrinology/PMC2898118.pdf",
    "PMC12400259": "data/clinical-trials/departments/gastroenterology/PMC12400259.pdf",
    "PMC11638529": "data/clinical-trials/departments/infectious-disease/PMC11638529.pdf",
    "PMC3701497": "data/clinical-trials/departments/nephrology/PMC3701497.pdf",
    "PMC10640530": "data/clinical-trials/departments/neurology/PMC10640530.pdf",
    "PMC4451740": "data/clinical-trials/departments/obstetrics/PMC4451740.pdf",
    "PMC5803577": "data/clinical-trials/departments/oncology-chemo/PMC5803577.pdf",
    "PMC2206501": "data/clinical-trials/departments/pediatrics/PMC2206501.pdf",
    "PMC12232468": "data/clinical-trials/departments/pulmonology/PMC12232468.pdf",
    "PMC4775830": "data/clinical-trials/departments/radiology/PMC4775830.pdf",
}

for pmc_id, path in pdfs.items():
    print(f"\n{'='*60}")
    print(f"=== {pmc_id} ===")
    print(f"{'='*60}")
    try:
        reader = pypdf.PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        # Print first 3000 chars
        print(text[:3000])
        print(f"\n... [{len(text)} total chars, {len(reader.pages)} pages]")
    except Exception as e:
        print(f"ERROR: {e}")
