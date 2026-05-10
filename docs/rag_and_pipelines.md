# RAG, ingestion, multi-agent topology, framework, caching, EHR integration

Shared design across all three versions. Per-version specifics (which managed service, which region, which model name) are in the proposal docs. This doc covers the **what and why** that are identical across A, B, C.

---

## 1. RAG strategy — complex medical PDFs + structured ICD-11

**Corpus profile**: hundreds of WHO guideline PDFs (100+ pages, mixed body text + vertical/horizontal tables + text-based flowcharts + figures), internal clinical trial reports with inconsistent tagging, treatment protocols in legacy PDFs, plus the structured [WHO ICD-11 API](https://id.who.int/swagger/index.html) for disease-level metadata. WHO publishes monthly updates that must land in the index within a day.

A naïve pypdf-extract → chunk → embed pipeline fails — tables become linearized garbage, text-only flowcharts lose structure. We picked the managed-parse route after comparing three strategies.

### Strategy comparison

| Strategy | Description | Verdict |
|---|---|---|
| A. Managed parse + managed RAG | [AWS Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) → [Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/); [Alibaba DocMind](https://www.alibabacloud.com/help/en/model-studio) + Qwen-VL-Max | **Chosen as primary** — zero custom parsing, strong table recognition, IAM-bounded compliance |
| B. Open-source parser ([Unstructured](https://unstructured.io) / [LlamaParse](https://docs.llamaindex.ai/en/stable/module_guides/loading/connector/llama_parse/) / [Docling](https://github.com/DS4SD/docling)) + self-managed vector DB | Max control; cheapest per page | Not chosen — ops burden; compliance covers your parser stack too |
| C. Multimodal page-image embeddings ([Amazon Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html) us-east-1 only; [tongyi-embedding-vision-plus](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings) on Alibaba SG) | Preserves figures/tables exactly; page-level citations | **Fallback only** for figure-heavy queries — higher embed cost + larger tokens per query |
| D. Managed GraphRAG (knowledge graph over the corpus) | [Bedrock KB GraphRAG on Neptune Analytics](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-build-graphs.html) (AWS GA March 2025); [AnalyticDB PG GraphRAG](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service) (Alibaba) | **Launch default on top of A** — managed entity/relation extraction; no self-hosted Neo4j |

Version A (AWS) also uses [Cohere Embed v4](https://aws.amazon.com/blogs/aws/cohere-embed-multimodal-embeddings-are-now-available-in-amazon-bedrock/) or [Amazon Titan Embed Text v2](https://aws.amazon.com/bedrock/titan/) for text. Version C uses [text-embedding-v4](https://www.alibabacloud.com/help/en/model-studio/text-embedding-v4) + [tongyi-embedding-vision-plus](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings). The `qwen3-vl-embedding` model listed in Alibaba's pricing page is **Chinese Mainland only** — not available on the Singapore International endpoint (see [`regional_services.md`](regional_services.md#alibaba)).

### Hierarchical chunking (shared)

- Parent 1500 tokens / child 300 tokens / 15% overlap
- Section-aware (heading boundaries respected)
- Metadata per chunk: `source`, `document_id`, `revision`, `document_type`, `publication_date`, `review_date`, `specialty`, `evidence_grade`, `page`, `section_heading`, `has_table`, `has_figure`

### Retrieval

**Emergency lane — hybrid one-pass** (speed first):
- BM25 + kNN HNSW, metadata pre-filter (`review_date >= NOW-18m`, specialty, tenant)
- Top-20 kNN → rerank to top-5 via [Amazon Rerank 1.0](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html) (AWS; Tokyo cross-region, since it's [single-region](https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported)) or [qwen3-rerank](https://www.alibabacloud.com/help/en/model-studio/rerank) (Alibaba SG)

**Complex lane — hybrid + agentic + graph** (accuracy first):
- Same hybrid retrieve as above
- Agent exposes four tools (see [Agentic RAG 2026 production guide](https://www.marsdevs.com/guides/agentic-rag-2026-guide) — agentic RAG earns its 3–10× cost on multi-hop clinical questions):
  ```python
  kb_retrieve(topic, source, max_age_days)      # hybrid BM25+kNN on vector KB
  graph_retrieve(entity, relation?, hops=2)     # managed GraphRAG traversal
  icd11_lookup(term, mode)                      # runtime WHO ICD-11 API
  pubmed_search(query, max_results)             # runtime NCBI E-utilities (3 req/s free,
                                                #   10 req/s with API key)
  ```
- Single-hop factual questions → `kb_retrieve`; multi-hop / relational / "summarize across" → `graph_retrieve` (per the Microsoft Research recommendation in [GraphRAG vs vector RAG](https://www.microsoft.com/en-us/research/blog/graphrag-unlocking-llm-discovery-on-narrative-private-data/))

### ICD-11 API as a first-class source (three uses)

1. **Ingest snapshot** — monthly walk writes one JSON per entity into the raw bucket, indexed with `source=icd11`. See [`scripts/download_who_icd.py`](../scripts/download_who_icd.py).
2. **Runtime tool call** — agent invokes `icd11_lookup(term)` hitting the live [`/mms/search`](https://id.who.int/swagger/index.html) endpoint for authoritative current codes.
3. **Query expansion** — when a clinician's question contains a disease name, a lightweight classifier calls ICD-11 search to get synonyms and code, then boosts those in the BM25 query.

### Freshness (summary — full schedule in §Ingestion below)

Graph + vector indexes refresh incrementally on WHO monthly push, SharePoint Graph webhook, and ICD-11 daily delta. The managed services (Bedrock KB on Neptune Analytics; AnalyticDB PG GraphRAG) both skip unchanged documents via revision-hash comparison.

Self-hosted fallback ([Microsoft GraphRAG](https://microsoft.github.io/graphrag/) / [LightRAG](https://github.com/HKUDS/LightRAG)) is reserved for on-prem Apsara Stack deployments where the managed service is unavailable.

---

## 2. Ingestion pipeline

**Principle**: the RAG index is always fresh via scheduled jobs, never lazy. Physicians don't wait while the bot crawls external systems — the index is ready when they ask.

### Schedule

| Source | Cadence | Trigger | Mode | Why |
|---|---|---|---|---|
| [WHO ICD-11 API](https://id.who.int/icdapi) | Daily 02:00 SGT | [EventBridge cron](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html) / [CloudOps Scheduler](https://www.alibabacloud.com/help/en/cloudops-scheduler) | Delta pull against `releaseId` | Catches updates without full re-walk |
| WHO guideline PDFs | Monthly day 1 02:30 SGT + RSS webhook for urgent living guidelines | Cron + API Gateway webhook | Diff on the WHO publications index | Matches "monthly protocol updates" requirement |
| Internal clinical trial reports (SharePoint) | Weekly Sun 03:00 SGT + Microsoft Graph webhook | Cron + [Graph subscription](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0) | Weekly batch + webhook on change | Weekly is the reconciliation safety net; webhook keeps current within minutes |
| Internal treatment protocols | Same as above | Same | Same | |
| Manual override (any source) | Any time | [Upload portal](#upload-portal-for-manual-ingestion) | Direct PUT behind VPN (data plane) + IdP | Urgent additions that can't wait |
| Monthly full reconciliation | Day 1 04:00 SGT | Cron | Full diff + re-index of changed docs | Catches anything incremental paths missed |

All jobs write to one raw bucket; a single [Step Functions](https://aws.amazon.com/step-functions/) / [Function Workflow](https://www.alibabacloud.com/help/en/functioncompute/developer-reference/function-workflow) picks up `ObjectCreated` and runs: parse → chunk → embed → upsert. One pipeline, many triggers.

### Idempotency

- `document_id` = hash(source + URI)
- `revision` = hash(bytes)
- Upsert re-embeds only when `revision` changed → zero wasted embedding cost on unchanged docs
- Manual backfill = object PUT with `revision=force`

### Upload portal for manual ingestion

Small internal web app behind a private SLB in the Nova VPC, reachable only via the data-plane [Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html) (AWS) / [Alibaba VPN Gateway](https://www.alibabacloud.com/help/en/vpn-gateway) tunnel from the hospital network. Authenticated via hospital IdP (EntraID / Okta / Keycloak). Role-gated: `nova-rag-curator` uploads, `nova-rag-admin` deletes.

Upload flow:

```
Hospital LAN user → HTTPS over S2S VPN → private ALB / SLB
  → Upload-portal container (ECS / SAE) — OIDC against hospital IdP
  → presigned PUT URL (10-min TTL)
  → S3 / OSS bucket "raw/manual/<document_id>/<revision>.pdf"
  → ObjectCreated
  → [GuardDuty Malware Protection](https://docs.aws.amazon.com/guardduty/latest/ug/malware-protection-s3.html) / [Security Center](https://www.alibabacloud.com/product/security_center) scan
  → [Macie](https://aws.amazon.com/macie/) / [SDDP](https://www.alibabacloud.com/product/sddp) PHI scan (quarantine on hit)
  → same ingestion pipeline → [Bedrock KB](https://aws.amazon.com/bedrock/knowledge-bases/) / [Model Studio KB](https://www.alibabacloud.com/help/en/model-studio/user-guide/rag-knowledge-base) sync
  → audit entry in CloudTrail / ActionTrail
```

Minimum portal features: upload (≤ 100 MB), choose document type, add metadata (specialty, review_date, owner_contact), list/search with status, reindex single doc without re-upload, admin delete (flushes KB chunks + semantic cache).

---

## 3. Multi-agent topology (Vietnamese tertiary hospital)

The clinical assistant mirrors the clinical structure of a large Vietnamese teaching hospital — 40 clinical departments. **The UI never exposes the list.** A router agent reads the clinician's prompt and routes to the right specialty. Only the **emergency toggle** is a hard if/else that bypasses the router.

Per research on multi-agent medical reasoning ([MMedAgent-RL on Qwen2.5-VL](https://arxiv.org/html/2506.00555v2), [MedRoute RL-trained specialist router](https://arxiv.org/abs/2604.06180)), specialist agents beat single-agent baselines on MedQA by 3–8 %. Our implementation is the **rule-based router + specialist agents** pattern — RL-trained routing is a continuous-ops upgrade path once we have ≥ 10 k routing-labeled production interactions.

### Department → agent mapping (full 40)

| Vietnamese name | English label (routing key) | Primary KB namespace | Typical queries |
|---|---|---|---|
| *Khoa Cấp cứu* | Emergency Medicine (`emergency`) | kb-who-emergency + sepsis/stroke/MI | **Emergency toggle always routes here, bypassing the router** |
| *Khoa Hồi sức tích cực* | Intensive Care (`icu`) | kb-who-critical-care + vasopressor + ventilation | Organ-failure support, sedation, vent tuning |
| *Khoa Gây mê - Hồi sức* | Anesthesiology (`anesthesia`) | kb-anesthesia + perioperative | Airway management, regional anesthesia, PACU |
| *Khoa Kiểm soát nhiễm khuẩn* | Infection Control / ID (`infectious-disease`) | kb-who-antimicrobial + openFDA | Antibiotic choice, resistance, nosocomial |
| *Khoa Nội Tim mạch* | Internal Cardiology (`cardiology-internal`) | kb-cardio + internal cardiology trials | ACS, HF, arrhythmia, device patients |
| *Khoa Tim mạch can thiệp* | Interventional Cardiology (`cardiology-intervention`) | kb-cardio-intervention | PCI, TAVR, peri-procedural anticoagulation |
| *Khoa Phẫu thuật Tim mạch* | Cardiac Surgery (`cardiac-surgery`) | kb-cardiac-surgery | CABG, valve surgery, post-op |
| *Khoa Lồng ngực - Mạch máu* | Thoracic & Vascular (`thoracic-vascular`) | kb-vascular + kb-thoracic | Aortic disease, PAD, thoracotomy |
| *Khoa Hô hấp* | Pulmonology (`pulmonology`) | kb-who-respiratory | COPD, asthma, pneumonia, PE, lung-cancer screening |
| *Khoa Thăm dò chức năng hô hấp* | Pulmonary Function Testing (`pulmonary-testing`) | kb-pulmonary-testing | PFT, spirometry, DLCO |
| *Khoa Tiêu hoá* | Gastroenterology (`gastroenterology`) | kb-who-gi + kb-gastro-protocols | IBD, GI bleeding, liver disease |
| *Khoa Nội soi* | Endoscopy (`endoscopy`) | kb-endoscopy | ERCP, EUS, therapeutic endoscopy |
| *Khoa Ngoại Gan - Mật - Tuỵ* | HPB Surgery (`hpb-surgery`) | kb-hpb-surgery | Liver resection, pancreatic cancer, biliary |
| *Khoa Ngoại Tiêu hoá* | GI Surgery (`gi-surgery`) | kb-gi-surgery | Colorectal resection, bariatric, esophageal |
| *Khoa Hậu môn - Trực tràng* | Colorectal Surgery (`colorectal`) | kb-colorectal | Hemorrhoids, fistula, pelvic floor |
| *Khoa Nội thận - Thận nhân tạo* | Nephrology & Dialysis (`nephrology`) | kb-who-kidney + kb-dialysis | CKD staging, AKI, dialysis access, electrolytes |
| *Khoa Tiết niệu* | Urology (`urology`) | kb-urology | BPH, urolithiasis, GU cancers |
| *Khoa Nội tiết* | Endocrinology (`endocrinology`) | kb-who-diabetes + kb-thyroid | T1/T2 DM, thyroid, adrenal |
| *Khoa Nội cơ xương khớp* | Rheumatology / MSK (`rheumatology`) | kb-rheumatology | RA, OA, autoimmune, DMARDs |
| *Khoa Chấn thương chỉnh hình* | Orthopedic Surgery (`orthopedics`) | kb-ortho | Fracture care, arthroplasty, spine |
| *Khoa Thần kinh* | Neurology (`neurology`) | kb-who-neurology + kb-stroke | Stroke pathway, seizure, neurodegenerative |
| *Khoa Ngoại Thần kinh* | Neurosurgery (`neurosurgery`) | kb-neurosurg | Craniotomy, spine, endovascular |
| *Khoa Hoá trị ung thư* | Medical Oncology (`oncology-chemo`) | kb-who-oncology + internal trials `oncology` | Regimen selection, dose adjustments |
| *Khoa Tuyến vú* | Breast Surgery / Oncology (`breast`) | kb-breast | Breast cancer, reconstruction, screening |
| *Khoa Phụ sản* | Obstetrics & Gynecology (`obstetrics`) | kb-who-maternal + kb-obgyn | Pre-eclampsia, PPH, pregnancy |
| *Khoa Sơ sinh* | Neonatology (`neonatology`) | kb-neonatology + weight-based dosing | NICU care, preemie dosing |
| *Khoa Lão - Chăm sóc giảm nhẹ* | Geriatrics & Palliative (`geriatrics`) | kb-geriatrics + kb-who-palliative | Polypharmacy, frailty, end-of-life |
| *Khoa Mắt* | Ophthalmology (`ophthalmology`) | kb-ophthalmology | Glaucoma, diabetic retinopathy, cataract |
| *Khoa Tai Mũi Họng* | Otorhinolaryngology (`ent`) | kb-ent | Sinus, otology, head-neck cancer |
| *Khoa Phẫu thuật Hàm mặt - Răng hàm mặt* | Oral & Maxillofacial Surgery (`ofms`) | kb-ofms | Facial trauma, dental surgery |
| *Khoa Da liễu - Thẩm mỹ da* | Dermatology (`dermatology`) | kb-derm | Skin conditions, phototherapy, cosmetic |
| *Khoa Tạo hình - Thẩm mỹ* | Plastic Surgery (`plastics`) | kb-plastics | Reconstruction, flap design |
| *Khoa Phục hồi chức năng* | Rehabilitation (`rehab`) | kb-rehab | Post-stroke, post-op PT, spinal cord |
| *Khoa Dược* | Clinical Pharmacy (`pharmacy`) | kb-drug-interactions + [openFDA](https://open.fda.gov/) | **Side-channel auto-invoked on any prescribing question** |
| *Khoa Dinh dưỡng, Tiết chế* | Clinical Nutrition (`nutrition`) | kb-nutrition | Enteral/parenteral nutrition, renal/diabetic diets |
| *Khoa Vi sinh* | Microbiology Lab (`microbiology`) | kb-microbiology | Culture interpretation, susceptibility |
| *Khoa Xét nghiệm* | Clinical Laboratory (`laboratory`) | kb-lab | Lab interpretation, reference ranges |
| *Khoa Giải phẫu bệnh* | Anatomic Pathology (`pathology`) | kb-pathology | Tissue-diagnosis interpretation |
| *Khoa Chẩn đoán hình ảnh* | Diagnostic Radiology (`radiology`) | kb-radiology + figure-heavy multimodal corpus | **Image attachment forces routing here; vision-capable model (Qwen3-VL / Claude Sonnet 4.5 vision)** |
| *Khoa Khám bệnh* + *Khoa Khám sức khoẻ theo yêu cầu* | General Medicine / Triage (`triage`) | kb-who-general + kb-icd11 | Router fallback when confidence < 0.6 |

### Special rules

- **Emergency toggle ON** → pure if/else → straight to Emergency Medicine agent. Router bypassed. p95 SLA ≤ 2 s.
- **Image attachment** → router forces Radiology agent on vision-capable model. The agent describes findings systematically and always closes with "Final interpretation requires a certified radiologist."
- **Prescribing questions (≥ 2 drugs or known allergy)** → Clinical Pharmacy auto-invoked as a side-channel alongside the primary specialist.
- **Confidence < 0.6** → route to General Medicine / Triage with a banner: "routed via triage; specify the organ system for a more specific answer".

### Router implementation

The router is a small workflow node running a cheap structured-output model:
- Version C: Qwen3.5-Flash with `temperature=0, response_format=json`
- Version A: [Amazon Nova Micro](https://aws.amazon.com/bedrock/nova/) (`apac.amazon.nova-micro-v1:0`), same pattern
- Version B: Qwen3 32B on Bedrock Sydney

Decision shape: `{"department": "cardiology-internal", "secondary": ["pharmacy"], "confidence": 0.92, "reason": "..."}`.

Router latency budget: ~150–200 ms on all three clouds. Not charged against the 2-s emergency SLA because emergency bypasses the router.

### Simpler fallback topology

If 40 agents prove operationally heavy in the first month, collapse to a **12-department core** (Emergency · Internal Cardiology · Pulmonology · Gastroenterology · Nephrology · Endocrinology · Neurology · Infectious Disease · Oncology-Chemo · Obstetrics · Pediatrics covers Neonatology · Radiology). All other departments route to General Surgery or General Medicine. Per-hospital tenant config picks which of the 40 are active.

---

## 4. Orchestration framework

Decision: **managed cloud-native framework as primary runtime, LangChain only for narrow glue.**

- **AWS primary**: [Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) + [Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/) + [Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/), all wired through the Converse API. Agent tools are Lambda functions exposed via OpenAPI.
- **Alibaba primary**: [Model Studio Agent Application](https://www.alibabacloud.com/help/en/model-studio/application-introduction) (conversational, LLM-driven tool selection) + [Workflow Application](https://www.alibabacloud.com/help/en/model-studio/application-introduction) (deterministic DAG for emergency lane).
- **LangChain used only for**:
  - Layer-1 semantic response cache (`RedisSemanticCache` against [ElastiCache](https://aws.amazon.com/elasticache/redis/) / [Tair](https://www.alibabacloud.com/product/tair))
  - Per-session chat memory (`ConversationBufferWindowMemory`)

Other frameworks considered and rejected for primary runtime: [LangGraph](https://langchain-ai.github.io/langgraph/) / LangChain for full orchestration (too much audit-trail plumbing to write), [LlamaIndex](https://docs.llamaindex.ai/) retrievers (Bedrock KB / Model Studio KB already provide production-grade retrieval), [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent) (reserved for hybrid / on-prem scenarios on Apsara Stack where Model Studio isn't available).

---

## 5. Caching — 3 layers

Hitting the 2-second emergency SLA cost-effectively requires three layers. Layer 1 is hosting-independent; Layer 2 is where the versions diverge.

### Layer 1 — Semantic response cache (LangChain, hosting-independent)

Hash the question embedding, look up the cached final answer, skip the LLM entirely.

- **AWS**: [`langchain.cache.RedisSemanticCache`](https://python.langchain.com/docs/integrations/llms/llm_caching/#redis-semantic-cache) against **ElastiCache for Redis OSS** with [RediSearch](https://redis.io/docs/stack/search/). Hit time: single-digit ms. Expected hit rate for emergency protocols that repeat across shifts: 30–45%.
- **Alibaba**: same pattern against **Tair** (Redis-compatible, not Valkey) + [TairVector](https://www.alibabacloud.com/help/en/tair/user-guide/tairvector-overview).

Tunables: similarity threshold 0.95, TTL 10 min for emergency / 24 hr for general. Invalidation on KB reindex (flush `source:*` tagged keys).

### Layer 2 — Prefix / KV cache (provider or inference-engine level)

LangChain cannot implement Layer 2. Reusing transformer KV tensors has to happen inside the model server.

| Version | Layer 2 | Notes |
|---|---|---|
| A (AWS + Claude) | ✅ [Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/) | Up to 90% off cached input + ~85% TTFT cut. Claude 4.x + Nova supported. Qwen3 NOT supported. |
| B (AWS + Qwen on Bedrock) | ❌ Not supported for Qwen3 on Bedrock (verified May 2026). Self-hosted path uses [vLLM APC](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html) or [SGLang RadixAttention](https://docs.sglang.ai/backend/server_arguments.html) | Self-hosted wins: no `<cachePoint/>` placement, no 5-min TTL, no cache-write premium |
| C (Alibaba + Qwen) | ✅ [Qwen Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache) | Implicit (zero-config from day 1) + explicit named cache IDs. Cache hits bill at 20% of standard input price. |

### Layer 3 — Reserved throughput (peak-only)

- **AWS**: [Bedrock Reserved Tier](https://aws.amazon.com/bedrock/pricing/) for Claude / Nova families
- **Alibaba**: [Qwen Provisioned Throughput Units (PTU)](https://www.alibabacloud.com/help/en/model-studio/model-training-and-deployment-billing)

Turn on only for the emergency lane once sustained TPM justifies it.

### Composed budget (emergency, Version A example)

```
Layer 1 hit  (semantic cache)    →     ~20 ms                   (30–45% of queries)
Layer 2 hit  (prompt cache)      →  1100 ms, 90% cheaper input  (bulk of remaining)
No cache     (cold path)         →  1800 ms, full price         (rare)
```

Blended p50 ~600–900 ms for cached-hot emergency, p95 < 2000 ms. The fast-lane model (Qwen3.5-Flash / Nova Micro / Qwen3 Next 80B MoE) is already small enough to fit the SLA. Fine-tuned students (see [`customization.md`](customization.md)) are complex-lane / fast-lane assets per version; they don't sit on the emergency critical path of Version C.

### Invalidation rules

| Event | What gets invalidated |
|---|---|
| WHO monthly refresh succeeds | Semantic cache keys tagged `source:who`; prompt-cache entries referencing WHO chunks rebuilt on next call |
| Internal trial upload | Semantic keys tagged `document_id:<id>` |
| ICD-11 daily delta | Semantic keys tagged `source:icd11` |
| Model version bump | Full flush (answers are model-specific) |
| Guardrail policy change | Full flush |

### Batch inference (for training data + eval)

Both clouds offer 50% off on-demand for batch. Used for teacher-model SFT dataset generation and nightly LLM-as-judge eval runs.

---

## 6. Corporate integration

### EHR / EMR — patient context at query time

Standard: **HL7 FHIR R4** + [**SMART App Launch v2**](http://docs.smarthealthit.org/). All three of Epic ([Epic on FHIR](https://fhir.epic.com)), Cerner / Oracle Health ([code.cerner.com](https://code.cerner.com)), and Allscripts expose FHIR R4 and support SMART on FHIR — build once, deploy everywhere via per-vendor config.

**EHR launch flow** (not backend services — backend is only for batch jobs that are out of scope for this assistant):

```
Clinician in Epic on patient chart clicks "Ask Nova"
  → Epic launches Nova's iframe with ?iss=<fhir-endpoint>&launch=<ctx>
  → SMART App Launch v2 authorization-code flow (PKCE, public client)
  → Access token carries patient context + scopes
  → Nova frontend → API Gateway → Lambda/FC /chat
    1. Exchange launch ctx → FHIR patient bundle
    2. Extract minimum slice for the question (data minimization)
    3. De-identify via [Comprehend Medical](https://aws.amazon.com/comprehend/medical/) (AWS Sydney) or [DataWorks SDDP](https://www.alibabacloud.com/product/sddp) (Alibaba SG)
    4. Build prompt: system template + RAG context + tokenized patient slice
    5. Call Bedrock / Model Studio; grounded + cited answer
    6. Re-identify tokens in the UI only; model never sees raw PHI
```

### FHIR resources read (scoped per call)

| Resource | Why |
|---|---|
| `Patient` | Demographics (tokenized before LLM) |
| `Condition` | Active + resolved diagnoses |
| `MedicationStatement` / `MedicationRequest` | Current meds; drug interactions |
| `AllergyIntolerance` | Critical for emergency dosing |
| `Observation` | Vitals + recent labs |
| `Encounter` | Current visit context |
| `DocumentReference` | Recent notes, on explicit request only |

Scopes requested: `launch openid fhirUser patient/Patient.rs patient/Condition.rs patient/MedicationStatement.rs patient/AllergyIntolerance.rs patient/Observation.rs patient/Encounter.rs offline_access`. All `.rs` (read + search); **never write**.

### EHR unreachable fallback

Hard 2-second timeout on FHIR call. The answer still runs without patient context, UI shows a banner ("No patient context loaded"). We never block the emergency SLA on EHR latency.

### [CDS Hooks](https://cds-hooks.org/) — out of scope for first release

A `patient-view` hook could proactively surface Nova's recommendations inline when the clinician opens a chart. Added via a separate feature launch after the core assistant is in production.

### Document integration — SharePoint / OneDrive

Real-time change notification via [Microsoft Graph subscription](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0):

```http
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

Subscription expiry is [30 days max](https://learn.microsoft.com/en-us/graph/api/resources/change-notifications-api-overview?view=graph-rest-1.0); a lifecycle job renews automatically. `clientState` validated on every inbound notification.

For high-traffic drives, switch to [Event Hubs delivery](https://learn.microsoft.com/en-us/graph/change-notifications-delivery-event-hubs) instead of HTTP webhooks.

**App permission**: **`Sites.Selected`** — hospital admin grants access per-specific-site, not tenant-wide. Secret rotated every 90 days.

### Other document sources

- **Google Drive** — same pattern with [`files.watch`](https://developers.google.com/drive/api/v3/reference/files/watch) push notifications
- **Confluence Cloud** — [webhooks](https://developer.atlassian.com/cloud/confluence/webhooks/) on `page_created`, `page_updated`
- **On-prem NFS / SMB share** — scheduled puller over Site-to-Site VPN

### Identity

Two populations:

| Population | AWS | Alibaba |
|---|---|---|
| Clinicians (external, hospital's IdP) | [Cognito user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-identity-federation.html) federates via SAML/OIDC to EntraID / Okta / ADFS | [Alibaba IDaaS (EIAM 2.0)](https://www.alibabacloud.com/help/en/idaas/) Premium+ federates to hospital IdP |
| Nova staff (internal) | [IAM Identity Center](https://aws.amazon.com/iam/identity-center/) federated to Nova EntraID | [Cloud SSO + RAM](https://www.alibabacloud.com/product/ram) federated to Nova EntraID |

Long-lived access keys banned. All programmatic access uses role assumption with session tokens. MFA enforced in hospital IdP.

### Authorization scopes

```
chat:clinical          POST /chat
kb:read                retrieve from KB via API (admin-only)
curator:upload         upload via portal
curator:delete         delete docs (admin-only)
admin:configure        change router / guardrail config
admin:evaluate         run eval harness
```

API Gateway authorizer checks `aud`, `iss`, `exp`, `scope` every call. Lambda/FC re-checks before privileged actions (defense in depth).

Sessions: 60 min clinicians, 15 min admins. Step-up MFA required for `admin:*` and for "living guideline override" uploads.

**Break-glass** — two named Nova admins, hardware MFA + second-admin approval ticket, auto-pages security.

---

## 7. Hospital connectivity — two-plane model

Two distinct network planes for hospital integration. Both are part of the baseline deployment.

**Control plane (clinician traffic)** — public HTTPS + TLS 1.3 + hospital-IdP federation (Cognito/IDaaS + SAML/OIDC) + WAF + Anti-DDoS + per-tenant WAF IP allow-list. Hospital egress firewall whitelists Nova's published IP range and API domain. Standard SaaS pattern (Epic cloud, Cerner CommunityWorks, Salesforce Health Cloud all onboard this way). Clinician prompts are SDDP-masked at FC preflight before they reach any LLM.

**Data plane (bulk PHI transfer)** — Site-to-Site IPsec VPN:

- **AWS**: [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html) to Virtual Private Gateway. IKEv2 + AES-256-GCM + SHA-2, dual-tunnel HA, BGP for failover.
- **Alibaba**: [IPsec-VPN on VPN Gateway](https://www.alibabacloud.com/help/en/vpn-gateway). Same cipher profile + dual tunnel. [Smart Access Gateway (SAG)](https://www.alibabacloud.com/product/smart-access-gateway) is a turnkey appliance alternative. [Express Connect](https://www.alibabacloud.com/product/express-connect) is the dedicated-line option (Alibaba equivalent of AWS Direct Connect), only used on explicit client request — not baseline.

**No Outposts, Direct Connect, or Apsara Stack in baseline.** Dedicated-line options exist for specific regulatory requirements but add 6–12 weeks of onboarding and $1,500+/mo vs single-digit-millisecond latency gains.

The data-plane VPN carries the backend system-to-system flows that move raw PHI in bulk: SharePoint / SMB trial-report pull, on-prem EHR FHIR callback, Upload Portal traffic from curators. The clinician's chat UI always uses the control-plane public HTTPS path — the VPN is never on the 2-second emergency critical path.

**Why a VPN for the data plane despite TLS 1.3 being technically sufficient**: clinical trial reports and FHIR bundles contain raw PHI that hasn't passed SDDP yet. Auditors for HIPAA / HITRUST / hospital procurement expect to see a VPN on bulk-PHI paths. The small monthly cost (~$110–150/mo) buys the defense-in-depth and the procurement story.

---

## 8. References (authoritative-source index)

- [Agentic RAG: The 2026 Production Guide — MarsDevs](https://www.marsdevs.com/guides/agentic-rag-2026-guide)
- [Bedrock Knowledge Bases — advanced parsing, chunking](https://aws.amazon.com/blogs/machine-learning/amazon-bedrock-knowledge-bases-now-supports-advanced-parsing-chunking-and-query-reformulation-giving-greater-control-of-accuracy-in-rag-based-applications/)
- [AnalyticDB PG — GraphRAG service](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service)
- [Bedrock KB GraphRAG on Neptune Analytics — GA March 2025](https://aws.amazon.com/blogs/machine-learning/announcing-general-availability-of-amazon-bedrock-knowledge-bases-graphrag-with-amazon-neptune-analytics/)
- [MMedAgent-RL — multi-agent medical reasoning on Qwen2.5-VL](https://arxiv.org/html/2506.00555v2)
- [MedRoute — RL-trained specialist routing](https://arxiv.org/abs/2604.06180)
- [SMART App Launch v2](http://docs.smarthealthit.org/)
- [Microsoft Graph change-notification subscriptions](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0)
- [NCBI E-utilities rate limits (PubMed)](https://support.nlm.nih.gov/knowledgebase/article/KA-05317/en-us)

*Content above is rephrased for compliance with licensing restrictions.*
