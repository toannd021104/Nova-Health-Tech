"""Upload local /data to an S3 bucket that a Bedrock Knowledge Base is watching,
then trigger a sync.

Usage:
    export AWS_PROFILE=nova-dev
    python scripts/ingest_to_bedrock_kb.py \
        --bucket nova-rag-raw-dev \
        --kb-id ABCDEFGHIJ \
        --ds-id KLMNOPQRST \
        --prefix-map clinical-trials=trials who=who-guidelines pubmed=pubmed

After the sync completes, query from Lambda with:
    bedrock_agent = boto3.client("bedrock-agent-runtime")
    bedrock_agent.retrieve_and_generate(...)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    import boto3
except ImportError:  # pragma: no cover
    print("pip install boto3", file=sys.stderr)
    raise


def _parse_map(pairs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for p in pairs:
        local, remote = p.split("=", 1)
        out[local] = remote
    return out


def upload(s3, bucket: str, prefix_map: dict[str, str]) -> int:
    count = 0
    for local, remote in prefix_map.items():
        base = Path("data") / local
        if not base.exists():
            print(f"  skip {local} (missing)")
            continue
        for fp in base.rglob("*"):
            if not fp.is_file():
                continue
            key = f"{remote}/{fp.relative_to(base).as_posix()}"
            print(f"  {fp} → s3://{bucket}/{key}")
            s3.upload_file(str(fp), bucket, key)
            count += 1
    return count


def sync(agent, kb_id: str, ds_id: str) -> str:
    resp = agent.start_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=ds_id)
    return resp["ingestionJob"]["ingestionJobId"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bucket", required=True)
    ap.add_argument("--kb-id", required=True)
    ap.add_argument("--ds-id", required=True)
    ap.add_argument("--prefix-map", nargs="+", required=True,
                    help="local=remote pairs, e.g. clinical-trials=trials")
    ap.add_argument("--region", default=os.getenv("AWS_REGION", "us-east-1"))
    args = ap.parse_args()

    session = boto3.Session(region_name=args.region)
    s3 = session.client("s3")
    agent = session.client("bedrock-agent")

    mapping = _parse_map(args.prefix_map)
    n = upload(s3, args.bucket, mapping)
    print(f"Uploaded {n} files to s3://{args.bucket}")

    job = sync(agent, args.kb_id, args.ds_id)
    print(f"Kicked off ingestion job: {job}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
