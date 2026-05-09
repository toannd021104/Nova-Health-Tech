"""Download WHO ICD-11 structured data.

Setup (free):
  1. Register at https://icd.who.int/icdapi
  2. Get clientId + clientSecret
  3. Export env vars:
        export WHO_ICD_CLIENT_ID=...
        export WHO_ICD_CLIENT_SECRET=...
  4. Run:
        python scripts/download_who_icd.py --entity 1435254666    # "sepsis"
        python scripts/download_who_icd.py --root                 # pull MMS root

Docs:
  Auth:  https://icd.who.int/docs/icd-api/API-Authentication/
  API :  https://icd.who.int/icdapi
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
API_BASE = "https://id.who.int/icd/release/11/2025-01/mms"


def get_token() -> str:
    cid = os.environ["WHO_ICD_CLIENT_ID"]
    sec = os.environ["WHO_ICD_CLIENT_SECRET"]
    data = urllib.parse.urlencode(
        {
            "client_id": cid,
            "client_secret": sec,
            "scope": "icdapi_access",
            "grant_type": "client_credentials",
        }
    ).encode("utf-8")
    req = urllib.request.Request(TOKEN_URL, data=data)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["access_token"]


def fetch(path: str, token: str) -> dict:
    url = f"{API_BASE}{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    req.add_header("Accept-Language", "en")
    req.add_header("API-Version", "v2")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--entity", help="ICD-11 entity id (leaf)")
    ap.add_argument("--root", action="store_true", help="fetch MMS root")
    ap.add_argument("--out", default="data/who")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    token = get_token()

    if args.root:
        data = fetch("", token)
        (out / "icd11_mms_root.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Wrote {out / 'icd11_mms_root.json'}")
    elif args.entity:
        data = fetch(f"/{args.entity}", token)
        (out / f"icd11_{args.entity}.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"Wrote {out / f'icd11_{args.entity}.json'}")
    else:
        ap.error("pass --root or --entity ID")

    return 0


if __name__ == "__main__":
    sys.exit(main())
