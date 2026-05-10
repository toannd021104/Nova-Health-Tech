"""Ship the app to the EC2 instance and start services.

Run after deploy.py succeeds. Uses plain `ssh` / `scp` from Windows / macOS / Linux.
"""
from __future__ import annotations

import os
import shlex
import subprocess
import sys
import tarfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_env() -> dict:
    env_path = HERE / ".outputs.env"
    if not env_path.exists():
        sys.exit("deploy.py hasn't been run. Missing .outputs.env")
    out = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k] = v
    return out


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    print("$ " + " ".join(shlex.quote(c) for c in cmd), flush=True)
    return subprocess.run(cmd, check=check)


def ssh_run(key: str, host: str, remote_cmd: str) -> None:
    run(["ssh", "-i", key,
         "-o", "StrictHostKeyChecking=no",
         "-o", "UserKnownHostsFile=/dev/null",
         "-o", "ConnectTimeout=10",
         f"ec2-user@{host}", remote_cmd])


def ssh_try(key: str, host: str, remote_cmd: str) -> bool:
    proc = subprocess.run(
        ["ssh", "-i", key,
         "-o", "StrictHostKeyChecking=no",
         "-o", "UserKnownHostsFile=/dev/null",
         "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
         f"ec2-user@{host}", remote_cmd],
        capture_output=True, text=True,
    )
    return proc.returncode == 0


def scp_push(key: str, host: str, local: Path, remote_path: str) -> None:
    run(["scp", "-i", key,
         "-o", "StrictHostKeyChecking=no",
         "-o", "UserKnownHostsFile=/dev/null",
         str(local), f"ec2-user@{host}:{remote_path}"])


def main() -> int:
    env = load_env()
    eip = env["EIP_ADDR"]
    region = env["REGION"]
    s3_bucket = env["S3_BUCKET"]
    key = str(HERE.parent.parent / "HA-sing.pem")

    print(f"[setup] Waiting for SSH on {eip} ...", flush=True)
    for i in range(1, 21):
        if ssh_try(key, eip, "true"):
            break
        print(f"  SSH not ready yet ({i}/20), sleeping 15s", flush=True)
        time.sleep(15)
    else:
        sys.exit("SSH never came up")

    print("[setup] Waiting for cloud-init user-data to finish (installs python/caddy) ...", flush=True)
    for i in range(1, 41):
        if ssh_try(key, eip, "test -f /var/lib/cloud/instance/user-data-done"):
            break
        print(f"  cloud-init still running ({i}/40), sleeping 10s", flush=True)
        time.sleep(10)

    print("[setup] Packaging the app directory", flush=True)
    tar_path = HERE / "nova-app.tar.gz"
    if tar_path.exists():
        tar_path.unlink()

    app_dir = HERE / "app"

    def _filter(tarinfo: tarfile.TarInfo):
        if "__pycache__" in tarinfo.name or tarinfo.name.endswith(".pyc"):
            return None
        return tarinfo

    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(app_dir, arcname="app", filter=_filter)
    print(f"[setup] Tarball: {tar_path.stat().st_size:,} bytes", flush=True)

    scp_push(key, eip, tar_path, "/home/ec2-user/")

    remote_cmd = f"""
set -euo pipefail
cd /home/ec2-user
rm -rf app
tar xzf nova-app.tar.gz
ls -la app

python3.11 -m venv /opt/nova/venv
source /opt/nova/venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r app/requirements.txt

sudo tee /etc/systemd/system/nova.service >/dev/null <<UNIT
[Unit]
Description=Nova Clinical GenAI Assistant
After=network-online.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/app
Environment=AWS_REGION={region}
Environment=S3_BUCKET={s3_bucket}
Environment=KB_PREFIX=kb-src
Environment=BEDROCK_MODEL_ID=global.anthropic.claude-haiku-4-5-20251001-v1:0
Environment=BEDROCK_TEACHER_MODEL_ID=global.anthropic.claude-sonnet-4-5-20250929-v1:0
Environment=EMBED_MODEL_ID=global.cohere.embed-v4:0
Environment=ENTRA_ENABLED=false
Environment=ENTRA_TENANT_ID={os.environ.get("ENTRA_TENANT_ID", "")}
Environment=ENTRA_CLIENT_ID={os.environ.get("ENTRA_CLIENT_ID", "")}
Environment=ENTRA_CLIENT_SECRET={os.environ.get("ENTRA_CLIENT_SECRET", "")}
ExecStart=/opt/nova/venv/bin/uvicorn server:app --host 127.0.0.1 --port 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo mkdir -p /etc/caddy
sudo tee /etc/caddy/Caddyfile >/dev/null <<CADDY
:80 {{
    encode gzip
    reverse_proxy 127.0.0.1:8000
}}
CADDY

sudo tee /etc/systemd/system/caddy.service >/dev/null <<UNIT
[Unit]
Description=Caddy
After=network-online.target

[Service]
User=ec2-user
ExecStart=/usr/local/bin/caddy run --config /etc/caddy/Caddyfile
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo mkdir -p /opt/nova/faiss
sudo chown -R ec2-user:ec2-user /opt/nova

sudo systemctl daemon-reload
sudo systemctl enable --now nova.service caddy.service
sleep 5
sudo systemctl status --no-pager --lines=0 nova.service caddy.service || true

echo '== first /api/health (will build FAISS from S3 on cold start) =='
curl -sS http://127.0.0.1:8000/api/health || true
echo
"""

    ssh_run(key, eip, remote_cmd)

    print("", flush=True)
    print("[setup] ---------------------------------------------", flush=True)
    print(f"[setup]  Demo URL: http://{eip}/", flush=True)
    print("[setup] ---------------------------------------------", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
