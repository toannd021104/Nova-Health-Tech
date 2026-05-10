# Department reference corpus

Open-access PubMed Central PDFs (fetched via `scripts/download_department_refs.py`) mapped to the 12-department demo subset used in the POC. The production build scales to the full 40-department Vietnamese-hospital topology documented in `docs/rag_and_pipelines.md` §Multi-agent topology.

Each PDF is a real English review / guideline article. We use PMC IDs as filenames so the provenance stays traceable in the RAG citations.

## Layout

```
departments/
├── cardiology-internal/     Heart failure guidelines
├── emergency/               Sepsis guidelines (aligned with WHO B09540)
├── endocrinology/           Type 2 diabetes management
├── gastroenterology/        IBD treatment
├── infectious-disease/      Antimicrobial stewardship
├── nephrology/              KDIGO CKD
├── neurology/               Acute ischemic stroke
├── obstetrics/              Pre-eclampsia management
├── oncology-chemo/          Breast cancer treatment
├── pediatrics/              Pediatric sepsis
├── pulmonology/             COPD (GOLD)
└── radiology/               Chest radiograph interpretation — figure-heavy PDFs
                             that exercise the vision agent
```

## Vietnamese ↔ English mapping (POC subset)

| Vietnamese name | POC routing label | English clinical area |
|---|---|---|
| Khoa Cấp cứu | `emergency` | Emergency Medicine |
| Khoa Nội Tim mạch | `cardiology-internal` | Internal Cardiology |
| Khoa Hô hấp | `pulmonology` | Pulmonology |
| Khoa Tiêu hoá | `gastroenterology` | Gastroenterology |
| Khoa Nội thận - Thận nhân tạo | `nephrology` | Nephrology & Dialysis |
| Khoa Nội tiết | `endocrinology` | Endocrinology |
| Khoa Thần kinh | `neurology` | Neurology |
| Khoa Kiểm soát nhiễm khuẩn | `infectious-disease` | Infection Control / Infectious Disease |
| Khoa Hoá trị ung thư | `oncology-chemo` | Medical Oncology |
| Khoa Phụ sản | `obstetrics` | Obstetrics & Gynecology |
| Khoa Sơ sinh (merged here) | `pediatrics` | Pediatrics + Neonatology |
| Khoa Chẩn đoán hình ảnh | `radiology` | Diagnostic Radiology (vision agent) |

The full 40-department mapping is in `docs/rag_and_pipelines.md` §Multi-agent topology.

## Source

All articles are open-access on PubMed Central and fetched via Europe PMC / NCBI PMC OA. The download script skips anything that isn't a real PDF (size < 5 KB or not starting with `%PDF`). Each file's PMC ID is preserved in the filename so `PMC6745362.pdf` traces back to [https://europepmc.org/articles/PMC6745362](https://europepmc.org/articles/PMC6745362).

## Refresh

```bash
# all 12 departments, 3 papers each
python scripts/download_department_refs.py --max-per-dept 3

# single department
python scripts/download_department_refs.py --dept radiology --max-per-dept 5
```

Re-running skips files that already exist, so it's safe to run on a schedule.

*Content above is rephrased for compliance with licensing restrictions.*
