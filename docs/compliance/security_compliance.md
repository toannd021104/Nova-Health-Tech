# Security & Compliance — Nova Health Tech Clinical GenAI

Region: **Singapore (AWS ap-southeast-1 / Alibaba Cloud Singapore).** All PHI stays in-region by default.

## 1. Regulations that apply

| Regulation | Where it applies | What it requires |
|---|---|---|
| **Singapore PDPA** (primary) | All personal data in Singapore | Consent, purpose limitation, protection, transfer limitation (no outbound transfer unless the recipient jurisdiction provides comparable protection), retention limitation, breach notification |
| **Singapore HCSA (Healthcare Services Act) 2020** | Telemedicine + clinical-decision-support software serving Singapore patients | Licensing, clinical-governance, record-keeping, incident reporting |
| **HIPAA + HITECH** (US) | Only when Nova serves US hospitals with US-resident PHI | Privacy Rule, Security Rule, BAA with AWS / Alibaba, audit logs retained **6 years** from creation or last effective date, encryption, access control, breach notification |
| **GDPR** (EU) | Only when Nova serves EU residents | DPIA, data-subject rights, 72-hour breach notice, DPO, data residency controls |
| **FDA SaMD + 21st Century Cures Act CDS carve-out** | If the output drives diagnostic decisions for US patients | QMS; the CDS carve-out applies when a clinician can independently review the basis of the recommendation |
| **EU AI Act** | EU deployment of a healthcare AI (high-risk) | Risk management, data governance, transparency, human oversight, post-market monitoring |
| **ISO 27001 / 27701 / 27018** | Industry baseline | InfoSec + PII handling in cloud |
| **HITRUST CSF** | Often required by US hospital procurement | Unified control framework mapping HIPAA + NIST |

## 2. Singapore-first compliance posture

Because the primary region is Singapore:

- **PDPA is the default regulatory frame.** Patient data stays in Singapore; no cross-border transfer unless a specific customer requires it and the PDPA transfer-limitation test is satisfied (comparable protection in the recipient jurisdiction, usually via contract + BCRs).
- **HCSA licensing** is the hospital's responsibility as the licensed provider; Nova is a data intermediary ("data processor" equivalent). Our contracts with hospitals spell out responsibilities.
- **HIPAA applies only for US-onboarded clients** — if Nova later takes on a US hospital, we sign an AWS BAA / Alibaba BAA for the US region and deploy a separate tenant in `us-east-1` / Virginia.

### Log retention — **6 years, not 7**

HIPAA Security Rule (§164.316(b)(2)) and HIPAA Privacy Rule (§164.530(j)) both require **six years** from the date of creation or the date when last in effect, whichever is later. This applies to policies, procedures, risk assessments, and audit logs involving ePHI.

Singapore PDPA does not prescribe a fixed log retention; it says "no longer than is necessary". 6 years harmonizes with HIPAA and is the retention we implement on both clouds.

Our default policy:

- **Audit logs** (CloudTrail / ActionTrail, Bedrock / Model Studio invocation logs, application audit entries): **6 years**, immutable via S3 Object Lock or OSS WORM.
- **PHI data** in the raw bucket: retained per the hospital's own retention schedule in their contract; default 6 years if unspecified.
- **RAG vector index**: retained as long as the source document is in force; purged when the source is withdrawn.
- **Model training artifacts**: 6 years for provenance.

## 3. Shared responsibility

The cloud provider secures the platform; Nova is responsible for configuration, architecture, encryption, access, logging, and clinical accuracy. Signing a BAA or equivalent doesn't make a deployment compliant — the controls below must be enforced.

## 4. AWS controls (Singapore, ap-southeast-1)

| HIPAA safeguard | AWS primary control | Bedrock-specific |
|---|---|---|
| §164.308 Administrative | IAM Identity Center + IAM Access Analyzer + Audit Manager (HIPAA framework) | Bedrock invocation logging + model version pinning |
| §164.310 Physical | AWS data-center certifications | N/A (managed) |
| §164.312(a) Access control | IAM least-privilege roles, MFA, SCPs, VPC endpoints | Bedrock Agents with scoped tool IAM |
| §164.312(b) Audit | CloudTrail → S3 Object Lock (WORM) + Security Lake | Bedrock invocation logs with request/response hashes |
| §164.312(c) Integrity | S3 versioning + Object Lock + Glacier Deep Archive | Guardrail grounding + citation validator |
| §164.312(d) Authentication | Cognito + hospital SSO via SAML/OIDC | Per-physician token embedded in Bedrock request |
| §164.312(e) Transmission security | TLS 1.3 + VPC endpoints | Private VPC access to Bedrock |
| §164.316 Documentation retention | S3 Object Lock **6-year retention** | Same for Bedrock logs |

### Must-enable before go-live

1. **Bedrock Guardrails** — deny topics (`self-diagnosis without clinician`, `dosage override`, `illegal drug synthesis`, `unsafe self-treatment`), PII filter (NAME, PHONE, ADDRESS, EMAIL, DATE_OF_BIRTH, SG_NRIC_FIN if applicable), custom MRN regex, grounding threshold ≥ 0.7, prompt-attack filter.
2. **Comprehend Medical DetectPHI** on every inbound message before the model sees it.
3. **Macie** weekly scans on `raw/` and quarantine on any PHI-leak match.
4. **Config + Security Hub** — HIPAA, NIST 800-53 conformance packs. Audit Manager nightly.
5. **KMS customer-managed keys** on S3, OpenSearch Serverless, ElastiCache, Secrets Manager, Lambda env vars.
6. **VPC endpoints** for Bedrock, S3, OpenSearch, Secrets Manager — Lambda has zero Internet egress.
7. **GuardDuty Malware Protection** on S3 uploads from the Internal Upload Portal.

### HIPAA-eligible services used in this design in Singapore

Bedrock, S3, Lambda, API Gateway, CloudFront, Cognito, OpenSearch Serverless, ElastiCache, Comprehend Medical, Macie, KMS, CloudTrail, CloudWatch, EventBridge, Step Functions, Textract, Bedrock Data Automation, Secrets Manager, GuardDuty, Security Hub. **Reconfirm eligibility list in `ap-southeast-1` before launch** (AWS updates monthly).

## 5. Alibaba Cloud controls (Singapore region)

| Safeguard | Alibaba primary control |
|---|---|
| Identity | RAM + Alibaba IDaaS (SAML/OIDC) — federates to hospital EntraID for clinicians, Nova EntraID for staff; MFA enforced; resource-group scoping |
| Network | VPC + PrivateLink to Model Studio/PAI-EAS; WAF + Anti-DDoS; ACL default-deny |
| Encryption at rest | KMS BYOK on OSS, OpenSearch, Tair, Log Service |
| Encryption in transit | TLS 1.3; Service Mesh (ASM) for mTLS |
| PHI handling | DataWorks Data Security Guard + SDDP classification and masking |
| LLM content safety | **Content Moderation 2.0 for generative AI** — jailbreak, hate, medical-misinformation, self-harm, bias filters + Nova custom medical template |
| Audit & retention | ActionTrail → SLS → OSS WORM **6-year retention**; immutable log integrity |
| Compliance posture | Cloud Config + Cloud Security Posture Management; PDPA / ISO / MLPS baselines available |
| Secrets | Credentials Manager with KMS + rotation FC |

### Alibaba Cloud compliance posture for Singapore

- ISO 27001 / 27017 / 27018 / 27701 / 22301
- SOC 1 / 2 / 3
- PCI DSS
- PDPA alignment (Singapore)
- GDPR-ready (for a later EU expansion)
- HIPAA-ready — Alibaba Cloud offers a HIPAA readiness assessment; BAA coverage is region-specific and must be confirmed with the account team before processing US PHI.

## 6. Site-to-Site VPN as the ingestion trust boundary

The hospital never exposes its SharePoint / file shares to the public Internet. The weekly pull of internal trial reports and treatment protocols runs over a **Site-to-Site IPsec VPN** (AWS Site-to-Site VPN or Alibaba VPN Gateway), AES-256-GCM, IKEv2, dual-tunnel HA. All manual uploads via the Internal Upload Portal traverse the same VPN.

Details in `docs/architecture/ingestion_and_identity.md`.

## 7. AI-specific medical compliance practices

- **No PHI in training data** — ever. Mask or synthesize before SFT/DPO.
- **Grounded answers only** — citation required; guardrail blocks unsourced answers.
- **Clinician in the loop** — UI labels the assistant as decision support; clinician reviews before any action on a patient (preserves FDA CDS carve-out when Nova serves US clients).
- **Emergency disclaimer** — acute emergency lane auto-prepends "Call emergency services immediately" for patient-facing scenarios; clinician lane shows the disclaimer but doesn't block.
- **Red-team / abuse-test before launch** — 200+ adversarial prompts (PHI exfiltration, jailbreak, dosing override, self-diagnosis).
- **Audit every interaction** — `{user_id, hospital_id, question_hash, retrieved_chunk_ids, model_version, guardrail_verdict, answer_hash, citation_ids, latency_ms}` retained 6 years.
- **Model version freeze** — pin production version; re-qualify with eval harness before moving.
- **Re-evaluate on every WHO refresh** — protocol changes can silently invalidate previously-correct answers.
- **Right to delete / rectify** — per-user chat history deletable without touching the RAG index (stored separately).
- **DR** — daily vector-store snapshots to a separate account/region (within Singapore's own AZs for PDPA simplicity); RPO ≤ 1 hour, RTO ≤ 4 hours.
- **Data minimization** — only the FHIR slice needed for the question goes to the model; never the full chart.
- **Separation of duties** — platform engineer and clinical-data custodian roles split; break-glass requires two-person approval + hardware MFA.

## 8. Pre-launch checklist

- [ ] Tenant deployed in Singapore region only; no default cross-border replication.
- [ ] AWS BAA (or Alibaba equivalent) signed and scoped if any US PHI.
- [ ] PDPA Data Protection Officer appointed (Nova side + hospital side).
- [ ] Bedrock Guardrails / Alibaba Content Moderation configured and red-teamed.
- [ ] All stores on customer-managed KMS keys.
- [ ] CloudTrail / ActionTrail → WORM storage for **6 years**.
- [ ] Macie / SDDP weekly PHI scan.
- [ ] Evaluation harness baseline locked (accuracy, latency, safety).
- [ ] DPIA (GDPR, if in scope) + HIPAA Security Risk Assessment (if in scope) completed.
- [ ] Clinician-approval UI gate.
- [ ] Emergency-disclaimer copy reviewed by legal.
- [ ] Third-party penetration test.
- [ ] Site-to-Site VPN configured; hospital IdP federation tested end-to-end.
- [ ] Model card + system card published to hospital clients.

## 9. Key references

- [Singapore PDPA — cross-border transfers (PDPC)](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers)
- [Singapore Healthcare Services Act 2020 — MOH](https://www.moh.gov.sg/policies-and-legislation/healthcare-services-act)
- [HIPAA Records Retention — 6-year rule](https://www.hipaajournal.com/hipaa-retention-requirements)
- [HIPAA compliance for generative AI solutions on AWS](https://aws.amazon.com/blogs/industries/hipaa-compliance-for-generative-ai-solutions-on-aws/)
- [How to safeguard healthcare data privacy using Amazon Bedrock Guardrails](https://aws.amazon.com/blogs/publicsector/how-to-safeguard-healthcare-data-privacy-using-amazon-bedrock-guardrails/)
- [Alibaba Cloud compliance center](https://www.alibabacloud.com/en/trust-center)
- [Alibaba Cloud Content Moderation for generative AI](https://www.alibabacloud.com/product/content-moderation)

*Content above is rephrased for compliance with licensing restrictions.*
