# Corporate Integration — EHR, SharePoint, and Upload Portal

The clinical assistant is useless without two live integrations:

1. **EHR / EMR (Epic, Cerner/Oracle Health, Allscripts, etc.)** — lets the assistant answer about a real patient, not just generic clinical knowledge.
2. **Document & knowledge management (SharePoint / OneDrive, Google Drive, Confluence, NFS)** — is where Nova's own clinical trial reports and treatment protocols actually live.

The third integration — the internal upload portal — covers the "manual override" path documented in `docs/architecture/ingestion_and_identity.md`.

## 1. EHR / EMR — patient-context at query time

### Standard: HL7 FHIR R4 + SMART on FHIR

All three of Epic, Cerner/Oracle Health, and Allscripts expose an **FHIR R4** API and support the **SMART on FHIR** authorization profile. We build once against SMART on FHIR and the same code works against every major EHR with per-vendor config.

Two launch modes matter here:

| Mode | What it does | When we use it |
|---|---|---|
| **EHR launch (SMART App Launch v2)** | Clinician launches the assistant from inside the EHR; the EHR injects an OAuth2 authorization-code flow; the returned token carries the current patient context (`launch/patient`, `launch/encounter`) | The clinical workflow — a physician on a patient chart clicks "Ask Nova" |
| **Backend Services (`client_credentials` + JWT)** | Server-to-server flow with a private-key-signed JWT; no clinician in the loop; system-level scopes | Batch jobs like nightly de-identified population-health extracts — **not used** for day-to-day clinical queries |

We use **EHR launch / SMART App Launch v2** as the primary path.

### Data we read (per-call, scoped)

| FHIR Resource | Why |
|---|---|
| `Patient` | Demographics (de-identified before the model sees them) |
| `Condition` | Active and resolved diagnoses |
| `MedicationStatement` / `MedicationRequest` | Current meds; drug-drug and drug-condition interactions |
| `AllergyIntolerance` | Allergies (critical for emergency dosing) |
| `Observation` | Vitals + recent labs |
| `Encounter` | Current visit context |
| `DocumentReference` | Recent notes, only when explicitly requested |

Scopes requested from the EHR:

```
launch                   # EHR launch context
openid fhirUser          # who the clinician is
patient/Patient.rs       # read, search — current patient only
patient/Condition.rs
patient/MedicationStatement.rs
patient/AllergyIntolerance.rs
patient/Observation.rs
patient/Encounter.rs
offline_access           # refresh token for long sessions
```

The trailing `.rs` = **read + search**. We never request write scopes; the assistant is read-only in the EHR.

### How a clinical query flows

```
  Clinician in Epic on patient chart
   │ clicks "Ask Nova"
   ▼
  Epic launches Nova's iframe with ?iss=<fhir-endpoint>&launch=<ctx>
   │
  SMART App Launch v2 authorization-code flow (PKCE, public client)
   │
   ▼
  Access token — carries patient context + scopes
   │
  Nova frontend → API Gateway → Lambda /chat
   │   (token attached)
   ▼
  Lambda:
   1. Exchange launch ctx → FHIR patient bundle (single call with `$everything` or per-resource)
   2. Extract the minimum slice needed for the question (data minimization)
   3. De-identify via Comprehend Medical / DataWorks SDDP (name, MRN, DOB → tokens)
   4. Build prompt: system template + RAG context + tokenized patient slice + question
   5. Call Bedrock / Model Studio; answer is grounded + cited
   6. Re-identify in the UI only (tokens → names), never in the model's context
```

The model never sees raw patient names, MRNs, or DOBs. PHI stays inside the trust boundary between the clinician's browser, API Gateway, and the PHI-masking Lambda.

### FHIR client on each cloud

- **AWS**: Python Lambda with `fhirclient` SDK (SMART Health IT). Tokens in Secrets Manager; per-tenant client credentials per hospital. Outbound calls go through a VPC NAT Gateway to the hospital's FHIR endpoint (public URL over TLS, or over the hospital Site-to-Site VPN if the EHR is on-prem).
- **Alibaba**: Function Compute with the same `fhirclient` SDK; tokens in Credentials Manager.

### Per-tenant config

Each hospital's EHR integration lives in a tenant config stored in DynamoDB (AWS) / TableStore (Alibaba):

```json
{
  "tenant_id": "hospital-sg-alpha",
  "ehr_vendor": "epic",
  "fhir_base_url": "https://fhir.alpha-hospital.sg/api/FHIR/R4",
  "authorize_url": "https://auth.alpha-hospital.sg/oauth2/authorize",
  "token_url":     "https://auth.alpha-hospital.sg/oauth2/token",
  "client_id":     "<nova-client-id>",
  "client_secret_ref": "secretsmanager:nova/ehr/hospital-sg-alpha",
  "launch_style":  "smart-app-launch-v2",
  "fhir_scopes":   ["launch", "openid", "fhirUser",
                    "patient/Patient.rs", "patient/Condition.rs",
                    "patient/MedicationStatement.rs",
                    "patient/AllergyIntolerance.rs",
                    "patient/Observation.rs", "patient/Encounter.rs"],
  "requires_vpn":  false,
  "timezone":      "Asia/Singapore"
}
```

### When the EHR is unreachable

The assistant degrades gracefully: it falls back to generic clinical knowledge and shows a banner ("No patient context loaded"). A hard timeout of 2 seconds on the FHIR call — we never block the 2-second emergency SLA on EHR latency. Patient context becomes a **soft** input; the answer still runs, it just doesn't personalize.

### CDS Hooks (out of scope for first release)

Epic and Cerner both support CDS Hooks (clinical-decision-support cards injected inline). A later release can register a `patient-view` hook that proactively surfaces Nova's recommendations when the clinician opens a chart. Not part of the launch build — would be added via a separate feature launch after the core assistant is in production.

## 2. SharePoint / OneDrive — keep internal docs in sync automatically

Nova's internal clinical trial reports and treatment protocols typically live in one of these systems. The integration has two jobs:

1. **Bulk discovery and weekly pull** — the scheduled job listed in `docs/architecture/ingestion_and_identity.md`.
2. **Real-time change notifications** — subscribe to Microsoft Graph so new/updated/deleted documents trigger re-ingestion within minutes, without waiting for the weekly cron.

### Microsoft Graph change-notification subscription

```
POST https://graph.microsoft.com/v1.0/subscriptions
{
  "changeType": "updated,created,deleted",
  "notificationUrl": "https://api.nova-health.sg/webhooks/graph",
  "lifecycleNotificationUrl": "https://api.nova-health.sg/webhooks/graph-lifecycle",
  "resource": "/sites/{site-id}/drives/{drive-id}/root",
  "expirationDateTime": "2026-05-16T00:00:00Z",
  "clientState": "<random-secret-per-tenant>"
}
```

- Subscription expiry maxes out below 30 days depending on resource type; a lifecycle job renews automatically.
- `clientState` is validated on every inbound notification so only genuine Graph payloads are accepted.
- For high-traffic drives (many updates per minute) we switch to **Event Hubs delivery** instead of webhooks — better back-pressure handling than HTTP webhook fanout.

### Webhook handler

```
Graph notification
   │
   ▼
 API Gateway (public) → Lambda /webhooks/graph (AWS)
                      or
                      → API Gateway (public) → Function Compute (Alibaba)
   │
   1. Verify `clientState` matches the tenant config
   2. Extract {site_id, drive_id, item_id, change_type}
   3. Call Graph with the **app-only** token to fetch the file bytes
   4. Write to s3://nova-raw/scheduled/sharepoint/<tenant>/<item_id>.<revision>.pdf
   5. Object-created event kicks the same ingestion pipeline (BDA parse → chunk → embed → KB sync)
```

### Auth for Microsoft Graph

Two options, we use **app-only (client credentials)**:

| Option | Permissions | Use |
|---|---|---|
| **App-only (client credentials)** | `Sites.Selected` + per-site grant from hospital admin (preferred) — or `Files.Read.All` tenant-wide if the hospital insists | Our default; Nova service reads the drive(s) the hospital explicitly grants |
| Delegated (user-bound) | `Files.Read` | Only used by the Upload Portal when a clinician uploads a file manually |

`Sites.Selected` is strongly preferred — the hospital admin grants access **per specific SharePoint site**, not tenant-wide, drastically reducing blast radius. Client secret in Secrets Manager / Credentials Manager, rotated 90 days.

### What about Google Drive / Confluence / NFS?

- **Google Drive** — same pattern with Drive API push notifications (`files.watch`).
- **Confluence Cloud** — webhooks on `page_created`, `page_updated`.
- **On-prem NFS / SMB share** — the hospital's scheduled agent inside their network writes changed files over the Site-to-Site VPN to a private S3 / OSS endpoint (no public Internet hop). Used when the hospital does not run SharePoint.

Pluggable connector model: one interface in code (`DocumentSource`), one connector class per source. The rest of the pipeline is source-agnostic because documents all land in the same `raw/` prefix.

## 3. Three integrations, one pipeline

```
┌─────────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────┐
│  EHR / EMR (Epic,       │     │  SharePoint / OneDrive   │     │  Internal Upload     │
│  Cerner, Allscripts)    │     │  (Graph API + webhooks)  │     │  Portal (hospital    │
│                          │     │                          │     │  VPN + IdP auth)     │
│  SMART App Launch v2    │     │  Sites.Selected grant +  │     │  clinicians upload   │
│  (per-clinician token)  │     │  Graph subscription      │     │  one-off PDFs        │
└──────────┬──────────────┘     └──────────┬───────────────┘     └──────────┬───────────┘
           │                               │                                │
           │ read-only query, per call     │ push notification on change    │ direct PUT
           ▼                               ▼                                ▼
    Lambda/FC on hot path             ingestion webhook              upload-portal backend
           │                               │                                │
           │ attaches to prompt            └──────────┬─────────────────────┘
           │ (de-identified slice)                    │
           │                                 ObjectCreated in raw bucket
           ▼                                          │
   RAG + generation                                   ▼
                                     Step Functions / Function Workflow
                                     BDA / DocMind parse → chunk → embed → KB sync
                                     (+ GuardDuty/Security Center scan, Macie/SDDP PHI scan)
```

- **EHR integration is hot-path** — used at every clinical query, never written to disk.
- **SharePoint and the upload portal are ingest-path** — trigger the same BDA/DocMind → chunk → embed → KB sync pipeline that the scheduled jobs do.
- Scheduled jobs from `docs/architecture/ingestion_and_identity.md` remain the safety net: they reconcile any notification the webhook missed.

## 4. Security for these integrations

| Integration | Control |
|---|---|
| SMART on FHIR | PKCE + short-lived access tokens (60 min); refresh token in the clinician's browser session only (not server); all calls over TLS; client secret in Secrets Manager per tenant |
| EHR calls from Lambda | Outbound via VPC NAT + VPC endpoint to the hospital's FHIR URL; WAF rate-limits inbound from the EHR side; no PHI written to CloudWatch (redacted before log) |
| PHI masking | Comprehend Medical (AWS) / DataWorks SDDP (Ali) runs **before** any model sees patient data; tokens reversed only in the frontend |
| Microsoft Graph webhook | `clientState` validated; signature checked; unknown tenant rejected; webhook behind WAF with per-tenant rate limit |
| Graph app permissions | Prefer `Sites.Selected` over tenant-wide scopes; admin consent per hospital; rotate secret every 90 days |
| Audit | Every FHIR call, every Graph event, every upload-portal PUT logged to CloudTrail / ActionTrail with correlation ID; 6-year retention |

## 5. Testing and sandboxes

- **Epic** — Epic on FHIR sandbox (`https://fhir.epic.com/interconnect-fhir-oauth/`) for pre-prod.
- **Oracle Health / Cerner** — code.cerner.com sandbox with SMART endpoint.
- **Allscripts** — Unity + FHIR sandbox.
- **Microsoft Graph** — Microsoft 365 developer tenant with sample SharePoint sites.
- Integration tests live in the CI pipeline; nightly job rotates through each sandbox and runs a canned clinical-question suite.

## 6. References

- [SMART App Launch v2 — SMART Health IT](http://docs.smarthealthit.org/)
- [Epic on FHIR — developer portal](https://fhir.epic.com)
- [SMART on FHIR App Development Guide](https://saga-it.com/blog/smart-on-fhir-guide)
- [How to Integrate FHIR APIs with Epic, Cerner, and other major EHRs](https://thescimus.com/blog/how-to-integrate-fhir-apis-with-epic-cerner-and-other-major-ehrs/)
- [Microsoft Graph — change notifications overview](https://learn.microsoft.com/en-us/graph/api/resources/change-notifications-api-overview?view=graph-rest-1.0)
- [Microsoft Graph — create subscription](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0)
- [Monitor SharePoint changes with Graph Subscriptions](https://www.koskila.net/graph-subscriptions-monitor-sharepoint-site/)
- [Microsoft Graph change notifications via Event Hubs (high volume)](https://learn.microsoft.com/en-us/graph/change-notifications-delivery-event-hubs)

*Content above is rephrased for compliance with licensing restrictions.*
