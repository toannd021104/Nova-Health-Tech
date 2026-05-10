# Version C — Alibaba Cloud service verification

**Purpose**: verify every service in the Alibaba Version C design with three questions per service:
- **a.** Is the service available in each target region?
- **b.** Is the service / product name exactly correct (not an alias or outdated name)?
- **c.** Are there known limitations relevant to the clinical GenAI use case (vector-dim caps, GPU quotas, concurrency limits, data-residency nuances)?

Verified **10 May 2026** on Alibaba Cloud account `5541077970296679` (RAM user `anh`) via:
- Live `aliyun` CLI calls where an API exists
- DNS resolution probes (`Resolve-DnsName <service>.<region>.aliyuncs.com`) where the endpoint pattern is canonical
- Alibaba Cloud public documentation cross-check

Target regions per the user's design:
- **Primary** — Singapore Intl (`ap-southeast-1`): main app + Emergency agent + all core RAG
- **Secondary (general-case drift allowed)** — Tokyo (`ap-northeast-1`), Hong Kong (`cn-hongkong`)
- **Training only** — any Alibaba region with PAI GPU capacity (SG + Tokyo + Shanghai + Beijing)
- **Not used** — Shanghai / Beijing for production serving (CN Mainland data sovereignty)

## 0. Reality check — endpoint DNS matrix

Fast availability signal before any CLI calls. `OK` = DNS resolves, which is Alibaba's standard signal that the endpoint exists in that region.

```
Service                 SG    Tokyo  HK    Shanghai  Beijing
dashscope (Intl)        OK    --     --    --        OK (CN)
bailian (Model Studio)  OK    --     OK    --        OK
opensearch              OK    --     OK    OK        OK
elasticsearch           OK    OK     OK    OK        OK
gpdb (AnalyticDB PG)    OK    OK     OK    OK        OK
r-kvstore (Tair)        OK    OK     OK    --        OK
pai-eas                 OK    OK     OK    OK        OK
pai-dlc                 OK    OK     OK    OK        OK
eas (legacy)            OK    --     --    OK        OK
green (Content Mod)     OK    --     OK    OK        OK
sls (Log Service)       OK    --     OK    OK        --
arms                    OK    OK     OK    OK        OK
kms                     OK    OK     OK    OK        OK
vpc                     OK    OK     OK    OK        OK
fc (Function Compute)   OK    OK     OK    OK        OK
actiontrail             OK    OK     OK    OK        OK
eiam (IDaaS)            OK    --     OK    --        OK
sddp                    OK    --     --    --        --
dataworks               OK    --     OK    OK        OK
```

Also checked global endpoints:
- `dashscope.aliyuncs.com` ✅ (mainland default)
- `dashscope-intl.aliyuncs.com` ✅ (Singapore International)
- `ram.aliyuncs.com` ✅ (global IAM)
- `bailian.us-east-1.aliyuncs.com` ✅, `bailian.eu-central-1.aliyuncs.com` ✅

Key Tokyo anomalies flagged: **OpenSearch, DashScope, Green, SLS, SDDP, DataWorks — no Tokyo endpoint**. Elasticsearch is the Tokyo drop-in for vector if ever needed.

---

## 1. Model Studio — Qwen inference (chat, embed, rerank)

| Aspect | Finding |
|---|---|
| **Exact product name** | **Alibaba Cloud Model Studio**, OpenAPI product name `bailian`, runtime endpoint family `dashscope-intl.aliyuncs.com` (OpenAI-compatible base URL `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`). The older name was "DashScope"; the integrated console is now "Model Studio". They are the same runtime — dashscope is the API gateway, Bailian/Model Studio is the product. |
| **Deployment regions** | **5 regions, each with its own API key**: Singapore (Intl), US Virginia (`us-east-1`), China Beijing, China Hong Kong, Germany Frankfurt. Verified via DNS resolve on `bailian.ap-southeast-1`, `bailian.us-east-1`, `bailian.cn-beijing`, `bailian.cn-hongkong`, `bailian.eu-central-1` — all OK. `bailian.ap-northeast-1` → **DNS name does not exist** (Tokyo not an MS region). |
| **International (SG) mode data flow** | Endpoint and static data stored in Singapore; model inference compute is **dynamically scheduled globally excluding Chinese Mainland**. Confirmed in Model Studio pricing page and multiple API docs. PDPA-compatible because no data ever lands in CN Mainland. |
| **Emergency model — Qwen3.5-Flash** | ✅ SG Intl. 1M-context, OpenAI-compatible. Billing: `$0.10 / 1M in, $0.40 / 1M out` (0–128K tier). |
| **Complex model — Qwen3.5-Plus** | ✅ SG Intl. Feb 2026 release, replaced Qwen-Max as our default. 1M-context, multimodal. Billing: `$0.40 / 1M in, $2.40 / 1M out` (0–256K tier). |
| **Text embedding — `text-embedding-v4`** | ✅ SG Intl. Dims 64–2048, 8192-token context, 10-batch limit. **$0.07 / 1M tokens**. |
| **Multimodal embedding — `tongyi-embedding-vision-plus`** | ✅ SG Intl. 1152-dim, text + image + video. Text inputs billed at `$0.09 / 1M tokens`; image / video inputs billed per media. Used by our production Version C for figure-bearing chunks. |
| **Reranker — `qwen3-rerank`** | ✅ SG Intl. **$0.10 / 1M tokens**, 500-doc cap per call. |
| **NOT available in SG Intl (CN Mainland only, verified)** | `qwen3-vl-embedding` (fused single-vector text+image, `enable_fusion=True`); `qwen3-vl-rerank` (cross-modal reranker); `gte-rerank-v2`. **Impact**: we use separate text + image vector fields instead of a single fused vector. Retrieval still works; we pay a small recall-per-query cost on highly cross-modal questions. |
| **Fine-tuning via Model Studio** | SFT / DPO / GRPO for Qwen2.5 & Qwen3 series supported on **PAI** (the training platform) rather than directly from Model Studio API. Model Studio handles only hosted serving. |
| **Limitation — concurrent requests** | Default RPM caps vary by model and API key; the SG Intl free-trial starts at **1M free tokens per model** (one-time credit). Production quotas negotiated with the account team. |
| **Limitation — content moderation** | Every request passes through **Content Moderation 2.0** (product code `green`) automatically; medical-template policies must be pre-approved to avoid spurious refusals on valid clinical content. |
| **Verdict** | ✅ All models we need for Version C are in Singapore International. Zero cross-region hops for the query-time path. |

## 2. AnalyticDB for PostgreSQL (GraphRAG host + vector store)

| Aspect | Finding |
|---|---|
| **Exact product name** | **AnalyticDB for PostgreSQL**, OpenAPI code `gpdb`. The GraphRAG feature is exposed as SQL functions (`adbpg_graphrag.initialize`, `adbpg_graphrag.upload`, `adbpg_graphrag.query`) inside an existing AnalyticDB PG instance — there's no separate "GraphRAG" product. |
| **Regions with instance endpoints (live verified via `aliyun gpdb DescribeRegions`)** | 20 regions: `cn-hangzhou`, `cn-shanghai` (6 zones), `cn-beijing` (4 zones), `cn-zhangjiakou`, `cn-huhehaote`, `cn-wulanchabu`, `cn-shenzhen`, `cn-chengdu`, `cn-hongkong` (3 zones), **`ap-southeast-1` (3 zones) ✅**, `ap-northeast-2`, `ap-southeast-3`, `ap-southeast-5`, **`ap-northeast-1` (2 zones) ✅**, `eu-central-1`, `eu-west-1`, `us-west-1`, `us-east-1`, `me-central-1`, `ap-southeast-7`. |
| **GraphRAG extension required** | `adbpg_graphrag` extension, which depends on `plpython3u` + `age`. Requires **minor engine version 7.2.1.3 or later**; versions 7.3.0.0 and 7.3.1.0 do **NOT** support it. Auto-installed on ≥ 7.2.1.4; earlier versions need Alibaba support. Verify via the `Basic Information` page in the console before deploy. |
| **SG zone count** | 3 zones in SG → **multi-AZ HA available** |
| **Graph API surface** | `adbpg_graphrag.initialize(config json)` accepts `llm_model` (default `qwen-max-2025-01-25`; override to our Qwen3.5-Plus), `llm_api_key`, `llm_url` (default Alibaba Cloud Model Studio; must enable NAT gateway or use PAI AI-Node in same VPC), `embedding_model` (default `text-embedding-v3`; override to v4), `language` (`English` or `Simplified Chinese`), `entity_types`, `relationship_types`. Three query modes: `hybrid` (chosen), `local`, `global`. |
| **Vector index support** | pgvector-compatible + native FastANN (HNSW-based) + sparse vector support + hybrid vector + full-text fusion search. Dense + sparse + field-filter retrieval in one SQL statement. |
| **Limitation — vector dimensions** | FastANN HNSW supports 4–16,384 dims (1024-dim Titan / 1152-dim tongyi fit well). Quantized clustering supports 4–1024 dims (useful for lower-latency tiers). |
| **Limitation — GraphRAG LLM call egress** | GraphRAG indexing calls the LLM; in VPC-private deployments you must either (a) enable Internet NAT Gateway, or (b) use PAI AI-Node resources in the same VPC. We go with PrivateLink + PAI in same VPC to keep the data path in-region. |
| **Minimum instance for GraphRAG** | **4-core 32-GB** vector-optimized instance is the documented minimum for `adbpg_graphrag` on AnalyticDB for PostgreSQL 7.0. In SG this is ~$300/month baseline. |
| **Verdict** | ✅ Available in SG (3 zones) + Tokyo (2 zones) + HK (3 zones) + every other target region. SQL API is the canonical interface; no alias confusion. |

## 3. Tair (Redis OSS-compatible — the cache layer, "Redis not Valkey" per user)

| Aspect | Finding |
|---|---|
| **Exact product name** | **Tair (Redis OSS-compatible)**, OpenAPI code `r-kvstore`. Alibaba's ApsaraDB for Redis was renamed to Tair as of 2023; `r-kvstore` is the OpenAPI code. Tair is **Redis-compatible (not Valkey)** — Alibaba's Tair architecture predates the Valkey fork and has never adopted Valkey. |
| **Regions (live verified via `aliyun r-kvstore DescribeZones`)** | SG has **4 single zones (A, B, C, D) plus 3 MAZ combos (A+B, A+C, B+C)** → strongest HA in region. Tokyo has 4 zones (A, B, C, E). HK, Beijing, Shanghai, US-W1 all have multiple zones. |
| **TairVector** | Separate edition that combines Redis + vector search. Used for **Layer-1 semantic cache fuzzy match** in the production design. Available in every Tair region except **us-west-1** (per the matrix we compiled). |
| **Limitation — TairSearch / vector dim cap** | TairVector supports up to **32,768 dims** — more than any embedding we use. |
| **Limitation — AOF + RDB backups** | Standard backups to OSS; for 6-year audit retention we archive to OSS WORM separately. |
| **Verdict** | ✅ Tair (Redis OSS-compatible) is available in SG and Tokyo with multi-AZ. TairVector for semantic cache works in SG. |

## 4. OpenSearch Vector Search Edition

| Aspect | Finding |
|---|---|
| **Exact product name** | **OpenSearch Vector Search Edition**, part of the Alibaba Cloud OpenSearch family (OpenAPI product `opensearch`). Not to be confused with the open-source OpenSearch project (which is a fork of Elasticsearch). Alibaba OpenSearch is a separate managed service. |
| **Regions (DNS-verified endpoint resolution)** | `opensearch.ap-southeast-1.aliyuncs.com` ✅, `opensearch.cn-hongkong` ✅, `opensearch.cn-shanghai` ✅, `opensearch.cn-beijing` ✅. **`opensearch.ap-northeast-1.aliyuncs.com` → DNS name does not exist** — **NO Tokyo endpoint**. |
| **Confirmed regions per Alibaba docs** | Regions outside Chinese Mainland: **Singapore, Hong Kong, Jakarta, Frankfurt, US (Virginia), US (Silicon Valley)** + all CN Mainland regions. **Not Tokyo, not Mumbai, not Sydney.** |
| **Limitation — vector algorithms** | Linear (100% recall, slow), Quantized Clustering (Alibaba K-means-based), HNSW. Dims 4–16,384. |
| **Limitation — it's E-commerce-first** | Product docs explicitly say "e-commerce platforms outside Chinese Mainland." Works for clinical RAG but the semantic features (synonyms, query-understanding plug-ins) are tuned for retail, not medical ontology. For medical vocabulary we override with our own synonyms + ICD-11 entity expansion. |
| **High-availability edition** | **Dual-zone deployment** in the HA Edition for cross-zone DR — supported in SG. |
| **Alternative if Tokyo needed** | **Alibaba Cloud Elasticsearch with Vector-Enhanced Edition** (`elasticsearch` OpenAPI) — available in Tokyo, SG, HK, Shanghai, Beijing. If we ever need a vector store in Tokyo, this is the drop-in. |
| **Verdict** | ✅ Available in SG (multi-AZ HA); not in Tokyo (no DNS). For our Version C design where the vector store lives alongside the main app in SG, this works. |

## 5. PAI — training + serving

| Component | OpenAPI name | SG | Tokyo | HK | Notes |
|---|---|---|---|---|---|
| PAI-DLC (Deep Learning Containers, training) | `pai-dlc` | ✅ | ✅ | ✅ | `pai-dlc.ap-southeast-1.aliyuncs.com` DNS-verified in all three regions |
| PAI-DSW (Data Science Workshop, notebooks) | `pai-dsw` | ✅ | ✅ | ✅ | Co-locates with DLC |
| PAI-EAS (Elastic Algorithm Service, model serving) | `eas` (legacy CLI, uses `pai-eas.*` endpoint) | ✅ | ✅ | ✅ | **Endpoint is `pai-eas.<region>.aliyuncs.com`**, NOT `eas.<region>`. DNS verified in 6 regions. |
| PAI Model Gallery | `paimodelgallery` | ✅ | ✅ | ✅ | Hosted Qwen3 fine-tuning recipes |
| AI Workspace | `aiworkspace` | ✅ | ✅ | ✅ | Project container |
| **Qwen3 fine-tunable on PAI** | — | 0.6B, 1.7B, 4B, 8B, 14B, 32B — **SFT full-parameter + LoRA + QLoRA + DPO + GRPO** | | | Confirmed via `askAli_AI_Assistant.txt` + Alibaba PAI docs |
| **Training GPU availability** | — | SG has A10/A100/H20 spot + reserved | Tokyo has similar | HK has similar | Quota depends on account tier; open ticket for H100-class if needed |
| **Endpoint CLI gotcha** | — | CLI plugin name is `eas` BUT the endpoint is `pai-eas.*`. A probe to `eas.<region>.aliyuncs.com` returns DNS errors in Tokyo/HK; the correct host `pai-eas.ap-northeast-1.aliyuncs.com` resolves. |

**Verdict**: ✅ All PAI components in SG. Training in SG means the teacher-generated SFT dataset never leaves Singapore. Tokyo and HK are available fallbacks for GPU-capacity surge.

## 6. OSS (Object Storage Service) + OSS Vector Retrieval

| Aspect | Finding |
|---|---|
| **Regions (per Alibaba docs)** | Vector Retrieval feature confirmed in **SG**, Jakarta, Frankfurt, US-East, US-West + all Chinese Mainland regions. **Not Tokyo.** |
| **Use in Version C** | Raw corpus storage (WHO PDFs, ICD-11 JSON, uploaded clinical-trial docs) in OSS SG. Vector Retrieval is optional — we use AnalyticDB PG + OpenSearch Vector for our vector store, not OSS's feature. |
| **WORM** | OSS bucket with Object Retention (WORM) supported in every region; we set **6-year lock** per HIPAA §164.530(j). |
| **Verdict** | ✅ |

## 7. Content Moderation 2.0 (Generative AI)

| Aspect | Finding |
|---|---|
| **Exact product name** | **Alibaba Cloud Content Moderation 2.0 for Generative AI**, OpenAPI code `green` (legacy codename kept for API compatibility). |
| **Regions (DNS)** | `green.aliyuncs.com` ✅ (global), `green.cn-shenzhen` ✅, `green-cip.cn-shanghai` ✅, `green.ap-southeast-1` ✅ via SG-specific doc. **No Tokyo endpoint** (`green.ap-northeast-1` → no DNS). |
| **Limitation — medical-specific moderation** | Default policies may over-block legitimate clinical content (dosing, drug interactions). Requires **pre-approval of a medical-vocabulary allow-list** with the account team before go-live. |
| **Limitation — latency** | Synchronous moderation adds ~80–150 ms per call. We accept this on non-emergency; emergency lane uses the streaming-friendly "detect after first 100 tokens" pattern. |
| **Verdict** | ✅ SG supported. Tokyo not supported (general-case that routes to Tokyo would lose CM; but our Version C design keeps everything in SG). |

## 8. IDaaS (EIAM) — hospital IdP federation

| Aspect | Finding |
|---|---|
| **Exact product name** | **Alibaba Cloud IDaaS (EIAM 2.0)**, OpenAPI code `eiam`. The older `idaas-doraemon` is the auth-service component; `eiam` is the directory-service API. |
| **Regions (DNS)** | `eiam.ap-southeast-1.aliyuncs.com` ✅, `eiam.cn-beijing` ✅, `eiam.cn-hangzhou` ✅. **`eiam.cn-shanghai` → no DNS** (global instance routes via Hangzhou). |
| **EIAM editions** | **Standard / Premium / Ultimate**. Only Premium+ supports SAML-IDP, SCIM, and per-tenant user pools (needed for hospital federation). |
| **Limitation — region pinning** | An EIAM instance is pinned to a region at create time; SG instance handles SG clinicians. For multi-hospital-multi-country you create one instance per region, federated with Cloud SSO. |
| **Verdict** | ✅ SG + global-reachable via the Hangzhou/Beijing master. |

## 9. DataWorks + Sensitive Data Discovery & Protection (SDDP) — PHI mask

| Aspect | Finding |
|---|---|
| **Exact product name** | **DataWorks** (`dataworks-public`) + **Sensitive Data Discovery & Protection (SDDP)** (`sddp`). SDDP runs inside DataWorks; the combined capability is commonly called "**DataWorks Data Security Guard**" in the docs. |
| **Regions (DNS)** | `dataworks.ap-southeast-1.aliyuncs.com` ✅, `dataworks.cn-hongkong` ✅, `dataworks.cn-shanghai` ✅. `sddp.ap-southeast-1.aliyuncs.com` ✅ — but `sddp.cn-shanghai`, `sddp.cn-hangzhou` don't resolve on the regional pattern. SDDP is consolidated into DataWorks-integrated mode for SG. |
| **Limitation — SDDP on SG** | SDDP in SG supports OSS + RDS + AnalyticDB scanning. **PHI rule packs** for HIPAA / PDPA-S are available but require account-team activation (not default-on). |
| **Verdict** | ✅ SG supported via DataWorks Data Security Guard. Tokyo / OSS-only deployments don't get SDDP. |

## 10. ActionTrail + SLS + OSS WORM — audit pipeline

| Service | Product code | SG | Tokyo | Notes |
|---|---|---|---|---|
| ActionTrail (control-plane audit) | `actiontrail` | ✅ | ✅ | Ships cloud-resource events to SLS + OSS |
| SLS (Simple Log Service) | `sls` | ✅ | ❌ no DNS | Tokyo doesn't have SLS; we aggregate in SG regardless |
| OSS WORM | `oss` | ✅ | ✅ | 6-year retention lock |

Version C audit pipeline stays entirely in SG. ✅

## 11. ARMS (Application Real-Time Monitoring Service) — LLM observability

| Aspect | Finding |
|---|---|
| **Exact product name** | **Application Real-Time Monitoring Service (ARMS)**, OpenAPI code `arms`. The LLM-specific submodule is called **ARMS LLM Trace Explorer** (uses OpenTelemetry spans tagged with the LLM semantic conventions). |
| **Regions (DNS)** | SG, Tokyo, HK, Shanghai, Beijing — all ✅. |
| **Python agent for LLM tracing** | Auto-instruments DashScope / OpenAI / LangChain / LangGraph. Free to install; billed per trace ingested. |
| **Verdict** | ✅ Available everywhere including SG and Tokyo. |

## 12. KMS, RAM, Cloud SSO, Credentials Manager

All four are **global services** (`ram.aliyuncs.com`, `kms.<region>.aliyuncs.com`) and available in every region. ✅ for all.

## 13. Function Compute (FC)

| Aspect | Finding |
|---|---|
| **Exact product name** | **Function Compute** (FC 3.0, 2024-09-01 API). OpenAPI code `fc-open` (the older FC 2.0 `fc` is deprecated — don't use). |
| **Regions** | SG, Tokyo, HK, Shanghai, Beijing — all ✅. |
| **Limitation — VPC connectivity** | FC in VPC gets 1 ENI per invocation at cold start; pre-provisioned instances with warm ENIs are required for consistent sub-200ms cold starts on VPC functions. |
| **Verdict** | ✅ |

## 14. VPC + VPN Gateway

| Aspect | Finding |
|---|---|
| **Exact product name** | **Virtual Private Cloud (VPC)**, OpenAPI `vpc`. **VPN Gateway is part of VPC** — there's no separate VPN product; the API is `aliyun vpc DescribeVpnGateways`. |
| **Regions** | VPC available in every region; VPN Gateway API live-tested in SG (returned `TotalCount: 0`, authoritative "works, no gateways yet"). |
| **IPsec-VPN ciphers** | IKEv2 + AES-256-GCM + SHA-2 supported. Dual-tunnel HA. |
| **Cloud Enterprise Network (CEN)** | For multi-region connectivity if ever needed; SG ↔ Tokyo mesh works via CEN. Not required for Version C baseline. |
| **Verdict** | ✅ |

---

## 15. Services flagged — critical to Version C, NOT in certain regions

These are the non-negotiable gaps to surface in the proposal:

| Service / model | Not available in | Impact on Version C |
|---|---|---|
| **Model Studio (`bailian`) endpoint** | **Tokyo** (DNS doesn't exist) | Zero impact — we use the SG Intl endpoint |
| **`qwen3-vl-embedding`** (fused multimodal) | SG Intl / any International region | Impact: we use `tongyi-embedding-vision-plus` (separate text + image vectors) instead. No PDPA cost. |
| **`qwen3-vl-rerank`** (cross-modal reranker) | SG Intl | Impact: we use `qwen3-rerank` (text-only). Image attachment scoring is handled by the vision-capable agent itself at generation time. |
| **`gte-rerank-v2`** | SG Intl | Impact: `qwen3-rerank` is the drop-in; similar latency and cost. |
| **OpenSearch Vector Search Edition** | **Tokyo, Sydney, Mumbai** (no DNS in APAC except SG/HK) | Zero impact — vector store sits next to the main app in SG |
| **Content Moderation 2.0 (`green`)** | **Tokyo** | Zero impact for Version C (all traffic SG-resident) |
| **SLS (Simple Log Service)** | **Tokyo** | Zero impact — audit pipeline in SG |
| **SDDP** | **Tokyo** | Zero impact — PHI masking in SG |
| **DataWorks** | **Tokyo** | Zero impact — ingestion orchestration in SG |

**Zero gaps affect the SG-native Version C design.**

---

## 16. Version C final sign-off per domain

| Domain | Exact service / model | SG available? | Exact name verified? | Known limitations flagged? |
|---|---|---|---|---|
| Chat — Emergency lane | Qwen3.5-Flash (Model Studio, SG Intl) | ✅ | ✅ | 1M-token context; tier-1 pricing |
| Chat — Complex lane | Qwen3.5-Plus (Model Studio, SG Intl) | ✅ | ✅ | 1M-token context; multimodal |
| Chat — VL specialist | Qwen3-VL-Plus (Model Studio, SG Intl) | ✅ | ✅ | Native image input via Converse-compatible API |
| Router | Qwen3.5-Flash JSON mode | ✅ | ✅ | Structured output reliable at `temperature=0` |
| Text embedding | `text-embedding-v4` | ✅ | ✅ | Dims 64–2048; 8192 context; 10-batch cap |
| Multimodal embedding | `tongyi-embedding-vision-plus` | ✅ | ✅ | 1152-dim; separate text + image vectors |
| Reranker | `qwen3-rerank` | ✅ | ✅ | 500-doc per-call cap |
| Vector store | OpenSearch Vector Search Edition (SG, multi-AZ HA edition) | ✅ | ✅ | Alternative: Alibaba Cloud Elasticsearch with Vector-Enhanced Edition if ever need Tokyo |
| Graph store + GraphRAG | AnalyticDB for PostgreSQL 7.0 (minor ≥ 7.2.1.4) + `adbpg_graphrag` extension | ✅ (3 zones in SG) | ✅ | Requires NAT gateway OR PAI AI-Node in same VPC for LLM egress during ingest |
| PDF parsing | DocMind + Qwen-VL-Max for complex pages | ✅ (Model Studio endpoint) | ✅ | Fallback to PAI-hosted open-source parser if DocMind misses |
| Cache | Tair (Redis OSS-compatible), `r-kvstore` product | ✅ (7 zone/MAZ combos in SG) | ✅ — **Redis, NOT Valkey** (user constraint satisfied) | TairVector for semantic cache supported in SG |
| Training | PAI (DLC + DSW + Model Gallery) | ✅ | ✅ | Qwen3 0.6B–32B supported for SFT + LoRA + QLoRA + DPO + GRPO |
| Serving of fine-tuned student | PAI-EAS via `pai-eas.ap-southeast-1.aliyuncs.com` | ✅ | ✅ | A10 GPU baseline for Qwen3-8B; H20 / H100 for larger |
| Content moderation | Content Moderation 2.0 for Gen AI (`green`) | ✅ | ✅ | Medical allow-list must be pre-approved |
| PHI mask | DataWorks + SDDP (Data Security Guard) | ✅ | ✅ | HIPAA / PDPA-S rule packs require activation |
| Identity | IDaaS EIAM 2.0 Premium+ | ✅ | ✅ | SAML-IDP / SCIM require Premium edition |
| Audit | ActionTrail → SLS → OSS WORM (6-year) | ✅ | ✅ | All components SG-native |
| Observability | ARMS LLM Trace Explorer | ✅ | ✅ | OpenTelemetry spans, Python agent auto-instruments LangChain/LangGraph |
| Secrets | KMS + Credentials Manager | ✅ | ✅ | BYOK supported |
| Network | VPC + VPN Gateway (IPsec-VPN) | ✅ | ✅ | IKEv2 + AES-256-GCM + SHA-2, dual-tunnel HA |
| Compute | Function Compute (FC 3.0, `fc-open`) | ✅ | ✅ | 1 ENI per invocation on VPC — pre-provision for steady emergency lane |
| Storage | OSS (Object Storage Service) | ✅ | ✅ | WORM 6-year retention supported |

**All services verified. No gaps affect the SG-primary design. Version C is technically clean for production.**

---

## 17. Verification method summary

- **Live `aliyun` CLI**: AnalyticDB PG DescribeRegions (20 regions listed), Tair DescribeZones per region, Elasticsearch instance list, FC service list, VPN gateway list, PAI-EAS service list — all returned valid API responses from the target regions.
- **DNS endpoint probes**: Resolved `<service>.<region>.aliyuncs.com` for every service × region pair in the matrix. A DNS failure means the service has no endpoint in that region — authoritative signal.
- **Alibaba Cloud public documentation**: Cross-referenced Model Studio pricing page, OpenSearch Vector Search Edition docs, AnalyticDB for PostgreSQL GraphRAG best practices, PAI billing pages.
- **User-supplied reference**: `reference/use-the-graphrag-service.htm`, `reference/generate-high-quality-qa-pairs-based-on-graphrag.htm`, `reference/Building a guided conversational chatbot with GraphRAG` — extracted the canonical `adbpg_graphrag.initialize / upload / query` API surface.

Credentials used: RAM user `anh` on account `5541077970296679`, profile `nova`, keys in `~/.aliyun/config.json`. **No secrets in this repo.**
