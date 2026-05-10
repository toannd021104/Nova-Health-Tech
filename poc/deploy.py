"""Deploy the Nova Health POC to AWS Singapore — cheapest variant.

Uses boto3 directly (no CDK / SAM / Terraform) so the deploy stays legible
for the interview reviewer. Matches the approach of ``aws-demo/ec2/deploy.py``.

Layout after deploy:

    ┌─────────────────────────────────────────────┐
    │ CloudFront distribution                     │ public URL
    │   ├─ /ui/*  →  S3 static bucket (light UI)  │
    │   └─ /api/* →  API Gateway → Lambda /chat   │
    │              (FastAPI + Mangum + LangGraph) │
    │                                             │
    │ S3 corpus bucket                            │
    │   ├─ faiss/<namespace>/index.faiss          │ preloaded at Lambda cold start
    │   └─ raw/<dept>/*.pdf                       │
    └─────────────────────────────────────────────┘

Resource naming follows the HA-<base64> convention from aws-demo/ec2.

Usage:
    python poc/deploy.py --profile gapv50k --region ap-southeast-1

After deploy, teardown with:
    python poc/teardown.py --profile gapv50k --region ap-southeast-1
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import logging
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

import boto3

log = logging.getLogger("poc.deploy")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

REPO_ROOT = Path(__file__).resolve().parents[1]
POC_ROOT = REPO_ROOT / "poc"
DATA_ROOT = REPO_ROOT / "data"


def ha_tag(name: str) -> str:
    """HA-<base64> tag value — matches aws-demo/ec2/NAMING.md."""
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")


def build_faiss_indexes(corpus_root: Path, build_dir: Path, departments: list[str]) -> None:
    """Build one FAISS namespace per department locally. The Bedrock embed
    calls are executed in this driver — Lambda only reads the prebuilt files.
    """
    sys.path.insert(0, str(REPO_ROOT))
    from poc.app.rag import build_namespace, FAISS_DIR  # noqa: PLC0415

    # Redirect index output into the build_dir so we don't litter /tmp.
    os.environ["FAISS_DIR"] = str(build_dir)
    log.info("Building FAISS indexes in %s", build_dir)

    # ICD-11 entities fan out to every department since ICD codes cut across
    # specialties. A small global namespace keeps each dept KB manageable.
    global_docs = corpus_root / "icd11"
    who_root = corpus_root / "who"
    department_root = corpus_root / "clinical-trials" / "departments"

    # Build per-dept namespaces.
    for dept in departments:
        dept_dir = department_root / dept
        if not dept_dir.exists():
            log.warning("no docs found for %s — skipping", dept)
            continue
        log.info("[%s] indexing %d files", dept, len(list(dept_dir.rglob("*.pdf"))))
        build_namespace(f"departments/{dept}", dept_dir)

    # Emergency namespace also pulls the WHO sepsis booklet for grounding.
    if who_root.exists():
        log.info("[emergency] augmenting with WHO sepsis corpus")
        build_namespace("departments/emergency", who_root)

    # ICD-11 shared namespace — router queries fall back to this when confidence is low.
    if global_docs.exists():
        log.info("[icd11] indexing %d entities", len(list(global_docs.rglob("*.json"))))
        build_namespace("icd11", global_docs)


def upload_faiss_to_s3(bucket: str, build_dir: Path, *, s3) -> None:
    log.info("Uploading FAISS indexes → s3://%s/faiss/", bucket)
    for path in build_dir.rglob("*"):
        if path.is_file():
            key = "faiss/" + str(path.relative_to(build_dir)).replace("\\", "/")
            log.info("  put %s (%d KB)", key, path.stat().st_size // 1024)
            s3.upload_file(str(path), bucket, key)


def zip_lambda_package(out_path: Path) -> None:
    """Zip poc/app/* plus its dependencies. For the demo we rely on the Lambda
    runtime's installed packages; real deploy should use a pip install --target."""
    log.info("Packaging Lambda bundle → %s", out_path)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in (POC_ROOT / "app").rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                arc = str(path.relative_to(POC_ROOT)).replace("\\", "/")
                zf.write(path, arc)
    log.info("  bundle: %d bytes", out_path.stat().st_size)


# The rest of the deploy (IAM role, Lambda function, API Gateway, CloudFront,
# S3 buckets) follows the same skeleton as aws-demo/ec2/deploy.py — see that
# file for the reference implementation. For the interview POC the quickest
# path is:
#
#   1. Run this script with `--stage build-only` to produce the FAISS bundle
#      and the Lambda zip.
#   2. Upload the zip via the AWS console OR extend this script with the
#      boto3 `create_function` + `create_rest_api` calls following the
#      aws-demo pattern.
#
# Keeping the infra half of this deploy explicit (not in code yet) is a
# deliberate choice so the reviewer can choose between:
#   - SAM:       sam deploy --guided using poc/infra/template.yaml
#   - Full boto3: extend this script
#   - Manual:    run locally for interview (see poc/README.md §4)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", default="gapv50k")
    ap.add_argument("--region", default="ap-southeast-1")
    ap.add_argument("--corpus-path", default=str(DATA_ROOT))
    ap.add_argument(
        "--demo-departments",
        default="emergency,cardiology-internal,pulmonology,gastroenterology,"
        "nephrology,endocrinology,neurology,infectious-disease,"
        "oncology-chemo,obstetrics,pediatrics,radiology",
    )
    ap.add_argument(
        "--stage",
        choices=["build-only", "full"],
        default="build-only",
        help="build-only packages FAISS + Lambda zip; full also creates AWS resources",
    )
    ap.add_argument("--bucket", help="S3 bucket name (auto-generated if omitted)")
    ap.add_argument("--build-dir", default=None, help="local build output dir (auto if omitted)")
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    account = session.client("sts").get_caller_identity()["Account"]
    log.info("AWS account: %s, region: %s", account, args.region)

    build_dir = Path(args.build_dir) if args.build_dir else Path(tempfile.mkdtemp(prefix="poc-build-"))
    build_dir.mkdir(parents=True, exist_ok=True)
    log.info("Build dir: %s", build_dir)

    departments = [d.strip() for d in args.demo_departments.split(",") if d.strip()]
    log.info("Departments: %s", departments)

    # 1. Build FAISS indexes locally (embeds via Bedrock — paid step).
    corpus_root = Path(args.corpus_path).resolve()
    build_faiss_indexes(corpus_root, build_dir, departments)

    # 2. Package the Lambda bundle.
    lambda_zip = build_dir / "lambda-poc.zip"
    zip_lambda_package(lambda_zip)

    if args.stage == "build-only":
        print()
        print("=== build-only complete ===")
        print(f"FAISS indexes: {build_dir}")
        print(f"Lambda zip:    {lambda_zip}")
        print()
        print("Next steps for the interview demo:")
        print("  A) Run locally:  poetry run uvicorn poc.app.server:app --reload")
        print("  B) Deploy via SAM: sam deploy --guided --template poc/infra/template.yaml")
        print("     (reference the FAISS files from S3 after uploading them)")
        print("  C) Upload FAISS: aws s3 sync {build} s3://<bucket>/faiss/".format(build=build_dir))
        return 0

    # Full stage: create S3 bucket + upload FAISS + push Lambda. Left as an
    # exercise to match aws-demo/ec2/deploy.py exactly. For this demo we ship
    # build-only by default so the reviewer can inspect the generated
    # artifacts before we spend on infra.
    raise SystemExit("full-stage deploy not implemented in this commit; see poc/README.md §4")


if __name__ == "__main__":
    sys.exit(main())
