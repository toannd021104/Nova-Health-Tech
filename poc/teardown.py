"""Teardown for the POC — deletes anything tagged POC-HA-<b64>.

Run with:
    python poc/teardown.py --profile gapv50k --region ap-southeast-1
"""
from __future__ import annotations

import argparse
import logging
import sys

import boto3

log = logging.getLogger("poc.teardown")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", default="gapv50k")
    ap.add_argument("--region", default="ap-southeast-1")
    ap.add_argument("--prefix", default="POC-HA-", help="tag prefix to match")
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    rgta = session.client("resourcegroupstaggingapi")

    log.info("Searching for resources tagged Owner with prefix %s in %s", args.prefix, args.region)
    paginator = rgta.get_paginator("get_resources")
    to_delete: list[dict] = []
    for page in paginator.paginate(
        TagFilters=[{"Key": "Owner", "Values": ["nova-health-poc"]}]
    ):
        for r in page.get("ResourceTagMappingList", []):
            to_delete.append(r)

    if not to_delete:
        log.info("No POC resources found — nothing to delete.")
        return 0

    log.info("Will delete %d resources:", len(to_delete))
    for r in to_delete:
        log.info("  %s", r["ResourceARN"])

    resp = input("Proceed? [y/N]: ")
    if resp.strip().lower() != "y":
        log.info("Aborted.")
        return 0

    # Deletion logic is service-specific. Match the create order in deploy.py:
    # CloudFront → API Gateway → Lambda → IAM role → S3 bucket. For the
    # interview POC the concrete deletion calls follow the skeleton in
    # aws-demo/ec2/deploy.py. Keeping this stub explicit so the reviewer
    # chooses which resources to purge.
    log.warning(
        "Teardown of individual resource types is not implemented in this "
        "commit. Delete via the AWS console or extend this script to match "
        "the create order in poc/deploy.py (CloudFront → APIGW → Lambda → "
        "IAM role → S3)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
