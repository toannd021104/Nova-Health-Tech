# Evaluation v2 — 50 Random Questions
## Multi-strategy chunking + numberOfResults=15 + streaming

**Date:** 2026-05-13 02:34
**Changes from v1:**
- Chunking: WHO=hierarchical (parent 1500, child 300), Clinical trials=semantic (max 512), ICD-11=no chunking
- numberOfResults: 5 -> 15
- Emergency lane: Vector KB only (no GraphRAG)
- Streaming endpoint: /api/chat/stream (SSE)
- Removed metadata filter

## Results

| Metric | v2 (this run) | v1 (900-question baseline) |
|---|---|---|
| Answered | 50/50 (100.0%) | 813/900 (90.3%) |
| Refused | 0/50 (0.0%) | 89/900 (9.9%) |
| Avg response time | 8569 ms | 7,811 ms |
| Emergency avg | 6239 ms | 5,825 ms |
| General avg | 11533 ms | 9,761 ms |
| Emergency SLA (<=5s) | 1/28 (3.6% if em_times else 'N/A') | 74/446 (16.6%) |
| General SLA (<=15s) | 22/22 (100.0% if gen_times else 'N/A') | 454/454 (100%) |
| Avg citations | 16.2 | 5.2 |
| p50 | 7089 ms | 7,490 ms |
| p95 | 13852 ms | 11,380 ms |

## Sample Answers

**[122] general** (11992ms, ANSWERED)
> Does WHO recommend colchicine for non-severe COVID-19?

Based on the retrieved WHO guidance:

**Answer:**  
No. WHO makes a **strong recommendation against** using colchicine for treatment of patients with non-severe COVID-19 [18].

**Rationale:**  
The gu...

---

**[328] general** (12720ms, ANSWERED)
> What is the WHO recommendation for antivirals in elderly COVID-19 patients?

Based on the retrieved context, I cannot provide a complete answer specific to elderly COVID-19 patients and antivirals from WHO guidance.

The context references WHO's living guideline on COVID-19 th...

---

**[515] emergency** (5448ms, ANSWERED)
> Non-severe COVID-19 outpatient at high risk. Should prophylactic anticoagulation be started per WHO?

# WHO Guidance on Prophylactic Anticoagulation in Non-Severe, High-Risk COVID-19

The retrieved context does not contain WHO recommendations on prophylactic anticoagulation for non-severe, high-risk C...

---

**[525] emergency** (7394ms, ANSWERED)
> Pregnant woman at 24 weeks with severe COVID-19. Can tocilizumab be used per WHO?

Based on the retrieved WHO COVID-19 therapeutics guideline, **the context does not contain explicit guidance on tocilizumab use in pregnant women.**

What the guideline does state:

- **Tocilizumab do...

---

**[663] emergency** (6269ms, ANSWERED)
> Non-severe COVID-19 patient at high risk with age 35 and HIV. Which antiviral does WHO recommend?

The retrieved context does not specify WHO's recommendation for a 35-year-old HIV-positive patient with non-severe COVID-19 at high risk.

The sources confirm that WHO makes conditional recommendation...

---

**[881] emergency** (5144ms, ANSWERED)
> [PMC4451740] Based on PMC4451740, a provider at a Nigerian facility has not been trained on MgSO4 — 

The retrieved context does not provide the specific percentage of providers who had received training on MgSO4 for PE/E management.

The document indicates that [2] "a majority of the providers (96%) ...

---

**[106] general** (10365ms, ANSWERED)
> What is the WHO recommendation regarding hydroxychloroquine for COVID-19?

**Recommendation:** WHO strongly recommends **not to use hydroxychloroquine or chloroquine** for COVID-19, regardless of disease severity [18].

**Supporting Evidence:**
- This strong recommendation a...

---

**[229] general** (9690ms, ANSWERED)
> What does very low certainty GRADE evidence mean in WHO COVID-19 guidelines?

Based on the retrieved context, I cannot find a specific definition or explanation of what "very low certainty" GRADE evidence means in the WHO COVID-19 guidelines. 

The retrieved excerpts reference ...

---

**[616] emergency** (6079ms, ANSWERED)
> Severe COVID-19 patient on corticosteroids is deteriorating. Should tocilizumab be added per WHO?

# Tocilizumab Addition in Deteriorating Severe COVID-19 on Corticosteroids

**The retrieved context does not contain WHO guidance on whether to add tocilizumab to patients already on corticosteroids w...

---

**[637] emergency** (5936ms, ANSWERED)
> Clinician asks whether to use a COVID-19 treatment with only observational evidence. What does WHO r

The retrieved context does not directly address WHO's stance on using COVID-19 treatments supported by observational evidence alone.

The context does indicate that WHO's living guideline on COVID-19 ...

---

