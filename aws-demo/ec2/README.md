# AWS Demo — EC2 deployment (Singapore)

Deploys a publicly-reachable demo of the Nova Clinical GenAI Assistant to AWS Singapore (`ap-southeast-1`). Minimal infra (no logs, firewall, VPN, DR) per request.

## What you get

- One `t4g.small` EC2 running FastAPI + LangChain + **LangGraph**.
- **Bedrock Claude Haiku 4.5** (emergency lane) + **Claude Sonnet 4.5** (complex lane), both via the `global.*` inference profiles that Singapore requires.
- **Cohere Embed v4** (`global.cohere.embed-v4:0`) for chunk + query embeddings. Titan is not available in Singapore today.
- FAISS in-memory vector store, built on first boot from the S3 corpus, persisted to `/opt/nova/faiss/`.
- Caddy in front of uvicorn on port 80.
- Optional **EntraID OIDC** (disabled by default).

## Architecture (in one picture)

```
browser ──(public IP, HTTP 80)──► Caddy ──► FastAPI (uvicorn 127.0.0.1:8000)
                                               │
                                      LangChain + LangGraph
                                      ┌────────┴────────┐
                                      ▼                 ▼
                                 FAISS in-mem     Bedrock
                                 (Cohere Embed     - Haiku 4.5  (emergency)
                                  v4 1024-dim)     - Sonnet 4.5 (complex)
                                      │
                              built from S3:
                              s3://ha-<b64>-<acct>/kb-src/
                                 ├── who/B09540-eng.pdf
                                 ├── protocols/Chapter1.pdf
                                 └── icd11/{mms_root.json, entities/*}
```

## Files

```
aws-demo/ec2/
├── NAMING.md             ← resource-name mapping (HA-<b64>)
├── deploy.py             ← provisions VPC/SG/IAM/EC2/S3/EIP, uploads corpus
├── setup_instance.py     ← SSHes in, installs deps, starts systemd units
├── user_data.sh          ← runs once on first boot (Python 3.11, Caddy)
└── app/
    ├── requirements.txt
    ├── server.py         ← FastAPI + optional EntraID OIDC + /api/chat
    ├── graph.py          ← LangGraph: classify → retrieve → answer (Haiku/Sonnet)
    ├── rag.py            ← FAISS build/load + pypdf + Cohere embeddings (Bedrock)
    └── static/           ← index.html + app.js + styles.css
```

## Deploy

From the repo root, any shell (Python is all you need locally):

```bash
# 1. AWS profile: credentials must be in ~/.aws/credentials under [gapv50k]
#    (region ap-southeast-1)

# 2. Provision infra and upload the demo corpus to S3
set AWS_PROFILE=gapv50k
set AWS_REGION=ap-southeast-1
cd aws-demo\ec2
python deploy.py

# 3. Install dependencies on the EC2 instance and start the services
# (add ENTRA_* env vars only if you want to enable EntraID OIDC)
python setup_instance.py
```

First deploy takes about 4 minutes (EC2 launch + pip install + FAISS cold-build from the corpus).

The last line of `setup_instance.py` prints:

```
Demo URL: http://<elastic-ip>/
```

Open that in a browser.

## Resource naming

Every resource is tagged `Name=HA-<base64url(logical-name)>`. See `NAMING.md` for the decode table. Regenerate a tag:

```python
import base64
print("HA-" + base64.urlsafe_b64encode(b"vpc-nova").decode().rstrip("="))
# HA-dnBjLW5vdmE
```

## EntraID (optional)

OIDC against the tenant `e5675247-08d2-407e-98e1-f2aabf5e9b18` is wired via **Authlib** in `server.py`. To enable it:

1. In the Azure app registration for client id `427891a5-6075-44e0-bea4-278fa5c2eb3c`, add `http://<elastic-ip>/api/auth/callback` as a redirect URI under "Web" platform.
2. Re-run `setup_instance.py` with the secrets exposed as env vars — the deploy script embeds them into the systemd unit but never commits them:
   ```
   set ENTRA_CLIENT_SECRET=<your secret>
   python setup_instance.py
   ```
   Also update the unit inline to `Environment=ENTRA_ENABLED=true` and `sudo systemctl daemon-reload && sudo systemctl restart nova.service`.

Without these, the app runs in "demo mode" and `/api/me` returns a stub user — you still get the full chat experience.

## What this demo skips (per user request)

- No CloudTrail, CloudWatch alarms, Bedrock invocation logging.
- No WAF or Network ACLs beyond the SG.
- No Site-to-Site VPN.
- No DR region or snapshots.
- No OpenSearch Serverless — FAISS is enough for a demo corpus.
- No Bedrock Guardrails wired yet.

## Teardown

```python
# from aws-demo/ec2/
python - <<'PY'
import boto3, os
s = boto3.Session(profile_name="gapv50k", region_name="ap-southeast-1")
ec2 = s.client("ec2"); s3 = s.client("s3"); iam = s.client("iam")
# find by tag and terminate / release / delete
PY
```

Or use the AWS console: search for `HA-` in any resource list.
