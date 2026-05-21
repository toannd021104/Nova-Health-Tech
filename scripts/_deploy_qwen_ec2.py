"""Deploy the aws_qwen PoC to a new EC2 instance with public IP.

Creates:
  - EC2 t4g.small (ARM, same as aws_claude instance)
  - Elastic IP
  - User data script installs Python, pip deps, starts uvicorn on port 80

The student model calls the SageMaker Endpoint (HA-c20tc3R1ZGVudC1lcA).
The teacher model calls Bedrock (Nova Pro, ap-southeast-1).
"""
import boto3
import base64
import time
import subprocess
import tarfile
import os
import sys
from pathlib import Path

AWS_PROFILE = "gapv50k"
REGION = "ap-southeast-1"
SUBNET_ID = "subnet-002f4bd416813c8e6"
SG_ID = "sg-0da0e74e1cd8cc643"
INSTANCE_PROFILE = "HA-ZWMyLWJlZHJvY2s"
KEY_NAME = "HA-sing"
INSTANCE_TYPE = "t4g.small"
AMI_ID = "ami-0a2d1c1bb8606359f"  # Amazon Linux 2023 ARM64 ap-southeast-1 (latest)

def ha(name):
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")

EC2_NAME = ha("ec2-qwen")   # HA-ZWMyLXF3ZW4
EIP_NAME = ha("eip-qwen")   # HA-ZWlwLXF3ZW4

USER_DATA = """#!/bin/bash
set -e
yum update -y
yum install -y python3.11 python3.11-pip

# Create venv
python3.11 -m venv /opt/nova-qwen/venv
source /opt/nova-qwen/venv/bin/activate

# Install deps
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" pydantic boto3 langchain-core langchain-community langchain-text-splitters langgraph redis numpy

# Extract app
cd /home/ec2-user
tar xzf nova-qwen-app.tar.gz

# Create systemd service
cat > /etc/systemd/system/nova-qwen.service << 'EOF'
[Unit]
Description=Nova Clinical AI — PoC Version B (Qwen)
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user
Environment=PATH=/opt/nova-qwen/venv/bin:/usr/bin
Environment=AWS_REGION=ap-southeast-1
Environment=BEDROCK_KB_ID=MUEEBGPRSJ
Environment=BEDROCK_GRAPHRAG_KB_ID=FU6SXD0B8B
Environment=STUDENT_ENDPOINT_NAME=HA-c20tc3R1ZGVudC1lcA
ExecStart=/opt/nova-qwen/venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 80
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nova-qwen.service
systemctl start nova-qwen.service
"""

def main():
    session = boto3.Session(profile_name=AWS_PROFILE, region_name=REGION)
    ec2 = session.client("ec2")

    # 1. Package the app
    HERE = Path(__file__).resolve().parent.parent / "poc" / "aws_qwen"
    app_dir = HERE / "app"
    tar_path = HERE / "nova-qwen-app.tar.gz"

    print(f"Packaging {app_dir} ...")
    if tar_path.exists():
        tar_path.unlink()
    with tarfile.open(str(tar_path), "w:gz") as tar:
        for root, dirs, files in os.walk(str(app_dir)):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for f in files:
                if f.endswith(".pyc"):
                    continue
                full_path = os.path.join(root, f)
                arcname = os.path.relpath(full_path, str(HERE))
                tar.add(full_path, arcname=arcname)
    print(f"Tarball: {tar_path.stat().st_size:,} bytes")

    # 2. Launch EC2
    print(f"Launching EC2 {INSTANCE_TYPE} ...")
    resp = ec2.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MinCount=1, MaxCount=1,
        SubnetId=SUBNET_ID,
        SecurityGroupIds=[SG_ID],
        IamInstanceProfile={"Name": INSTANCE_PROFILE},
        UserData=USER_DATA,
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": EC2_NAME},
                {"Key": "Owner", "Value": "nova-health-poc"},
                {"Key": "LogicalName", "Value": "ec2-qwen"},
            ],
        }],
    )
    instance_id = resp["Instances"][0]["InstanceId"]
    print(f"Instance: {instance_id}")

    # 3. Wait for running
    print("Waiting for instance to be running ...")
    waiter = ec2.get_waiter("instance_running")
    waiter.wait(InstanceIds=[instance_id])
    print("Instance running.")

    # 4. Allocate and associate EIP
    eip_resp = ec2.allocate_address(Domain="vpc", TagSpecifications=[{
        "ResourceType": "elastic-ip",
        "Tags": [
            {"Key": "Name", "Value": EIP_NAME},
            {"Key": "Owner", "Value": "nova-health-poc"},
            {"Key": "LogicalName", "Value": "eip-qwen"},
        ],
    }])
    eip = eip_resp["PublicIp"]
    alloc_id = eip_resp["AllocationId"]
    print(f"Elastic IP: {eip}")

    ec2.associate_address(InstanceId=instance_id, AllocationId=alloc_id)
    print(f"EIP associated to {instance_id}")

    # 5. Wait for SSH then SCP the tarball
    print("Waiting 30s for SSH to be ready ...")
    time.sleep(30)

    key_path = str(Path(__file__).resolve().parent.parent / "HA-sing.pem")
    host = eip

    def ssh(cmd):
        full = ["ssh", "-i", key_path, "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null", "-o", "ConnectTimeout=15",
                f"ec2-user@{host}", cmd]
        return subprocess.run(full, capture_output=True, timeout=120)

    def scp(local, remote):
        full = ["scp", "-i", key_path, "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null", str(local), f"ec2-user@{host}:{remote}"]
        return subprocess.run(full, capture_output=True, timeout=120)

    # Retry SCP until SSH is ready
    for attempt in range(6):
        r = scp(tar_path, "/home/ec2-user/nova-qwen-app.tar.gz")
        if r.returncode == 0:
            print("Tarball uploaded.")
            break
        print(f"  SCP attempt {attempt+1} failed, retrying in 15s...")
        time.sleep(15)
    else:
        print("ERROR: Could not SCP to instance. Check security group.")
        sys.exit(1)

    # 6. Wait for user-data to finish and service to start
    print("Waiting 60s for user-data to complete ...")
    time.sleep(60)

    r = ssh("sudo systemctl status nova-qwen.service --no-pager | head -15")
    stdout = r.stdout.decode("utf-8", errors="replace")
    print(stdout)

    r = ssh("curl -sS http://127.0.0.1:80/healthz")
    stdout = r.stdout.decode("utf-8", errors="replace")
    print(f"Healthz: {stdout}")

    print(f"\n{'='*60}")
    print(f"PoC Version B (AWS + Qwen) deployed!")
    print(f"  Instance: {instance_id} ({EC2_NAME})")
    print(f"  Public IP: {eip}")
    print(f"  URL: http://{eip}")
    print(f"  Student endpoint: HA-c20tc3R1ZGVudC1lcA (SageMaker)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
