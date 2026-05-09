# Data Sources for Nova Health Tech Clinical GenAI Assistant

Four corpora feed the RAG pipeline, matching the scenario:

1. **Internal clinical trial reports** → represented by ClinicalTrials.gov (public proxy) + FDA drug labels + a real arXiv medical-radiology-report paper as the "legacy PDF with inconsistent tagging" test fixture.
2. **Treatment protocols** → openFDA drug-label API.
3. **WHO guidelines (monthly updates)** → WHO IRIS PDFs + WHO ICD-11 API (structured).
4. **PubMed literature** → MedRAG PubMed chunk (15,377 abstracts) as the external literature corpus.

## ✅ Automated downloads (already in this repo)

| Source | File | Size | Notes |
|---|---|---|---|
| ClinicalTrials.gov v2 API — diabetes (5 studies) | `data/clinical-trials/sample_diabetes_studies.json` | ~100 KB | Full protocol + results JSON. API: `https://clinicaltrials.gov/api/v2/studies` |
| ClinicalTrials.gov v2 API — sepsis (5 studies) | `data/clinical-trials/sample_sepsis_studies.json` | ~100 KB | Emergency-care relevant. |
| ClinicalTrials.gov v2 API — stroke (5 studies) | `data/clinical-trials/sample_stroke_studies.json` | ~100 KB | Emergency-care relevant. |
| openFDA drug-label API — sepsis drugs | `data/clinical-trials/fda_sepsis_drugs.json` | ~50 KB | FDA-approved indications & usage. |
| arXiv 2409.10576 — RAG for diagnostic reports | `data/clinical-trials/arxiv_radiology_rag.pdf` | 773 KB | Real PDF with figures/tables — use as "legacy PDF with inconsistent tagging" test fixture. |
| MedRAG PubMed (HuggingFace mirror) | `data/pubmed/pubmed_medrag_sample.jsonl` | 34 MB | 15,377 abstracts from `pubmed23n0001`. Full dataset: 23M abstracts. **Not committed to git — run `bash scripts/download_medrag_pubmed.sh` to fetch.** |

Total automated pull: ~35 MB — enough to demo and benchmark the RAG pipeline end-to-end.

## ⚠️ Manual downloads required

Two sources actively block automated IPs (rate-limiting / anti-bot) and must be downloaded from a browser or an authenticated account.

### WHO Guidelines (PDF) — iris.who.int

The IRIS repository now serves via a JavaScript single-page app, so `curl`/`wget` get an empty HTML shell. **Open these in a browser and save into `data/who/`:**

| Guideline | Link |
|---|---|
| WHO Guidelines for malaria (13 Aug 2025, updated monthly) | https://www.who.int/publications/i/item/guidelines-for-malaria |
| WHO Therapeutics and COVID-19: living guideline | https://www.who.int/publications/i/item/B09540 |
| Clinical practice guidelines for influenza | https://www.who.int/publications/i/item/9789240097759 |
| Consolidated HIV guidelines | https://www.who.int/publications/i/item/9789240031593 |
| Clinical management for mpox (living) | https://www.who.int/publications/i/item/B09434 |
| All approved WHO guidelines (monthly index) | https://www.who.int/publications/who-guidelines |

**Automation recommendation for production:** do not scrape WHO. Use the **WHO ICD-11 API** (free, OAuth2) for structured disease metadata, and for guideline PDFs either license the WHO IRIS OAI-PMH feed or subscribe to the monthly `who-guidelines` RSS, downloading from a whitelisted IP. See `scripts/download_who_icd.py`.

### WHO ICD-11 API (structured, the "structured API" in the scenario)

- Register (free) → https://icd.who.int/icdapi → creates `clientId` / `clientSecret`.
- Auth: OAuth2 client-credentials against `https://icdaccessmanagement.who.int/connect/token`.
- Base URL: `https://id.who.int/icd/release/11/mms`.
- FHIR flavor also available (CodeSystem + ValueSet resources).
- Use `scripts/download_who_icd.py` (included).

### PubMed via E-utilities — currently IP-blocked

NCBI returned `Access Denied — blocked for possible abuse` to our client IP during testing. For a production pipeline:

- Register a free NCBI API key: https://account.ncbi.nlm.nih.gov/ → increases rate from 3 req/s to 10 req/s.
- Use with `&api_key=YOUR_KEY` on every call.
- Alternative bulk route: **PubMed baseline FTP** — 2,000+ XML files covering all abstracts. `ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/`
- Or use the MedRAG HuggingFace mirror we already downloaded (daily updates at `https://huggingface.co/datasets/MedRAG/pubmed`).

See `scripts/download_pubmed.py` for the E-utilities pattern.

### Internal clinical trial reports (simulated)

The real "internal" reports live inside Nova Health Tech and are not publicly accessible. For testing, stand in with:

- **ClinicalTrials.gov Full Protocol + SAP downloads** — many sponsors post the protocol PDF on each study page (see `largeDocumentModule.largeDocs[]` in the API JSON response). Example:
  `https://cdn.clinicaltrials.gov/large-docs/87/NCT03302897/Prot_SAP_000.pdf`
- **PMC Open Access Subset** — full-text trial articles with figures: https://pmc.ncbi.nlm.nih.gov/tools/openftlist/
- **MIMIC-IV demo** (de-identified ICU data, credentialed): https://physionet.org/content/mimic-iv-demo/

## Data layout ingested into the RAG pipeline

```
S3 / OSS bucket
├── raw/
│   ├── who-guidelines/*.pdf              (monthly, triggers re-index)
│   ├── clinical-trials-json/*.json
│   ├── protocols-pdf/*.pdf               (internal Nova PDFs — inconsistent tagging)
│   ├── pubmed-jsonl/*.jsonl
│   └── fda-labels/*.json
├── processed/
│   ├── chunks/*.jsonl                    (after Textract + cleaning + chunking)
│   └── embeddings/*.parquet              (if caching)
└── vector-index/                         (OpenSearch snapshot backups)
```

The monthly-update SLA for WHO is handled by an EventBridge (AWS) / EventBridge-equivalent (Alibaba) rule running on day 1 of each month — see the architecture docs.
