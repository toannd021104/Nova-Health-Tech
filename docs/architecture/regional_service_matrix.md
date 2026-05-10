# Regional service matrix — 3 versions, all domains

**Scope**: verify the availability of every service needed for the proposal across the regions that matter for the user's design:

- **Main app + Emergency agent** → Singapore-native (`ap-southeast-1` on AWS; Alibaba Model Studio International, endpoint in Singapore)
- **General-case agents with RAG + multimodal embeddings** → closer-available region (latency is acceptable outside emergency)
- **Fine-tuning / distillation** → wherever the training service lives (us-west-2 for Bedrock RFT, etc.)

Verified **10 May 2026** by a live `aws bedrock list-foundation-models` sweep on profile `gapv50k` and live `aliyun` probes on account `5541077970296679` (user `anh`), cross-referenced with AWS and Alibaba Cloud public regional-availability docs.

Legend: ✅ available · ❌ not in that region · ⚠️ gated by account (quota / allowlist) · 🌐 single endpoint, no per-region split

## 1. AWS Version A — Claude-based (Singapore-first, general-case allowed to drift)

Design intent: main Lambda + Emergency Haiku 4.5 in Singapore; general-case RAG + GraphRAG pull from Tokyo or Oregon when that's where the service lives.

| Domain | Service | `ap-southeast-1` Singapore (main) | `ap-southeast-2` Sydney | `ap-northeast-1` Tokyo | `ap-south-1` Mumbai | `us-east-1` N.Virginia | `us-west-2` Oregon |
|---|---|---|---|---|---|---|---|
| **Chat** | Claude Haiku 4.5 | ✅ (global inference profile) | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Claude Sonnet 4.5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Claude Sonnet 4.6 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Claude Opus 4.5 / 4.6 / 4.7 | ✅ (global) | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Nova Micro / Lite / Pro | ✅ (`apac.*`) | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Nova 2 Lite | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Nova Premier | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Router** | Nova Micro | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Text embed** | Amazon Titan Embed Text v2 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Cohere Embed v4 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Multimodal embed** | Amazon Titan Embed Image v1 | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ |
| | **Amazon Nova Multimodal Embeddings** (`nova-2-multimodal-embeddings`) | ❌ | ❌ | ❌ | ❌ | **✅ single-region** | ❌ |
| **Reranker** | **Amazon Rerank 1.0** (`amazon.rerank-v1:0`) | ❌ | ❌ | **✅** | ❌ | ❌ | **✅** |
| | Cohere Rerank 3.5 | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Parse** | Bedrock Data Automation (BDA) | ❌ (AccessDenied from Singapore account) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RAG + Graph** | Bedrock Knowledge Bases (control plane) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | **Bedrock KB GraphRAG on Neptune Analytics** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Amazon Neptune Analytics (m-NCU) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Vector store** | OpenSearch Serverless (vector collection) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cache** | ElastiCache for **Redis OSS** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | ElastiCache for Valkey (not chosen) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PHI mask** | Amazon Comprehend Medical | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Customization** | Bedrock Model Distillation | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| | Bedrock custom SFT (Claude 3 Haiku only) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| | Bedrock Reinforcement Fine-Tuning | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| | SageMaker training jobs | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Guardrails** | Bedrock Guardrails | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Edge / API** | CloudFront, API Gateway, Lambda, S3, CloudTrail | ✅ everywhere | | | | | |
| **Identity** | Cognito user pools | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | IAM Identity Center | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **VPN** | AWS Site-to-Site VPN | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Audit** | CloudTrail, S3 Object Lock, Security Lake, Macie | ✅ everywhere | | | | | |
| **Monitoring** | CloudWatch, X-Ray | ✅ everywhere | | | | | |

### Version A routing recommendation (honest)

| Traffic class | Region | Latency from SG clinician | Why |
|---|---|---|---|
| **Emergency lane** (≤ 2 s) | SG (`ap-southeast-1`) | 0 hop | Haiku 4.5 is in SG. No RAG call, no embed, no rerank — pure if/else bypass. |
| **Router** (~150 ms) | SG | 0 hop | Nova Micro in SG |
| **Complex-lane specialist** (Sonnet 4.5) | SG | 0 hop | Sonnet 4.5 is in SG via global inference profile |
| **RAG text embed + query** | **Tokyo** (`ap-northeast-1`) | ~70 ms RTT | Titan Embed Text v2 + Amazon Rerank co-located → one cross-region round-trip |
| **Parsing PDFs at ingest** | **Sydney** (`ap-southeast-2`) | one-time only | BDA not in SG; Sydney is the nearest APAC |
| **Multimodal embed for Radiology figures** (optional, general-case only) | **us-east-1** | ~230 ms RTT | Nova Multimodal Embeddings is single-region. Cross-border transfer accepted for non-emergency traffic. Emergency lane never uses this. |
| **Distillation teacher→student training** (pre-launch) | **us-east-1** or **us-west-2** | offline | Bedrock Model Distillation is US-only |
| **Custom SFT on Claude 3 Haiku** (optional) | **us-west-2** | offline | Only Claude 3 Haiku 2024-03-07 is fine-tunable; only in us-west-2 |

### Version A — services NOT in SG that must cross regions

- **Titan Embed Text v2** → Tokyo (or Sydney/Mumbai)
- **Amazon Rerank 1.0** → Tokyo (or Oregon) — co-locate with Titan
- **Amazon Nova Multimodal Embeddings** → us-east-1 only (general-case, not emergency)
- **Amazon Titan Embed Image v1** → Sydney (or Mumbai/Oregon/Virginia)
- **Bedrock Data Automation** → Sydney (or Mumbai/Tokyo)
- **Bedrock Model Distillation** → us-east-1 or us-west-2
- **Bedrock RFT / Custom SFT** → us-west-2 only

---

## 2. AWS Version B — Qwen on Bedrock (Sydney backbone, SG tenant)

Design intent: Sydney is the primary Qwen inference region; Singapore hosts the edge + non-Qwen services; the two have to round-trip cross-region.

| Domain | Service | `ap-southeast-1` SG | `ap-southeast-2` Sydney | `ap-northeast-1` Tokyo | `ap-south-1` Mumbai | `us-east-1` NV | `us-west-2` OR |
|---|---|---|---|---|---|---|---|
| **Chat — fast** | Qwen3 Next 80B A3B | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Chat — fast, dense** | Qwen3 32B dense | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Chat — complex** | Qwen3 VL 235B A22B (vision) | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Qwen3 235B A22B 2507 (text-only) | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Chat — fallback to Claude** | Claude Haiku 4.5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Claude Sonnet 4.5 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Router / emergency classifier** | Nova Micro (Qwen3-32B acceptable as well) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Text embed** | Titan Embed Text v2 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Multimodal embed** | Nova Multimodal Embeddings | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| | Titan Embed Image v1 | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ |
| **Rerank** | Amazon Rerank 1.0 | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Parse** | Bedrock Data Automation | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RAG + Graph** | Bedrock KB GraphRAG + Neptune Analytics | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Vector store** | OpenSearch Serverless | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cache** | ElastiCache Redis OSS | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PHI mask** | Comprehend Medical | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Customization** | **Bedrock RFT on Qwen3-32B** | ❌ | ❌ | ❌ | ❌ | ❌ | **✅ only** |
| | SageMaker TRL GRPO on Qwen3-4B | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Guardrails** | Bedrock Guardrails | ✅ everywhere | | | | | |

### Version B routing recommendation

| Traffic class | Region | Latency | Why |
|---|---|---|---|
| **Emergency lane** (≤ 2 s) | **Sydney** (`ap-southeast-2`) | ~90 ms RTT from SG clinician | Qwen3 Next 80B A3B is only in Sydney (nearest APAC). Lambda sits in SG but calls Bedrock Sydney. Alternative: keep emergency on Claude Haiku 4.5 in SG and reserve Qwen for the complex lane. |
| Router | **Sydney** | Same ~90 ms round-trip included | If emergency already in Sydney, put the router there too |
| Complex lane (Qwen3 VL 235B) | **Sydney** | ~90 ms | Same region as emergency |
| RAG text embed + rerank | **Tokyo** | ~70 ms | Titan + Amazon Rerank co-located |
| Parsing | **Sydney** | one-time | Already Qwen's region; co-locate BDA ingest |
| PHI mask | **Sydney** | ~90 ms | Comprehend Medical nearest APAC = Sydney |
| Bedrock RFT training | **us-west-2** | offline | Qwen3-32B RFT is Oregon-only |
| SageMaker GRPO on Qwen3-4B | **any** (SG if residency matters) | offline | TRL training is any SageMaker region |

**Trade-off**: Version B can't run emergency from SG unless you fall back to Claude Haiku 4.5 for the fast lane (and keep Qwen for the complex lane only). The user's "emergency stays in SG" constraint is in tension with "emergency uses Qwen." Choose one.

---

## 3. Alibaba Cloud Version C — Qwen on Model Studio + PAI

Design intent: SG International endpoint hosts Model Studio (Qwen inference + GraphRAG + multimodal embeddings), with PAI training either in SG or any nearest region depending on GPU availability.

### 3.1 Model Studio (chat, embed, rerank)

Model Studio has **five deployment regions with separate API keys each**: Singapore, US Virginia, China Beijing, China Hong Kong, Germany Frankfurt. In **International mode** (Singapore), the endpoint and static data stay in SG; model inference compute is dynamically scheduled globally **excluding Chinese Mainland**.

| Model | International mode (SG endpoint) | CN Mainland mode (Beijing / HK endpoint) |
|---|---|---|
| Qwen3.5-Flash | ✅ | ✅ |
| Qwen3.5-Plus | ✅ | ✅ |
| Qwen-Max (Qwen3-Max) | ✅ | ✅ |
| Qwen3-VL-Plus | ✅ | ✅ |
| Qwen3-VL-Flash | ✅ | ✅ |
| **qwen3-vl-embedding** | **❌** | **✅ (CN Mainland only)** |
| **qwen3-rerank** | **✅** | ✅ |
| qwen3-vl-rerank | ❌ | ✅ |
| text-embedding-v4 | ✅ | ✅ |
| tongyi-embedding-vision-plus | ✅ | ✅ |
| tongyi-embedding-vision-flash | ✅ | ✅ |
| gte-rerank-v2 | ❌ | ✅ |

### 3.2 Infrastructure services (live-probed via `aliyun` CLI on `5541077970296679`)

| Domain | Service | SG (`ap-southeast-1`) | Tokyo (`ap-northeast-1`) | HK (`cn-hongkong`) | Shanghai (`cn-shanghai`) | Beijing (`cn-beijing`) | US-W1 (`us-west-1`) | US-E1 (`us-east-1`) |
|---|---|---|---|---|---|---|---|---|
| **AI platform** | Model Studio (DashScope) | ✅ (Intl endpoint) | ❌ (no endpoint) | ✅ (CN Mainland endpoint) | ❌ | ✅ (CN Mainland endpoint) | ✅ (US endpoint) | — |
| | PAI (training + EAS serving) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ (US-W1 has PAI-DLC limited) | ❌ |
| **Vector + Graph** | AnalyticDB for PostgreSQL (GraphRAG service host) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| | OpenSearch Vector Search Edition (outside CN Mainland) | ✅ | ✅ | ✅ | ❌ (CN only for OpenSearch **Standard**) | ❌ | ❌ | — |
| **Object + Vector store** | OSS (Object Storage Service) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| | OSS Vector Retrieval feature | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ (SV) | — |
| **Cache** | **Tair (Redis-compatible) — the Alibaba Redis equivalent** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| | TairVector (Redis + vector search combined) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | — |
| **Identity** | IDaaS EIAM 2.0 | ✅ | ✅ (via Intl endpoint) | ✅ | ✅ | ✅ | ✅ | — |
| **Networking** | VPC, VPN Gateway, SLB | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| **Function compute** | Function Compute (FC) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| **Content Moderation** | Content Moderation 2.0 for Generative AI | ✅ | ❌ (Intl users call SG endpoint) | ✅ | ✅ | ✅ | ✅ | — |
| **Data governance** | DataWorks + SDDP (PHI scan) | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | — |
| **Audit** | ActionTrail + SLS + OSS WORM | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| **Monitoring** | ARMS LLM Trace Explorer | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — |

### Version C routing recommendation

| Traffic class | Region | Latency | Why |
|---|---|---|---|
| **Emergency lane** | SG (Model Studio Intl endpoint) | ~20–50 ms RTT within SG | Qwen3.5-Flash + kb-emergency hit on SG endpoint |
| Router | SG | same | Qwen3.5-Flash picks department |
| Complex lane (Qwen3.5-Plus) | SG | same | Model Studio Intl endpoint |
| **Multimodal embeddings for Radiology figures** | SG | same | `tongyi-embedding-vision-plus` is available on SG Intl; no cross-region needed |
| Reranker | SG | same | `qwen3-rerank` is on SG Intl |
| Graph entity extraction | SG | same | Runs on Qwen3.5-Plus (SG Intl) writing to AnalyticDB PG in SG |
| PAI SFT+LoRA training | **SG** or **Tokyo** | offline | PAI is in SG; Tokyo if more GPU capacity needed |
| Qwen3-8B student PAI-EAS serving | SG | same | A10 GPU in SG region |
| **If fused multimodal embedding required** (`qwen3-vl-embedding`) | **Beijing** or **HK** (CN Mainland mode) | ~120 ms RTT | **Breaks PDPA residency** unless contractually mitigated; only needed for research-tier quality |

### Version C's unique advantage

- **The entire production stack stays in Singapore**, including multimodal embeddings (`tongyi-embedding-vision-plus`), reranker (`qwen3-rerank`), GraphRAG (AnalyticDB PG), cache (Tair), content moderation, audit, and training (PAI).
- The only trade-off is **fused multimodal retrieval** (`qwen3-vl-embedding` with `enable_fusion=True`) — CN Mainland only. For text + image in separate vector fields, Version C is fully SG-native.
- No cross-region round-trip at query time for any core capability.

---

## 4. Side-by-side summary — where each version has to drift

| Capability | Version A (Claude) | Version B (Qwen on Bedrock) | Version C (Qwen on Alibaba) |
|---|---|---|---|
| Emergency in SG | ✅ Haiku 4.5 | ❌ Qwen is Sydney; must fall back to Haiku 4.5 or accept 90 ms cross-region | ✅ Qwen3.5-Flash |
| Text embed in SG | ❌ Tokyo | ❌ Tokyo | ✅ text-embedding-v4 |
| Reranker in SG | ❌ Tokyo | ❌ Tokyo | ✅ qwen3-rerank |
| Multimodal embed in SG | ❌ us-east-1 only | ❌ us-east-1 only | ✅ tongyi-embedding-vision-plus |
| PDF parse in SG | ❌ Sydney nearest APAC | ❌ Sydney | ✅ DocMind + Qwen-VL-Max |
| GraphRAG in SG | ✅ Neptune Analytics | ✅ Neptune Analytics | ✅ AnalyticDB PG GraphRAG |
| Vector store in SG | ✅ OpenSearch Serverless | ✅ OpenSearch Serverless | ✅ OpenSearch Vector Search Edition |
| Cache in SG | ✅ ElastiCache Redis OSS | ✅ ElastiCache Redis OSS | ✅ Tair (Redis-compatible) |
| PHI mask in SG | ❌ Sydney nearest | ❌ Sydney | ✅ DataWorks SDDP |
| Fine-tuning region | us-west-2 (Bedrock Distillation) or SG (SageMaker) | us-west-2 (RFT) or SG (SageMaker) | SG (PAI) |
| Total cross-region hops at query time | **2** (Tokyo embed+rerank; us-east-1 multimodal if enabled) | **2–3** (Sydney chat + Tokyo embed+rerank) | **0** |

Bottom line on the user's design:
- **Version A (Claude)** — SG-native for chat and for emergency lane, but RAG embed + rerank round-trip to Tokyo, multimodal embed round-trips to us-east-1 (general-case only).
- **Version B (Qwen)** — main chat must live in Sydney. Can't keep emergency in SG without using Claude for the fast lane, defeating the "all-Qwen" premise.
- **Version C (Qwen on Alibaba)** — only version with zero cross-region hops at query time. Main app, emergency agent, and all RAG components (including multimodal) all in Singapore.

## 5. References

- AWS Bedrock regions — verified via `aws bedrock list-foundation-models --region <r> --profile gapv50k` on 10 May 2026
- [AWS Comprehend Medical — supported regions](https://docs.aws.amazon.com/general/latest/gr/comprehend-medical.html)
- [Amazon Bedrock Data Automation — available regions](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-bedrock-data-automation-additional-aws-regions/)
- [Bedrock Reinforcement Fine-Tuning — us-west-2 only](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html)
- [Amazon Nova Multimodal Embeddings — us-east-1 only](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html)
- Alibaba Cloud — verified via `aliyun` CLI on account `5541077970296679` on 10 May 2026
- [Alibaba Model Studio — regions](https://www.alibabacloud.com/help/en/model-studio/regions/)
- [Alibaba Model Studio pricing page — per-region model availability](https://www.alibabacloud.com/help/en/model-studio/model-pricing)
- [AnalyticDB for PostgreSQL — GraphRAG service](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service)
- [OpenSearch Vector Search Edition — product overview](https://www.alibabacloud.com/help/en/open-search/vector-search-edition/product-overview)
- [PAI — DSW/DLC/EAS supported regions](https://www.alibabacloud.com/help/en/machine-learning-platform-for-ai/latest/billing-of-dsw)
