"""Deploy the AWS + Claude PoC (Version A) — reduced-data 10-day demo.

What this creates in `ap-southeast-1` (profile `gapv50k` by default):

    DynamoDB resource-map    (HA-<b64>)   ← logical → encoded → ARN mapping
    VPC + subnet + IGW + RT + SG
    IAM role + instance profile          (Bedrock + S3 + DDB read/write)
    S3 bucket                            (ha-<b64>-<acct>)  holds the reduced corpus
    EC2 t4g.small                        (HA-<b64>)         runs the FastAPI app
    Elastic IP                           (HA-<b64>)         public URL for the reviewer

Everything is idempotent — re-running reuses by tag and skips the create.

Corpus reduction (per user brief "just reduce the amount"):
    - WHO:           only `data/who/B09540-eng.pdf` (therapeutics & COVID-19)
    - ICD-11:        only `mms_root.json` + first 5 entities
    - Departments:   first PDF per department folder (12 PDFs, not 36)

That keeps the FAISS build under 1 minute and the S3 footprint under 50 MB.

Usage:
    python poc/aws_claude/deploy.py --profile gapv50k --region ap-southeast-1

Teardown:
    python poc/aws_claude/teardown.py --profile gapv50k --region ap-southeast-1
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import logging
import os
import sys
import time
import urllib.request
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

log = logging.getLogger("poc.aws_claude.deploy")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
STACK_TAG = "poc-claude"


def ha(name: str) -> str:
    """HA-<base64url(name)> tag value, padding stripped. Matches NAMING.md."""
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")


def ha_s3(name: str, account_id: str) -> str:
    """Lowercased DNS-safe S3 bucket name. Account suffix guarantees uniqueness."""
    encoded = base64.urlsafe_b64encode(name.encode()).decode().rstrip("=").lower()
    return f"ha-{encoded}-{account_id}"


# ---------- Logical names — every resource in one place ----------
N_DDB = "poc-claude-map"
N_VPC = "poc-claude-vpc"
N_SUBNET = "poc-claude-subnet"
N_IGW = "poc-claude-igw"
N_RT = "poc-claude-rt"
N_SG = "poc-claude-sg"
N_ROLE = "poc-claude-role"
N_BUCKET = "poc-claude-bucket"
N_EC2 = "poc-claude-ec2"
N_EIP = "poc-claude-eip"

T_DDB = ha(N_DDB)
T_VPC = ha(N_VPC)
T_SUBNET = ha(N_SUBNET)
T_IGW = ha(N_IGW)
T_RT = ha(N_RT)
T_SG = ha(N_SG)
T_ROLE = ha(N_ROLE)
T_EC2 = ha(N_EC2)
T_EIP = ha(N_EIP)


def record(ddb, region: str, logical: str, encoded: str, rtype: str, arn_or_id: str) -> None:
    """Upsert one row into the resource-map table."""
    ddb.put_item(
        TableName=T_DDB,
        Item={
            "logical_name": {"S": logical},
            "encoded_name": {"S": encoded},
            "resource_type": {"S": rtype},
            "arn_or_id": {"S": arn_or_id},
            "region": {"S": region},
            "stack_tag": {"S": STACK_TAG},
            "created_at": {"S": dt.datetime.now(dt.timezone.utc).isoformat()},
        },
    )


# ---------- 1. DynamoDB resource-map (must come first) ----------
def ensure_ddb(ddb, region: str) -> None:
    try:
        ddb.describe_table(TableName=T_DDB)
        log.info("DDB table %s already exists", T_DDB)
        return
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
    log.info("Creating DDB resource-map table %s", T_DDB)
    ddb.create_table(
        TableName=T_DDB,
        AttributeDefinitions=[{"AttributeName": "logical_name", "AttributeType": "S"}],
        KeySchema=[{"AttributeName": "logical_name", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
        Tags=[
            {"Key": "Name", "Value": T_DDB},
            {"Key": "Owner", "Value": "nova-health-poc-claude"},
            {"Key": "Stack", "Value": STACK_TAG},
        ],
    )
    ddb.get_waiter("table_exists").wait(TableName=T_DDB)
    # Self-reference: record the table itself.
    record(ddb, region, N_DDB, T_DDB, "ddb", f"arn:aws:dynamodb:{region}:*:table/{T_DDB}")


# ---------- 2. VPC + subnet + IGW + route table ----------
def ensure_network(ec2, ddb, region: str) -> dict[str, str]:
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "tag:Name", "Values": [T_VPC]}])["Vpcs"]
    if vpcs:
        vpc_id = vpcs[0]["VpcId"]
    else:
        log.info("Creating VPC %s", T_VPC)
        vpc_id = ec2.create_vpc(
            CidrBlock="10.30.0.0/16",
            TagSpecifications=[{
                "ResourceType": "vpc",
                "Tags": [
                    {"Key": "Name", "Value": T_VPC},
                    {"Key": "Owner", "Value": "nova-health-poc-claude"},
                    {"Key": "Stack", "Value": STACK_TAG},
                ],
            }],
        )["Vpc"]["VpcId"]
        ec2.get_waiter("vpc_available").wait(VpcIds=[vpc_id])
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})
    record(ddb, region, N_VPC, T_VPC, "vpc", vpc_id)

    igws = ec2.describe_internet_gateways(
        Filters=[{"Name": "tag:Name", "Values": [T_IGW]}]
    )["InternetGateways"]
    if igws:
        igw_id = igws[0]["InternetGatewayId"]
    else:
        log.info("Creating IGW %s", T_IGW)
        igw_id = ec2.create_internet_gateway(
            TagSpecifications=[{
                "ResourceType": "internet-gateway",
                "Tags": [
                    {"Key": "Name", "Value": T_IGW},
                    {"Key": "Owner", "Value": "nova-health-poc-claude"},
                    {"Key": "Stack", "Value": STACK_TAG},
                ],
            }],
        )["InternetGateway"]["InternetGatewayId"]
    # attach_internet_gateway is idempotent enough for the PoC — check first
    igw = ec2.describe_internet_gateways(InternetGatewayIds=[igw_id])["InternetGateways"][0]
    if not igw.get("Attachments"):
        ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    record(ddb, region, N_IGW, T_IGW, "igw", igw_id)

    subs = ec2.describe_subnets(Filters=[{"Name": "tag:Name", "Values": [T_SUBNET]}])["Subnets"]
    if subs:
        subnet_id = subs[0]["SubnetId"]
    else:
        log.info("Creating subnet %s", T_SUBNET)
        subnet_id = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock="10.30.1.0/24",
            AvailabilityZone=f"{region}a",
            TagSpecifications=[{
                "ResourceType": "subnet",
                "Tags": [
                    {"Key": "Name", "Value": T_SUBNET},
                    {"Key": "Owner", "Value": "nova-health-poc-claude"},
                    {"Key": "Stack", "Value": STACK_TAG},
                ],
            }],
        )["Subnet"]["SubnetId"]
        ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={"Value": True})
    record(ddb, region, N_SUBNET, T_SUBNET, "subnet", subnet_id)

    rts = ec2.describe_route_tables(
        Filters=[
            {"Name": "tag:Name", "Values": [T_RT]},
            {"Name": "vpc-id", "Values": [vpc_id]},
        ]
    )["RouteTables"]
    if rts:
        rt_id = rts[0]["RouteTableId"]
    else:
        log.info("Creating route table %s", T_RT)
        rt_id = ec2.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[{
                "ResourceType": "route-table",
                "Tags": [
                    {"Key": "Name", "Value": T_RT},
                    {"Key": "Owner", "Value": "nova-health-poc-claude"},
                    {"Key": "Stack", "Value": STACK_TAG},
                ],
            }],
        )["RouteTable"]["RouteTableId"]
        ec2.create_route(
            RouteTableId=rt_id,
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=igw_id,
        )
        ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
    record(ddb, region, N_RT, T_RT, "rt", rt_id)

    return {"vpc_id": vpc_id, "subnet_id": subnet_id, "igw_id": igw_id, "rt_id": rt_id}


def ensure_sg(ec2, ddb, region: str, vpc_id: str) -> str:
    try:
        my_ip = urllib.request.urlopen(
            "https://checkip.amazonaws.com", timeout=10
        ).read().decode().strip() + "/32"
    except Exception:  # noqa: BLE001
        my_ip = "0.0.0.0/0"
    log.info("SSH CIDR: %s", my_ip)

    sgs = ec2.describe_security_groups(
        Filters=[
            {"Name": "tag:Name", "Values": [T_SG]},
            {"Name": "vpc-id", "Values": [vpc_id]},
        ]
    )["SecurityGroups"]
    if sgs:
        sg_id = sgs[0]["GroupId"]
    else:
        log.info("Creating SG %s", T_SG)
        sg_id = ec2.create_security_group(
            GroupName=T_SG,
            Description="Nova PoC Claude SG (SSH restricted + HTTP 80)",
            VpcId=vpc_id,
            TagSpecifications=[{
                "ResourceType": "security-group",
                "Tags": [
                    {"Key": "Name", "Value": T_SG},
                    {"Key": "Owner", "Value": "nova-health-poc-claude"},
                    {"Key": "Stack", "Value": STACK_TAG},
                ],
            }],
        )["GroupId"]
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22,
                 "IpRanges": [{"CidrIp": my_ip, "Description": "SSH from deployer"}]},
                {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80,
                 "IpRanges": [{"CidrIp": "0.0.0.0/0", "Description": "Public HTTP for reviewer"}]},
            ],
        )
    record(ddb, region, N_SG, T_SG, "sg", sg_id)
    return sg_id


# ---------- 3. IAM role + instance profile ----------
def ensure_role(iam, ddb, region: str, bucket: str) -> str:
    try:
        iam.get_role(RoleName=T_ROLE)
        role_exists = True
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "NoSuchEntity":
            raise
        role_exists = False

    if not role_exists:
        log.info("Creating IAM role %s", T_ROLE)
        trust = {"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow",
             "Principal": {"Service": "ec2.amazonaws.com"},
             "Action": "sts:AssumeRole"}]}
        iam.create_role(
            RoleName=T_ROLE,
            AssumeRolePolicyDocument=json.dumps(trust),
            Tags=[
                {"Key": "Name", "Value": T_ROLE},
                {"Key": "Owner", "Value": "nova-health-poc-claude"},
                {"Key": "Stack", "Value": STACK_TAG},
            ],
        )
        policy = {"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow",
             "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream",
                        "bedrock:Converse", "bedrock:ConverseStream",
                        "bedrock:Rerank", "bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
             "Resource": "*"},
            {"Effect": "Allow",
             "Action": ["s3:GetObject", "s3:ListBucket", "s3:PutObject"],
             "Resource": [f"arn:aws:s3:::{bucket}", f"arn:aws:s3:::{bucket}/*"]},
            {"Effect": "Allow",
             "Action": ["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan"],
             "Resource": f"arn:aws:dynamodb:{region}:*:table/{T_DDB}"},
        ]}
        iam.put_role_policy(RoleName=T_ROLE, PolicyName="bedrock-s3-ddb",
                            PolicyDocument=json.dumps(policy))
        try:
            iam.create_instance_profile(InstanceProfileName=T_ROLE)
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "EntityAlreadyExists":
                raise
        try:
            iam.add_role_to_instance_profile(InstanceProfileName=T_ROLE, RoleName=T_ROLE)
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "LimitExceeded":
                raise
        log.info("Waiting 15s for IAM propagation")
        time.sleep(15)
    role_arn = iam.get_role(RoleName=T_ROLE)["Role"]["Arn"]
    record(ddb, region, N_ROLE, T_ROLE, "role", role_arn)
    return T_ROLE


# ---------- 4. S3 bucket + reduced-corpus upload ----------
def ensure_bucket(s3, ddb, region: str, bucket: str) -> None:
    try:
        s3.head_bucket(Bucket=bucket)
        log.info("S3 bucket %s already exists", bucket)
    except ClientError as exc:
        code = exc.response["Error"]["Code"]
        if code not in ("404", "NoSuchBucket", "NotFound"):
            raise
        log.info("Creating S3 bucket %s", bucket)
        s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
        s3.put_public_access_block(
            Bucket=bucket,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True, "IgnorePublicAcls": True,
                "BlockPublicPolicy": True, "RestrictPublicBuckets": True,
            },
        )
        s3.put_bucket_tagging(
            Bucket=bucket,
            Tagging={"TagSet": [
                {"Key": "Name", "Value": bucket},
                {"Key": "Owner", "Value": "nova-health-poc-claude"},
                {"Key": "Stack", "Value": STACK_TAG},
            ]},
        )
    record(ddb, region, N_BUCKET, bucket, "s3", f"arn:aws:s3:::{bucket}")


def upload_reduced_corpus(s3, bucket: str) -> dict[str, int]:
    """Upload only the slices the PoC needs — not the whole `data/` tree."""
    uploaded = {"who": 0, "icd11": 0, "departments": 0}

    def put(local: Path, key: str) -> None:
        if not local.exists():
            log.warning("corpus file missing, skipping: %s", local)
            return
        s3.upload_file(str(local), bucket, key)
        log.info("  put s3://%s/%s (%d KB)", bucket, key, local.stat().st_size // 1024)

    # WHO — only B09540-eng.pdf per the user brief.
    put(REPO / "data/who/B09540-eng.pdf", "kb-src/who/B09540-eng.pdf")
    uploaded["who"] = 1

    # ICD-11 — root + first 5 entities (router fallback namespace).
    put(REPO / "data/icd11/mms_root.json", "kb-src/icd11/mms_root.json")
    icd_dir = REPO / "data/icd11/entities"
    if icd_dir.exists():
        for p in sorted(icd_dir.glob("*.json"))[:5]:
            put(p, f"kb-src/icd11/entities/{p.name}")
            uploaded["icd11"] += 1

    # Departments — first PDF of each dept folder. The 12 dept agents stay
    # wired up; each just has a single representative reference document.
    dept_root = REPO / "data/clinical-trials/departments"
    if dept_root.exists():
        for dept_dir in sorted(dept_root.iterdir()):
            if not dept_dir.is_dir():
                continue
            pdfs = sorted(dept_dir.glob("*.pdf"))
            if not pdfs:
                continue
            first = pdfs[0]
            put(first, f"kb-src/departments/{dept_dir.name}/{first.name}")
            uploaded["departments"] += 1

    log.info("Corpus uploaded — who=%d, icd11=%d, departments=%d",
             uploaded["who"], uploaded["icd11"], uploaded["departments"])
    return uploaded


# ---------- 5. EC2 instance ----------
def pick_ami(ssm) -> str:
    ami = ssm.get_parameters(
        Names=["/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"]
    )["Parameters"][0]["Value"]
    log.info("AMI (AL2023 arm64): %s", ami)
    return ami


def ensure_ec2(ec2, ddb, region: str, ami: str, subnet_id: str,
               sg_id: str, role_name: str, key_name: str,
               instance_type: str, user_data: str) -> str:
    insts = ec2.describe_instances(Filters=[
        {"Name": "tag:Name", "Values": [T_EC2]},
        {"Name": "instance-state-name",
         "Values": ["running", "pending", "stopped", "stopping"]},
    ])["Reservations"]
    for r in insts:
        for i in r["Instances"]:
            record(ddb, region, N_EC2, T_EC2, "ec2", i["InstanceId"])
            return i["InstanceId"]

    log.info("Launching EC2 %s (%s)", T_EC2, instance_type)
    resp = ec2.run_instances(
        ImageId=ami, InstanceType=instance_type,
        KeyName=key_name,
        SecurityGroupIds=[sg_id], SubnetId=subnet_id,
        IamInstanceProfile={"Name": role_name},
        UserData=user_data,
        BlockDeviceMappings=[{
            "DeviceName": "/dev/xvda",
            "Ebs": {"VolumeSize": 20, "VolumeType": "gp3"},
        }],
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": T_EC2},
                {"Key": "Owner", "Value": "nova-health-poc-claude"},
                {"Key": "Stack", "Value": STACK_TAG},
            ],
        }],
        MaxCount=1, MinCount=1,
    )
    instance_id = resp["Instances"][0]["InstanceId"]
    log.info("Waiting for instance running")
    ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
    record(ddb, region, N_EC2, T_EC2, "ec2", instance_id)
    return instance_id


def ensure_eip(ec2, ddb, region: str, instance_id: str) -> str:
    addrs = ec2.describe_addresses(
        Filters=[{"Name": "tag:Name", "Values": [T_EIP]}]
    )["Addresses"]
    if addrs:
        alloc_id = addrs[0]["AllocationId"]
        eip = addrs[0]["PublicIp"]
        assoc_id = addrs[0].get("AssociationId")
    else:
        log.info("Allocating Elastic IP %s", T_EIP)
        ra = ec2.allocate_address(
            Domain="vpc",
            TagSpecifications=[{
                "ResourceType": "elastic-ip",
                "Tags": [
                    {"Key": "Name", "Value": T_EIP},
                    {"Key": "Owner", "Value": "nova-health-poc-claude"},
                    {"Key": "Stack", "Value": STACK_TAG},
                ],
            }],
        )
        alloc_id = ra["AllocationId"]
        eip = ra["PublicIp"]
        assoc_id = None
    if not assoc_id:
        log.info("Associating %s -> %s", eip, instance_id)
        ec2.associate_address(AllocationId=alloc_id, InstanceId=instance_id)
    record(ddb, region, N_EIP, T_EIP, "eip", f"{alloc_id}:{eip}")
    return eip


# ---------- User data (runs as root on first boot) ----------
def build_user_data(region: str, bucket: str, stack_tag: str) -> str:
    # Keep UserData small — it only installs OS deps, the app tarball is
    # pushed later via setup_instance.py (same pattern as aws-demo/ec2).
    return f"""#!/bin/bash
exec > /var/log/user-data.log 2>&1
set -x
dnf -y update
dnf -y install python3.11 python3.11-pip git tar gzip

CADDY_VER=2.10.0
curl -L -o /tmp/caddy.tar.gz \\
    "https://github.com/caddyserver/caddy/releases/download/v${{CADDY_VER}}/caddy_${{CADDY_VER}}_linux_arm64.tar.gz"
tar xzf /tmp/caddy.tar.gz -C /usr/local/bin caddy
chmod +x /usr/local/bin/caddy

ln -sf /usr/bin/python3.11 /usr/local/bin/python

mkdir -p /opt/nova
chown ec2-user:ec2-user /opt/nova

echo 'AWS_REGION={region}'      > /etc/profile.d/nova-env.sh
echo 'S3_BUCKET={bucket}'       >> /etc/profile.d/nova-env.sh
echo 'STACK_TAG={stack_tag}'    >> /etc/profile.d/nova-env.sh

touch /var/lib/cloud/instance/user-data-done
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", default="gapv50k")
    ap.add_argument("--region", default="ap-southeast-1")
    ap.add_argument("--keypair", default="HA-sing",
                    help="existing EC2 key pair name (default matches aws-demo/ec2)")
    ap.add_argument("--instance-type", default="t4g.small")
    args = ap.parse_args()

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    account = session.client("sts").get_caller_identity()["Account"]
    log.info("Profile=%s  Region=%s  Account=%s", args.profile, args.region, account)

    bucket = ha_s3(N_BUCKET, account)
    log.info("S3 bucket will be: %s", bucket)

    ec2 = session.client("ec2")
    iam = session.client("iam")
    s3 = session.client("s3")
    ssm = session.client("ssm")
    ddb = session.client("dynamodb")

    # Order matters — map table first so every subsequent step can record to it.
    ensure_ddb(ddb, args.region)
    net = ensure_network(ec2, ddb, args.region)
    sg_id = ensure_sg(ec2, ddb, args.region, net["vpc_id"])
    ensure_bucket(s3, ddb, args.region, bucket)
    upload_reduced_corpus(s3, bucket)
    role_name = ensure_role(iam, ddb, args.region, bucket)
    ami = pick_ami(ssm)
    user_data = build_user_data(args.region, bucket, STACK_TAG)
    instance_id = ensure_ec2(
        ec2, ddb, args.region, ami, net["subnet_id"], sg_id,
        role_name, args.keypair, args.instance_type, user_data,
    )
    eip = ensure_eip(ec2, ddb, args.region, instance_id)

    (HERE / ".outputs.env").write_text(
        f"EIP_ADDR={eip}\nINSTANCE_ID={instance_id}\nS3_BUCKET={bucket}\n"
        f"REGION={args.region}\nDDB_TABLE={T_DDB}\n",
        encoding="utf-8",
    )

    log.info("--------------------------------------------------")
    log.info(" Infra deploy complete.")
    log.info(" Public IP:      %s", eip)
    log.info(" Instance ID:    %s", instance_id)
    log.info(" S3 bucket:      s3://%s/kb-src/", bucket)
    log.info(" Resource map:   DynamoDB %s", T_DDB)
    log.info(" Region:         %s", args.region)
    log.info(" Next:           python poc/aws_claude/setup_instance.py")
    log.info("--------------------------------------------------")
    return 0


if __name__ == "__main__":
    sys.exit(main())
