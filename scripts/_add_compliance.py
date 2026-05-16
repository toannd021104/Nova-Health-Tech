import pathlib
f = pathlib.Path('docs/Client_QA_500_Questions.md')
content = f.read_text(encoding='utf-8')

addendum = '''

---

## Compliance Addendum: Singapore Regulatory Updates (May 2026)

*This section corrects and supplements the compliance answers throughout this document based on regulatory developments in 2024-2026.*

---

### UPDATE 1: AIHGle 2.0 — AI in Healthcare Guidelines (MOH + HSA, 10 March 2026)

**What it is**: MOH and HSA jointly published revised AI in Healthcare Guidelines (AIHGle 2.0), replacing the 2021 version. This is now the **primary governance document** for AI in Singapore healthcare.

**Who it applies to**: Three stakeholder groups:
- **Developers** (manufacturers like Nova): responsible for safe design, documentation, post-market surveillance
- **Deployers** (healthcare organizations, Nova's hospital clients): responsible for governance, risk assessment, staff training
- **Users** (clinicians): responsible for appropriate use, maintaining professional judgment

**Two AI use case categories**:
- **Clinical**: AI that directly impacts patient care outcomes (diagnosis, monitoring, treatment). Our system falls here.
- **Clinical-Ops**: AI in clinical workflow without direct clinical impact (e.g., transcription, scheduling).

**Seven core ethical principles** (all must be addressed):
1. Safety
2. Fairness
3. Transparency
4. Explainability
5. Robustness
6. Security and data protection
7. AI alignment to human values/goals

**Generative AI section**: AIHGle 2.0 explicitly addresses generative AI (our system uses Claude/Qwen), including risk mitigation strategies specific to LLMs.

**Our system's alignment**: All 7 principles are addressed in our architecture. Citation grounding covers transparency/explainability. Guardrails cover safety/robustness. KMS + audit trail cover security/data protection.

> Reference: https://www.bakermckenzie.com/en/insight/publications/2026/03/singapore-moh-and-hsa-launch-refreshed-ai-in-healthcare-guidelines

---

### UPDATE 2: Health Information Act (HIA) — Passed January 2026, Effective Early 2027

**What it is**: The Health Information Act (HIA) was passed in Parliament in January 2026. It replaces the previous voluntary NEHR framework with **mandatory health data sharing**.

**Key requirements**:
- All HCSA licensees (hospitals, clinics) **must** contribute key health information to NEHR
- Information includes: allergies, vaccinations, diagnoses, medications, lab results, radiology images, discharge summaries
- AI tools accessing NEHR data require specific patient consent and audit trail
- Cybersecurity and data security standards are mandatory (see Update 4)

**Effective date**: Early 2027 (MOH giving healthcare providers time to prepare)

**Impact on our system**:
- Our current deployment does NOT use NEHR data (hospital-internal data only)
- When HIA takes effect, hospitals may want to integrate NEHR data into AI queries
- This requires: specific patient consent, audit trail to NEHR central registry, data minimization
- We have planned a NEHR-Pro connector for Year 2 deployment (~,000-150,000 one-time engineering)

**What changed from our earlier Q&A**: We previously described this as "HIE Bill (pending)." It is now **enacted law** (HIA 2026), effective early 2027.

> Reference: https://www.bakermckenzie.com/en/insight/publications/2026/01/singapore-health-information-bill-passed-in-parliament

---

### UPDATE 3: PDPC Advisory Guidelines on AI (1 March 2024)

**What it is**: The Personal Data Protection Commission published Advisory Guidelines on the use of personal data in AI recommendation and decision systems.

**Key guidance**:
- Covers three stages: **development** (training AI), **deployment** (B2C), **procurement** (B2B)
- Organizations can use personal data for AI where there is meaningful consent, OR rely on PDPA exceptions (e.g., business improvement, research purposes)
- Transparency requirements: users should be informed when personal data is used to train AI systems
- Note: These guidelines apply to **discriminative AI** (recommendation/decision systems). Generative AI guidelines are expected separately.

**Impact on our system**:
- Our fine-tuning uses de-identified data only (no PHI) — compliant
- We do not train on patient data without explicit consent — compliant
- Transparency: we disclose AI use in patient consent forms — compliant
- Procurement: hospitals procuring our system should review these guidelines for their vendor due diligence

> Reference: https://www.pdpc.gov.sg/media-events/advisory-guidelines-on-use-of-personal-data-in-ai-recommendation-and-decision-systems-now-available

---

### UPDATE 4: MOH Cybersecurity and Data Security Essentials (April 2026)

**What it is**: MOH published Cybersecurity and Data Security Essentials guidelines under the HIA framework, developed in consultation with CSA, IMDA, and PDPC.

**Who it applies to**: All HIA entities, including HCSA licensees (our hospital clients) and NEHR contributors.

**Three areas covered**:

**Cybersecurity (IT and software)**:
- Prompt installation of software updates
- Measures to secure hardware and software
- Backup and storage protocols
- Asset identification and protection

**Data Security (data-related practices)**:
- Policies to identify and protect health information
- Purpose-limited retention periods
- Authorized disclosure on need-to-know basis
- Prevention of improper transfers

**Common Practices (organizational)**:
- Personnel training
- Vendor management responsibilities
- Regular internal audits and security reviews
- Proper disposal
- Emergency planning and incident response

**Impact on our system**:
- Our architecture already meets all requirements
- Vendor management: hospitals must assess Nova as a vendor under these guidelines
- We provide: security documentation, audit logs, penetration test reports, ISO 27001 (inherited)
- Incident response: our runbooks and 24/7 SRE coverage satisfy the emergency planning requirement

> Reference: https://www.bakermckenzie.com/en/insight/publications/2026/04/singapore-moh-publishes-cybersecurity-and-data-security

---

### UPDATE 5: HSA SHARE Platform (July 2025)

**What it is**: HSA transitioned from MEDICS to SHARE (Submission for Harmonized Evaluation and Registration) for medical device submissions in July 2025.

**Impact on our system**:
- All new SaMD (Software as a Medical Device) submissions must use SHARE
- Our HSA Class B registration should be submitted via SHARE
- No change to classification criteria or requirements — only the submission portal changed

> Reference: https://asiaactual.com/blog/medical-device-submission-singapore-hsa-platform-update/

---

### UPDATE 6: Singapore Achieves WHO's Highest Tier for Medical Device Regulation (March 2026)

**What it means**: Singapore became the first WHO Member State to attain the highest classification for medical device regulation. This signals:
- Singapore's regulatory framework is internationally recognized as world-class
- HSA's SaMD guidelines are aligned with global best practices
- Easier mutual recognition with other high-tier countries (US FDA, EU, Australia TGA)
- Stronger credibility for Singapore-registered medical devices globally

**Impact on our system**:
- Our HSA Class B registration carries more international weight
- Easier to expand to other markets using Singapore registration as reference
- Demonstrates Singapore's commitment to rigorous AI medical device oversight

> Reference: https://www.who.int/news/item/10-03-2026-singapore-sets-global-first-by-reaching-who-s-highest-classification-for-medical-device-regulation

---

### SUMMARY: Compliance Checklist (Updated May 2026)

| Regulation | Status | Our Position |
|---|---|---|
| PDPA (2012, amended 2020) | Active | Compliant: PHI masking, KMS, audit trail, DPO |
| HCSA 2020 | Active | Compliant: HCSA license required for hospital deployer |
| AIHGle 2.0 (March 2026) | Active | Compliant: all 7 principles addressed in architecture |
| HIA 2026 | Enacted, effective early 2027 | Planned: NEHR connector for Year 2 |
| PDPC AI Guidelines (March 2024) | Active | Compliant: de-identified training data, transparency |
| MOH Cybersecurity Essentials (April 2026) | Active | Compliant: all requirements met |
| HSA SaMD Class B | Required | Planned: submit via SHARE platform |
| Cybersecurity Act 2018 (CII) | Active for CII hospitals | Compliant: Anti-DDoS, WAF, audit logs, incident response |
| IMDA AI Verify | Voluntary (de facto for gov contracts) | Planned: self-assessment in Month 5 |
| ISO 27001 / SOC 2 | Active | Inherited from AWS/Alibaba |

'''

f.write_text(content + addendum, encoding='utf-8')
print('Addendum written, new size:', f.stat().st_size)
