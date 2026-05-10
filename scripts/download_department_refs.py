"""Download open-access English reference PDFs for each demo department.

Fetches ~5 open-access PMC articles per department into
``data/clinical-trials/departments/<dept>/``. Uses NCBI E-utilities (free,
3 req/s without key, 10 req/s with key — export NCBI_API_KEY to bump).

Queries are tuned to WHO-style / guideline-style review articles so the RAG
corpus gets real clinical content. Radiology queries prefer PubMed Central
full-text so we get PDFs with real figures.

Usage:
    python scripts/download_department_refs.py
    python scripts/download_department_refs.py --dept radiology
    python scripts/download_department_refs.py --max-per-dept 3

Docs:
    https://www.ncbi.nlm.nih.gov/books/NBK25497/   (E-utilities overview)
    https://europepmc.org/RestfulWebService         (Europe PMC fallback)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path


EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
EPMC = "https://europepmc.org/backend/ptpmcrender.fcgi"
USER_AGENT = "NovaHealth-RAG/1.0 (research PoC; contact: reviewer)"

# Each department gets a PubMed Central query biased toward open-access
# guideline / review articles. PMC's `open access[filter]` gets us OA PDFs.
DEPT_QUERIES: dict[str, str] = {
    "emergency": "sepsis guidelines AND open access[filter]",
    "cardiology-internal": "heart failure guidelines AND open access[filter]",
    "pulmonology": "COPD GOLD guidelines AND open access[filter]",
    "gastroenterology": "inflammatory bowel disease treatment AND open access[filter]",
    "nephrology": "chronic kidney disease KDIGO AND open access[filter]",
    "endocrinology": "type 2 diabetes management AND open access[filter]",
    "neurology": "acute ischemic stroke treatment AND open access[filter]",
    "infectious-disease": "antimicrobial stewardship AND open access[filter]",
    "oncology-chemo": "breast cancer treatment guidelines AND open access[filter]",
    "obstetrics": "pre-eclampsia management AND open access[filter]",
    "pediatrics": "pediatric sepsis AND open access[filter]",
    # Radiology gets a figure-heavy query so the PDFs include imaging examples
    # (chest X-ray, CT, MRI interpretation) — matches the Radiology department
    # agent's clinical-triage-report scenario.
    "radiology": "chest radiograph interpretation AND open access[filter]",
}


def _http_get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def esearch(query: str, retmax: int) -> list[str]:
    """Return a list of PMC IDs (e.g. 'PMC1234567') from an E-search."""
    api_key = os.environ.get("NCBI_API_KEY", "")
    key_arg = f"&api_key={api_key}" if api_key else ""
    url = (
        f"{EUTILS}/esearch.fcgi?db=pmc&retmode=json"
        f"&term={urllib.parse.quote(query)}"
        f"&retmax={retmax}"
        f"&sort=relevance"
        f"{key_arg}"
    )
    data = json.loads(_http_get(url))
    ids = data.get("esearchresult", {}).get("idlist", [])
    return [f"PMC{pmc_id}" for pmc_id in ids]


def download_pmc_pdf(pmc_id: str, out_path: Path) -> bool:
    """Download a PMC article PDF. Tries Europe PMC's PDF URL first, falls back
    to NCBI PMC OA.

    Returns True on success, False on any failure (so the loop can keep going).
    """
    # Europe PMC publishes PDFs at a predictable URL for OA articles. The
    # ftp-delivery service occasionally 302-redirects; follow with urllib's
    # default opener (handles redirects).
    candidate_urls = [
        f"https://europepmc.org/articles/{pmc_id}?pdf=render",
        f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/pdf/",
    ]
    for url in candidate_urls:
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "application/pdf,*/*",
                },
            )
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
        except Exception as exc:  # noqa: BLE001
            print(f"    fetch failed for {pmc_id} via {url[:50]}…: {exc}")
            continue
        if not data or len(data) < 5_000:
            print(f"    {pmc_id}: body too small on {url[:50]}… ({len(data)} bytes)")
            continue
        if not data[:5].startswith(b"%PDF"):
            # some mirrors return an HTML error page when OA isn't available
            print(f"    {pmc_id}: not a PDF on {url[:50]}…, trying next")
            continue
        out_path.write_bytes(data)
        print(f"    saved {pmc_id} ({len(data) // 1024} KB)")
        return True
    return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dept", help="single department to fetch (default: all)")
    ap.add_argument("--max-per-dept", type=int, default=5)
    ap.add_argument("--out", default="data/clinical-trials/departments")
    args = ap.parse_args()

    depts = [args.dept] if args.dept else sorted(DEPT_QUERIES.keys())
    out_root = Path(args.out)
    out_root.mkdir(parents=True, exist_ok=True)

    total_saved = 0
    for dept in depts:
        if dept not in DEPT_QUERIES:
            print(f"[skip] unknown department: {dept}")
            continue

        query = DEPT_QUERIES[dept]
        print(f"\n[{dept}] query: {query}")

        dept_dir = out_root / dept
        dept_dir.mkdir(parents=True, exist_ok=True)

        # Over-fetch — many PMC records have no open-access PDF even when
        # they're indexed in PMC. Filter down after download attempts.
        ids = esearch(query, retmax=args.max_per_dept * 3)
        print(f"  found {len(ids)} candidate articles")

        saved = 0
        for pmc_id in ids:
            if saved >= args.max_per_dept:
                break
            out_path = dept_dir / f"{pmc_id}.pdf"
            if out_path.exists():
                print(f"    {pmc_id}: already have it")
                saved += 1
                continue
            if download_pmc_pdf(pmc_id, out_path):
                saved += 1
            time.sleep(0.4)  # polite; upgrade to 0.2 if NCBI_API_KEY is set
        total_saved += saved
        print(f"  [{dept}] kept {saved} PDFs")

    print(f"\nDone. {total_saved} PDFs across {len(depts)} department(s) → {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
