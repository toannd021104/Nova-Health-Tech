"""Pack the app tarball and deploy to EC2 via SCP + SSH."""
import tarfile
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent / "poc" / "aws_claude"
REPO = HERE.parent.parent
KEY = str(REPO / "HA-sing.pem")
HOST = "47.130.120.152"

def ssh_cmd(cmd):
    full = [
        "ssh", "-i", KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=10",
        f"ec2-user@{HOST}", cmd
    ]
    print(f"$ ssh ... {cmd[:80]}")
    return subprocess.run(full, capture_output=True, timeout=120)

def scp_push(local, remote):
    full = [
        "scp", "-i", KEY,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        str(local), f"ec2-user@{HOST}:{remote}"
    ]
    print(f"$ scp {local} -> {remote}")
    return subprocess.run(full, capture_output=True, timeout=60)

# 1. Create tarball
tar_path = HERE / "nova-claude-app.tar.gz"
if tar_path.exists():
    tar_path.unlink()

app_dir = HERE / "app"
print(f"Packaging {app_dir} ...")
with tarfile.open(str(tar_path), "w:gz") as tar:
    for root, dirs, files in os.walk(str(app_dir)):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for f in files:
            if f.endswith(".pyc"):
                continue
            full_path = os.path.join(root, f)
            arcname = os.path.relpath(full_path, str(HERE))
            tar.add(full_path, arcname=arcname)
    tar.add(str(HERE / "requirements.txt"), arcname="app/requirements.txt")

print(f"Tarball: {tar_path.stat().st_size:,} bytes")

# 2. SCP to EC2
r = scp_push(tar_path, "/home/ec2-user/nova-claude-app.tar.gz")
if r.returncode != 0:
    print(f"SCP failed: {r.stderr.decode('utf-8', errors='replace')}")
    sys.exit(1)
print("SCP done.")

# 3. SSH: extract and restart service
deploy_cmd = """
cd /home/ec2-user
rm -rf app
tar xzf nova-claude-app.tar.gz
source /opt/nova/venv/bin/activate
pip install -r app/requirements.txt -q
sudo systemctl restart nova-claude.service
sleep 3
sudo systemctl status --no-pager nova-claude.service | head -20
curl -sS http://127.0.0.1:80/healthz || curl -sS http://127.0.0.1:8000/healthz || echo 'healthz failed'
"""
r = ssh_cmd(deploy_cmd)
stdout = r.stdout.decode('utf-8', errors='replace') if r.stdout else ""
stderr = r.stderr.decode('utf-8', errors='replace') if r.stderr else ""
print("STDOUT:", stdout[-2000:])
if stderr:
    print("STDERR:", stderr[-1000:])
if r.returncode != 0:
    print(f"Deploy failed with code {r.returncode}")
    sys.exit(1)

print("\nDeploy complete. Test at http://47.130.120.152/healthz")
