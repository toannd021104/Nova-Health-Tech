# Data — Nova Health Tech RAG Input Corpus

**Only real business data goes here.** Reference / research material belongs in `/reference/` (if created later), not here.

## Layout

```
data/
├── who/                         ← WHO guideline PDFs (100+ pages each, body text + tables + figures)
│   └── *.pdf                    (8 files present, see below)
├── icd11/                       ← WHO ICD-11 structured data (live API)
│   ├── mms_root.json
│   ├── entities/*.json          ← 28 chapter-level entities from depth-0 walk
│   └── search_*.json            ← keyword search snapshots (sepsis, stroke, MI)
└── clinical-trials/
    └── protocols/               ← drop internal trial PDFs here; large files .gitignored
```

## WHO guidelines currently present

| File | About |
|---|---|
| `9789240031593-eng.pdf` | Consolidated HIV prevention, testing, treatment, service delivery guidelines |
| `9789240097759-eng.pdf` | Clinical practice guidelines for influenza |
| `9789240115606-eng.pdf` | (confirm by opening) |
| `9789240115774-eng.pdf` | (confirm by opening) |
| `9789240118164-eng.pdf` | (confirm by opening) |
| `B09434-eng.pdf` | Clinical management and IPC for mpox (living guideline) |
| `B09514-eng.pdf` | WHO Guidelines for malaria (Aug 2025) |
| `B09540-eng.pdf` | Therapeutics and COVID-19 living guideline |

These PDFs contain the mix (horizontal and vertical tables, text-based decision flowcharts, some figures) that drives the RAG strategy decision in `docs/architecture/rag_strategy.md`.

## ICD-11 data

Produced by running the real WHO API — see `scripts/download_who_icd.py`. The repo's `data/icd11/` holds:

- `mms_root.json` — top of the MMS linearization (28 chapters).
- `entities/*.json` — one file per chapter-level entity (full definition, inclusions/exclusions, children). Produced by `--walk --max-depth 0`.
- `search_<term>.json` — keyword search results for emergency-care terms (sepsis, stroke, myocardial infarction). Produced by `--search <term>`.

In production the monthly refresh runs `--walk --max-depth 2` to ingest the full hierarchy (~10–15k entities). This repo keeps it small for demo footprint.

## Clinical trials (protocols/)

This folder is for Nova's internal trial PDFs. Since those are private, the folder ships empty in the repo. Teams backfilling a test corpus can use `scripts/download_clinicaltrials.py` to pull public ClinicalTrials.gov records into `clinical-trials/public-samples/` (not gitignored), but **do not put those under `protocols/`** — that folder is reserved for Nova's own documents.

## What is NOT here (intentionally)

- **PubMed corpus** — out of scope per current requirements.
- **Sample / fake data** — removed; real data only.
- **RAG research PDFs / blog PDFs** — those live in `/reference/` if needed (not committed here).
