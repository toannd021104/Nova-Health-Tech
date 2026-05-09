"""Download clinical trial study records from ClinicalTrials.gov v2 API.

Usage:
    python scripts/download_clinicaltrials.py --condition sepsis --pages 3 --page-size 20

Docs: https://clinicaltrials.gov/data-api/api

The v2 API has no auth requirement and no API key. It supports JSON/CSV/XML.
This script pages through results and writes one JSON file per page under
``data/clinical-trials/<condition>/``.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://clinicaltrials.gov/api/v2/studies"


def fetch(condition: str, page_size: int, page_token: str | None) -> dict:
    params = {
        "query.cond": condition,
        "pageSize": str(page_size),
        "format": "json",
    }
    if page_token:
        params["pageToken"] = page_token
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "NovaHealth-RAG/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--condition", required=True, help="e.g. sepsis, stroke, covid-19")
    ap.add_argument("--pages", type=int, default=1)
    ap.add_argument("--page-size", type=int, default=50)
    ap.add_argument("--out", default="data/clinical-trials")
    args = ap.parse_args()

    out_dir = Path(args.out) / args.condition.replace(" ", "-")
    out_dir.mkdir(parents=True, exist_ok=True)

    token = None
    for i in range(args.pages):
        print(f"Fetching page {i + 1} …")
        data = fetch(args.condition, args.page_size, token)
        (out_dir / f"page_{i + 1:03d}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        token = data.get("nextPageToken")
        if not token:
            print("No more pages.")
            break
        time.sleep(0.5)  # be polite

    print(f"Done → {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
