# Version C — Alibaba Cloud + Qwen (Singapore)

**Recommended default.** The only version with **zero cross-region hops at query time**, the lowest monthly bill, and the most flexible fine-tuning toolbox. Singapore-native for PDPA.

- Primary region: **Singapore International** ([Model Studio SG Intl](https://www.alibabacloud.com/help/en/model-studio/regions/))
- All data and all query-path compute stay in Singapore
- Fast lane: [Qwen3.5-Flash](https://www.alibabacloud.com/help/en/model-studio/model-pricing) · Complex lane: Qwen3.5-Plus · Vision specialist: Qwen3-VL-Plus
- Student served from day one: Qwen3-8B on [PAI-EAS](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models) with SFT + LoRA
- Managed GraphRAG via [AnalyticDB for PostgreSQL GraphRAG service](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service)
- Monthly cost: **~$2,220 base** / ~$2,280–3,060 with student

---

## 1. Executive summary

The executive board needs a GenAI assistant that answers complex medical questions, grounds every answer in internal trial reports + [WHO guidelines](https://www.who.int/publications) + [WHO ICD-11 API](https://id.who.int/swagger/index.html), hits a 2-second SLA on emergency queries, runs auditable for six years per [HIPAA §164.530(j)](https://www.hipaajournal.com/hipaa-retention-requirements/), and respects [Singapore PDPA data residency](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers).

Version C delivers this on Alibaba Cloud Singapore International in a single-region topology. The entire query path — chat, retrieval, rerank, moderation, graph traversal — runs inside `ap-southeast-1` with no cross-border hops. The five-region [Model Studio](https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio) deployment (Singapore, Virginia, Beijing, Hong Kong, Frankfurt — **not Tokyo**, verified via DNS on 10 May 2026) means Singapore International is a first-class region, not a lift-and-shift.

Every capability listed below is **active on day one**. Training for the Qwen3-8B student happens pre-launch; continuous retraining runs after. No phases.

| Scenario requirement | How Version C meets it |
|---|---|
| Complex medical Q&A | Qwen3.5-Plus on complex lane + agentic RAG + managed GraphRAG |
| Ground in internal trials + WHO + external sources | Hybrid retrieval on OpenSearch Vector Search Edition + ICD-11 API runtime tool + PubMed E-utilities tool |
| Auditable, compliant | ActionTrail → SLS → OSS WORM 6-year; [Content Moderation 2.0](https://www.alibabacloud.com/product/content-moderation); [DataWorks SDDP](https://www.alibabacloud.com/product/sddp) PHI mask |
| Fast enough for diagnosis (≤ 2 s emergency) | Pure if/else emergency toggle + Qwen3.5-Flash + Qwen3-8B student + 3-layer cache + Qwen PTU on peak |
| Monthly WHO refresh | EventBridge-equivalent cron pulls WHO monthly; incremental re-index of AnalyticDB PG graph |
| Patient-sensitive trial data | DataWorks SDDP classification + reversible tokenization + in-region KMS BYOK |
| Consistent tone | Qwen supports `seed=42` for determinism + SFT on Nova-approved answers + `temperature=0.1` |
| Legacy PDF ingestion | [DocMind](https://www.alibabacloud.com/help/en/model-studio) + Qwen-VL-Max for complex pages |
| Structured WHO ICD-11 API | Daily delta pull + runtime `icd11_lookup` tool + query expansion |

---

## 2. Region and data residency

| | Setting |
|---|---|
| Primary region | Singapore International (`ap-southeast-1`) |
| Backup / surge region for PAI GPU capacity | Tokyo (`ap-northeast-1`) — training only, optional |
| PDPA posture | No default cross-border transfer. All query-path data stays in SG. |
| [Model Studio regional coverage](https://www.alibabacloud.com/help/en/model-studio/regions/) | SG, Virginia, Beijing, Hong Kong, Frankfurt |
| Cross-region hops at query time | **0** |

Model Studio Singapore International endpoint is `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`. In International mode, inference compute is scheduled globally **excluding Chinese Mainland** — PDPA-compatible since no data ever lands in CN Mainland.

No Apsara Stack / on-prem in scope. Hospital connects over Site-to-Site IPsec VPN on [VPN Gateway](https://www.alibabacloud.com/help/en/vpn/) (IKEv2 + AES-256-GCM + SHA-2, dual-tunnel HA).

---

## 3. Component diagram

```
              ┌──────────────────────────────────────────────────────────────┐
              │   Hospital network (clinician workstations + EHR + SharePoint)│
              └──┬──────────────────────────────────────────────┬────────────┘
                 │                                              │
         AI chat │                                Internal mgmt │ HTTPS over
                 │ HTTPS                                         │ IPsec VPN
                 ▼                                               ▼
     ┌──────────────────────┐                      ┌──────────────────────────┐
     │ Anti-DDoS + WAF +    │                      │ Customer Gateway on-prem │
     │ Alibaba CDN          │                      └──────────┬───────────────┘
     └──────┬───────────────┘                                 │
            │                                                 │
     ┌──────▼──────────┐   ─────── Site-to-Site IPsec VPN ───►│ VPN Gateway
     │ API Gateway     │                                      │ (private side)
     │  + RAM / IDaaS  │                                      └──────────┬───────────┘
     │    authorizer   │                                                 │
     └──────┬──────────┘                                                 ▼
            │                                                 ┌──────────────────────┐
            │                                                 │ Private SLB + IDaaS  │
            │                                                 │ OIDC/SAML ← EntraID  │
            │                                                 │                      │
            │                                                 │ SAE container:       │
            │                                                 │  Upload Portal       │
            │                                                 └──────────┬───────────┘
            │                                                            │
            ▼                                                            ▼
   ┌──────────────────────────────┐                        ┌──────────────────────────┐
   │ Function Compute /chat (VPC) │                        │ OSS raw bucket            │
   │  0. RAM/IDaaS token check    │◄──── semantic cache ──┤ /raw/scheduled/...        │
   │  1. PHI mask (DataWorks SDDP) │     hit returns early │ /raw/manual/...           │
   │  2. if/else on emergency      │                       │ /raw/icd11/...            │
   │     toggle (pure, no LLM)     │                       │ /raw/who/...              │
   │  3. Model Studio Agent /      │                       └──────────┬───────────────┘
   │     Workflow app invoke       │                                  │ ObjectCreated
   │  4. ground-check + audit      │                                  ▼
   └─────┬──────────────┬──────────┘                       ┌──────────────────────────┐
         │              │                                  │ Function Workflow         │
 Layer 1 │    Layer 2   │  Generation                      │  DocMind parse → chunk →  │
 Tair    │    Qwen      │  (Model Studio + PAI-EAS):       │  embed → KB + graph sync  │
 +Tair   │    Context   │   Qwen3.5-Flash (fast, router,   │                           │
 Vector  │    Cache     │     Emergency agent)             │ + Security Center scan    │
 semantic│  (implicit + │   Qwen3.5-Plus (complex +        │ + SDDP PHI scan           │
 cache   │   explicit)  │     teacher + 39 specialists)    │                           │
         │              │   Qwen3-VL-Plus (Radiology)      │                           │
         │              │   Qwen3-8B student (PAI-EAS,     │                           │
         │              │     ~60% of complex traffic)     │                           │
         │              │   + Content Moderation 2.0       │                           │
         │              │                                  └──────────┬───────────────┘
         │              │                                             ▼
         │              │                             ┌────────────────────────────┐
         │              │                             │ Model Studio Knowledge Base│
         │              │                             │  kb-who-guidelines         │
         │              │                             │  kb-internal-trials        │
         │              │                             │  kb-treatment-protocols    │
         │              │                             │  kb-icd11                  │
         │              │                             │  on OpenSearch Vector      │
         │              │                             │  Search Edition (HA)       │
         │              │                             │  + text-embedding-v4       │
         │              │                             │  + tongyi-embedding-       │
         │              │                             │    vision-plus             │
         │              │                             │  + qwen3-rerank            │
         │              │                             ├────────────────────────────┤
         │              │                             │ AnalyticDB PG GraphRAG     │
         │              │                             │  (4-core 32GB, 3 zones)    │
         │              │                             │  adbpg_graphrag.query()    │
         │              │                             └────────────────────────────┘
         ▼              ▼
  All traffic → ActionTrail → SLS → OSS (WORM, 6-year retention)
```

---

## 4. Data pipeline

Shared design in [`../rag_and_pipelines.md`](../rag_and_pipelines.md). Version C specifics:

### 4.1 Ingestion sources and schedule

| Source | Cadence | Trigger | Service |
|---|---|---|---|
| WHO ICD-11 API | Daily 02:00 SGT | [CloudOps Scheduler](https://www.alibabacloud.com/help/en/cloudops-orchestration-service) cron | Function Compute |
| WHO guideline PDFs | Monthly day 1 02:30 SGT + RSS webhook | Cron + API Gateway webhook | FC + DocMind |
| Internal clinical trial reports (SharePoint) | Weekly Sun 03:00 SGT + [Microsoft Graph webhook](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions) | Cron + API Gateway | FC |
| Manual upload (urgent additions) | Any time | Upload Portal over VPN | SAE container → OSS |
| Monthly full reconciliation | Day 1 04:00 SGT | Cron | Function Workflow |

Idempotency: `document_id = hash(source + URI)` · `revision = hash(bytes)`. Unchanged docs cost zero embedding spend.

### 4.2 Parsing

- **Default**: [DocMind](https://www.alibabacloud.com/help/en/model-studio) — handles body text, simple tables, headers across hundreds of pages.
- **Complex pages** (multi-page tables, text-based flowcharts, figures): PAI pipeline invokes Qwen-VL-Max with a structured-output prompt to emit markdown preserving table structure.
- **Chunking**: hierarchical 1500 / 300 tokens, 15% overlap, section-aware.
- **Metadata**: `source`, `document_id`, `revision`, `document_type`, `publication_date`, `review_date`, `specialty`, `evidence_grade`, `page`, `section_heading`, `has_table`, `has_figure`.

### 4.3 Embeddings and rerank

| Use | Model | Pricing | Notes |
|---|---|---|---|
| Text chunks | [`text-embedding-v4`](https://www.alibabacloud.com/help/en/model-studio/text-embedding-v4) | [$0.07 / 1M tokens](https://www.alibabacloud.com/help/en/model-studio/model-pricing) | Dims 64–2048 (use 1024); 8192-token context |
| Figure-bearing chunks | [`tongyi-embedding-vision-plus`](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings) | $0.09 / 1M text tokens + per-image | 1152-dim; SG International |
| Rerank top-20 recall | [`qwen3-rerank`](https://www.alibabacloud.com/help/en/model-studio/rerank) | $0.10 / 1M tokens | 500-doc per-call cap |

`qwen3-vl-embedding` (fused single vector) and `qwen3-vl-rerank` (cross-modal) are **Chinese Mainland only** — not available on SG International (DNS-verified). Version C uses separate text + image vector fields and merges at rerank time. No PDPA cost.

### 4.4 Vector store

[**OpenSearch Vector Search Edition**](https://www.alibabacloud.com/help/en/open-search/vector-search-edition/product-overview), HA Edition, dual-zone in Singapore. Supports linear, Quantized Clustering, HNSW with dim cap 4–16,384 (1024-dim text + 1152-dim multimodal both fit).

If the hospital ever needs a Tokyo deployment, [Alibaba Cloud Elasticsearch with Vector-Enhanced Edition](https://www.alibabacloud.com/help/en/doc-detail/187127.htm) is the drop-in — OpenSearch Vector Search Edition has no Tokyo endpoint.

### 4.5 Managed GraphRAG

[**AnalyticDB for PostgreSQL GraphRAG service**](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service) — managed knowledge-graph extraction + multi-hop query, exposed as SQL functions:

```sql
SELECT adbpg_graphrag.initialize('{
  "llm_model":       "qwen-plus-2025-02",
  "llm_api_key":     "<from-credentials-manager>",
  "embedding_model": "text-embedding-v4",
  "language":        "English",
  "entity_types":    ["Disease","Drug","Symptom","Procedure","Anatomy"],
  "relationship_types": ["treats","causes","contraindicates","interacts_with","indicates"]
}');

SELECT adbpg_graphrag.upload('{"file_path":"/oss/raw/who/<doc-id>.pdf"}');

SELECT adbpg_graphrag.query(
  'What diseases can hydroxychloroquine cause if the patient has G6PD deficiency?',
  'hybrid'  -- hybrid | local | global
);
```

**Service requirements (verified 10 May 2026):**
- AnalyticDB PG 7.0, minor version **≥ 7.2.1.4** (7.3.0.0 and 7.3.1.0 do NOT support `adbpg_graphrag`)
- Minimum 4-core 32-GB vector-optimized instance
- 3 zones available in SG → multi-AZ HA available
- GraphRAG LLM egress in VPC requires NAT gateway OR PAI AI-Node in the same VPC — we deploy PrivateLink + PAI in same VPC to keep data in-region

LazyGraphRAG and self-hosted Microsoft GraphRAG are rejected — the managed service is the right tradeoff. Self-hosted is only an option for on-prem Apsara Stack deployments.

### 4.6 Retrieval

**Emergency lane — hybrid one-pass** (speed first):
- BM25 + kNN HNSW, metadata pre-filter (`review_date >= NOW-18m`, specialty, tenant)
- Top-20 kNN → rerank to top-5 via `qwen3-rerank`

**Complex lane — hybrid + agentic + graph** (accuracy first):
- Agent exposes four tools:
  - `kb_retrieve(topic, source, max_age_days)` — hybrid BM25+kNN on vector KB
  - `graph_retrieve(entity, relation?, hops=2)` — AnalyticDB PG GraphRAG traversal
  - `icd11_lookup(term, mode)` — runtime WHO ICD-11 API
  - `pubmed_search(query, max_results)` — runtime [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25500/) (3 req/s free)

### 4.7 WHO ICD-11 API — three uses

1. Monthly snapshot into OSS via OAuth2 client → indexed with `source=icd11` (see [`scripts/download_who_icd.py`](../../scripts/download_who_icd.py))
2. Runtime tool call to live `/mms/search` endpoint for authoritative current codes
3. Silent query expansion — synonym boost in BM25 query when disease name detected

---

## 5. Model orchestration

### 5.1 Framework — Model Studio Application

Per the [Model Studio application-building guide](https://www.alibabacloud.com/help/en/model-studio/getting-started/application-building-instructions):

- **Agent Application** — conversational, LLM-driven tool selection. Used for the general clinical chat and all specialty departments.
- **Workflow Application** — deterministic DAG (retrieve → prompt → generate → moderation). Used for the emergency lane where auditability and a fixed path matter most.

LangChain only for Layer-1 semantic cache against Tair + TairVector (`RedisSemanticCache`) and per-session chat memory (`ConversationBufferWindowMemory`). No LangChain in the primary runtime path.

### 5.2 Routing — two steps

**Step 1 — Lane selection (pure if/else, no LLM call).** The chat UI has an explicit emergency toggle. Its state is authoritative — matches [`aws-demo/ec2/app/graph.py`](../../aws-demo/ec2/app/graph.py) `_route_next`:

```python
def _route_lane(state):
    return "emergency" if state["emergency"] else "complex"
```

No classifier LLM call on the hot path — saves ~300 ms.

**Step 2 — Department selection (router agent, complex lane only).** Qwen3.5-Flash with `temperature=0, response_format=json` picks one of 40 departments. Emergency lane skips this step entirely.

Router decision shape:

```json
{"department": "cardiology-internal", "secondary": ["pharmacy"], "confidence": 0.92, "reason": "..."}
```

Router latency budget ~150–200 ms. Not charged against the 2-s emergency SLA.

### 5.3 Lane models and hyperparameters

| Question class | Model | Hyperparameters | Guardrail | Latency target |
|---|---|---|---|---|
| Emergency (toggle ON, bypass router) | **Qwen3.5-Flash** + Qwen3-8B student on PAI-EAS | `temperature=0.1, top_p=0.7, top_k=40, seed=42` | Strict PHI + emergency disclaimer | **≤ 2 s** |
| Router (complex lane) | Qwen3.5-Flash, JSON mode | `temperature=0, response_format=json` | Standard | ~200 ms |
| Complex differential (department agent) | **Qwen3.5-Plus** for most specialties | `temperature=0.2, top_p=0.9, seed=42` | Standard | 3–6 s |
| Radiology (image attachment) | **Qwen3-VL-Plus** | `temperature=0.2, top_p=0.9` | Standard | 3–6 s |
| Literature / citation | Qwen3.5-Flash, grounded-only mode | `temperature=0.1, top_p=0.7, top_k=40` | No-hallucination | 1.5–2 s |
| Patient-education phrasing | Qwen3.5-Flash with tone preset | `temperature=0.2, top_p=0.9` | Standard + tone | 1–2 s |

Qwen supports `seed`, which we pin per deployment to maximize determinism.

### 5.4 Multi-agent department topology

40 specialty agents mirroring a Vietnamese tertiary hospital structure. **UI never exposes the list.** Router classifies the prompt. Only the emergency toggle bypasses the router.

Full Vietnamese → English → KB namespace mapping in [`../rag_and_pipelines.md` §Multi-agent topology](../rag_and_pipelines.md#3-multi-agent-topology-vietnamese-tertiary-hospital). Summary:

- **Emergency toggle ON → Emergency Medicine agent** (if/else bypass)
- **Image attached → Radiology agent on Qwen3-VL-Plus**
- **Prescribing question (≥ 2 drugs or allergy) → Clinical Pharmacy auto-invoked as side-channel**
- **Router confidence < 0.6 → General Medicine / Triage with banner**

Per-hospital tenant config enables a subset of the 40 (a 20-bed hospital runs 12; a 1,200-bed teaching hospital runs all 40).

Implementation: one Model Studio Agent Application per department, each with its own system prompt + tool set + KB binding. One Workflow Application drives the routing.

### 5.5 Agent tools (Model Studio plug-ins)

All read-only:

- `retrieve_guideline(topic, source=WHO, max_age_days=90)` — KB retrieval
- `retrieve_trial(doc_id)` — internal KB
- `graph_retrieve(entity, relation?, hops=2)` — AnalyticDB PG GraphRAG `adbpg_graphrag.query(..., 'hybrid')`
- `icd11_lookup(term, mode)` — FC wrapping live WHO ICD-11 API
- `pubmed_search(query, max_results)` — FC wrapping NCBI E-utilities
- `icd11_expand_query(term)` — silent query expansion for retrieval

---

## 6. Fine-tuning and distillation

Detailed technique catalog in [`../customization.md`](../customization.md). Version C specifics:

### 6.1 Technique stack

- **SFT + LoRA** on [PAI Model Gallery Qwen3-8B](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models) — teacher-generated answers from Qwen3.5-Plus
- **DPO** (optional, monthly) — on clinician preference pairs collected post-launch
- **GRPO** (optional, ad-hoc) — when tool-calling regressions appear

### 6.2 Hyperparameters

```
LoRA rank:           16
LoRA alpha:          32
LoRA dropout:        0.05
learning_rate:       2e-4
epochs:              3
warmup_ratio:        0.03
bf16:                true
batch_size:          4 per device
grad_accum_steps:    4
```

GPU: A10 or A100 on PAI DLC in Singapore.

### 6.3 Training pipeline

```
1. Seed prompts
   (a) de-identified clinician questions from invocation logs
       (DataWorks SDDP masks PHI before logging)
   (b) teacher-paraphrases of WHO / protocol chunks
   target: 10k–30k prompts

2. Teacher generation (Qwen3.5-Plus batch, 50% off)
   for each prompt: retrieve RAG context → ask teacher → record triple

3. Clinician review (Alibaba Human Verification, ~15% sample)
   approved → SFT dataset; clinician-preferred choices → DPO pairs

4. Train on PAI Model Gallery — Qwen3-8B SFT + LoRA (hyperparams above)

5. Eval harness
   Qwen3.5-Plus as LLM-judge on: accuracy, citation coverage,
   PHI leakage (must be 0), tone, emergency-appropriateness

6. Promote to PAI-EAS
   gate: student ≥ 95% of teacher on holdout + zero regression on safety suite
   launch-day: 100% on emergency lane
   post-launch retrains: 5% canary for 72 hours
```

### 6.4 Per-run cost

| Step | Cost |
|---|---|
| Teacher generation on Qwen3.5-Plus batch (80 M in + 6 M out) | `(80 × $0.20) + (6 × $1.20)` ≈ **$23** |
| Training: 2–4 GPU-hr × $1–2/hr on PAI A10 | **$5–30** |
| Clinician review (in-house) | $0 |
| **Total per run** | **~$15–40** |

Cheapest retrain cadence of the three versions. Can run monthly without impacting the budget.

### 6.5 Serving the student

Qwen3-8B on PAI-EAS (`pai-eas.ap-southeast-1.aliyuncs.com` — endpoint is `pai-eas.*` not `eas.*`), A10 GPU, always-on. Student takes ~60% of complex-lane traffic at launch, freeing Qwen3.5-Plus for the hardest queries and reducing cost.

---

## 7. Security architecture

| Layer | Control |
|---|---|
| Account isolation | [Resource Directory](https://www.alibabacloud.com/help/en/resource-directory) + Control Policy Service; one account per environment in SG |
| Network | FC in VPC; Model Studio + PAI-EAS via [PrivateLink](https://www.alibabacloud.com/product/privatelink); OpenSearch Vector in VPC; no public egress from chat FC |
| Identity — clinicians | [**IDaaS (EIAM 2.0)**](https://www.alibabacloud.com/help/en/idaas/) Premium+ federated via SAML/OIDC to each hospital's IdP (EntraID / Okta / ADFS). MFA enforced. |
| Identity — Nova staff | [Cloud SSO + RAM](https://www.alibabacloud.com/product/ram) federated to Nova's EntraID; short-lived SSO credentials. |
| Hospital ↔ cloud | Site-to-Site IPsec VPN on [VPN Gateway](https://www.alibabacloud.com/help/en/vpn/) — IKEv2 + AES-256-GCM + SHA-2, dual-tunnel HA |
| Data at rest | OSS, OpenSearch, AnalyticDB PG, Tair, Credentials Manager all on [KMS BYOK](https://www.alibabacloud.com/product/kms) |
| Data in transit | TLS 1.3; [ASM](https://www.alibabacloud.com/product/servicemesh) for mTLS |
| PHI handling | [DataWorks](https://www.alibabacloud.com/product/dataworks) + [SDDP](https://www.alibabacloud.com/product/sddp) (Data Security Guard) classify → reversible tokenization in FC (KMS-backed) |
| LLM safety | [Content Moderation 2.0 for Generative AI](https://www.alibabacloud.com/product/content-moderation) — jailbreak, hate, medical misinformation, self-harm, bias (pre-approve clinical allow-list) |
| Audit | [ActionTrail](https://www.alibabacloud.com/product/actiontrail) → [SLS](https://www.alibabacloud.com/product/log-service) → OSS WORM with **6-year retention** per HIPAA §164.530(j); Model Studio observability captures every call |
| Ingestion safety | [Security Center](https://www.alibabacloud.com/product/security_center) scan on uploaded PDFs; SDDP PHI scan; quarantine + notify on leak |
| Secrets | [Credentials Manager](https://www.alibabacloud.com/help/en/kms/user-guide/secrets-manager-overview) with KMS + rotation FC for WHO ICD-11 OAuth client |
| Compliance | ISO 27001/27017/27018/27701, SOC 1/2/3, PDPA alignment; [Alibaba Cloud Trust Center](https://www.alibabacloud.com/en/trust-center) |

Full compliance mapping (PDPA / HIPAA / HCSA / FDA / EU AI Act) in [`../compliance.md`](../compliance.md).

---

## 8. Cost — monthly pilot (600k calls, 30/70 emergency/complex)

Assumptions shared with other versions in [`../overview.md`](../overview.md). All figures list prices, USD, early 2026.

### 8.1 Base — Qwen3.5-Plus complex + Qwen3.5-Flash fast (no student yet)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3.5-Flash | 180k × 65% (post-L1-cache) × $0.0004 | ~$47 |
| Complex lane — Qwen3.5-Plus | 420k × $0.0026 | ~$1,105 |
| `text-embedding-v4` | ~500M tokens × $0.07 / 1M | ~$35 |
| `tongyi-embedding-vision-plus` (figures) | ~5M text × $0.09 + ~50k images metered | ~$50 |
| `qwen3-rerank` (top-20, ~10% of complex) | ~500M tokens amortized | ~$50 |
| Content Moderation 2.0 | per call | ~$50 |
| OpenSearch Vector Search (HA, small cluster) | | ~$180 |
| **AnalyticDB PG GraphRAG** — 4-core 32 GB vector-optimized + Qwen-Plus extraction tokens | | **~$300** |
| DataWorks SDDP PHI masking | | ~$120 |
| Function Compute + API Gateway + CDN + WAF | | ~$90 |
| OSS + ActionTrail + SLS WORM | | ~$70 |
| Tair (Redis OSS-compatible, NOT Valkey) | | ~$60 |
| IPsec VPN Gateway | | ~$60 |
| **Base total** | | **~$2,220** |

### 8.2 With Qwen3-8B student active (launch-day target)

| Item | Cost |
|---|---|
| Base as above | $2,220 |
| SFT+LoRA training, amortized quarterly | +$15–40 |
| PAI-EAS A10 always-on | +$720–1,500 |
| Student takes ~60% of complex traffic (replaces Qwen3.5-Plus calls) | −$660 |
| **Total at launch** | **~$2,280–3,060** |

### 8.3 Per-call cost

- Emergency call (post-L1-cache, L2-cache hit on system prefix): **~$0.0008**
- Complex call (Qwen3.5-Plus, with context cache): **~$0.0026**
- Emergency call on student (Qwen3-8B PAI-EAS): **~$0.0003** (amortized on endpoint hours)

### 8.4 Cost sensitivities

- **Student off** (Qwen3.5-Plus takes 100% complex): saves ~$720 endpoint but adds ~$660 tokens → net ~$60 saving. Keep student on for quality.
- **Toggle shift 30/70 → 60/40 emergency/complex**: saves ~$900/mo.
- **OpenSearch HA → single-AZ**: saves ~$90/mo, loses DR.
- **AnalyticDB PG 4-core → 8-core**: +$300/mo, enables larger graph.

### 8.5 Qwen Context Cache (Layer 2)

[Qwen Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache) is the cheapest Layer 2 of the three versions:
- **Implicit from day one** (zero config on enabled models)
- **Explicit named cache IDs** for larger static prefixes (system prompt + KB preamble)
- Cache hits bill at **20% of standard input price**

Composed emergency p95:

```
 25 ms   Tair semantic cache hit (Layer 1; 30–45% of emergency queries)
100 ms   IDaaS auth + PHI mask
 70 ms   OpenSearch Vector hybrid retrieval + rerank
300 ms   Qwen3.5-Flash first-token (Qwen Context Cache hit)
1,100 ms Qwen3.5-Flash full answer (250 tokens, streaming)
110 ms   Moderation + citation check
──────
≤ 1,700 ms  p95
```

---

## 9. Performance budget

| Traffic class | p50 | p95 | SLA |
|---|---|---|---|
| Emergency (cached) | 300–500 ms | 900 ms | ≤ 2 s |
| Emergency (cold, student) | 700–1,100 ms | 1,700 ms | ≤ 2 s |
| Emergency (cold, Qwen3.5-Flash fallback) | 900–1,300 ms | 1,900 ms | ≤ 2 s |
| Complex (cached prefix) | 1,500–3,000 ms | 4,500 ms | ≤ 6 s |
| Complex (cold) | 3,000–5,000 ms | 6,000 ms | ≤ 6 s |

Latency levers:
1. **Pure if/else emergency routing** saves ~300 ms vs classifier LLM call
2. **Tair semantic cache** (30–45% hit rate on emergency)
3. **Qwen Context Cache** (~50% input token reduction)
4. **Qwen3-8B student on PAI-EAS** (smaller = faster than Qwen3.5-Plus by ~2×)
5. **Qwen PTU** on the emergency lane once sustained TPM justifies (Layer 3)
6. **Streaming** — first token SLA ~300 ms; full answer 1.1–1.3 s

---

## 10. Continuous operations (post-launch)

| Cadence | Action |
|---|---|
| Daily 02:00 SGT | WHO ICD-11 delta ingest; Tair semantic-cache invalidation for `source:icd11` tags |
| Weekly Sun 03:00 SGT | SharePoint / trial-report reconciliation (safety net for missed webhooks) |
| Monthly day 1 02:30 SGT | WHO guideline PDF refresh + incremental AnalyticDB PG graph re-index |
| Monthly | DPO micro-run on clinician preference pairs (~$15–40 per run) |
| Quarterly | Full Qwen3-8B student retrain (SFT + LoRA); re-qualify on eval harness; 5% canary for 72 hours |
| Event-driven | Red-team re-run after any Content Moderation incident; retrain on new adversarial examples |

No "phase 2" language. Everything above is standing operations.

---

## 11. Flagged limitations and mitigations

| Limitation | Mitigation |
|---|---|
| AnalyticDB PG `adbpg_graphrag` extension requires engine minor ≥ 7.2.1.4 (7.3.0.0 and 7.3.1.0 do NOT support it) | Verify via Basic Information page in console before deploy |
| GraphRAG indexing calls the LLM from inside VPC | PrivateLink + PAI AI-Node in same VPC for egress |
| AnalyticDB PG minimum for GraphRAG = 4-core 32 GB | ~$300/mo baseline in SG (cost tables account for this) |
| Content Moderation 2.0 adds ~80–150 ms per call | Emergency lane uses streaming "detect after first 100 tokens" pattern |
| Content Moderation may over-block legitimate clinical content | Pre-approve medical vocabulary allow-list with account team before go-live |
| DataWorks SDDP HIPAA / PDPA-S rule packs not default-on | Open ticket with account team before production PHI scan |
| EIAM Premium+ required for SAML-IDP / SCIM hospital federation; region-pinned | One instance per region + Cloud SSO for multi-country |
| Model Studio default RPM caps vary by model + API key | Production quotas negotiated with account team |
| Function Compute VPC cold start adds 1 ENI attach time | Pre-provisioned warm instances for emergency lane |
| `qwen3-vl-embedding` fused / `qwen3-vl-rerank` / `gte-rerank-v2` — Chinese Mainland only | Use `tongyi-embedding-vision-plus` (separate text+image) + `qwen3-rerank`. Documented trade-off: slightly lower cross-modal recall, no PDPA cost. |
| OpenSearch Vector Search Edition not in Tokyo | Zero impact — we stay SG-resident. If Tokyo ever needed: Elasticsearch with Vector-Enhanced Edition drop-in. |
| PAI-EAS endpoint is `pai-eas.<region>.aliyuncs.com`, NOT `eas.<region>` | Documented in runbook; CLI plugin is `eas` but endpoint is different |

Full verification table in [`../regional_services.md` §Alibaba](../regional_services.md#2-alibaba-cloud--live-probed-for-version-c).

---

## 12. Deployment approach

Single-region public cloud in Singapore, multi-AZ where applicable:

- Model Studio, PAI DLC + EAS, OpenSearch Vector HA, AnalyticDB PG (3 zones), Tair (4 zones + 3 MAZ combos), OSS, Function Compute — all in `ap-southeast-1`
- Hospital integration over Site-to-Site IPsec VPN. No dedicated line unless specifically requested.
- DR via cross-AZ within Singapore. Cross-region warm-standby is a roadmap item pending PDPA review.

### Launch scope — everything on day one

| Capability | State at launch |
|---|---|
| Scheduled ingestion + Upload Portal over IPsec VPN | ✅ |
| Hybrid retrieval (BM25 + kNN on OpenSearch Vector Search HA + `qwen3-rerank`) | ✅ |
| Managed GraphRAG on AnalyticDB PG | ✅ |
| Emergency toggle + if/else router | ✅ |
| Qwen3.5-Flash on fast lane + Qwen3.5-Plus on complex lane + Qwen3-VL-Plus on Radiology | ✅ |
| Qwen3-8B student on PAI-EAS (trained pre-launch, serving from day one) | ✅ |
| 40-department multi-agent topology | ✅ (configurable subset per tenant) |
| Tair semantic cache + Qwen Context Cache | ✅ |
| Qwen PTU on emergency lane (sized to peak TPM) | ✅ |
| Content Moderation 2.0 + DataWorks SDDP + grounding + citation validator | ✅ |
| ActionTrail → SLS → OSS WORM 6-year audit | ✅ |
| [EHR SMART App Launch v2](http://docs.smarthealthit.org/) on FHIR R4 | ✅ per configured tenant |

### Corporate integration

Full design in [`../rag_and_pipelines.md` §Corporate integration](../rag_and_pipelines.md#6-corporate-integration). Summary:

- **EHR** via [SMART App Launch v2](http://docs.smarthealthit.org/) against Epic / Cerner (Oracle Health) / Allscripts on FHIR R4. Function Compute de-identifies patient slice (DataWorks SDDP) before calling Model Studio. Read-only scopes only.
- **SharePoint / OneDrive** — [Microsoft Graph subscriptions](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0) with `Sites.Selected`, delivered via HTTPS webhook → FC → OSS → ingestion pipeline.
- **Clinician SSO** — IDaaS federation per hospital tenant.
- **Admin SSO** — Cloud SSO → Nova's EntraID.
- **Audit export** — SLS → OSS nightly → hospital SIEM.

---

## 13. Pre-launch build (before cut-over)

| Week | Activity |
|---|---|
| 1–2 | Provision SG resources; ingest WHO + ICD-11; run DocMind + embed + graph extraction |
| 3–4 | Train Qwen3-8B student (SFT + LoRA + optional DPO); eval harness green |
| 5–6 | EHR integration (SMART on FHIR sandboxes); SharePoint Graph; IDaaS federation per hospital |
| 7–8 | Red team 200+ adversarial prompts; tune Content Moderation 2.0 allow-list; Qwen PTU sizing |
| Launch | Cut-over; all capabilities active |

---

## 14. References

- [Model Studio overview](https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio)
- [Model Studio regions](https://www.alibabacloud.com/help/en/model-studio/regions/)
- [Model Studio pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [Application types — Agent vs Workflow](https://www.alibabacloud.com/help/en/model-studio/application-introduction)
- [Qwen Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache)
- [AnalyticDB PG — GraphRAG service](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service)
- [text-embedding-v4](https://www.alibabacloud.com/help/en/model-studio/text-embedding-v4) · [tongyi-embedding-vision-plus](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings) · [qwen3-rerank](https://www.alibabacloud.com/help/en/model-studio/rerank)
- [PAI quick start — Qwen3 deploy / fine-tune / evaluate](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models)
- [Tair (Redis OSS-compatible)](https://www.alibabacloud.com/product/tair) · [TairVector](https://www.alibabacloud.com/help/en/tair/user-guide/tairvector-overview)
- [OpenSearch Vector Search Edition](https://www.alibabacloud.com/help/en/open-search/vector-search-edition/product-overview)
- [Content Moderation 2.0 for Gen AI](https://www.alibabacloud.com/product/content-moderation)
- [IDaaS EIAM 2.0](https://www.alibabacloud.com/help/en/idaas/)
- [Alibaba Cloud Trust Center](https://www.alibabacloud.com/en/trust-center)

*Content above is rephrased for compliance with licensing restrictions.*
