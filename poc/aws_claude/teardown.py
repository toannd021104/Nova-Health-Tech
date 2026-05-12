"""Tear down everything deploy.py created, using the DDB resource map as the truth.

Order of deletion (reverse of creation order, with one exception):
    EIP release  ->  EC2 terminate  ->  IAM role/profile  ->  S3 empty+delete
    ->  SG  ->  RT  ->  subnet  ->  IGW detach+delete  ->  VPC
    ->  DDB table (last, so the table can be read for the whole teardown)

Usage:
    python poc/aws_claude/teardown.py --profile gapv50k --region ap-southeast-1
    python poc/aws_claude/teardown.py --yes          # skip confirmation
"""
from __future__ import annotations

import argparse
import base64
import logging
import sys
import time

import boto3
from botocore.exceptions import ClientError

log = logging.getLogger("poc.aws_claude.teardown")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def ha(name: str) -> str:
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")


T_DDB = ha("poc-claude-map")
STACK_TAG = "poc-claude"


def load_map(ddb) -> dict[str, dict]:
    """Return {logical_name: {encoded_name, resource_type, arn_or_id, ...}}."""
    out: dict[str, dict] = {}
    try:
        resp = ddb.scan(TableName=T_DDB)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ResourceNotFoundException":
            log.warning("DDB table %s not found — nothing to tear down (or already deleted)", T_DDB)
            return {}
        raise
    for item in resp.get("Items", []):
        stack = item.get("stack_tag", {}).get("S", "")
        if stack and stack != STACK_TAG:
            continue
        out[item["logical_name"]["S"]] = {
            "encoded_name": item.get("encoded_name", {}).get("S", ""),
            "resource_type": item.get("resource_type", {}).get("S", ""),
            "arn_or_id": item.get("arn_or_id", {}).get("S", ""),
        }
    return out


def delete_eip(ec2, entry: dict) -> None:
    # arn_or_id stored as "eipalloc-...:1.2.3.4"
    raw = entry["arn_or_id"]
    alloc_id = raw.split(":")[0]
    try:
        addrs = ec2.describe_addresses(AllocationIds=[alloc_id])["Addresses"]
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "InvalidAllocationID.NotFound":
            return
        raise
    for a in addrs:
        if assoc := a.get("AssociationId"):
            log.info("Disassociating EIP %s", a["PublicIp"])
            ec2.disassociate_address(AssociationId=assoc)
        log.info("Releasing EIP %s", a["PublicIp"])
        ec2.release_address(AllocationId=a["AllocationId"])


def delete_ec2(ec2, entry: dict) -> None:
    iid = entry["arn_or_id"]
    try:
        ec2.describe_instances(InstanceIds=[iid])
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "InvalidInstanceID.NotFound":
            return
        raise
    log.info("Terminating EC2 %s", iid)
    ec2.terminate_instances(InstanceIds=[iid])
    ec2.get_waiter("instance_terminated").wait(InstanceIds=[iid])


def delete_role(iam, entry: dict) -> None:
    role = entry["encoded_name"]
    try:
        for policy in iam.list_role_policies(RoleName=role).get("PolicyNames", []):
            iam.delete_role_policy(RoleName=role, PolicyName=policy)
        try:
            iam.remove_role_from_instance_profile(InstanceProfileName=role, RoleName=role)
        except ClientError:
            pass
        try:
            iam.delete_instance_profile(InstanceProfileName=role)
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "NoSuchEntity":
                raise
        log.info("Deleting IAM role %s", role)
        iam.delete_role(RoleName=role)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "NoSuchEntity":
            return
        raise


def delete_bucket(s3, entry: dict) -> None:
    bucket = entry["encoded_name"]
    try:
        log.info("Emptying S3 bucket %s", bucket)
        paginator = s3.get_paginator("list_object_versions")
        for page in paginator.paginate(Bucket=bucket):
            to_del: list[dict] = []
            for v in page.get("Versions", []):
                to_del.append({"Key": v["Key"], "VersionId": v["VersionId"]})
            for m in page.get("DeleteMarkers", []):
                to_del.append({"Key": m["Key"], "VersionId": m["VersionId"]})
            if to_del:
                s3.delete_objects(Bucket=bucket, Delete={"Objects": to_del, "Quiet": True})
        # Cover the non-versioned path (we didn't enable versioning, so this catches everything).
        page_iter = s3.get_paginator("list_objects_v2").paginate(Bucket=bucket)
        for page in page_iter:
            objs = [{"Key": o["Key"]} for o in page.get("Contents", [])]
            if objs:
                s3.delete_objects(Bucket=bucket, Delete={"Objects": objs, "Quiet": True})
        log.info("Deleting S3 bucket %s", bucket)
        s3.delete_bucket(Bucket=bucket)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("NoSuchBucket", "404"):
            return
        raise


def delete_sg(ec2, entry: dict) -> None:
    sg_id = entry["arn_or_id"]
    try:
        log.info("Deleting SG %s", sg_id)
        ec2.delete_security_group(GroupId=sg_id)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("InvalidGroup.NotFound", "InvalidGroupId.NotFound"):
            return
        raise


def delete_rt(ec2, entry: dict) -> None:
    rt_id = entry["arn_or_id"]
    try:
        rt = ec2.describe_route_tables(RouteTableIds=[rt_id])["RouteTables"][0]
        for assoc in rt.get("Associations", []):
            if assoc.get("Main"):
                continue
            ec2.disassociate_route_table(AssociationId=assoc["RouteTableAssociationId"])
        log.info("Deleting RT %s", rt_id)
        ec2.delete_route_table(RouteTableId=rt_id)
    except ClientError as exc:
        if exc.response["Error"]["Code"] in ("InvalidRouteTableID.NotFound",):
            return
        raise


def delete_subnet(ec2, entry: dict) -> None:
    sn_id = entry["arn_or_id"]
    try:
        log.info("Deleting subnet %s", sn_id)
        ec2.delete_subnet(SubnetId=sn_id)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "InvalidSubnetID.NotFound":
            return
        raise


def delete_igw(ec2, entry: dict, vpc_id: str | None) -> None:
    igw_id = entry["arn_or_id"]
    try:
        if vpc_id:
            try:
                ec2.detach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
            except ClientError as exc:
                if exc.response["Error"]["Code"] != "Gateway.NotAttached":
                    raise
        log.info("Deleting IGW %s", igw_id)
        ec2.delete_internet_gateway(InternetGatewayId=igw_id)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "InvalidInternetGatewayID.NotFound":
            return
        raise


def delete_vpc(ec2, entry: dict) -> None:
    vpc_id = entry["arn_or_id"]
    try:
        log.info("Deleting VPC %s", vpc_id)
        ec2.delete_vpc(VpcId=vpc_id)
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "InvalidVpcID.NotFound":
            return
        raise


def delete_ddb(ddb) -> None:
    try:
        log.info("Deleting DDB table %s (last)", T_DDB)
        ddb.delete_table(TableName=T_DDB)
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", default="gapv50k")
    ap.add_argument("--region", default="ap-southeast-1")
    ap.add_argument("--yes", action="store_true", help="skip confirmation prompt")
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    ddb = session.client("dynamodb")
    ec2 = session.client("ec2")
    iam = session.client("iam")
    s3 = session.client("s3")

    resource_map = load_map(ddb)
    if not resource_map:
        log.info("Nothing to tear down.")
        return 0

    log.info("Stack %s has %d tracked resources:", STACK_TAG, len(resource_map))
    for name, entry in resource_map.items():
        log.info("  %-20s  %-10s  %s", name, entry["resource_type"], entry["arn_or_id"])

    if not args.yes:
        if input("\nProceed with teardown? [y/N]: ").strip().lower() != "y":
            log.info("Aborted.")
            return 0

    vpc_id = resource_map.get("poc-claude-vpc", {}).get("arn_or_id")

    # EIP release first so EC2 terminate doesn't leave a dangling association.
    if "poc-claude-eip" in resource_map:
        delete_eip(ec2, resource_map["poc-claude-eip"])
    if "poc-claude-ec2" in resource_map:
        delete_ec2(ec2, resource_map["poc-claude-ec2"])
    if "poc-claude-role" in resource_map:
        delete_role(iam, resource_map["poc-claude-role"])
    if "poc-claude-bucket" in resource_map:
        delete_bucket(s3, resource_map["poc-claude-bucket"])

    # Networking teardown. SG before subnet/RT so any ENIs released by EC2
    # have time to clear; a 10s sleep covers the lingering ENI race AWS has
    # after terminate_instances returns.
    time.sleep(10)

    if "poc-claude-sg" in resource_map:
        delete_sg(ec2, resource_map["poc-claude-sg"])
    if "poc-claude-rt" in resource_map:
        delete_rt(ec2, resource_map["poc-claude-rt"])
    if "poc-claude-subnet" in resource_map:
        delete_subnet(ec2, resource_map["poc-claude-subnet"])
    if "poc-claude-igw" in resource_map:
        delete_igw(ec2, resource_map["poc-claude-igw"], vpc_id)
    if "poc-claude-vpc" in resource_map:
        delete_vpc(ec2, resource_map["poc-claude-vpc"])

    delete_ddb(ddb)
    log.info("Teardown complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
