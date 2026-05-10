# Security & Compliance

Region: **Singapore** ([AWS `ap-southeast-1`](https://aws.amazon.com/compliance/aws-regions/) / Alibaba Cloud Singapore International). All PHI stays in-region by default.

## 1. Regulations in scope

| Regulation | When it applies | Key requirement |
|---|---|---|
| [**Singapore PDPA**](https://www.pdpc.gov.sg/) (primary) | All personal data in Singapore | Consent, purpose limitation, protection, [transfer limitation](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers), retention limitation, breach notification |
| [**Singapore HCSA 2020**](https://www.moh.gov.sg/policies-and-legislation/healthcare-services-act) | Telemedicine + clinical-decision-support software for SG patients | Licensing, clinical governance, record-keeping, incident reporting |
| [**HIPAA + HITECH**](https://www.hipaajournal.com/hipaa-retention-requirements/) (US) | Only when serving US hospitals with US-resident PHI | Privacy Rule, Security Rule, BAA with cloud provider, audit logs retained **6 years** from creation or last effective date |
| [GDPR](https://gdpr.eu/) (EU) | Only when serving EU residents | DPIA, data-subject rights, 72-hr breach notice, DPO, data residency |
| [FDA SaMD + 21st Century Cures Act CDS carve-out](https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software) | If output drives diagnostic decisions for US patients | QMS; CDS carve-out applies when clinician can independently review the basis of the recommendation |
| [EU AI Act](https://artificialintelligenceact.eu/) | EU deployment of a healthcare AI (high-risk) | Risk management, data governance, transparency, human oversight, post-market monitoring |
| [ISO 27001 / 27701 / 27018](https://www.iso.org/standard/27001) | Industry baseline | InfoSec + PII handling in cloud |
| [HITRUST CSF](https://hitrustalliance.net/) | Often required by US hospital procurement | Unified control framework mapping HIPAA + NIST |

## 2. Singapore-first compliance posture

Because the primary region is Singapore:

- **PDPA is the default frame.** Patient data stays in SG; no cross-border transfer unless the [transfer-limitation test](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers) is satisfied (comparable protection, usually via contract clauses / BCRs).
- **HCSA licensing** is the hospital's responsibility as the licensed provider; Nova is a data intermediary (data processor). Contracts spell out responsibilities.
- **HIPAA only for US-onboarded clients** — if Nova takes on a US hospital, sign AWS / Alibaba BAA for the US region and deploy a separate tenant in `us-east-1`.

### Log retention — **6 years, not 7**

[HIPAA Security Rule §164.316(b)(2)](https://www.law.cornell.edu/cfr/text/45/164.316) and [Privacy Rule §164.530(j)](https://www.law.cornell.edu/cfr/text/45/164.530) both require **six years** from the date of creation or the date when last in effect, whichever is later. Applies to policies, procedures, risk assessments, and audit logs involving ePHI.

PDPA doesn't prescribe a fixed log retention; it says "no longer than is necessary". 6 years harmonizes with HIPAA — our default on both clouds.

Our retention policy:

| Data class | Retention |
|---|---|
| Audit logs (CloudTrail / ActionTrail, Bedrock / Model Studio invocation logs, application audit) | **6 years** immutable via [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) / OSS WORM |
| PHI data in raw bucket | Per hospital's contract; default 6 years if unspecified |
| RAG vector index | As long as source document is in force; purged when source is withdrawn |
| Model training artifacts | 6 years for provenance |

## 3. Shared responsibility

Cloud provider secures the platform; Nova is responsible for configuration, architecture, encryption, access, logging, and clinical accuracy. **Signing a BAA doesn't make a deployment compliant** — the controls below must be enforced.

## 4. AWS controls (Singapore `ap-southeast-1`)

| HIPAA safeguard | AWS primary control | Bedrock-specific |
|---|---|---|
| §164.308 Administrative | [IAM Identity Center](https://aws.amazon.com/iam/identity-center/) + [IAM Access Analyzer](https://aws.amazon.com/iam/features/analyze-access/) + [Audit Manager (HIPAA framework)](https://aws.amazon.com/audit-manager/) | Bedrock invocation logging + model version pinning |
| §164.310 Physical | [AWS data-center certifications](https://aws.amazon.com/compliance/data-center/controls/) | N/A (managed) |
| §164.312(a) Access control | IAM least-privilege roles, MFA, SCPs, [VPC endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html) | [Bedrock Agents](https://aws.amazon.com/bedrock/agents/) with scoped tool IAM |
| §164.312(b) Audit | [CloudTrail](https://aws.amazon.com/cloudtrail/) → S3 Object Lock (WORM) + [Security Lake](https://aws.amazon.com/security-lake/) | Bedrock invocation logs with request/response hashes |
| §164.312(c) Integrity | S3 versioning + Object Lock + [Glacier Deep Archive](https://aws.amazon.com/s3/storage-classes/glacier/instant-retrieval/) | [Guardrail](https://aws.amazon.com/bedrock/guardrails/) grounding + citation validator |
| §164.312(d) Authentication | [Cognito](https://aws.amazon.com/cognito/) + hospital SSO via SAML/OIDC | Per-physician token embedded in Bedrock request |
| §164.312(e) Transmission security | TLS 1.3 + VPC endpoints | Private VPC access to Bedrock |
| §164.316 Documentation retention | S3 Object Lock **6-year retention** | Same for Bedrock logs |

### Must-enable before go-live

1. **[Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/)** — deny topics (`self-diagnosis without clinician`, `dosing override`, `illegal drug synthesis`), PII filter (NAME, PHONE, ADDRESS, EMAIL, DOB, SG_NRIC_FIN), custom MRN regex, grounding threshold ≥ 0.7, prompt-attack filter.
2. **[Comprehend Medical DetectPHI](https://docs.aws.amazon.com/comprehend/latest/dg/how-medical-phi.html)** on every inbound message before the model sees it.
3. **[Macie](https://aws.amazon.com/macie/)** weekly scans on `raw/`; quarantine on PHI-leak match.
4. **[Config + Security Hub](https://aws.amazon.com/security-hub/)** — HIPAA, NIST 800-53 conformance packs. Audit Manager nightly.
5. **[KMS customer-managed keys](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#customer-cmk)** on S3, OpenSearch Serverless, ElastiCache, Secrets Manager, Lambda env vars.
6. **VPC endpoints** for Bedrock, S3, OpenSearch, Secrets Manager — Lambda has zero Internet egress.
7. **[GuardDuty Malware Protection for S3](https://docs.aws.amazon.com/guardduty/latest/ug/malware-protection-s3.html)** on uploads from the Internal Upload Portal.

### HIPAA-eligible services used in this design (Singapore)

Bedrock, S3, Lambda, API Gateway, CloudFront, Cognito, OpenSearch Serverless, ElastiCache, Comprehend Medical, Macie, KMS, CloudTrail, CloudWatch, EventBridge, Step Functions, Textract, Bedrock Data Automation, Secrets Manager, GuardDuty, Security Hub. **Reconfirm eligibility in `ap-southeast-1` before launch** — AWS updates [monthly](https://aws.amazon.com/compliance/services-in-scope/).

## 5. Alibaba Cloud controls (Singapore)

| Safeguard | Alibaba primary control |
|---|---|
| Identity | [RAM](https://www.alibabacloud.com/product/ram) + [IDaaS EIAM 2.0](https://www.alibabacloud.com/help/en/idaas/) (SAML/OIDC) — federates hospital EntraID for clinicians, Nova EntraID for staff; MFA enforced; resource-group scoping |
| Network | VPC + [PrivateLink](https://www.alibabacloud.com/product/privatelink) to Model Studio / PAI-EAS; WAF + Anti-DDoS; ACL default-deny |
| Encryption at rest | [KMS BYOK](https://www.alibabacloud.com/product/kms) on OSS, OpenSearch, Tair, SLS |
| Encryption in transit | TLS 1.3; [ASM](https://www.alibabacloud.com/product/servicemesh) for mTLS |
| PHI handling | [DataWorks Data Security Guard](https://www.alibabacloud.com/product/dataworks) + [SDDP](https://www.alibabacloud.com/product/sddp) classification and masking |
| LLM content safety | [Content Moderation 2.0 for Generative AI](https://www.alibabacloud.com/product/content-moderation) — jailbreak, hate, medical misinformation, self-harm, bias filters |
| Audit + retention | [ActionTrail](https://www.alibabacloud.com/product/actiontrail) → [SLS](https://www.alibabacloud.com/product/log-service) → OSS WORM **6-year retention**; immutable log integrity |
| Compliance | Cloud Config + [Cloud Security Posture Management](https://www.alibabacloud.com/product/security-center); PDPA / ISO / MLPS baselines available |
| Secrets | [Credentials Manager](https://www.alibabacloud.com/help/en/kms/user-guide/secrets-manager-overview) with KMS + rotation FC |

### Alibaba Cloud Singapore compliance posture

ISO 27001 / 27017 / 27018 / 27701 / 22301, SOC 1 / 2 / 3, PCI DSS, PDPA alignment, GDPR-ready, HIPAA-ready (BAA coverage is region-specific — confirm with account team before processing US PHI). See [Alibaba Cloud Trust Center](https://www.alibabacloud.com/en/trust-center).

## 6. Hospital connectivity — SaaS-default with optional VPN

**Mode 1 (default)**: hospital accesses Nova over public HTTPS with TLS 1.3 + IdP federation + WAF + Anti-DDoS + optional per-tenant IP allow-list. PDPA regulates where data lands (Singapore, ≤ our Nova VPC); HIPAA §164.312(e) requires TLS-strength transmission security, which TLS 1.3 satisfies. No VPN required for modern hospitals whose FHIR + SharePoint are Internet-reachable.

**Mode 2 (opt-in)**: Site-to-Site IPsec VPN for hospitals with on-prem-only EHR or file shares. [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html) or [Alibaba VPN Gateway](https://www.alibabacloud.com/help/en/vpn-gateway) — AES-256-GCM, IKEv2, dual-tunnel HA. Carries only backend system-to-system flows (SharePoint pull, on-prem FHIR callback, Upload Portal if required). Clinician chat uses public HTTPS in both modes.

Full design in [`rag_and_pipelines.md` §Hospital connectivity](rag_and_pipelines.md#7-hospital-connectivity) (shared) and [`proposals/version_c_alibaba_qwen.md` §7.6](proposals/version_c_alibaba_qwen.md#76-hospital-connectivity--saas-default-with-optional-vpn) (Version C specifics).

## 7. AI-specific medical compliance

- **No PHI in training data** — ever. Mask or synthesize before SFT/DPO.
- **Grounded answers only** — citation required; guardrail blocks unsourced answers.
- **Clinician in the loop** — UI labels the assistant as decision support; preserves [FDA CDS carve-out](https://www.fda.gov/medical-devices/software-medical-device-samd/clinical-decision-support-software) for US clients.
- **Emergency disclaimer** — acute-lane responses auto-prepend "Call emergency services immediately" for patient-facing scenarios; clinician lane shows the disclaimer but doesn't block.
- **Red-team before launch** — 200+ adversarial prompts (PHI exfiltration, jailbreak, dosing override, self-diagnosis).
- **Audit every interaction** — `{user_id, hospital_id, question_hash, retrieved_chunk_ids, model_version, guardrail_verdict, answer_hash, citation_ids, latency_ms}` retained 6 years.
- **Model version freeze** — pin production version; re-qualify with eval harness before moving.
- **Re-evaluate on WHO refresh** — protocol changes can silently invalidate previously-correct answers.
- **Right to delete / rectify** — per-user chat history deletable without touching the RAG index (stored separately).
- **DR** — daily vector-store snapshots to a separate account/region (within SG's own AZs for PDPA simplicity); RPO ≤ 1 hour, RTO ≤ 4 hours.
- **Data minimization** — only the FHIR slice needed for the question goes to the model; never the full chart.
- **Separation of duties** — platform engineer and clinical-data custodian roles split; break-glass requires two-person approval + hardware MFA.

## 8. Pre-launch checklist

- [ ] Tenant in Singapore only; no default cross-border replication
- [ ] AWS BAA / Alibaba equivalent signed and scoped if any US PHI
- [ ] PDPA Data Protection Officer appointed (Nova side + hospital side)
- [ ] Bedrock Guardrails / Alibaba Content Moderation configured and red-teamed
- [ ] All stores on customer-managed KMS keys
- [ ] CloudTrail / ActionTrail → WORM storage for **6 years**
- [ ] Macie / SDDP weekly PHI scan
- [ ] Evaluation harness baseline locked (accuracy, latency, safety)
- [ ] DPIA (GDPR, if in scope) + HIPAA Security Risk Assessment (if in scope) completed
- [ ] Clinician-approval UI gate
- [ ] Emergency-disclaimer copy reviewed by legal
- [ ] Third-party penetration test
- [ ] Site-to-Site VPN configured; hospital IdP federation tested end-to-end
- [ ] Model card + system card published to hospital clients

## 9. References

- [HIPAA Records Retention — 6-year rule](https://www.hipaajournal.com/hipaa-retention-requirements)
- [HIPAA compliance for generative AI on AWS](https://aws.amazon.com/blogs/industries/hipaa-compliance-for-generative-ai-solutions-on-aws/)
- [Safeguard healthcare data with Bedrock Guardrails](https://aws.amazon.com/blogs/publicsector/how-to-safeguard-healthcare-data-privacy-using-amazon-bedrock-guardrails/)
- [Alibaba Cloud Trust Center](https://www.alibabacloud.com/en/trust-center)
- [Alibaba Content Moderation for Gen AI](https://www.alibabacloud.com/product/content-moderation)

*Content above is rephrased for compliance with licensing restrictions.*
