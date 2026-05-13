"""Ship the FastAPI app to the EC2 host and start it behind Caddy.

Run after `deploy.py` succeeds. Uses plain ssh/scp (no boto3 SSM) to keep
the flow identical to aws-demo/ec2/setup_instance.py.

Usage:
    python poc/aws_claude/setup_instance.py
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
REPO = HERE.parent.parent


def load_env() -> dict[str, str]:
    env_path = HERE / ".outputs.env"
    if not env_path.exists():
        sys.exit("deploy.py hasn't been run. Missing .outputs.env")
    out: dict[str, str] = {}
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


def ssh_args(key: str) -> list[str]:
    return [
        "ssh", "-i", key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=10",
    ]


def ssh_run(key: str, host: str, remote_cmd: str) -> None:
    run([*ssh_args(key), f"ec2-user@{host}", remote_cmd])


def ssh_try(key: str, host: str, remote_cmd: str) -> bool:
    proc = subprocess.run(
        [*ssh_args(key), "-o", "BatchMode=yes", f"ec2-user@{host}", remote_cmd],
        capture_output=True, text=True,
    )
    return proc.returncode == 0


def scp_push(key: str, host: str, local: Path, remote_path: str) -> None:
    run([
        "scp", "-i", key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        str(local), f"ec2-user@{host}:{remote_path}",
    ])


def _filter(tarinfo: tarfile.TarInfo):
    # Strip bytecode caches so the tarball is deterministic and small.
    if "__pycache__" in tarinfo.name or tarinfo.name.endswith(".pyc"):
        return None
    return tarinfo


def package_app() -> Path:
    """Tar up `poc/aws_claude/app` as `app/` so imports match the host layout."""
    tar_path = HERE / "nova-claude-app.tar.gz"
    if tar_path.exists():
        tar_path.unlink()
    app_dir = HERE / "app"
    print(f"[setup] Packaging {app_dir} -> {tar_path}", flush=True)
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(app_dir, arcname="app", filter=_filter)
        tar.add(HERE / "requirements.txt", arcname="app/requirements.txt", filter=_filter)
    print(f"[setup] Tarball: {tar_path.stat().st_size:,} bytes", flush=True)
    return tar_path


REMOTE_TEMPLATE = """
set -euo pipefail
cd /home/ec2-user
rm -rf app
tar xzf nova-claude-app.tar.gz
ls -la app

python3.11 -m venv /opt/nova/venv
source /opt/nova/venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r app/requirements.txt

# Stop Caddy if running (uvicorn serves directly on port 80 now)
sudo systemctl stop caddy.service 2>/dev/null || true
sudo systemctl disable caddy.service 2>/dev/null || true

sudo tee /etc/systemd/system/nova-claude.service >/dev/null <<UNIT
[Unit]
Description=Nova Clinical AI — PoC Version A (Claude)
After=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/ec2-user/app
Environment=AWS_REGION={region}
Environment=S3_BUCKET={bucket}
Environment=BEDROCK_KB_ID={kb_id}
Environment=BEDROCK_GRAPHRAG_KB_ID={graphrag_kb_id}
Environment=GUARDRAIL_ID={guardrail_id}
Environment=STACK_TAG={stack_tag}
Environment=PYTHONPATH=/home/ec2-user
ExecStart=/opt/nova/venv/bin/uvicorn app.server:app --host 0.0.0.0 --port 80
Restart=on-failure

[Install]
WantedBy=multi-user.target
UNIT

sudo mkdir -p /opt/nova
sudo chown -R ec2-user:ec2-user /opt/nova

sudo systemctl daemon-reload
sudo systemctl enable --now nova-claude.service
sleep 5
sudo systemctl status --no-pager --lines=0 nova-claude.service || true

echo '== /healthz =='
for i in 1 2 3 4 5 6; do
    curl -sS http://127.0.0.1:80/healthz && break
    echo "  waiting for uvicorn ($i/6) ..."; sleep 3
done
echo
"""


def main() -> int:
    env = load_env()
    eip = env["EIP_ADDR"]
    region = env["REGION"]
    bucket = env["S3_BUCKET"]
    stack_tag = env.get("STACK_TAG", "poc-claude")
    key = str(REPO / "HA-sing.pem")

    if not Path(key).exists():
        sys.exit(f"SSH key missing: {key}. Re-use the one from aws-demo/ec2.")

    print(f"[setup] Waiting for SSH on {eip} ...", flush=True)
    for i in range(1, 21):
        if ssh_try(key, eip, "true"):
            break
        print(f"  SSH not ready ({i}/20), sleeping 15s", flush=True)
        time.sleep(15)
    else:
        sys.exit("SSH never came up")

    print("[setup] Waiting for cloud-init user-data to finish ...", flush=True)
    for i in range(1, 41):
        if ssh_try(key, eip, "test -f /var/lib/cloud/instance/user-data-done"):
            break
        print(f"  cloud-init still running ({i}/40), sleeping 10s", flush=True)
        time.sleep(10)

    # Load managed outputs for KB IDs
    managed_path = HERE / ".managed_outputs.json"
    managed: dict[str, str] = {}
    if managed_path.exists():
        import json
        managed = json.loads(managed_path.read_text())

    tar_path = package_app()
    scp_push(key, eip, tar_path, "/home/ec2-user/")
    ssh_run(key, eip, REMOTE_TEMPLATE.format(
        region=region,
        bucket=bucket,
        stack_tag=stack_tag,
        kb_id=managed.get("kb_id", "MUEEBGPRSJ"),
        graphrag_kb_id=managed.get("graphrag_kb_id", "FU6SXD0B8B"),
        guardrail_id=managed.get("guardrail_id", "azsgfl02i9gn"),
    ))

    print()
    print("[setup] ---------------------------------------------")
    print(f"[setup]  Demo URL: http://{eip}/")
    print(f"[setup]  API:       http://{eip}/api/chat")
    print(f"[setup]  Healthz:   http://{eip}/healthz")
    print("[setup] ---------------------------------------------")
    return 0


if __name__ == "__main__":
    sys.exit(main())
