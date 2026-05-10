# Regional service availability — live-verified matrix

Verified **10 May 2026** via `aws bedrock list-foundation-models` on profile `gapv50k`, `aliyun` CLI on account `5541077970296679` (RAM user `anh`), and DNS endpoint probes. Public documentation cross-referenced in the references below.

Legend: ✅ available · ❌ not in that region · ⚠️ gated by account quota / allowlist · 🌐 single endpoint, no per-region split

**Note on "SG Intl" (Alibaba column):** Alibaba Cloud has two consoles — [International site](https://www.alibabacloud.com/) (`alibabacloud.com`, USD billing) and Mainland China site (`aliyun.com`, RMB billing). "SG Intl" = Singapore region (`ap-southeast-1`) accessed through the International site. Some Qwen variants exist only on CN Mainland. All Version C tenants live on the International site. See [`proposals/version_c_alibaba_qwen.md` §1.5](proposals/version_c_alibaba_qwen.md#15-a-note-on-singapore-international--sg-intl) for the full explanation.

---

## 1. AWS — where each service actually lives

Verified sweep across the six regions that matter for the design:

| Domain | Service | `ap-southeast-1` SG | `ap-southeast-2` Sydney | `ap-northeast-1` Tokyo | `ap-south-1` Mumbai | `us-east-1` N.Virginia | `us-west-2` Oregon |
|---|---|---|---|---|---|---|---|
| **Chat** | [Claude Haiku 4.5](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html) | ✅ global | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Claude Sonnet 4.5 / 4.6 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Claude Opus 4.5 / 4.6 / 4.7 | ✅ global | ✅ | ✅ | ✅ | ✅ | ✅ |
| | [Nova Micro / Lite / Pro](https://aws.amazon.com/bedrock/nova/) | ✅ apac.* | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Nova 2 Lite | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Nova Premier | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| | [Qwen3 Next 80B A3B](https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/model-card-qwen-qwen3-next-80b-a3b.html) / VL 235B / 32B / 235B 2507 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Embeddings** | [Amazon Titan Embed Text v2](https://aws.amazon.com/bedrock/titan/) | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | [Cohere Embed v4](https://aws.amazon.com/blogs/aws/cohere-embed-multimodal-embeddings-are-now-available-in-amazon-bedrock/) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | Amazon Titan Embed Image v1 | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ |
| | **[Amazon Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html)** (`nova-2-multimodal-embeddings`) | ❌ | ❌ | ❌ | ❌ | **✅ single-region** | ❌ |
| **Reranker** | [Amazon Rerank 1.0](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html) (`amazon.rerank-v1:0`) | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| | Cohere Rerank 3.5 | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **Parse** | [Bedrock Data Automation (BDA)](https://aws.amazon.com/bedrock/bda/) | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **RAG + Graph** | [Bedrock KB (control plane)](https://aws.amazon.com/bedrock/knowledge-bases/) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | **[Bedrock KB GraphRAG on Neptune Analytics](https://aws.amazon.com/blogs/machine-learning/announcing-general-availability-of-amazon-bedrock-knowledge-bases-graphrag-with-amazon-neptune-analytics/)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | [Amazon Neptune Analytics](https://aws.amazon.com/neptune/features/) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Vector store** | [OpenSearch Serverless (vector)](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector.html) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Cache** | **[ElastiCache for Redis OSS](https://aws.amazon.com/elasticache/redis/)** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PHI mask** | [Amazon Comprehend Medical](https://aws.amazon.com/comprehend/medical/) | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Customization** | [Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html) | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| | [Bedrock custom SFT (Claude 3 Haiku only)](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-fine-tuning.html) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| | [Bedrock Reinforcement Fine-Tuning (Qwen3-32B / gpt-oss-20B)](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html) | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| | [SageMaker training jobs](https://aws.amazon.com/sagemaker/) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Guardrails** | [Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Identity** | [Cognito user pools](https://aws.amazon.com/cognito/) / [IAM Identity Center](https://aws.amazon.com/iam/identity-center/) | ✅ everywhere | | | | | |
| **VPN** | [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Audit** | [CloudTrail](https://aws.amazon.com/cloudtrail/) / [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) / [Security Lake](https://aws.amazon.com/security-lake/) / [Macie](https://aws.amazon.com/macie/) | ✅ everywhere | | | | | |

### AWS — critical callouts

- **Nova Multimodal Embeddings** is the only Amazon multimodal embedding; it's **us-east-1 single-region**. Using from a SG tenant means PDPA-relevant cross-border transfer at ingest.
- **Amazon Rerank 1.0** is Tokyo + Oregon only — if we're SG-native we co-locate with Titan Embed in **Tokyo** to get one round-trip.
- **Bedrock Data Automation** is not in Singapore — our account gets `AccessDeniedException` on SG. Ingestion does its one-time parse in Sydney.
- **Qwen on Bedrock is Sydney-primary in APAC** — Singapore has no Qwen.
- **Bedrock Distillation / RFT / custom SFT are all US-only** — all three fine-tuning paths cross the Pacific during training. Deployed model can be served from any region once trained.

### AWS — Version routing implications

| Traffic class | Version A (Claude) | Version B (Qwen) |
|---|---|---|
| Emergency lane | SG (Haiku 4.5) | Sydney Qwen3 Next 80B (~90 ms from SG) or fallback to Haiku in SG |
| Router | SG (Nova Micro) | Sydney (Qwen3 32B) or SG |
| Complex lane | SG (Sonnet 4.5) | Sydney (Qwen3 VL 235B) |
| Text embed | Tokyo (Titan v2) | Tokyo |
| Rerank | Tokyo (Amazon Rerank) | Tokyo |
| Multimodal embed (general-case only) | us-east-1 (Nova Multimodal) | us-east-1 |
| PDF parse (one-time ingest) | Sydney (BDA) | Sydney |
| Distillation training | us-east-1 / us-west-2 | us-west-2 (RFT) or SG (SageMaker) |

Version B trade-off: can't keep emergency in SG without falling back to Claude Haiku 4.5. Pure "all-Qwen on AWS" requires accepting ~90 ms SG→Sydney cross-region.

---

## 2. Alibaba Cloud — live-probed for Version C

### 2.1 Endpoint DNS matrix (fast availability signal)

`OK` = `<service>.<region>.aliyuncs.com` resolves. Standard Alibaba signal that the endpoint exists in that region.

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

Global endpoints also confirmed: `dashscope-intl.aliyuncs.com` ✅, `ram.aliyuncs.com` ✅, `bailian.us-east-1` ✅, `bailian.eu-central-1` ✅.

**Tokyo anomalies**: Model Studio (bailian), OpenSearch Vector Search Edition, Content Moderation (green), SLS, SDDP, DataWorks have **no Tokyo endpoint**. Elasticsearch is the Tokyo drop-in for vector if ever needed.

### 2.2 [Model Studio](https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio) — chat, embed, rerank

Five deployment regions, each with its own API key: **Singapore (Intl), US Virginia, China Beijing, China Hong Kong, Germany Frankfurt** ([confirmed in docs](https://www.alibabacloud.com/help/en/model-studio/text-generation)).

In International mode, endpoint + static data stay in Singapore; model inference compute is dynamically scheduled globally **excluding Chinese Mainland**. PDPA-compatible.

| Model | SG Intl | CN Mainland (Beijing / HK) |
|---|---|---|
| [Qwen3.5-Flash](https://www.alibabacloud.com/help/en/model-studio/model-pricing) | ✅ | ✅ |
| Qwen3.5-Plus | ✅ | ✅ |
| Qwen3-Max | ✅ | ✅ |
| Qwen3-VL-Plus / Flash | ✅ | ✅ |
| [text-embedding-v4](https://www.alibabacloud.com/help/en/model-studio/text-embedding-v4) | ✅ | ✅ |
| [tongyi-embedding-vision-plus](https://www.alibabacloud.com/help/en/model-studio/multimodal-embeddings) | ✅ | ✅ |
| tongyi-embedding-vision-flash | ✅ | ✅ |
| [qwen3-rerank](https://www.alibabacloud.com/help/en/model-studio/rerank) | ✅ | ✅ |
| **qwen3-vl-embedding** (fused single vector, `enable_fusion=True`) | **❌** | ✅ |
| **qwen3-vl-rerank** (cross-modal) | ❌ | ✅ |
| gte-rerank-v2 | ❌ | ✅ |

**Impact**: Version C uses `tongyi-embedding-vision-plus` for multimodal (separate text + image vectors) instead of the fused `qwen3-vl-embedding`. Retrieval runs two parallel kNN searches and merges at rerank time. No PDPA cost.

### 2.3 Infrastructure services

| Domain | Service | SG | Tokyo | HK | Shanghai | Beijing | US-W1 |
|---|---|---|---|---|---|---|---|
| AI platform | [Model Studio (Bailian)](https://www.alibabacloud.com/help/en/model-studio/what-is-model-studio) | ✅ Intl | ❌ | ✅ CN | ❌ | ✅ CN | ✅ US |
| | [PAI (DLC training + EAS serving + Model Gallery + AI Workspace)](https://www.alibabacloud.com/help/en/pai) | ✅ | ✅ | ✅ | ✅ | ✅ | limited |
| Vector + Graph | **[AnalyticDB PG (GraphRAG host)](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service)** | ✅ 3 zones | ✅ 2 zones | ✅ 3 zones | ✅ 6 zones | ✅ 4 zones | ✅ |
| | [OpenSearch Vector Search Edition](https://www.alibabacloud.com/help/en/open-search/vector-search-edition/product-overview) | ✅ | ❌ | ✅ | — (CN-std only) | — (CN-std only) | ❌ |
| | [Alibaba Cloud Elasticsearch with Vector-Enhanced Edition](https://www.alibabacloud.com/help/en/doc-detail/187127.htm) (Tokyo drop-in) | ✅ | ✅ | ✅ | ✅ | ✅ | — |
| Object + Vector | [OSS](https://www.alibabacloud.com/product/oss) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| | [OSS Vector Retrieval feature](https://www.alibabacloud.com/help/en/oss/user-guide/vector-retrieval) | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ SV |
| Cache | **[Tair (Redis OSS-compatible)](https://www.alibabacloud.com/product/tair)** | ✅ 4 zones + 3 MAZ | ✅ 4 zones | ✅ | ✅ | ✅ | ✅ |
| | [TairVector](https://www.alibabacloud.com/help/en/tair/user-guide/tairvector-overview) (combined Redis + vector) | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| Identity | [IDaaS EIAM 2.0](https://www.alibabacloud.com/help/en/idaas/) | ✅ | — (via Intl master) | ✅ | ✅ | ✅ | ✅ |
| Network | [VPC + VPN Gateway (IPsec)](https://www.alibabacloud.com/help/en/vpn-gateway) + SLB | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Content Moderation | [Content Moderation 2.0 for Gen AI](https://www.alibabacloud.com/product/content-moderation) (`green`) | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Data governance | [DataWorks](https://www.alibabacloud.com/product/dataworks) + [SDDP](https://www.alibabacloud.com/product/sddp) | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ |
| Audit | [ActionTrail](https://www.alibabacloud.com/product/actiontrail) + [SLS](https://www.alibabacloud.com/product/log-service) + OSS WORM | ✅ | partial (no SLS in Tokyo) | ✅ | ✅ | ✅ | ✅ |
| Observability | [ARMS LLM Trace Explorer](https://www.alibabacloud.com/help/en/arms/application-monitoring/user-guide/llm-trace-explorer) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Function compute | [Function Compute (FC 3.0, `fc-open`)](https://www.alibabacloud.com/product/function-compute) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Secrets | [KMS](https://www.alibabacloud.com/product/kms) + [RAM](https://www.alibabacloud.com/product/ram) + Credentials Manager | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

### 2.4 Alibaba product-name gotchas (verified during the CLI sweep)

| Common name | Actual OpenAPI product code | Why it matters |
|---|---|---|
| Model Studio | `bailian` (OpenAPI) + `dashscope-intl` (runtime endpoint) | Two names for the same service — Model Studio is the console, Bailian is the OpenAPI product, DashScope is the API gateway |
| ApsaraDB for Redis | **Tair** / `r-kvstore` (OpenAPI) | Renamed in 2023; `r-kvstore` is the stable product code; Tair is **Redis OSS-compatible, never Valkey** |
| PAI-EAS serving | Endpoint is `pai-eas.<region>.aliyuncs.com` | CLI plugin is `eas` but probing `eas.<region>` fails in Tokyo/HK — always use `pai-eas.*` |
| AnalyticDB PG GraphRAG | `gpdb` product + [`adbpg_graphrag` SQL extension](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service) | There is NO separate "GraphRAG" product — it's a PG extension requiring engine version ≥ 7.2.1.4 |
| Function Compute | `fc-open` (3.0 API) | `fc` is the deprecated 2.0 product; don't use |
| Content Moderation for Gen AI | `green` (OpenAPI code) | Legacy codename kept for API compatibility; console name is "Content Moderation 2.0 for Generative AI" |
| IDaaS EIAM | `eiam` (directory) + `idaas-doraemon` (auth) | Two-part product; hospital SAML federation lives in `eiam` |
| VPN | Under VPC | No separate `vpn` product — `aliyun vpc DescribeVpnGateways` |

### 2.5 Version C — zero cross-region hops

| Traffic class | Region | Latency | Why |
|---|---|---|---|
| Emergency lane | SG (Model Studio Intl) | ~20–50 ms within SG | Qwen3.5-Flash in SG |
| Router | SG | same | Qwen3.5-Flash JSON mode |
| Complex lane | SG | same | Qwen3.5-Plus |
| Multimodal embed (Radiology) | SG | same | `tongyi-embedding-vision-plus` on SG Intl |
| Reranker | SG | same | `qwen3-rerank` on SG Intl |
| Graph extraction | SG | same | Qwen3.5-Plus writing to AnalyticDB PG in SG |
| PAI SFT+LoRA training | SG (or Tokyo if GPU capacity) | offline | PAI in SG |
| Qwen3-8B student PAI-EAS | SG | same | A10 GPU in SG |

**Only Version C has zero cross-region hops at query time.**

---

## 3. Known limitations per Version C service (relevant to clinical GenAI)

| Service | Limitation | Mitigation |
|---|---|---|
| [AnalyticDB PG GraphRAG](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service) | GraphRAG indexing calls the LLM; VPC-private deployments need NAT gateway OR PAI AI-Node in same VPC for LLM egress | Use PrivateLink + PAI in same VPC |
| AnalyticDB PG | `adbpg_graphrag` extension requires minor engine version ≥ 7.2.1.4; versions 7.3.0.0 and 7.3.1.0 do NOT support it | Verify via Basic Information page in console before deploy |
| AnalyticDB PG vector index | HNSW: 4–16,384 dims; Quantized clustering: 4–1024 dims | 1152-dim `tongyi-embedding-vision-plus` fits HNSW |
| AnalyticDB PG minimum for GraphRAG | 4-core 32 GB vector-optimized instance | ~$300/mo baseline in SG |
| Model Studio | Default RPM caps vary by model + API key; SG Intl free-trial = 1M free tokens per model | Production quotas via account team |
| Model Studio | Content Moderation 2.0 auto-gates every request; medical content can trigger false refusals | Pre-approve medical vocabulary allow-list |
| [Tair vector](https://www.alibabacloud.com/help/en/tair/user-guide/tairvector-overview) | Supports up to 32,768 dims | No practical impact — more than any embedding we use |
| [OpenSearch Vector Search Edition](https://www.alibabacloud.com/help/en/open-search/vector-search-edition/product-overview) | Optimized for e-commerce; semantic plug-ins tuned for retail, not medical ontology | Override with custom synonyms + ICD-11 entity expansion |
| OpenSearch HA Edition | Dual-zone deployment supported in SG | Use for cross-zone DR |
| Content Moderation 2.0 | Adds ~80–150 ms per call (synchronous) | Emergency lane uses streaming "detect after first 100 tokens" pattern |
| DataWorks SDDP | HIPAA / PDPA-S rule packs require account-team activation (not default-on) | Open ticket before production PHI scan |
| EIAM | Premium+ edition required for SAML-IDP and SCIM hospital federation; region-pinned at create | One instance per region + Cloud SSO for multi-country |
| [Function Compute](https://www.alibabacloud.com/help/en/functioncompute/product-overview/overview) | 1 ENI per invocation at cold start on VPC | Pre-provision warm instances for consistent < 200 ms emergency cold starts |
| Qwen fine-tunable on PAI | 0.6B / 1.7B / 4B / 8B / 14B / 32B — SFT (full / LoRA / QLoRA), DPO, GRPO | Full range available |

---

## 4. References

- AWS Bedrock per-region verification via `aws bedrock list-foundation-models --region <r> --profile gapv50k` — 10 May 2026
- Alibaba per-region verification via `aliyun` CLI + DNS probes on account `5541077970296679` — 10 May 2026
- [AWS Comprehend Medical — supported regions](https://docs.aws.amazon.com/general/latest/gr/comprehend-medical.html)
- [AWS Bedrock Data Automation — available regions (GA July 2025)](https://aws.amazon.com/about-aws/whats-new/2025/07/amazon-bedrock-data-automation-additional-aws-regions/)
- [Alibaba Cloud global locations](https://www.alibabacloud.com/about/global-locations)
- [Alibaba Model Studio — regions](https://www.alibabacloud.com/help/en/model-studio/regions/)
- [AnalyticDB for PostgreSQL — GraphRAG best practices](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service)
- [Alibaba PAI DSW / DLC / EAS supported regions](https://www.alibabacloud.com/help/en/machine-learning-platform-for-ai/latest/billing-of-dsw)

*Content above is rephrased for compliance with licensing restrictions.*
