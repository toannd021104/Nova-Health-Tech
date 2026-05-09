# Alibaba Cloud Architecture — Nova Health Tech Clinical GenAI (Production Plan)

Parallel production design to the AWS build, using Qwen and Alibaba Cloud's managed services. Same production scope: real hundreds-of-documents RAG, monthly WHO refresh, fine-tuned student model for the 2-second emergency lane.

## 1. Why Qwen on Alibaba Cloud for Nova

- Qwen3 / 3.5 / 3.6 models are open-weight and natively fine-tunable on PAI with SFT / LoRA / QLoRA / DPO — confirmed in `askAli_AI_Assistant.txt`. That makes the distillation play (see `docs/architecture/fine_tuning_and_distillation.md`) far cheaper than the AWS equivalent.
- `qwen3-vl-embedding` produces a single fused vector across text + figures on a page, which matches the WHO PDFs' mix of body text, tables, and flowcharts.
- Qwen pricing is 5–10× cheaper per token than Claude / Nova; at Nova's expected volume the monthly bill is materially smaller.
- Alibaba's Singapore and Frankfurt regions hold ISO 27001/27017/27018/27701 and support GDPR posture; Shanghai supports MLPS 2.0 Level 3 for any mainland-China expansion.

## 2. Component diagram

```
                ┌────────────────────────────────────────────────────┐
                │               Clinician / Hospital                 │
                └──────────────────┬─────────────────────────────────┘
                            HTTPS + SSO (IDaaS SAML/OIDC)
                                   │
                    ┌──────────────▼──────────────┐
                    │  Anti-DDoS + WAF + CDN      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   API Gateway + RAM         │
                    └──────────────┬──────────────┘
                                   │
             ┌─────────────────────▼──────────────────────┐
             │   Function Compute — /chat handler         │
             │    (private VPC; no public egress)         │
             │  0. authn/z, 1. PHI mask, 2. classify,     │
             │  3. cache check, 4. retrieve, 5. generate, │
             │  6. ground check, 7. audit                 │
             └─┬─────────┬─────────────┬──────────────┬───┘
               │         │             │              │
   DataWorks /  │ Layer 1 │  Layer 2    │    Gen       │ Log
    SDDP mask   │ Tair    │  Qwen       │ (students,   │
               │ semantic│  Context    │  teacher)    │
               │ cache   │  Cache      │              │
               ▼         ▼             ▼              ▼
    ┌────────────────┐ ┌──────────┐ ┌──────────────────────┐ ┌─────────────────┐
    │ Reversible     │ │   Tair   │ │  Model Studio        │ │  SLS + OSS WORM │
    │ tokenization   │ │  (Redis- │ │  ┌────────────────┐  │ │  7-yr retention │
    │ via KMS        │ │  compat, │ │  │ Qwen3-Max      │  │ └─────────────────┘
    └────────────────┘ │  Tair    │ │  │ (teacher)      │  │
                       │  Vector) │ │  │ Qwen3-8B       │  │
                       └──────────┘ │  │ (student, SFT  │  │
                                    │  │  on PAI-EAS)   │  │
                                    │  └────────────────┘  │
                                    │  + Content Moderation│
                                    └──────────┬───────────┘
                                               │
                                ┌──────────────▼──────────────┐
                                │  OpenSearch Vector Search   │
                                │  Edition                    │
                                │  - index-who-guidelines     │
                                │  - index-internal-trials    │
                                │  - index-icd11              │
                                │  + text-embedding-v4 (text) │
                                │  + qwen3-vl-embedding (fig) │
                                └──────────────┬──────────────┘
                                               │
                                         OSS chunk store

Ingestion (async, event-driven):

  OSS raw bucket ──► EventBridge ──► Function Workflow
      ├── DocMind (general PDFs) + Qwen-VL-Max (complex tables / figures)
      ├── FC chunker (hierarchical 1500/300 tok, 15% overlap)
      ├── embed (text → text-embedding-v4; figure → qwen3-vl-embedding fused)
      ├── SDDP scan for PHI leakage (quarantine if found)
      └── OpenSearch upsert (by doc-hash)

Monthly refresh:

  CloudOps Scheduler (day 1, 00:00 UTC)
   └── Function Workflow
         ├── poll WHO guidelines RSS + download changed PDFs
         ├── walk WHO ICD-11 API delta
         └── ingestion pipeline for changed docs

Distillation (quarterly):

  OSS training-data bucket ◄── Model Studio Batch (Qwen3-Max, 50% off)
        └── clinician review ── DPO pair builder
              └── PAI Model Gallery (Qwen3-8B SFT + LoRA, optional DPO)
                    └── PAI-EAS (private endpoint) ── eval harness ── promote
```

## 3. Data pipeline

See `docs/architecture/rag_strategy.md` — the Alibaba-side realization of Strategy A (managed parse + managed RAG).

### 3.1 Sources

Identical to the AWS side — internal clinical trial PDFs, WHO guideline PDFs, WHO ICD-11 API. Same hierarchical 1500/300 chunking, same metadata fields on every chunk.

### 3.2 Parsing and embedding

- **DocMind** for general PDFs (body text + regular tables).
- **Qwen-VL-Max** invoked via PAI-pipeline for pages flagged as complex (flowcharts, multi-page tables, figures).
- **Text chunks** → `text-embedding-v4` (or `text-embedding-v3` if v4 not in region) — 1024 or 1536 dim depending on model.
- **Figure-bearing chunks** → `qwen3-vl-embedding` with `enable_fusion=True` (2560-dim), per `askAli_AI_Assistant.txt`.
- **OpenSearch Vector Search Edition** — the Model Studio embedding plugin handles re-vectorization on upload; one index per source with hybrid BM25 + kNN.

### 3.3 ICD-11 API as first-class source

Three integration points (same pattern as AWS):

1. **Ingest** — monthly `scripts/download_who_icd.py --walk --max-depth 2` writes JSON to OSS → chunker indexes one record per entity.
2. **Runtime tool call** — Model Studio Application exposes `icd11_lookup(term)` as a tool; Function Compute does the live API call.
3. **Query expansion** — a small FC step expands the clinician's query with ICD-11 synonyms before the hybrid BM25 call.

ICD-11 credentials live in **KMS-encrypted Secrets Manager** equivalent (Credentials Manager), accessible only to the Function Compute role.

## 4. Model orchestration

### 4.1 Router

A small FC classifier (optionally a distilled Qwen3-0.6B) picks the lane:

| Question class | Model | Temperature / top_p / top_k / seed | Guardrail | Latency target |
|---|---|---|---|---|
| Emergency / acute | **Fine-tuned Qwen3-8B student** on PAI-EAS (streaming) | 0.1 / 0.7 / 40 / 42 | Strict PHI + emergency disclaimer injector | **≤ 2 s** |
| Complex differential | **Qwen3-Max** (teacher, streaming) | 0.2 / 0.9 / — / — | Standard | 3–6 s |
| Literature / citation lookup | Student, grounded-only mode | 0.1 / 0.7 / 40 / 42 | No-hallucination | 1.5–2 s |
| Patient-education phrasing | Student with tone-preset system prompt | 0.2 / 0.9 / 40 / 42 | Standard + tone | 1–2 s |

Until the Qwen3-8B student is trained, the fast lane uses **Qwen3.5-Flash** directly — cheap and fast enough for the SLA, but without the tone alignment.

Qwen API is OpenAI-compatible, so the router code is the same as the AWS version with a different `base_url` and auth header.

### 4.2 Agent tools

Same four tools as AWS (`retrieve_guideline`, `lookup_trial`, `icd11_lookup`, `icd11_expand_query`), defined in Model Studio Application's tool config. Tools are read-only.

## 5. Security architecture

| Layer | Control |
|---|---|
| Account isolation | Resource Directory with Control Policy Service; one account per env |
| Network | FC in VPC; Model Studio + PAI-EAS via PrivateLink; OpenSearch Vector in VPC; no Internet egress |
| Identity | RAM + IDaaS SAML/OIDC; MFA enforced |
| Data at rest | OSS, OpenSearch, Tair, Credentials Manager all on customer-managed KMS (BYOK) |
| Data in transit | TLS 1.3; ASM for service-mesh mTLS |
| PHI handling | DataWorks Data Security Guard + SDDP classify → reversible tokenization in FC (KMS-backed) |
| LLM safety | Content Moderation 2.0 for generative AI — medical-misinformation, jailbreak, PII, bias filters. Fail → block + log |
| Audit | ActionTrail → SLS → OSS WORM 7-yr retention |
| Model risk | Eval harness gates every student retrain; production pins model version |
| Secrets | Credentials Manager with KMS; rotation Lambda for ICD-11 API credential |
| Compliance | ISO 27001/17/18/27701, MLPS 2.0 L3 (Shanghai), GDPR-aligned services (Singapore/Frankfurt) |

## 6. Deployment approach

### 6.1 Region strategy

| Hospital client | Region | Compliance posture |
|---|---|---|
| International SaaS default | Singapore or Frankfurt | ISO + GDPR |
| Mainland China | Shanghai | MLPS L3 + PIPL |
| On-prem (hospital DC) | Apsara Stack (Alibaba private-cloud) or ACK-Edge | Full local control; central cloud still does training |

### 6.2 Phased rollout

Mirrors the AWS phases; costs are materially smaller:

| Phase | Deliverable | Typical cost |
|---|---|---|
| 1 (weeks 1–6) | RAG + Qwen3.5-Flash fast lane + Qwen3-Max slow lane | Low hundreds of USD/mo in pilot |
| 2 (weeks 7–10) | Distill Qwen3-8B from Qwen3-Max outputs, LoRA on PAI | $30–100 per retrain |
| 3 (weeks 11–14) | 100% canary; add DPO; enable context caching + PTU on emergency lane | Marginal; PTU only if sustained TPM high |
| 4 (quarterly) | Retrain with new WHO + clinician data | < $100 per retrain |

### 6.3 Corporate integration

- **EHR / HIS bridge** — custom FastAPI container on ECS-equivalent (Serverless App Engine) exposing HL7v2 / FHIR → FC endpoint.
- **SSO** — IDaaS SAML 2.0 / OIDC.
- **Audit export** — SLS → OSS nightly → hospital SIEM.

## 7. Performance optimization — closing the 2-second budget

See `docs/architecture/caching_strategy.md`.

```
     25 ms   Tair semantic cache hit (30–45% of emergency queries)  ← return fast
    100 ms   Authn + PHI mask
     70 ms   Hybrid retrieval (OpenSearch Vector)
    300 ms   Student first-token (with Qwen context cache hit)
    1100 ms  Student full answer (250 tokens, streaming, PAI-EAS)
    110 ms   Moderation + citation check
  ────────
   ≤ 1,700 ms  p95 emergency budget
```

## 8. References

- [Fine-tune Qwen — Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/text-generation-model-tuning)
- [Quick start: Deploy, fine-tune, and evaluate Qwen3 models on PAI](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models)
- [Multimodal embeddings | Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings)
- [Context Cache feature for Qwen models](https://www.alibabacloud.com/help/en/model-studio/context-cache)
- [RAG-based application on PAI for finance and healthcare](https://www.alibabacloud.com/help/en/pai/use-cases/development-of-rag-application-flow)
- [Stream Model Responses with Low Latency via SSE](https://www.alibabacloud.com/help/en/model-studio/stream)
- [WHO ICD-11 API Swagger](https://id.who.int/swagger/index.html)

*Content above is rephrased for compliance with licensing restrictions.*
