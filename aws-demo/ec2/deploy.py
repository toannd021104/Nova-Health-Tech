"""Deploy the AWS demo to Singapore (ap-southeast-1) using boto3.

Idempotent: safe to re-run; reuses resources by tag.

Usage:
    cd aws-demo/ec2
    python deploy.py

Env / CLI overrides:
    AWS_PROFILE           default: gapv50k
    AWS_REGION            default: ap-southeast-1
    KEYPAIR_NAME          default: HA-sing
    INSTANCE_TYPE         default: t4g.small
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

REGION       = os.environ.get("AWS_REGION", "ap-southeast-1")
PROFILE      = os.environ.get("AWS_PROFILE", "gapv50k")
KEYPAIR_NAME = os.environ.get("KEYPAIR_NAME", "HA-sing")
INSTANCE_TYPE = os.environ.get("INSTANCE_TYPE", "t4g.small")

# Resource tags (see NAMING.md)
TAG_VPC      = "HA-dnBjLW5vdmE"
TAG_SUBNET   = "HA-c3VibmV0LXB1Yg"
TAG_IGW      = "HA-aWd3LW5vdmE"
TAG_RT       = "HA-cnQtcHVi"
TAG_SG       = "HA-c2ctd2Vi"
TAG_ROLE     = "HA-ZWMyLWJlZHJvY2s"
TAG_S3_PFX   = "ha-czmtynvja2v0"
TAG_INSTANCE = "HA-ZWMyLW5vdmE"
TAG_EIP      = "HA-ZWlwLW5vdmE"

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent


def log(m: str) -> None:
    print(f"[deploy] {m}", flush=True)


def session():
    return boto3.Session(profile_name=PROFILE, region_name=REGION)


def find_by_tag(items, key="Name"):
    """Given a list of AWS resource dicts, return the one with Tag Name=key."""
    for it in items:
        for t in it.get("Tags", []) or []:
            if t["Key"] == "Name" and t["Value"] == key:
                return it
    return None


def main() -> int:
    s = session()
    ec2 = s.client("ec2")
    iam = s.client("iam")
    s3  = s.client("s3")
    sts = s.client("sts")
    ssm = s.client("ssm")

    account = sts.get_caller_identity()["Account"]
    log(f"Region: {REGION}  Profile: {PROFILE}  Account: {account}")
    s3_bucket = f"{TAG_S3_PFX}-{account}"

    # ── 1. VPC ─────────────────────────────────────────────────────
    vpcs = ec2.describe_vpcs(Filters=[{"Name": "tag:Name", "Values": [TAG_VPC]}])["Vpcs"]
    if vpcs:
        vpc_id = vpcs[0]["VpcId"]
    else:
        log(f"Creating VPC {TAG_VPC}")
        vpc_id = ec2.create_vpc(
            CidrBlock="10.20.0.0/16",
            TagSpecifications=[{"ResourceType": "vpc",
                                "Tags": [{"Key": "Name", "Value": TAG_VPC}]}],
        )["Vpc"]["VpcId"]
        ec2.get_waiter("vpc_available").wait(VpcIds=[vpc_id])
        ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})
    log(f"VPC: {vpc_id}")

    # ── 2. IGW ─────────────────────────────────────────────────────
    igws = ec2.describe_internet_gateways(
        Filters=[{"Name": "tag:Name", "Values": [TAG_IGW]}]
    )["InternetGateways"]
    if igws:
        igw_id = igws[0]["InternetGatewayId"]
    else:
        log("Creating IGW")
        igw_id = ec2.create_internet_gateway(
            TagSpecifications=[{"ResourceType": "internet-gateway",
                                "Tags": [{"Key": "Name", "Value": TAG_IGW}]}]
        )["InternetGateway"]["InternetGatewayId"]
        ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    log(f"IGW: {igw_id}")

    # ── 3. Subnet ──────────────────────────────────────────────────
    subs = ec2.describe_subnets(
        Filters=[{"Name": "tag:Name", "Values": [TAG_SUBNET]}]
    )["Subnets"]
    if subs:
        subnet_id = subs[0]["SubnetId"]
    else:
        log("Creating subnet")
        subnet_id = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock="10.20.1.0/24",
            AvailabilityZone=f"{REGION}a",
            TagSpecifications=[{"ResourceType": "subnet",
                                "Tags": [{"Key": "Name", "Value": TAG_SUBNET}]}]
        )["Subnet"]["SubnetId"]
        ec2.modify_subnet_attribute(SubnetId=subnet_id,
                                    MapPublicIpOnLaunch={"Value": True})
    log(f"Subnet: {subnet_id}")

    # ── 4. Route table ─────────────────────────────────────────────
    rts = ec2.describe_route_tables(
        Filters=[{"Name": "tag:Name", "Values": [TAG_RT]},
                 {"Name": "vpc-id",   "Values": [vpc_id]}]
    )["RouteTables"]
    if rts:
        rt_id = rts[0]["RouteTableId"]
    else:
        log("Creating route table")
        rt_id = ec2.create_route_table(
            VpcId=vpc_id,
            TagSpecifications=[{"ResourceType": "route-table",
                                "Tags": [{"Key": "Name", "Value": TAG_RT}]}]
        )["RouteTable"]["RouteTableId"]
        ec2.create_route(RouteTableId=rt_id,
                         DestinationCidrBlock="0.0.0.0/0",
                         GatewayId=igw_id)
        ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
    log(f"RT: {rt_id}")

    # ── 5. Security group ──────────────────────────────────────────
    my_ip = urllib.request.urlopen("https://checkip.amazonaws.com", timeout=10).read().decode().strip() + "/32"
    log(f"Restricting SSH to {my_ip}")
    sgs = ec2.describe_security_groups(
        Filters=[{"Name": "tag:Name", "Values": [TAG_SG]},
                 {"Name": "vpc-id",   "Values": [vpc_id]}]
    )["SecurityGroups"]
    if sgs:
        sg_id = sgs[0]["GroupId"]
    else:
        log("Creating SG")
        sg_id = ec2.create_security_group(
            GroupName=TAG_SG,
            Description="Nova demo SG (SSH + HTTP + HTTPS)",
            VpcId=vpc_id,
            TagSpecifications=[{"ResourceType": "security-group",
                                "Tags": [{"Key": "Name", "Value": TAG_SG}]}]
        )["GroupId"]
        ec2.authorize_security_group_ingress(GroupId=sg_id,
            IpPermissions=[
                {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22,
                 "IpRanges": [{"CidrIp": my_ip}]},
                {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80,
                 "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
                {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443,
                 "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
            ])
    log(f"SG: {sg_id}")

    # ── 6. IAM role + instance profile ─────────────────────────────
    role_exists = True
    try:
        iam.get_role(RoleName=TAG_ROLE)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            role_exists = False
        else:
            raise

    if not role_exists:
        log(f"Creating IAM role {TAG_ROLE}")
        trust = {"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow", "Principal": {"Service": "ec2.amazonaws.com"},
             "Action": "sts:AssumeRole"}]}
        iam.create_role(RoleName=TAG_ROLE,
                        AssumeRolePolicyDocument=json.dumps(trust))
        policy = {"Version": "2012-10-17", "Statement": [
            {"Effect": "Allow",
             "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream",
                        "bedrock:Converse", "bedrock:ConverseStream",
                        "bedrock:Retrieve", "bedrock:RetrieveAndGenerate"],
             "Resource": "*"},
            {"Effect": "Allow",
             "Action": ["s3:GetObject", "s3:ListBucket", "s3:PutObject"],
             "Resource": [f"arn:aws:s3:::{s3_bucket}",
                          f"arn:aws:s3:::{s3_bucket}/*"]},
        ]}
        iam.put_role_policy(RoleName=TAG_ROLE,
                            PolicyName="bedrock-and-s3",
                            PolicyDocument=json.dumps(policy))
        try:
            iam.create_instance_profile(InstanceProfileName=TAG_ROLE)
        except ClientError as e:
            if e.response["Error"]["Code"] != "EntityAlreadyExists":
                raise
        try:
            iam.add_role_to_instance_profile(InstanceProfileName=TAG_ROLE,
                                             RoleName=TAG_ROLE)
        except ClientError as e:
            if e.response["Error"]["Code"] != "LimitExceeded":
                raise
        log("Waiting 15s for IAM propagation")
        time.sleep(15)
    log(f"IAM role: {TAG_ROLE}")

    # ── 7. S3 bucket ───────────────────────────────────────────────
    bucket_exists = True
    try:
        s3.head_bucket(Bucket=s3_bucket)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket", "NotFound"):
            bucket_exists = False
        else:
            raise

    if not bucket_exists:
        log(f"Creating S3 bucket {s3_bucket}")
        s3.create_bucket(Bucket=s3_bucket,
                         CreateBucketConfiguration={"LocationConstraint": REGION})
        s3.put_public_access_block(Bucket=s3_bucket,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": True, "IgnorePublicAcls": True,
                "BlockPublicPolicy": True, "RestrictPublicBuckets": True})
        s3.put_bucket_tagging(Bucket=s3_bucket,
                              Tagging={"TagSet": [{"Key": "Name", "Value": TAG_S3_PFX}]})
    log(f"S3: {s3_bucket}")

    # ── 8. Upload demo corpus ──────────────────────────────────────
    log(f"Uploading demo corpus → s3://{s3_bucket}/kb-src/")
    def put(local: Path, key: str):
        s3.upload_file(str(local), s3_bucket, key)
        print(f"  put {key} ({local.stat().st_size:,} bytes)")

    put(REPO / "data/who/B09540-eng.pdf", "kb-src/who/B09540-eng.pdf")
    put(REPO / "data/clinical-trials/protocols/Chapter1.pdf",
        "kb-src/protocols/Chapter1.pdf")
    put(REPO / "data/icd11/mms_root.json", "kb-src/icd11/mms_root.json")
    ent_dir = REPO / "data/icd11/entities"
    for p in sorted(ent_dir.glob("*.json"))[:20]:
        put(p, f"kb-src/icd11/entities/{p.name}")
    log("Demo corpus uploaded")

    # ── 9. AMI lookup ──────────────────────────────────────────────
    ami = ssm.get_parameters(
        Names=["/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-arm64"]
    )["Parameters"][0]["Value"]
    log(f"AMI: {ami}")

    # ── 10. EC2 instance ───────────────────────────────────────────
    insts = ec2.describe_instances(Filters=[
        {"Name": "tag:Name",              "Values": [TAG_INSTANCE]},
        {"Name": "instance-state-name",   "Values": ["running", "pending", "stopped"]},
    ])["Reservations"]
    instance_id = None
    for r in insts:
        for i in r["Instances"]:
            instance_id = i["InstanceId"]
            break
        if instance_id:
            break

    if not instance_id:
        log(f"Launching EC2 {TAG_INSTANCE} ({INSTANCE_TYPE})")
        ud = (HERE / "user_data.sh").read_text(encoding="utf-8")
        resp = ec2.run_instances(
            ImageId=ami, InstanceType=INSTANCE_TYPE,
            KeyName=KEYPAIR_NAME,
            SecurityGroupIds=[sg_id], SubnetId=subnet_id,
            IamInstanceProfile={"Name": TAG_ROLE},
            UserData=ud,
            BlockDeviceMappings=[{
                "DeviceName": "/dev/xvda",
                "Ebs": {"VolumeSize": 20, "VolumeType": "gp3"},
            }],
            TagSpecifications=[{"ResourceType": "instance",
                                "Tags": [{"Key": "Name", "Value": TAG_INSTANCE}]}],
            MaxCount=1, MinCount=1,
        )
        instance_id = resp["Instances"][0]["InstanceId"]
        log("Waiting for instance running")
        ec2.get_waiter("instance_running").wait(InstanceIds=[instance_id])
    log(f"Instance: {instance_id}")

    # ── 11. Elastic IP ─────────────────────────────────────────────
    addrs = ec2.describe_addresses(
        Filters=[{"Name": "tag:Name", "Values": [TAG_EIP]}]
    )["Addresses"]
    if addrs:
        alloc_id = addrs[0]["AllocationId"]
        eip      = addrs[0]["PublicIp"]
        assoc_id = addrs[0].get("AssociationId")
    else:
        log("Allocating Elastic IP")
        ra = ec2.allocate_address(Domain="vpc",
            TagSpecifications=[{"ResourceType": "elastic-ip",
                                "Tags": [{"Key": "Name", "Value": TAG_EIP}]}])
        alloc_id = ra["AllocationId"]
        eip      = ra["PublicIp"]
        assoc_id = None

    if not assoc_id:
        log(f"Associating {eip} → {instance_id}")
        ec2.associate_address(AllocationId=alloc_id, InstanceId=instance_id)
    log(f"Public IP: {eip}")

    # ── 12. Write outputs ──────────────────────────────────────────
    (HERE / ".outputs.env").write_text(
        f"EIP_ADDR={eip}\nINSTANCE_ID={instance_id}\nS3_BUCKET={s3_bucket}\nREGION={REGION}\n",
        encoding="utf-8")

    print()
    log("---------------------------------------------------------------")
    log(" Infra deploy complete.")
    log(f" Public IP:    {eip}")
    log(f" SSH:          ssh -i ..\\..\\HA-sing.pem ec2-user@{eip}")
    log(f" S3 bucket:    s3://{s3_bucket}/kb-src/")
    log(f" Region:       {REGION}")
    log(" Next:         python setup_instance.py")
    log("---------------------------------------------------------------")
    return 0


if __name__ == "__main__":
    sys.exit(main())
