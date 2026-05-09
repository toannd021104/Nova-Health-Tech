# Security & Compliance — Clinical GenAI Assistant

Best-practice summary gathered from AWS documentation, Alibaba Cloud documentation, and industry HealthTech guidance. **All quoted content is paraphrased; see references.**

## 1. Regulations that apply to Nova Health Tech

| Regulation | Where it applies | What it requires |
|---|---|---|
| **HIPAA + HITECH** (US) | US hospitals, US physician users, any ePHI | Privacy Rule, Security Rule, Breach Notification; BAA with any cloud processor; encryption, access control, audit, 7-year retention. |
| **GDPR** (EU) | EU patient data, EU physicians | Lawful basis, DPIA, data-subject rights, data-residency, 72-hour breach notice. |
| **FDA SaMD** (US) | If the assistant's output drives diagnostic decisions, it may be a Software-as-a-Medical-Device | Quality system, validation, post-market surveillance. Clinical-decision-support carve-out (21st Century Cures) may apply if clinician can independently review the basis. |
| **EU AI Act** | Healthcare AI classified as high-risk | Risk management, data governance, transparency, human oversight, post-market monitoring. |
| **MLPS 2.0 Level 3** (China) | Mainland-China deployment | Graded protection: network zoning, encryption, audit, annual third-party assessment. |
| **DSL + PIPL** (China) | Mainland-China patient data | Data classification, localization, cross-border transfer review (CAC filing). |
| **Singapore PDPA / HK PDPO** | APAC deployment | Consent, breach notification, data protection officer. |
| **ISO 27001 / 27701 / 27018** | Industry baseline | Information security mgmt + PII handling in cloud. |
| **HITRUST CSF** | Often required by US hospital procurement | Unified control framework mapping HIPAA + NIST. |

## 2. Shared-responsibility snapshot

- **Cloud provider** secures the platform: AWS signs a BAA covering HIPAA-eligible services; Alibaba Cloud holds ISO 27001/27017/27018/27701, MLPS L3 for relevant regions, and has a GDPR-ready product set in Singapore/Frankfurt.
- **Nova** configures the services, architecture, encryption, access, logging. **Using a compliant cloud does not make Nova compliant** — controls must be enforced in every deployment.

## 3. AWS controls for clinical GenAI (mapped to HIPAA Security Rule)

| HIPAA safeguard | AWS primary control | Bedrock-specific control |
|---|---|---|
| §164.308 Administrative (workforce, training, audit) | IAM Identity Center + IAM Access Analyzer + Audit Manager (HIPAA framework) | Bedrock Model Invocation Logging |
| §164.310 Physical | AWS data-center certifications | N/A (managed) |
| §164.312(a) Access control | IAM least-privilege roles, MFA, SCPs, VPC endpoints | Bedrock Agents with scoped tool IAM |
| §164.312(b) Audit | CloudTrail + S3 Object Lock (WORM) + Security Lake | Bedrock request/response logging |
| §164.312(c) Integrity | S3 versioning + Object Lock + Glacier Deep Archive | Guardrail grounding + citation check |
| §164.312(d) Person/entity authentication | Cognito + hospital SSO | Per-physician token embedded in Bedrock request |
| §164.312(e) Transmission security | TLS 1.3, VPC endpoints | Private VPC access to Bedrock |
| §164.316 Documentation retention | S3 Object Lock 7-year retention | Same for Bedrock logs |

### AWS-specific guardrails (must enable before go-live)

1. **Bedrock Guardrails** — create a "nova-health-clinical" guardrail with:
   - Denied topics: `self-diagnosis without clinician`, `dosage override`, `illegal drug synthesis`, `unsafe emergency self-treatment`.
   - PII filter: `NAME, PHONE, ADDRESS, EMAIL, AGE, DATE_OF_BIRTH, US_SSN, US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER` → anonymize.
   - Custom regex for MRN patterns.
   - Contextual grounding threshold ≥ 0.7 → block ungrounded answers.
   - Prompt attack filter.
2. **Comprehend Medical DetectPHI** on every inbound user message **before** it reaches the model.
3. **Macie** weekly scans on the S3 `raw/` prefix (it will flag PHI in uploaded documents).
4. **Config + Security Hub** — HIPAA, NIST 800-53, and PCI conformance packs. Audit Manager nightly assessment.
5. **KMS customer-managed keys** on S3, OpenSearch, ElastiCache, Lambda env vars.
6. **VPC endpoints** for Bedrock, S3, OpenSearch, Secrets Manager — Lambda has no internet egress.

### AWS HIPAA-eligible services used in this design

Bedrock, S3, Lambda, API Gateway, CloudFront, Cognito, OpenSearch Serverless, ElastiCache, Comprehend Medical, Macie, KMS, CloudTrail, CloudWatch, EventBridge, Step Functions, Textract, SageMaker. **Confirm current eligibility list before launch** (AWS updates monthly).

## 4. Alibaba Cloud controls for clinical GenAI

| Safeguard | Alibaba primary control |
|---|---|
| Identity | RAM + Cloud IDaaS (SAML/OIDC); enforce MFA; resource-group scoping |
| Network | VPC + Cloud Enterprise Network + PrivateLink to Model Studio/PAI; WAF + Anti-DDoS |
| Encryption at rest | KMS BYOK on OSS, OpenSearch, Tair, Log Service |
| Encryption in transit | TLS 1.3; Service Mesh (ASM) for mTLS between microservices |
| PHI handling | DataWorks Data Security Guard + Sensitive Data Protection (SDDP) to classify and mask |
| LLM content safety | **Content Moderation 2.0 (Green Net)** for generative AI — jailbreak, hate, medical-misinformation, self-harm, bias filters |
| Audit & retention | ActionTrail → SLS → OSS with WORM retention ≥ 7 yr; immutable log integrity |
| Compliance posture | Cloud Config + Cloud Security Posture Management; MLPS / GDPR / ISO baselines available |
| Cross-border transfer | If any mainland data leaves China, register with CAC; otherwise keep PHI in-region |

### Alibaba Cloud compliance certifications relevant to Nova

- ISO 27001 / 27017 / 27018 / 27701 / 22301
- SOC 1 / 2 / 3
- MLPS 2.0 Level 3 (and Level 4 for some regions)
- PCI DSS
- GDPR-aligned services with Singapore + Frankfurt regions
- HIPAA-ready — Alibaba Cloud offers a HIPAA readiness assessment. **Unlike AWS, Alibaba's BAA coverage is region-specific; confirm with account team before processing US PHI.**

## 5. AI-specific medical compliance best practices (cloud-agnostic)

Drawn from AWS, WHO, and HealthTech literature; applies to both clouds.

1. **No PHI in training data.** Mask or synthesize before any fine-tune run.
2. **Grounded answers only.** Every clinical claim carries a citation; unsourced answers are blocked by guardrails.
3. **Clinician in the loop.** The UI should label the assistant as "decision support" and require the clinician to accept/edit before acting — preserves the FDA CDS carve-out.
4. **Emergency disclaimer.** If the question is classified as acute emergency, always surface a disclaimer plus the local emergency number; never delay answer on the disclaimer.
5. **Red-team / abuse-test before launch.** Run ≥ 200 adversarial prompts (prompt-injection, PHI exfiltration, self-diagnosis, dosage override, jailbreaks).
6. **Audit every interaction.** Store `{user_id, question_hash, retrieved_chunk_ids, model_version, guardrail_verdict, answer_hash, citation_ids, latency_ms}` with 7-year retention.
7. **Model version freeze.** Pin a model version for production; don't auto-upgrade. Re-qualify with evaluation harness when moving to a new version.
8. **Re-evaluate on every WHO refresh.** A protocol change can silently invalidate previously-correct answers.
9. **Right to delete / right to rectify.** Keep per-user vectors and chat history deletable without touching the RAG index (store them separately).
10. **Disaster recovery.** Daily OpenSearch snapshots to a separate account/region; RPO ≤ 1 hour, RTO ≤ 4 hours.
11. **Data minimization.** Never send full patient chart to the model — pass only the FHIR slice needed for the question.
12. **Separation of duties.** Production data-access roles split between platform engineer and clinical-data custodian; break-glass requires two-person approval.

## 6. Recommended pre-launch checklist

- [ ] AWS BAA signed (or Alibaba equivalent per region).
- [ ] Bedrock Guardrails / Alibaba Content Moderation configured and red-teamed.
- [ ] All stores on customer-managed KMS keys.
- [ ] CloudTrail / ActionTrail → WORM storage for 7 years.
- [ ] Macie / SDDP weekly PHI scan.
- [ ] Evaluation harness baseline locked (accuracy, latency, safety).
- [ ] DPIA (GDPR) + HIPAA Security Risk Assessment completed.
- [ ] Clinician-approval UI gate in the frontend.
- [ ] Emergency disclaimer copy reviewed by legal.
- [ ] Third-party penetration test (external).
- [ ] Model card + system card published to hospital clients.

## 7. Key references

- [HIPAA compliance for generative AI solutions on AWS](https://aws.amazon.com/blogs/industries/hipaa-compliance-for-generative-ai-solutions-on-aws/)
- [How to safeguard healthcare data privacy using Amazon Bedrock Guardrails](https://aws.amazon.com/blogs/publicsector/how-to-safeguard-healthcare-data-privacy-using-amazon-bedrock-guardrails/)
- [Is Amazon Bedrock HIPAA‑eligible — Accountable HQ](https://www.accountablehq.com/post/is-amazon-bedrock-hipaa-eligible-what-to-know-about-the-aws-baa-and-using-phi)
- [Building a Secure GenAI Architecture in HealthTech — Sekurno](https://www.sekurno.com/post/building-a-secure-genai-architecture-in-healthtech-avoiding-hipaa-gdpr-pitfalls)
- [Fine-tuning LLMs in healthcare — AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/latest/generative-ai-nlp-healthcare/fine-tuning.html)
- [Alibaba Cloud compliance center](https://www.alibabacloud.com/en/trust-center)
- [Alibaba Cloud Content Moderation](https://www.alibabacloud.com/product/content-moderation)

*Content above is rephrased for compliance with licensing restrictions.*
