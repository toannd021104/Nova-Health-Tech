# Scheduled Ingestion, Upload Portal, Site-to-Site VPN, and Identity

The RAG index is **always fresh via scheduled jobs, never lazy**. Physicians don't wait while the bot crawls WHO or internal systems — the index is ready when they ask.

## 1. Ingestion schedule

| Source | Cadence | Trigger | Mode | Why |
|---|---|---|---|---|
| WHO ICD-11 structured API | Daily 02:00 SGT | EventBridge cron (AWS) / CloudOps Scheduler (Ali) | Delta pull against `releaseId` | Catches updates without full re-walk |
| WHO guideline PDFs | Monthly, day 1 at 02:30 SGT + RSS webhook for urgent living guidelines | EventBridge cron + API Gateway webhook | Diff on the WHO publications index; download changed PDFs | Matches the scenario's "monthly protocol updates" |
| Internal clinical trial reports | **Weekly, Sunday 03:00 SGT** — AND real-time Microsoft Graph webhook for SharePoint changes (see `docs/architecture/corporate_integration.md` §2) | EventBridge cron + Graph subscription webhook | Weekly batch pull from SharePoint; webhook fires on any create/update/delete | Weekly is the reconciliation safety net; webhook keeps the index current within minutes |
| Internal treatment protocols | Same as above | Same | Same | |
| Manual override (any source) | Any time | Upload portal (see §2) | Direct user upload | Handles urgent additions / corrections that can't wait for the weekly |
| Monthly full reconciliation | Day 1, 04:00 SGT | EventBridge cron | Full diff + re-index of any document whose hash changed | Catches anything incremental paths missed |

All jobs write to the same **raw S3 / OSS bucket**, then a single Step Functions / Function Workflow picks up the object-created event and runs: parse → chunk → embed → upsert. One ingestion pipeline, many triggers.

### Idempotency and backfills

Each document gets a stable `document_id` (hash of source + URI) and a `revision` (hash of bytes). The upsert only re-embeds a chunk whose `revision` changed — zero wasted embedding cost on unchanged docs. A manual backfill is just an object PUT with `revision=force`.

## 2. Internal Upload Portal (for manual additions)

A small internal web app lets clinical-ops users upload trial PDFs, treatment protocols, and WHO guideline PDFs they have pre-downloaded. This app is not public:

- Hosted in a private subnet, reachable **only from the hospital network via Site-to-Site VPN to the cloud VPC**.
- Authenticated with the hospital identity provider (EntraID / Okta / Keycloak — see §4).
- Authorization: only users in the `nova-rag-curator` group can upload; only `nova-rag-admin` can delete or rename.
- Virus-scan every upload (GuardDuty Malware Protection on AWS / Alibaba Cloud Security Center on Ali) before the object is accepted into `raw/`.
- Each upload is PHI-scanned (Macie / SDDP) on arrival; anything flagged is quarantined and not indexed until reviewed.

### Upload flow

```
 User on hospital LAN
      │
  HTTPS over Site-to-Site VPN
      │
      ▼
 Private ALB / Server Load Balancer
      │
      ▼
 Upload-portal container (ECS / SAE) — OIDC auth against hospital IdP
      │
 presigned PUT URL (10-min TTL)
      │
      ▼
 S3 / OSS bucket  "raw/manual/<document_id>/<revision>.pdf"
      │
 ObjectCreated event
      │
      ▼
 GuardDuty Malware / Security Center scan
      │
      ▼
 Macie / SDDP PHI scan
      │  (quarantine on PHI leak)
      ▼
 Ingestion pipeline (same as scheduled path)
      │
      ▼
 Bedrock KB / Model Studio KB sync
      │
      ▼
 Audit log entry in CloudTrail / ActionTrail
```

### Minimum portal features

- Upload file (≤ 100 MB per file; split larger).
- Choose document type: `internal-trial | treatment-protocol | who-guideline-manual`.
- Add metadata: `speciality`, `review_date`, `owner_contact`.
- List / search recent uploads with status (Processing / Ready / Quarantined).
- Request reindex of a single document without re-upload.
- Delete a document (admin-only; also flushes its chunks from the KB and the semantic cache).

Built on the same stack as the demo UI (React frontend + Lambda/FC backend), behind the private ALB instead of CloudFront.

## 3. Site-to-Site VPN between hospital and cloud

### AWS Singapore (ap-southeast-1)

- **AWS Site-to-Site VPN** between the hospital's on-prem VPN device (Cisco ASA, FortiGate, Palo Alto, etc.) and a **Virtual Private Gateway** on Nova's VPC.
- IKEv2 + AES-256-GCM + SHA-2 for the tunnel; dual-tunnel per VPN connection for HA.
- Routing: static or BGP; prefer BGP for failover.
- Only two things reachable from the hospital: the **internal upload portal** (private ALB) and the **trial-repository pull endpoint** (for the scheduled puller to reach the hospital's SharePoint / SMB share over SMB-on-TLS or HTTPS).
- Nothing from the cloud side initiates traffic *into* the hospital unless the hospital explicitly whitelists the scheduled puller's NAT egress IP.

We do **not** use AWS Outposts or Direct Connect here — Singapore region is close enough and the VPN throughput (1.25 Gbps per tunnel) is ample for document uploads and weekly pulls.

### Alibaba Cloud Singapore

- **IPsec-VPN on VPN Gateway** between the hospital VPN device and Nova's VPC.
- Same cipher profile; dual-tunnel for HA.
- **Smart Access Gateway (SAG)** is an alternative when the hospital wants a turnkey appliance; we default to IPsec-VPN for simplicity.
- Cloud Enterprise Network can be added later if Nova needs to stitch multiple cloud regions together.

Both paths keep all inbound traffic to the Nova VPC on private, encrypted channels. Nothing goes over the public Internet.

## 4. Identity and Authorization

Two distinct populations need to be authenticated, with different trust levels.

### Population A — Clinicians using the AI assistant (external to Nova)

They log in from the hospital side. The identity provider is **the hospital's own IdP** (typically Microsoft Entra ID / Azure AD, sometimes Okta, Keycloak, or on-prem ADFS). We integrate via standard federation:

| On AWS | On Alibaba |
|---|---|
| **Amazon Cognito** user pool federates to the hospital IdP via **SAML 2.0 or OIDC**. Cognito issues the JWT used to call API Gateway. | **Alibaba IDaaS** (Cloud Identity) federates to hospital IdP via SAML 2.0 / OIDC. IDaaS issues the token used by API Gateway. |

### Population B — Nova staff (curators, admins, DevOps)

| On AWS | On Alibaba |
|---|---|
| **IAM Identity Center** federated to Nova's own EntraID tenant; staff assume roles per account / env. No local IAM users for humans. | **RAM + Cloud SSO** federated to Nova's EntraID; staff use short-lived SSO credentials. |

Long-lived access keys are banned in both accounts; all programmatic access uses IAM role assumption with session tokens.

### Authorization model

Scoped by token claims issued during login:

```
scope:                 what it allows
─────────────────────────────────────────────────
chat:clinical          call POST /chat on the AI assistant
kb:read                retrieve from the KB via API (admin-only)
curator:upload         upload documents via the internal portal
curator:delete         delete documents (admin-only)
admin:configure        change router / guardrail config
admin:evaluate         run the eval harness
```

The API Gateway authorizer checks the token's `aud`, `iss`, `exp`, and `scope` claims on every call. Lambda / FC re-checks the scope before doing anything privileged — defense in depth.

### Session and MFA

- All logins enforce MFA in the hospital IdP.
- Token lifetime is 60 min for clinicians, 15 min for admins; refresh tokens rotate.
- Step-up MFA is required for `admin:*` actions and for any upload flagged "living guideline override".
- Sessions carry `physician_id`, `hospital_id`, `specialty`, `role` so the audit log and retrieval filter can use them.

### Break-glass

Two named Nova admins hold a break-glass role (bypasses normal scope filtering) only usable with hardware MFA + a Slack / Feishu approval ticket from the other admin. Break-glass use auto-pages the security team.

## 5. Audit trail (for completeness — full details in compliance doc)

Every document ingestion event, every upload, every auth event, every model call, every admin action lands in:

- AWS: CloudTrail → S3 Object Lock (immutable) → Security Lake.
- Alibaba: ActionTrail → SLS → OSS with WORM enabled.

Retention per HIPAA Security Rule documentation requirements: **6 years** from creation or last effective date, whichever is later. (Not 7 — that was a misremembered figure in an earlier draft.)

## References

- [AWS Site-to-Site VPN — user guide](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [Alibaba Cloud VPN Gateway — IPsec-VPN](https://www.alibabacloud.com/help/en/vpn/)
- [Amazon Cognito — federate with SAML / OIDC](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-identity-federation.html)
- [Alibaba IDaaS — overview](https://www.alibabacloud.com/help/en/idaas/)
- [Singapore PDPA — Guide to Cross-Border Data Transfers (PDPC)](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers)
- [HIPAA Records Retention — 6-year rule](https://www.hipaajournal.com/hipaa-retention-requirements)

*Content above is rephrased for compliance with licensing restrictions.*
