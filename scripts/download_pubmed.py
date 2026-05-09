"""Download PubMed abstracts via NCBI E-utilities.

Usage:
    export NCBI_API_KEY=your_key_from_https://account.ncbi.nlm.nih.gov/
    python scripts/download_pubmed.py --term "sepsis emergency" --retmax 100

NCBI will rate-limit (and eventually block) anonymous clients. Register for a free
API key and set it in NCBI_API_KEY to get 10 req/s instead of 3 req/s.

If you still get blocked, use the MedRAG HuggingFace mirror already downloaded
to ``data/pubmed/pubmed_medrag_sample.jsonl``, or pull the PubMed baseline FTP
(ftp://ftp.ncbi.nlm.nih.gov/pubmed/baseline/) for bulk use.
"""
from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def _ua():
    return (
        f"NovaHealth-RAG/1.0 ({os.getenv('NCBI_USER_EMAIL', 'ops@example.com')})"
    )


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": _ua()})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def _auth(params: dict) -> str:
    key = os.getenv("NCBI_API_KEY")
    if key:
        params.setdefault("api_key", key)
    return urllib.parse.urlencode(params)


def search(term: str, retmax: int) -> list[str]:
    url = f"{ESEARCH}?{_auth({'db': 'pubmed', 'term': term, 'retmax': str(retmax), 'retmode': 'json'})}"
    import json as _json

    data = _json.loads(_get(url))
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_abstracts(pmids: list[str]) -> str:
    if not pmids:
        return ""
    url = f"{EFETCH}?{_auth({'db': 'pubmed', 'id': ','.join(pmids), 'rettype': 'abstract', 'retmode': 'text'})}"
    return _get(url).decode("utf-8", errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--term", required=True)
    ap.add_argument("--retmax", type=int, default=100)
    ap.add_argument("--out", default="data/pubmed")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    print(f"Searching: {args.term!r} …")
    pmids = search(args.term, args.retmax)
    print(f"Found {len(pmids)} PMIDs")

    # Batch to respect URL length limits
    chunk = 50
    all_text: list[str] = []
    for i in range(0, len(pmids), chunk):
        batch = pmids[i : i + chunk]
        print(f"  fetching {i + 1}-{i + len(batch)} …")
        all_text.append(fetch_abstracts(batch))
        time.sleep(0.34)  # 3 req/s without key; with key you can go faster

    slug = args.term.replace(" ", "_").replace("/", "_")
    path = out / f"{slug}.txt"
    path.write_text("\n\n".join(all_text), encoding="utf-8")
    print(f"Done → {path} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
