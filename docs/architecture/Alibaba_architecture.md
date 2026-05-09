# Alibaba Cloud Architecture — Nova Health Tech Clinical GenAI Assistant (Qwen)

## 1. Why Alibaba Cloud + Qwen for Nova

- **Qwen3 / Qwen3.5 / Qwen3.6** are open-weight, fine-tunable on Alibaba Cloud PAI with SFT, LoRA, QLoRA, DPO and GRPO — confirmed in `askAli_AI_Assistant.txt`.
- **qwen3-vl-embedding** on Model Studio produces a single fused vector across text + images + video — ideal for the "legacy PDFs with figures and inconsistent tagging" problem Nova describes.
- Strong price/performance: qwen3.5-flash at $0.10 / 1M input tokens, Qwen-Plus at $0.4/$1.2 for input/output (per 1M), vs Claude Haiku 4.5 ~$1/$5.
- Mainland-China and APAC data-residency advantages if Nova expands into those markets.
- Alibaba Cloud has a 1M-free-token quota per Qwen model for trial, plus PAI workspace activation is free (pay per job).

## 2. Component diagram (textual)

```
                ┌────────────────────────────────────────────────────┐
                │               Clinician / Hospital                 │
                └──────────────────┬─────────────────────────────────┘
                            HTTPS + SSO (IDaaS)
                                   │
                    ┌──────────────▼──────────────┐
                    │  Anti-DDoS + WAF + CDN      │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   API Gateway + RAM         │   ← per-physician token
                    └──────────────┬──────────────┘
                                   │
             ┌─────────────────────▼──────────────────────┐
             │   Function Compute (FC) — /chat handler    │
             │    (in private VPC; no public egress)      │
             └─┬─────────┬─────────────┬──────────────┬───┘
               │         │             │              │
    1. PHI mask│ 2. Cache│ 3. Retrieve │ 4. Generate  │ 5. Audit
               ▼         ▼             ▼              ▼
    ┌────────────────┐ ┌────────────┐ ┌────────────────┐ ┌─────────────────┐
    │ DataWorks PII  │ │ Tair       │ │ OpenSearch     │ │ Model Studio    │
    │ Detection /    │ │ (Redis-    │ │ Vector Search  │ │  Qwen3-Plus /   │
    │ custom masking │ │ compatible)│ │ Edition        │ │  Qwen3-Flash    │
    │ + KMS reversal │ │ sem cache  │ │ + RAG app      │ │  + Guardrails   │
    └────────────────┘ └────────────┘ └────────┬───────┘ └────────┬────────┘
                                               │                  │
                                  Hybrid (BM25+kNN) with metadata filter
                                               │                  │
                                      ┌────────▼────────┐ ┌───────▼───────┐
                                      │ OSS (bucket)    │ │ SLS Log Store │
                                      │  + OSS Vectors  │ │ + Audit Trail │
                                      │  (multi-KB)     │ │ 7-yr retention│
                                      └─────────────────┘ └───────────────┘

Ingestion pipeline:

  OSS raw bucket ──► EventBridge ──► Function Workflow (serverless FC orchestration)
                                           │
                                           ├─► DocMind / Unstructured-on-PAI (PDF → structured)
                                           │   + Qwen-VL for figure captioning (inconsistent tagging fix)
                                           │
                                           ├─► FC chunker (section-aware, 512 tok, 15% overlap)
                                           │
                                           ├─► qwen3-vl-embedding (enable_fusion=True)
                                           │
                                           └─► OpenSearch Vector Search index sync

Monthly WHO refresh:

  CloudOps Scheduler (day 1, 00:00 UTC)
     └─► FC workflow: poll WHO IRIS RSS + ICD-11 API
             └─► download to OSS ──► ingestion pipeline (incremental upsert)

Fine-tuning lane (periodic):

  OSS training data ──► PAI-DSW (notebook) or PAI Model Gallery
                               └─► Qwen3-8B SFT + LoRA (+ DPO)
                                       └─► PAI-EAS online endpoint (private VPC)
```

## 3. Data pipeline

| Source | Format | Ingest service | Why |
|---|---|---|---|
| Internal clinical trial PDFs (legacy, inconsistent tagging) | PDF | OSS → **DocMind** (Alibaba doc parser) or PAI-pipeline with Qwen-VL captioning | Qwen-VL handles scanned tables + figures; DocMind produces structured JSON |
| WHO guideline PDFs | PDF | OSS → DocMind + Qwen-VL | Monthly cron via CloudOps Scheduler |
| WHO ICD-11 | JSON/FHIR | FC → OSS (direct) | No parsing needed — structured API |
| PubMed abstracts | JSONL (MedRAG) / XML (FTP) | FC → OSS | Daily delta |
| FDA drug labels | JSON | FC → OSS | Weekly |

### 3.1 Embedding strategy — multimodal for PDFs with figures

Per `askAli_AI_Assistant.txt`, **qwen3-vl-embedding with `enable_fusion=True`** is the right choice: a single 2560-dim vector covers the text + images on each PDF page, so a clinician asking "show me the TKI resistance pathway diagram" can retrieve the figure directly.

```python
# Example (pseudo-code used in FC handler)
resp = dashscope.MultiModalEmbedding.call(
    model="qwen3-vl-embedding",
    input=[{"text": chunk_text}, {"image": f"oss://nova-raw/{page_image_key}"}],
    enable_fusion=True,
)
vector = resp.output["embeddings"][0]["embedding"]   # 2560-dim fused
```

Fallback model: `tongyi-embedding-vision-plus` when separate text/image vectors are required (e.g., cross-modal search where we want "find images matching this text").

### 3.2 Vector store — OpenSearch Vector Search Edition

- Native Qwen3 embedding integration — no separate embedding service to manage.
- Supports hybrid (keyword + vector) with HNSW.
- Metadata filtering by `{source, speciality, date, evidence_grade}` in the same query.
- Automatic re-vectorization when the OpenSearch Model Studio plugin is configured.

### 3.3 Monthly WHO update workflow

```
Day 1 of month, 00:00 UTC
   │
   └─► FC Workflow `who_monthly_refresh`
         ├─► Poll WHO ICD-11 API (delta since last run)
         ├─► Download latest guideline PDFs (authenticated IP)
         ├─► DocMind parse
         ├─► Chunk + embed (qwen3-vl-embedding)
         ├─► OpenSearch upsert (by doc-hash to skip unchanged chunks)
         └─► Send Slack/Feishu alert with summary of new protocols
```

## 4. Model orchestration

Model Studio **Application (RAG)** feature manages the retrieve-then-generate flow, with routing layered on top:

| Question class | Model | Guardrail | Latency target |
|---|---|---|---|
| Emergency / acute | **Qwen3.5-Flash** streaming | Medical safety moderation + strict PHI | **≤ 2 s** |
| Complex reasoning | Qwen3-Max | Standard | 3–6 s |
| Patient education / tone | Fine-tuned Qwen3-8B (LoRA) on Nova-voice corpus, served on PAI-EAS | Standard | 1–2 s |
| Citation lookup | Qwen3.5-Flash + grounded mode | Strict no-hallucination | ~1.5 s |

Qwen API is **OpenAI-compatible**, so the same Lambda/Function-Compute router code works with minimal change (`base_url=https://dashscope-intl.aliyuncs.com/compatible-mode/v1`).

### 4.1 Agent tools

- `retrieve_guideline(topic, source=WHO, date_gte=90d)` — via Model Studio RAG app or direct OpenSearch query.
- `lookup_trial(nct_id)` — FC that fetches ClinicalTrials.gov.
- `icd11_code(clinical_term)` — FC calling WHO ICD-11 API.

## 5. Security architecture

| Layer | Control |
|---|---|
| Account & resource isolation | Separate Alibaba Cloud accounts (prod/stage/dev) under Resource Directory; SCP-equivalent via Control Policy Service |
| Network | All FC in VPC; Model Studio accessed via PrivateLink; OpenSearch Vector in VPC; security group default-deny |
| Identity | RAM + IDaaS federated SSO; per-physician role with least privilege |
| Data at rest | OSS + OpenSearch + Tair encrypted via KMS BYOK (customer-managed keys) |
| Data in transit | TLS 1.3; internal mTLS for service mesh (ASM) |
| PHI handling | DataWorks Data Security Guard scans training & ingest data for PHI; custom FC for reversible tokenization backed by KMS |
| Prompt safety | **Content Moderation (Green Net) for Qwen** — jailbreak, medical misinformation, prompt-injection filters; custom "medical-safety" template added per product requirements |
| Audit | ActionTrail → SLS + OSS (WORM retention ≥ 7 yr); every Qwen call logged via Model Studio observability |
| Grounding check | Post-generation rerank + citation validator in FC; reject if no retrieved chunk is cited |
| Compliance scan | Cloud Config + Cloud Security Posture Management; weekly HIPAA / ISO 27001 / MLPS L3 checks |
| Medical data residency | Mainland China: deploy in Shanghai region under **MLPS Level 3**; International: Singapore or Frankfurt for GDPR + ISO 27001/27701/27018 |

## 6. Deployment approach

### 6.1 RAG first, then Qwen fine-tune

| Phase | Delivers | Platform | Budget feasibility |
|---|---|---|---|
| 1 | RAG-only assistant | Model Studio RAG app + OpenSearch Vector | Lowest cost — pay only for tokens + OpenSearch OCU |
| 2 | Tone SFT on **Qwen3-8B** (LoRA) | PAI Model Gallery → PAI-EAS | Single GPU-A10/A100 job, typically $50–150 for a 10k-sample run |
| 3 | Medical domain SFT on **Qwen3-14B or Qwen2.5-7B-Instruct** + optional **DPO** for safety alignment | PAI Model Gallery | Multi-GPU, a few hundred USD. DPO needs a preference dataset — budget for clinician labeling. |
| 4 (aspirational) | **GRPO** reinforcement learning on medical reasoning (Qwen3 supports GRPO) | PAI-DSW | High cost, only justified if evaluation plateaus |

### 6.2 Emergency-care feasibility within budget

- **Qwen3.5-Flash** alone can hit the 2-second SLA for 90%+ of emergency queries without any fine-tune; its first-token latency is typically ~300 ms. Fine-tuning is only needed for tone and edge cases.
- For the budget-constrained case, use Qwen-Plus on pure RAG — roughly $0.4/$1.2 per 1M input/output tokens. A realistic emergency query (~2k input + 300 output tokens with RAG context) costs about $0.0012 per answer.

### 6.3 Public cloud vs hybrid vs on-prem

Recommendation: **Hybrid** for Nova because hospital clients range widely in risk appetite.

| Option | When |
|---|---|
| Alibaba Cloud public region (Singapore/Frankfurt) + VPC isolation | Default for Nova-hosted SaaS |
| Alibaba Cloud Shanghai region + MLPS L3 | For mainland hospital clients |
| **Apsara Stack** (Alibaba's private-cloud stack) on-prem at hospital | For hospitals that refuse any public-cloud PHI traffic |
| **ACK-Edge** (edge Kubernetes) with a Qwen3-8B fine-tuned model served on PAI-EAS at edge | Hospital data center needs local inference; central cloud still trains & syncs embeddings |

### 6.4 Corporate integration

- **EHR / HIS** via custom FastAPI bridge (HL7 v2 + FHIR) → FC endpoint.
- **SSO** via IDaaS (SAML 2.0 / OIDC).
- **Audit export** nightly to hospital SIEM via SLS OSS archive.

## 7. Performance optimization (2-second SLA)

| Technique | Savings |
|---|---|
| Qwen3.5-Flash with streaming | First-token ~300 ms |
| Tair semantic cache (Redis-compatible) | 30–45% hit rate expected |
| OpenSearch Vector HNSW + hybrid retrieval | Retrieval < 100 ms |
| `parameters.result_format="message", stream=true` | Streaming SSE to client |
| Reserved PTU (Provisioned Throughput Units) for Qwen during peak ER hours | Eliminates queueing |
| Context caching on Qwen (input-token discount when repeated context) | Reduces cost for repeated clinical-protocol prompts |
| Edge rerank with smaller Qwen3-0.6B (distilled) in FC | Skip full-model call for high-confidence cache hits |

**Budget:**

```
  200 ms  → API Gateway + RAM auth
  100 ms  → PHI mask
   90 ms  → OpenSearch Vector hybrid retrieve
  300 ms  → Qwen3.5-Flash first token
 1200 ms  → full answer (300 tokens)
  110 ms  → moderation + citation check
-------
 2000 ms  ← target
```

## 8. What gets built vs. bought

| Custom code | Managed services used |
|---|---|
| FC router + PHI masker | Model Studio, PAI Model Gallery, PAI-EAS, DashScope embeddings |
| FHIR/HL7 EHR bridge | OpenSearch Vector Search Edition, OSS, Tair, DocMind |
| Evaluation harness | Content Moderation, KMS, RAM, IDaaS, ActionTrail, SLS |

## 9. References

- [Fine-tune Qwen — Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/text-generation-model-tuning)
- [Quick start: Deploy, fine-tune, and evaluate Qwen3 models on PAI](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models)
- [Multimodal embeddings | Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings)
- [RAG-based application on PAI for finance and healthcare](https://www.alibabacloud.com/help/en/pai/use-cases/development-of-rag-application-flow)
- [Model Studio billing and free quota](https://www.alibabacloud.com/help/en/model-studio/new-free-quota)
- [Model training and deployment billing (PTU and token)](https://www.alibabacloud.com/help/en/model-studio/model-training-and-deployment-billing)

*Content above is rephrased for compliance with licensing restrictions.*
