# Nova Health Tech Clinical GenAI — Proposal overview

Three production architectures for Nova Health Tech's clinical decision-support assistant. All three hit the same scenario requirements: complex medical Q&A grounded in internal trial reports + WHO guidelines + [WHO ICD-11 API](https://id.who.int/swagger/index.html), ≤ 2 s emergency response, auditable, PDPA / HIPAA / HCSA compliant, with [monthly WHO updates](https://www.who.int/publications) and patient-sensitive internal trial data.

## Three versions at a glance

| | **Version A — AWS + Claude** | **Version B — AWS + Qwen** | **Version C — Alibaba + Qwen** |
|---|---|---|---|
| Primary region | Singapore `ap-southeast-1` | Sydney `ap-southeast-2` Bedrock + SG tenant | Singapore `ap-southeast-1` via Alibaba Cloud International site |
| Fast-lane model | Claude Haiku 4.5 (or Nova Micro) | Qwen3 Next 80B A3B (MoE, 3B active) | Qwen3.5-Flash |
| Complex-lane model | Claude Sonnet 4.5 | Qwen3 VL 235B A22B | Qwen3.5-Plus |
| Student (pre-launch SFT) | Nova Lite via [Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html) | Qwen3-32B via [Bedrock RFT](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html) (us-west-2) | Qwen3-8B on PAI SFT+LoRA+GRPO |
| GraphRAG | [Bedrock KB GraphRAG on Neptune Analytics](https://aws.amazon.com/blogs/machine-learning/announcing-general-availability-of-amazon-bedrock-knowledge-bases-graphrag-with-amazon-neptune-analytics/) | Same | [AnalyticDB PG GraphRAG](https://www.alibabacloud.com/help/en/analyticdb/analyticdb-for-postgresql/user-guide/use-the-graphrag-service) |
| Cache (Layer 1 semantic) | ElastiCache Redis OSS | ElastiCache Redis OSS | Tair (Redis-compatible) |
| Cache (Layer 2 prefix) | [Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/) | ❌ Qwen3 not supported; self-hosted path uses [vLLM APC](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html) | [Qwen Context Cache](https://www.alibabacloud.com/help/en/model-studio/context-cache) (implicit + explicit) |
| Cross-region hops at query time | 2 (Tokyo embed+rerank) | 2–3 (Sydney chat + Tokyo embed+rerank) | **0** |
| Monthly cost (600 k calls, launch-day with student) | ~$4,655–5,655 A1+ / ~$5,765 A2 | ~$3,240 | **~$2,280–3,060** |
| Singapore data residency | ✅ | ⚠️ Sydney; PDPA contract-mitigable | ✅ |

Full cost breakdown lives in each version's proposal doc. Regional-availability truth table lives in [`regional_services.md`](regional_services.md).

## Which version to pick

| Client profile | Recommended version |
|---|---|
| APAC / PDPA-strict hospital, cost-sensitive, open to Alibaba | **Version C** — the only version with zero cross-region hops at query time and the lowest monthly bill |
| US or ANZ hospital with Anthropic brand preference; AWS BAA mandatory | **Version A2** — Haiku 4.5 + Sonnet 4.5, fully SG-native for chat, some embed/rerank cross-region to Tokyo |
| Cost-sensitive AWS client with Nova quality acceptable | **Version A1+** — Nova Micro + Nova Pro, cheapest fully-AWS-SG option |
| Open-weights mandate under AWS BAA; Sydney residency acceptable | **Version B** — all-Qwen on Bedrock + [Bedrock RFT for Qwen3-32B](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html) |

## Common design (identical across all three versions)

These choices are locked in, regardless of version:

- **Primary region: Singapore.** No [Outposts](https://aws.amazon.com/outposts/) / [Direct Connect](https://aws.amazon.com/directconnect/) / [Apsara Stack](https://www.alibabacloud.com/product/apsara-stack). Hospital connectivity uses a **two-plane model**: clinician chat over public HTTPS with TLS 1.3 + IdP federation + per-tenant WAF IP allow-list (hospital whitelists Nova's IP/domain on their egress firewall); bulk-PHI backend flows over Site-to-Site IPsec VPN ([AWS S2S VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html) / [Alibaba VPN Gateway](https://www.alibabacloud.com/help/en/vpn-gateway)) for SharePoint / on-prem FHIR / Upload Portal.
- **Emergency routing: pure if/else on an explicit chat-panel toggle.** No classifier LLM call — saves ~300 ms and makes routing deterministic. Matches [`aws-demo/ec2/app/graph.py`](../aws-demo/ec2/app/graph.py) `_route_next`.
- **Multi-agent topology: 40 clinical departments** mirroring a Vietnamese tertiary hospital structure. UI never exposes the list; a router agent classifies the prompt. Full mapping in [`rag_and_pipelines.md` §Multi-agent topology](rag_and_pipelines.md#multi-agent-topology-vietnamese-tertiary-hospital).
- **Retrieval: hybrid BM25 + kNN + rerank for emergency · agentic + GraphRAG for complex.** See [`rag_and_pipelines.md` §Retrieval](rag_and_pipelines.md#retrieval).
- **Audit retention: 6 years** per [HIPAA §164.530(j)](https://www.hipaajournal.com/hipaa-retention-requirements/) — CloudTrail → S3 Object Lock (AWS) / ActionTrail → SLS → OSS WORM (Alibaba).
- **EHR integration via [SMART App Launch v2](http://docs.smarthealthit.org/) on FHIR R4** — Epic / Cerner / Allscripts sandboxes covered.
- **Document integration via [Microsoft Graph subscriptions](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0)** on SharePoint with `Sites.Selected` scoping.

## One product, no staged rollout

Every capability listed in each proposal is **active on launch day**: fine-tuned student, multi-agent specialists, GraphRAG, all three cache layers, guardrails, audit. Training runs during a 6–10 week pre-launch build window, not as a "phase 2". What runs after launch is **continuous retraining**:

| Cadence | Action |
|---|---|
| Daily | ICD-11 delta ingest; cache invalidation |
| Weekly | SharePoint reconciliation (safety net for missed webhooks) |
| Monthly | WHO guideline refresh + GraphRAG re-index; DPO micro-run on clinician preference pairs |
| Quarterly | Full student retrain (SFT + optional GRPO); re-qualify on eval harness; promote via 5% canary |
| Event-driven | Red-team re-run after any guardrail incident |

## Read order

1. This doc.
2. [`proposals/version_c_alibaba_qwen.md`](proposals/version_c_alibaba_qwen.md) — the recommended default, most technically complete.
3. [`proposals/version_a_aws_claude.md`](proposals/version_a_aws_claude.md) and [`proposals/version_b_aws_qwen.md`](proposals/version_b_aws_qwen.md) — comparators.
4. [`rag_and_pipelines.md`](rag_and_pipelines.md) — shared RAG / ingestion / multi-agent / EHR / framework / caching design.
5. [`customization.md`](customization.md) — SFT / DPO / GRPO / distillation per version.
6. [`regional_services.md`](regional_services.md) — live-verified service availability matrix.
7. [`compliance.md`](compliance.md) — PDPA / HIPAA / HCSA / FDA / EU AI Act / audit retention.

## Running artifacts

- **EC2 demo** at `13.213.123.169` — Version A2 baseline (Claude + RAG + LangGraph + FAISS), Singapore, [Cohere Embed v4](https://aws.amazon.com/blogs/aws/cohere-embed-multimodal-embeddings-are-now-available-in-amazon-bedrock/). Deploy code in [`aws-demo/ec2/`](../aws-demo/ec2/).
- **POC folder** — two sibling POCs ([`poc/aws_claude/`](../poc/aws_claude/) and [`poc/aws_qwen/`](../poc/aws_qwen/)) for a 10-day / 100-question interview demo; costs ~$165 and ~$197 respectively.

*Content above is rephrased for compliance with licensing restrictions.*
