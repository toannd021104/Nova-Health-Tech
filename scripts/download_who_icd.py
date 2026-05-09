"""Download WHO ICD-11 structured data for the RAG knowledge base.

This hits the live WHO ICD-11 API (https://id.who.int/swagger/index.html) to build
a local snapshot of the MMS (Mortality and Morbidity Statistics) linearization.

Setup (free):
  1. Register at https://icd.who.int/icdapi
  2. Set env vars (never commit these):
        export WHO_ICD_CLIENT_ID=...
        export WHO_ICD_CLIENT_SECRET=...
  3. Run one of:
        python scripts/download_who_icd.py --root                     # top-level chapters
        python scripts/download_who_icd.py --entity 1435254666        # one entity
        python scripts/download_who_icd.py --search "sepsis"          # keyword search
        python scripts/download_who_icd.py --walk --max-depth 2       # walk hierarchy

The --walk flag is the one used by the monthly refresh job: it descends the
full MMS tree up to --max-depth levels and writes one JSON file per entity under
``data/icd11/entities/``.  Each entity JSON holds the full description,
definition, inclusions/exclusions, coded parents, and the index terms that RAG
uses for retrieval.
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

TOKEN_URL = "https://icdaccessmanagement.who.int/connect/token"
RELEASE = "2024-01"
MMS_BASE = f"https://id.who.int/icd/release/11/{RELEASE}/mms"


def _auth_token() -> str:
    cid = os.environ["WHO_ICD_CLIENT_ID"]
    sec = os.environ["WHO_ICD_CLIENT_SECRET"]
    body = urllib.parse.urlencode(
        {
            "client_id": cid,
            "client_secret": sec,
            "scope": "icdapi_access",
            "grant_type": "client_credentials",
        }
    ).encode()
    req = urllib.request.Request(TOKEN_URL, data=body)
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def _get(url: str, token: str) -> dict:
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    req.add_header("Accept-Language", "en")
    req.add_header("API-Version", "v2")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def _entity_id(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def walk(out_dir: Path, token: str, max_depth: int) -> int:
    root = _get(MMS_BASE, token)
    (out_dir / "mms_root.json").write_text(
        json.dumps(root, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    entities_dir = out_dir / "entities"
    entities_dir.mkdir(parents=True, exist_ok=True)

    queue: list[tuple[str, int]] = [(c, 0) for c in root.get("child", [])]
    seen: set[str] = set()
    count = 0

    while queue:
        url, depth = queue.pop(0)
        eid = _entity_id(url)
        if eid in seen:
            continue
        seen.add(eid)
        try:
            ent = _get(url, token)
        except Exception as exc:
            print(f"  skip {eid}: {exc}")
            continue
        (entities_dir / f"{eid}.json").write_text(
            json.dumps(ent, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        count += 1
        if count % 25 == 0:
            print(f"  fetched {count} entities (depth {depth})")

        if depth < max_depth:
            for child in ent.get("child", []):
                queue.append((child, depth + 1))

        time.sleep(0.2)  # stay polite (~5 req/s)

    return count


def search(term: str, out_dir: Path, token: str) -> int:
    q = urllib.parse.quote(term)
    url = f"{MMS_BASE}/search?q={q}&flatResults=true&useFlexisearch=false"
    data = _get(url, token)
    out_file = out_dir / f"search_{term.replace(' ', '_')}.json"
    out_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return len(data.get("destinationEntities", []))


def fetch_entity(entity_id: str, out_dir: Path, token: str) -> None:
    url = f"{MMS_BASE}/{entity_id}"
    data = _get(url, token)
    (out_dir / f"entity_{entity_id}.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", action="store_true", help="fetch MMS root + chapters")
    ap.add_argument("--entity", help="ICD-11 entity id (leaf or chapter)")
    ap.add_argument("--search", metavar="TERM", help="keyword search")
    ap.add_argument("--walk", action="store_true", help="descend the hierarchy")
    ap.add_argument("--max-depth", type=int, default=2)
    ap.add_argument("--out", default="data/icd11")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    token = _auth_token()

    if args.walk:
        n = walk(out, token, args.max_depth)
        print(f"Walked {n} entities → {out / 'entities'}")
    elif args.root:
        data = _get(MMS_BASE, token)
        (out / "mms_root.json").write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Wrote {out / 'mms_root.json'} ({len(data.get('child', []))} chapters)")
    elif args.entity:
        fetch_entity(args.entity, out, token)
        print(f"Wrote {out / f'entity_{args.entity}.json'}")
    elif args.search:
        n = search(args.search, out, token)
        print(f"{n} search hits for {args.search!r}")
    else:
        ap.error("pass --root, --walk, --entity, or --search")

    return 0


if __name__ == "__main__":
    sys.exit(main())
