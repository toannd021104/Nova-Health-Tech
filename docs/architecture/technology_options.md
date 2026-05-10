# Technology Options — Per Requirement Domain (Qwen-centric)

This doc lists the realistic options for every requirement in the Nova Health Tech brief, with what each option solves, pros and cons, cost and complexity, and which Nova version it fits. Technology-wise we orient around **Qwen on Alibaba Cloud** (Version C) as the headline stack, with AWS Claude (Version A) and AWS Qwen (Version B) as alternatives when clients pin residency or BAA.

Scenario anchors from the brief:
- Complex medical Q&A, ground in internal trial reports + treatment protocols + external sources (PubMed, WHO)
- Auditable, compliant, ≤ 2 s emergency, consistent tone
- Monthly WHO updates, patient-sensitive internal trials, legacy PDFs with inconsistent tagging, WHO structured API

The seven domains below map directly to the brief's five bullets (Data pipeline, Model orchestration, Security, Deployment, Performance optimization) plus two that the brief implies (Retrieval is a sub-choice of data pipeline; Observability is a sub-choice of compliance).

## Phase legend (used throughout this doc)

The rollout plan in `docs/architecture/AWS_architecture.md` §7.2 and `docs/architecture/Alibaba_architecture.md` §7.2 runs in four phases:

| Phase | Weeks | Goal | What actually ships |
|---|---|---|---|
| **Phase 1 — Ship the pilot** | 1–6 | Get it running with real data, meet the 2 s SLA without fine-tuning | Scheduled ingestion (WHO + ICD-11 + SharePoint), upload portal over VPN, hybrid retrieval + rerank, base LLM on both lanes, emergency toggle, Layer-1 + Layer-2 caching where supported, eval harness baseline. **No fine-tuning.** |
| **Phase 2 — Customize on real data** | 7–10 | Close the tone and specialty gaps using usage logs from Phase 1 | Teacher-data generation + clinician review → SFT / LoRA / distillation student at 5 % canary. Optional: specialist multi-agent on complex lane; LazyGraphRAG over WHO corpus. Explicit Qwen Context Cache on system-prompt prefix (C). |
| **Phase 3 — Make it cheap and fast at scale** | 11–14 | Promote student to 100 %, add preference / RL tuning, reserve capacity | Student 100 % on fast lane; DPO / GRPO round; Bedrock Reserved Tier or Qwen PTU on the emergency lane if sustained-TPM justifies it. Feature-flag the specialist agents and KG-RAG on per-hospital. |
| **Phase 4 — Keep it fresh** | quarterly | Prevent drift | Retrain student on new clinician data + new WHO / ICD-11 releases; re-qualify with eval harness before promoting; WHO-refresh invalidates cached answers. |

"Phase 1 default" in the tables below means **ships in weeks 1–6**. "Phase 2 option" means **ships only if Phase 1 measurements show we need it**. Deferring to Phase 2/3 is not a "maybe later" — it's an explicit decision to let real usage data pick the extension point.

---

## 1. Data pipeline options

What "data pipeline" has to do: get WHO PDFs, ICD-11 JSON, PubMed records, internal SharePoint PDFs, and manual uploads into a searchable form the LLM can cite — monthly for WHO, weekly for internal, webhook-triggered on SharePoint, daily delta on ICD-11.

| Option | What it solves | Pros | Cons | Cost | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. Fully-managed parse + KB (Alibaba DocMind + Model Studio RAG Application / AWS Bedrock Data Automation + Knowledge Bases)** | Single service handles OCR, tables, chunking, embedding, indexing | One vendor, one IAM boundary, built-in compliance audit trail, table-aware parsing out of the box | Per-page cost higher than OSS; less control over chunk heuristics; table-in-table occasionally split | ~$0.01–$0.04 per page for parse; embed + storage on top | Low | **Version C (default)** and A |
| **B. Open-source parser (Unstructured / LlamaParse / Docling) + self-managed vector DB** | Max control; swap parser when a better one lands | Cheapest per page; per-doc-type chunking rules | You own ops, compliance review covers your parser stack, quality varies by doc type | Compute + storage only | Medium–High | Clients that insist on open source |
| **C. Multimodal page-image embeddings (Amazon Nova Multimodal on AWS; tongyi-embedding-vision-plus on Alibaba SG Intl)** | Preserve tables and flowcharts exactly; no chunking loss | Great for "show me the dosing flowchart" queries | Higher embed cost; larger tokens per query; citations at page level only | 2–5× embed cost vs text-only | Medium | **Fallback lane** for figure-heavy queries |
| **D. Hybrid — Managed parse primary, Strategy C fallback for figure-bearing chunks** | Takes the 90 % case (body text) cheap and the 10 % hard case (figures) accurate | Best of both; lowest total cost at equivalent recall | Two pipelines to version together | +10–15 % over Option A alone | Medium | **Our recommendation for all three versions** — already in `rag_strategy.md` |

Status in this repo: Option D chosen. WHO scheduled cron + ICD-11 daily delta + SharePoint Graph webhook + Upload Portal all land in one raw bucket, one ingestion workflow (see `docs/architecture/ingestion_and_identity.md`).

### Ingestion triggers (already designed, listed here for completeness)

| Trigger | Cadence | Target |
|---|---|---|
| WHO ICD-11 structured API | daily 02:00 SGT | `raw/icd11/` |
| WHO guideline PDFs | monthly day 1 + RSS webhook | `raw/who/` |
| Internal trial reports (SharePoint) | weekly Sun + Graph webhook | `raw/sharepoint/` |
| Treatment protocols | same | `raw/sharepoint/` |
| PubMed E-utilities (optional for specific topics) | on-demand or weekly | `raw/pubmed/` |
| Internal Upload Portal (VPN + IdP) | ad hoc | `raw/manual/` |

**PubMed note** — NCBI E-Utilities allow 3 req/s without a key, 10 req/s with a free API key. The free tier is plenty for scheduled topic-based pulls; we do not try to mirror all of PubMed. Use PubMed as a **runtime tool call** for rare-query coverage, not a bulk ingest.

---

## 2. Retrieval options (sub-choice of data pipeline)

This is the big question: plain vector RAG, hybrid RAG, agentic RAG, or knowledge-graph RAG. All of these can coexist; picking a **default** plus **optional paths** keeps cost and latency under control.

| Option | What it solves | Pros | Cons | Cost per query | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. Plain vector RAG (kNN only)** | Semantic similarity retrieval | Simple, fast (< 80 ms), cheap | Misses exact-term queries (drug names, ICD codes), no reasoning over relationships | Baseline | Low | Not chosen |
| **B. Hybrid RAG (BM25 + kNN + rerank)** | Adds keyword exact match and rerank precision | Best general-purpose; covers drug names, codes, and semantics; 5–15 % recall lift over plain vector | Slightly slower (~100 ms); rerank adds cost | Baseline + `qwen3-rerank` $0.10/1M | Low | **Default for emergency lane + citation / literature lane** |
| **C. Agentic RAG (iterative retrieve → reason → retrieve)** | Multi-hop: "what does treatment X do for patient with condition Y and allergy Z?" | Higher answer quality on multi-hop; the agent can call PubMed / ICD-11 / SharePoint as separate tools and compose | 3–10× more tokens, 2–5× latency vs one-pass (per the 2026 production guide) | ~$0.006–0.015 per complex call vs $0.0026 one-pass | Medium | **Default for complex differential lane (non-emergency)** |
| **D. Knowledge-Graph RAG (GraphRAG / LightRAG / LazyGraphRAG)** | "Global" questions that span the whole corpus: "what are the main themes across all WHO sepsis guidelines?" | Answers global queries vector RAG cannot; disambiguates entities (sepsis vs septic shock vs severe sepsis) | KG construction cost is real; Microsoft GraphRAG indexing ~$20–80 per 100 MB of text; LazyGraphRAG drops this 700×; small-LLM KG-RAG shows mixed gains per Apr 2026 paper | LazyGraphRAG ~0.1 % of full GraphRAG query cost, same quality on global queries | **High** for GraphRAG; **Medium** for LazyGraphRAG / LightRAG | **Optional** layer for complex lane; use LazyGraphRAG on the WHO + guideline corpus, not on PubMed |
| **E. Agentic Medical Graph-RAG (AMG-RAG, MedGraphRAG)** | Automates continuous MKG updates + integrates reasoning + PubMed live | Research-leading on MedQA benchmarks; designed for clinical use | Most complex of the lot; more research than production | Research-tier cost; no managed offering yet | **Very High** | Future roadmap — not phase 1 |

### Our stack

- **Emergency lane**: **B — hybrid RAG one-pass**. Speed-first.
- **Complex lane**: **B + C — agentic RAG by default**, with a tool for KG search if D is available. The agent's tools:
  - `kb_retrieve(topic, source, max_age_days)` — hybrid on Model Studio KB
  - `icd11_lookup(term, mode)` — runtime WHO ICD-11 API
  - `pubmed_search(query, max_results)` — runtime E-utilities (free tier key)
  - `graph_query(subject, relation, object)` — optional, only if D is deployed
- **Optional D**: **LazyGraphRAG over the WHO + internal guideline corpus** (not PubMed). Indexed monthly during the ingestion job. Turn on if the eval harness shows the agent struggles on "summarize across all the living WHO hepatitis guidelines" style questions.
- **Not E** for phase 1. Roadmap item once we have a stable evaluation harness.

### Why agentic RAG is worth the cost on the complex lane

> *Content rephrased for compliance with licensing restrictions.*
>
> Per the MarsDevs 2026 production guide, agentic RAG costs 3–10× more tokens and adds 2–5× latency versus one-pass RAG. It earns that price on multi-hop questions, ambiguous queries, and high-stakes domains (legal, medical, financial). It does not earn it on FAQ bots or single-fact lookups.

The emergency lane is single-hop ("sepsis bundle dose?"). The complex lane is multi-hop ("54-year-old with eGFR 35 and a sulfa allergy, what antibiotic for UTI?") — the agent pays for itself.

Sources: [Agentic RAG: The 2026 Production Guide](https://www.marsdevs.com/guides/agentic-rag-2026-guide), [Agentic Medical Knowledge Graphs (AMG-RAG)](https://arxiv.org/abs/2502.13010), [MedGraphRAG](https://arxiv.org/abs/2408.04187), [LazyGraphRAG (Microsoft Research)](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/), [KG-RAG with small LLMs, Apr 2026](https://arxiv.org/html/2504.10982v5).

---

## 3. Model orchestration options

What orchestration has to do: route a question to the right model(s), call retrieval tools, enforce guardrails, keep a cost-latency budget.

### 3a. Router / orchestrator framework

| Option | What it solves | Pros | Cons | Cost | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. Managed cloud agent (Model Studio Agent + Workflow Application; AWS Bedrock Agents)** | Tool calling + KB + guardrails in one service | Compliance surface small, audit built in, zero infra to patch | Vendor-locked orchestration (models and data still portable) | Included in model cost | Low | **Default for all three versions** |
| **B. LangGraph + Qwen-Agent + LangChain** | Code-level control over the graph; portable across clouds | State management, conditional edges, MCP tools, works with Qwen 3.x | You own the runtime; compliance audit needs custom glue | + container ops | Medium | Chosen when the managed Agent blocks a specific pattern |
| **C. Plain SDK calls (DashScope / Bedrock Runtime)** | Thin Lambda/FC; no abstraction | Zero abstraction tax | You re-implement tool calling, memory, routing, guardrails | Minimal | Low at first, high after 3 months | Not chosen |

**Decision**: **A (managed) as the primary**, LangChain used only for the semantic cache and per-session chat memory. The router between fast / complex lanes is a **pure if/else on the explicit emergency toggle** — no classifier LLM call. That's already reflected across all docs and in `aws-demo/ec2/app/graph.py`.

### 3b. Single-agent vs multi-agent (specialist) orchestration

This is where your "multi-agent like different specialty doctors" question fits.

| Option | What it solves | Pros | Cons | Cost | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. Single agent with broad system prompt** | Simple, one model per lane | Lowest latency; lowest cost; one prompt to maintain | General-purpose answers on deeply specialized questions (rare genetics, pediatric dosing, oncology protocols) | Baseline | Low | Emergency lane + most complex-lane queries |
| **B. Router + specialist agents (general practitioner → specialist pattern)** | Mirrors real clinical triage; a GP agent decides if the case needs cardiology / oncology / pediatrics / emergency; a specialist agent answers | Better domain accuracy; separate system prompts + tool sets per specialty; auditable division of labor | More agents = more orchestration; latency overhead for specialist call; prompt-engineering burden per specialty | 1.5–3× cost on the complex lane when specialist is invoked | Medium | **Optional on the complex lane** — toggleable per hospital |
| **C. Multi-specialist parallel (MoA pattern, all specialists run simultaneously, moderator agent aggregates)** | Maximum reasoning depth; mirrors tumor-board style discussion | Highest clinical quality on hard cases; research shows it beats single-agent on MedQA by 3–8 % | 3–5× cost; 2–3× latency; much harder to audit who said what | Premium tier only | High | Phase-3 research path; not phase 1 |
| **D. Multi-agent with RL-trained router (MedRoute, MMedAgent-RL pattern)** | The router itself is RL-trained to pick specialists dynamically | Higher routing accuracy than rule-based | Requires a training pipeline, labeled routing data, evaluation harness | Training + inference | High | Phase-3 once we have clinical-feedback data |

### Proposed specialty topology (Option B) on Version C

Specialties we'd actually wire up — based on WHO / ICD-11 chapters that have distinct treatment logic and a realistic volume at Nova's hospital clients:

| Agent | Primary knowledge base / tool | Model | Typical queries |
|---|---|---|---|
| **Triage / GP agent** | kb-who-guidelines + kb-icd11 | Qwen3.5-Flash | Classifies the case, routes to the specialist, integrates final answer |
| **Emergency medicine** | kb-who-emergency + sepsis + stroke + MI protocols | Qwen3.5-Flash (low temp, high grounding) | Emergency toggle always routes here |
| **Infectious disease** | kb-who-antimicrobial + treatment-protocols tagged `infectious` | Qwen3.5-Plus | Antibiotic choice, resistance patterns, empiric coverage |
| **Oncology** | kb-who-oncology + internal trials tagged `oncology` | Qwen3.5-Plus | Staging, regimen selection, protocol deviations |
| **Cardiology** | kb-cardio + internal cardiology trials | Qwen3.5-Plus | ACS pathways, dosing, device patient considerations |
| **Pediatrics** | kb-pediatrics-dosing + weight-based calcs | Qwen3.5-Plus (strict PHI + age filter) | Weight-based dosing, age-appropriate contraindications |
| **Obs / Gyn** | kb-who-maternal + obstetric emergency | Qwen3.5-Plus | Pre-eclampsia, post-partum hemorrhage |
| **Pharmacology / drug-interaction** | kb-drug-interactions + openFDA | Qwen3.5-Flash + tool | Any query with ≥ 2 drugs or a known allergy |

Simpler fallback if multi-agent proves operationally heavy: **3 specialties + GP + Emergency** (most common hospital services). You don't need all 8 from day 1. Start with Emergency + ID + General; add specialties per client demand.

### Qwen-specific framework for Option B

- **Alibaba Model Studio Agent Application** — multiple agent applications, each with its own system prompt, tools, and KB binding. Route between them through a **Workflow Application** that's driven by the GP/triage agent's output.
- **Qwen-Agent** (GitHub, 11.7k⭐) — open-source framework for Qwen ≥ 3.0 with function calling, MCP, RAG, browser tools. Used when we want LangGraph-style orchestration on a self-hosted Qwen (hybrid / on-prem scenarios, Version C-prem).

Sources: [MMedAgent-RL (Qwen2.5-VL)](https://arxiv.org/html/2506.00555v2), [MedRoute RL router](https://arxiv.org/abs/2604.06180), [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent), [AWS Bedrock multi-agents](https://aws.amazon.com/blogs/machine-learning/build-multi-agent-systems-with-langgraph-and-amazon-bedrock/), [AWS Bedrock AgentCore — health care](https://aws.amazon.com/blogs/machine-learning/building-health-care-agents-using-amazon-bedrock-agentcore/).

---

## 4. Training / model adaptation options

What adaptation has to do: close the gap between a general model and Nova's clinical tone, reduce cost on the fast lane, specialize on Nova's corpus.

| Option | What it solves | Pros | Cons | Cost per run | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. No fine-tune (prompt engineering + RAG + caching only)** | Gets 80 % of the tone and grounding benefit at zero training cost | Fastest to ship; no retraining ops | Tone consistency hits a ceiling; latency is what the base model gives you | $0 | Low | **Phase 1 default on every version** |
| **B. SFT on teacher-generated data (distillation)** | Teacher-generated dataset + small student = fast + on-brand | Proven recipe; works on any cloud | Needs 5k+ seed prompts + a review process | AWS Model Distillation ~$1.5–2.5k; PAI SFT+LoRA ~$15–40; SageMaker TRL ~$70–100 | Medium | Phase 2–3 on Versions A, B, C |
| **C. DPO (preference tuning)** | Uses `(chosen, rejected)` pairs to nudge tone and phrasing | Cheap once the data exists; pairs well with SFT | Needs clinician-labeled preferences | Similar to SFT | Medium | Phase 3 |
| **D. GRPO (RL with verifiable reward)** | "Did the answer cite a real chunk? Did it match the ICD-11 code?" — rewarded | Cheap, no labels needed, great for tool-calling; AWS builder article used GRPO on Qwen3-4B at ~$80/run | Rewards must be computable automatically | AWS Bedrock RFT on Qwen3 32B = $80/hr (~$640/run); SageMaker GRPO on Qwen3-4B ~$70–100; PAI GRPO ~$15–50 | Medium–High | **Most attractive path on Versions B and C** |
| **E. RLHF (reward model + PPO)** | The classical RL path | Strong results if you have labeling budget | Heavier and slower than DPO/GRPO; rarely beats them on clinical QA | 10–100× DPO | High | Not chosen |
| **F. Continued pre-training (CPT) on medical corpus** | Inject broad domain knowledge | Good for base-model weak spots | Huge dataset and compute; marginal over RAG | 10–100× SFT | Very High | Not chosen — RAG already handles knowledge freshness |

### Per-version adaptation path (matches `fine_tuning_and_distillation.md`)

| Version | Phase 1 | Phase 2–3 |
|---|---|---|
| A — AWS + Claude | No fine-tune | Bedrock Model Distillation Sonnet 4.5 → Nova Lite; optional Claude 3 Haiku SFT on us-west-2 (with trade-offs) |
| B — AWS + Qwen (Bedrock Sydney) | No fine-tune | Bedrock Reinforcement Fine-Tuning on Qwen3-32B (us-west-2, $80/hr) — RFT preferred for tool-calling reliability; SageMaker GRPO on Qwen3-4B if SG residency required |
| C — Alibaba + Qwen (Singapore) | No fine-tune | PAI SFT+LoRA on Qwen3-8B (~$15–40/run), optional DPO, optional GRPO per Alibaba PAI docs |

Source: [AWS Builder GRPO article](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai), [Qwen fine-tuning on PAI](https://www.alibabacloud.com/help/en/pai/use-cases/quick-start-deploy-fine-tune-and-evaluate-qwen3-models), [AgenticQwen — training small agentic LMs with dual data flywheels](https://arxiv.org/abs/2604.21590).

---

## 5. Corporate integration options

What corporate integration has to do: get the assistant into the clinician's existing workflow (EHR, SharePoint, hospital IdP, VPN).

### 5a. EHR / EMR integration

| Option | What it solves | Pros | Cons | Cost | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. HL7 FHIR R4 + SMART App Launch v2 (EHR launch)** | Clinician launches the assistant from inside Epic/Cerner/Allscripts; EHR injects patient context + OAuth2 | Industry standard across all three majors; read-only scopes; per-clinician tokens; minimum-scope principle | Each hospital needs OAuth registration; SMART on FHIR implementations vary slightly per vendor | Per-tenant config only; SDKs free | Medium | **Default** for Versions A, B, C |
| **B. FHIR Backend Services (`client_credentials` + JWT)** | Server-to-server; no clinician in the loop | Batch jobs (nightly de-identified extracts) | Not used for day-to-day queries — no patient-specific auditability on the backend path | Same as A | Medium | Batch use cases only |
| **C. HL7 v2 legacy interfaces (Mirth / Corepoint / Rhapsody)** | Covers older hospitals that haven't turned on FHIR yet | Works everywhere eventually | Much more plumbing; reverse-engineering pipe-delimited messages | Integration engine + ops | High | Fallback when the hospital can't do FHIR |
| **D. No EHR integration** | Simplest | Nothing to ship | Assistant can't personalize answers; clinician copies/pastes; real-world usability drops | $0 | None | Phase-0 pilot only |

**Chosen**: A. Already designed in `docs/architecture/corporate_integration.md`.

### 5b. Document / knowledge-management integration

| Option | What it solves | Pros | Cons | Cost | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. Microsoft Graph subscriptions on SharePoint + OneDrive** | Real-time webhook on create/update/delete | Fast; tenant-scoped via `Sites.Selected`; official MS path | Subscription expiry < 30 days, needs renewal job | Free | Low | **Default** |
| **B. Google Drive API `files.watch`** | Same as A for Google Workspace customers | Official | Less common in APAC hospitals | Free | Low | Google-first clients |
| **C. Confluence Cloud webhooks** | Same for Confluence-based clients | Official | Lower priority | Free | Low | Confluence-first clients |
| **D. Hospital NFS / SMB share via scheduled puller over VPN** | On-prem-only clients without SharePoint | Works everywhere | Slower freshness (cron, not push) | Minimal | Medium | On-prem fallback |

**Chosen**: A + D. Already designed.

### 5c. Deployment model

| Option | What it solves | Pros | Cons | Cost delta | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. Public cloud in Singapore (our default)** | Shortest time-to-value; native compliance certifications | Fastest, cheapest; scales on demand | Assumes SG data residency is acceptable | Baseline | Low | Default for all three versions |
| **B. Hybrid (cloud + hospital on-prem via Site-to-Site VPN)** | Hospital keeps certain data on-prem; inference in cloud | Compromise between control and speed | VPN throughput matters; partial network ownership | +10 % ops | Medium | When the hospital's legal team insists |
| **C. Dedicated / on-prem (Apsara Stack / AWS Outposts)** | Full data sovereignty | Ultimate control | $$$$; long lead time; much slower iteration | 5–10× baseline | Very High | Rejected per your requirements |

**Chosen**: A. Hybrid via VPN for document upload + EHR. No Outposts / Direct Connect / Apsara Stack.

---

## 6. Performance optimization options

What performance has to do: hit the 2-second p95 emergency target, keep cost under the pilot budget, handle spikes.

### 6a. Caching (see `docs/architecture/caching_strategy.md` for full detail)

| Layer | Option | Saves |
|---|---|---|
| 1 — Semantic response cache | LangChain `RedisSemanticCache` on ElastiCache Valkey (A/B) or Tair + TairVector (C) | Entire LLM call; 30–45 % hit rate on emergency |
| 2 — Prefix / prompt cache | Bedrock Prompt Caching (A: Claude + Nova), Qwen Context Cache implicit+explicit (C), vLLM APC / SGLang RadixAttention on self-hosted (B self-hosted path). **B on Bedrock default has no Layer 2** — Qwen3 models on Bedrock don't support it (verified May 2026). | Up to 90 % off cached input tokens + ~300 ms TTFT |
| 3 — Reserved throughput | Bedrock Reserved Tier (A/B), Qwen PTU (C) | Flat rate + no queueing at peak |

### 6b. Model-level

| Option | Impact | Version fit |
|---|---|---|
| **MoE fast-lane model (Qwen3.5-Flash, Qwen3 Next 80B A3B, Nova Micro)** | Lower TTFT + lower cost per token | C / B / A respectively |
| **Streaming (SSE)** | First token to clinician in ~300–500 ms regardless of full-answer length | All three versions |
| **Batch inference** for offline jobs | 50 % off tokens | Teacher-data generation; eval harness |
| **Inference-engine tuning (vLLM paged-attention, continuous batching, quantization)** | Higher throughput on self-hosted Qwen | B self-hosted + C self-hosted |

### 6c. Retrieval-level

| Option | Impact |
|---|---|
| Metadata pre-filter (review_date, specialty, tenant) before kNN | Shrinks the search space 5–20× on large KBs |
| Top-20 kNN → top-5 rerank (not top-100) | Balances recall and rerank cost |
| Cohere Rerank 3.5 (AWS) / qwen3-rerank (Ali) only on borderline-score queries | Keeps rerank cost low (~10 % of complex calls) |

### 6d. Network-level

| Option | Impact |
|---|---|
| Region pinning to Singapore (matches hospital) | Eliminates ~90–180 ms cross-region RTT |
| CDN + WAF at the edge | Connection-setup reduction |
| HTTP/2 + keep-alive | Avoids handshake per request |

---

## 7. Observability & compliance monitoring options

What observability has to do: show every token, every retrieval, every guardrail verdict, every model version — auditably, for 6 years, across all three versions.

| Option | What it solves | Pros | Cons | Cost | Complexity | Best for |
|---|---|---|---|---|---|---|
| **A. Native LLM trace (Alibaba ARMS LLM Trace Explorer; AWS Bedrock invocation logs + CloudWatch)** | OpenTelemetry-standard LLM trace spans: input, output, token count, tool calls, cost per request, session analysis | Already deployed by your cloud; maps to Qwen / Claude / Nova; covers multi-turn conversations | Vendor-scoped; federation across clouds needs a collector layer | Part of the platform; ARMS agent for Python is free, billed by trace ingest | Low | **Default** |
| **B. OpenTelemetry + Langfuse / Arize / Phoenix self-hosted** | Vendor-neutral trace store you own | Portable across clouds; full control over retention | Another service to run; storage cost on top | Container hosting | Medium | When a hospital mandates trace data residency |
| **C. Build-your-own audit log (structured JSON → S3 / OSS WORM)** | Minimum compliant path | Simple; already in our design | Manual dashboards | Negligible | Low | Already implemented (our CloudTrail + Bedrock invocation logs path) |
| **D. Full-stack APM (DataDog / New Relic / Grafana Cloud)** | End-to-end app observability | Comprehensive; pretty dashboards | Cross-border data concerns; $$ | Per-host + per-ingest | Medium | Nova-internal visibility, not PHI path |

**Chosen**: **A + C**. ARMS LLM Trace for live observability on Version C (and the Python backend on A/B). CloudTrail/ActionTrail → WORM for the immutable compliance audit, 6-year retention.

### Metrics that actually matter for a clinical assistant

| Metric | Target | Where it lives |
|---|---|---|
| p50 / p95 / p99 latency, emergency lane | p50 ≤ 900 ms · p95 ≤ 2000 ms | ARMS / CloudWatch |
| p95 latency, complex lane (agentic RAG) | ≤ 6000 ms | ARMS / CloudWatch |
| Semantic-cache hit rate, emergency | ≥ 30 % | ARMS span attribute |
| Citation coverage (every answer has ≥ 1 valid cite to a chunk) | ≥ 98 % | Custom grounding-check log |
| Guardrail block rate (grounding / PHI / injection) | < 3 % after first-month tuning | ARMS + Guardrails logs |
| Token cost per call, per lane | tracked vs budget | ARMS cost span |
| Stale-answer rate (cached answer on doc that changed after cache TTL) | < 0.5 % | Index version tag comparison |
| Router mis-route rate (toggle off but question obviously emergency) | < 5 % | Offline audit sample, labeled by clinician review |

Sources: [ARMS LLM Trace Explorer](https://www.alibabacloud.com/help/en/arms/application-monitoring/user-guide/llm-trace-explorer), [ARMS monitor LLM applications (Python)](http://www.alibabacloud.com/help/en/arms/application-monitoring/user-guide/use-the-arms-agent-for-python-to-monitor-llm-applications), [ARMS LLM scenario analysis — sessions + token usage](https://www.alibabacloud.com/help/en/arms/application-monitoring/user-guide/llm-scenario-based-analysis).

---

## 8. What the choice set looks like end-to-end (Qwen-centric, Version C default)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Ingestion (scheduled + webhook + portal)                               │
│    DocMind advanced parse → chunk → text-embedding-v4 (text) /          │
│    tongyi-embedding-vision-plus (figures) → OpenSearch Vector Search    │
│    + AnalyticDB PG hybrid option (BM25 + kNN + sparse)                  │
│    Optional LazyGraphRAG index over WHO + guideline corpus              │
└──────────────────────────────────┬──────────────────────────────────────┘
                                   │
┌──────────────────────────────────┴──────────────────────────────────────┐
│  Runtime (Model Studio Agent + Workflow Application)                    │
│                                                                         │
│   If toggle ON → Emergency Workflow App                                 │
│     1-hop hybrid retrieve (Model Studio KB)                             │
│     Qwen3.5-Flash (low temp) + qwen3-rerank                             │
│     target p95 ≤ 2 s                                                    │
│                                                                         │
│   If toggle OFF → Complex Agent (multi-agent optional, see §3b)         │
│     GP / triage agent (Qwen3.5-Flash) → picks specialist                │
│     Specialist agent (Qwen3.5-Plus) with tools:                         │
│       - kb_retrieve(topic, source, max_age_days)                        │
│       - icd11_lookup(term, mode)                                        │
│       - pubmed_search(query)                                            │
│       - graph_query(s,r,o) if LazyGraphRAG deployed                     │
│     Moderator step: ground-check + citation validator                   │
│                                                                         │
│   All behind: Content Moderation 2.0 + qwen3-rerank + IDaaS SSO         │
│   Cached by: Layer 1 Tair semantic + Layer 2 Qwen Context Cache         │
│   Observed by: ARMS LLM Trace Explorer + ActionTrail → OSS WORM 6-yr    │
└─────────────────────────────────────────────────────────────────────────┘
```

## 9. Summary decision table (per domain)

| Domain | Version C default (recommended) | Version A default | Version B default |
|---|---|---|---|
| Data pipeline | Managed DocMind + multimodal fallback (option 1-D) | BDA + Nova Multimodal fallback (1-D) | BDA + Nova Multimodal fallback (1-D) |
| Retrieval | Hybrid (B) for emergency + **Agentic (C)** for complex; optional LazyGraphRAG (D) on WHO corpus | Same pattern | Same pattern |
| Orchestration | Model Studio Agent + Workflow Application; **multi-agent specialist on complex lane (§3b option B, start with 3 specialties)** | Bedrock Agents; single-agent phase 1 | Bedrock Agents; single-agent phase 1 |
| Training | Phase 1: RAG-only. Phase 2: PAI SFT+LoRA on Qwen3-8B. Phase 3: GRPO option. | Phase 2: Bedrock Model Distillation Sonnet → Nova Lite | Phase 2: Bedrock RFT on Qwen3-32B (us-west-2) |
| Corporate integration | SMART on FHIR + Graph subscriptions + Upload Portal + IPsec VPN | Same | Same |
| Performance optimization | Layers 1 + 2 (Qwen Context Cache implicit from day 1) + streaming + metadata pre-filter | Layers 1 + 2 (Bedrock Prompt Caching from day 1) + streaming | Layer 1 only on Bedrock default (Qwen3 no prompt cache); vLLM APC on self-hosted path |
| Observability | ARMS LLM Trace + ActionTrail → OSS WORM 6 yr | CloudWatch + Bedrock logs + CloudTrail → S3 Object Lock 6 yr | Same as A |

## 10. Questions we still need to answer for the rollout

1. Do we ship the **multi-agent specialist topology** (3b option B) in phase 1 or defer to phase 2? Recommend phase 2 — start with single-agent on the complex lane, add GP + ID + Emergency specialists once we see the volume per specialty in production.
2. Do we deploy **LazyGraphRAG** in phase 1 or wait for the eval harness to show the agent struggles on global queries? Recommend phase 2 — it's cheap to layer in later (Microsoft publishes the reference implementation).
3. **PubMed as a runtime tool call** — yes, with the free E-utilities API key (10 rps). Tool name `pubmed_search(query, max_results=5)` returns PMID + title + abstract snippet.
4. **Multi-agent evaluation** — do we plan a tumor-board-style MoA phase? Defer to phase 3, only if single-agent + specialist routing misses quality targets on MedQA-style internal evals.

## 11. References

- [Alibaba Cloud Model Studio — Agent Applications](https://www.alibabacloud.com/help/en/model-studio/getting-started/application-building-instructions)
- [Model Studio RAG Knowledge Base](https://www.alibabacloud.com/help/en/model-studio/user-guide/rag-knowledge-base)
- [OpenSearch Vector Search Edition — product overview](https://www.alibabacloud.com/help/en/open-search/vector-search-edition/product-overview)
- [AnalyticDB for PostgreSQL — hybrid search (vector + BM25 + sparse)](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/fusion-search-use-guide)
- [AnalyticDB PG — managed RAG service](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/what-is-rag-service)
- [Qwen-Agent — framework on GitHub](https://github.com/QwenLM/Qwen-Agent)
- [Qwen-Agent docs](https://qwen.readthedocs.io/en/latest/framework/qwen_agent.html)
- [Deploy a Qwen 3 Agentic RAG — DailyDose](https://www.dailydoseofds.com/p/deploy-a-qwen-3-agentic-rag/)
- [Agentic RAG: The 2026 Production Guide (MarsDevs)](https://www.marsdevs.com/guides/agentic-rag-2026-guide)
- [Agentic Medical Graph-RAG (AMG-RAG) — arXiv 2502.13010](https://arxiv.org/abs/2502.13010)
- [MedGraphRAG — Towards Safe Medical LLMs via Graph RAG, arXiv 2408.04187](https://arxiv.org/abs/2408.04187)
- [LazyGraphRAG — Microsoft Research blog](https://www.microsoft.com/en-us/research/blog/lazygraphrag-setting-a-new-standard-for-quality-and-cost/)
- [LazyGraphRAG 700× cheaper — Particula blog](https://particula.tech/blog/lazygraphrag-700x-cheaper-graphrag-knowledge-graphs)
- [KG-RAG with small LLMs on Japanese medical QA — arXiv 2504.10982](https://arxiv.org/html/2504.10982v5)
- [MMedAgent-RL — Qwen2.5-VL multi-agent medical reasoning, arXiv 2506.00555](https://arxiv.org/html/2506.00555v2)
- [MedRoute — RL dynamic specialist routing, arXiv 2604.06180](https://arxiv.org/abs/2604.06180)
- [Boosting Medical Reasoning via Multi-Round Agentic RAG — arXiv 2603.03292](https://arxiv.org/abs/2603.03292)
- [AgenticQwen — dual data flywheels for agentic RL, arXiv 2604.21590](https://arxiv.org/abs/2604.21590)
- [AWS Bedrock multi-agent systems with LangGraph](https://aws.amazon.com/blogs/machine-learning/build-multi-agent-systems-with-langgraph-and-amazon-bedrock/)
- [AWS Bedrock AgentCore — health care agents](https://aws.amazon.com/blogs/machine-learning/building-health-care-agents-using-amazon-bedrock-agentcore/)
- [AWS LangGraph multi-agent medical chatbot sample](https://aws-samples.github.io/amazon-bedrock-samples/agents-and-function-calling/open-source-agents/langgraph/02_medibot_V3_agents/)
- [NCBI E-utilities API access limits](https://support.nlm.nih.gov/knowledgebase/article/KA-05317/en-us)
- [ARMS LLM Trace Explorer](https://www.alibabacloud.com/help/en/arms/application-monitoring/user-guide/llm-trace-explorer)
- [ARMS — monitor LLM applications with the Python agent](http://www.alibabacloud.com/help/en/arms/application-monitoring/user-guide/use-the-arms-agent-for-python-to-monitor-llm-applications)
- [ARMS scenario-based analysis — LLM sessions and token usage](https://www.alibabacloud.com/help/en/arms/application-monitoring/user-guide/llm-scenario-based-analysis)

*Content above is rephrased for compliance with licensing restrictions.*
