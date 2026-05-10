# Version A — AWS + Claude (Singapore)

AWS-native clinical assistant on Bedrock with Anthropic Claude as the primary chat family. Singapore-primary region; fine-tuning happens on US regions then serves from SG via the `global.anthropic.*` / `apac.amazon.*` inference profiles.

- Primary region: **Singapore `ap-southeast-1`** (for chat, retrieval, guardrails, audit)
- Secondary regions: Tokyo for [Titan Embed Text v2](https://aws.amazon.com/bedrock/titan/) + [Amazon Rerank 1.0](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html); Sydney for [Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/); us-east-1 for [Amazon Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html); us-east-1 / us-west-2 for [Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html)
- **Two sub-variants:**
  - **A1+** — Nova Micro + Nova Pro, **~$2,955/mo** (cheapest SG-native under AWS BAA)
  - **A2** — Claude Haiku 4.5 + Claude Sonnet 4.5, **~$7,295/mo** (quality-first, running demo baseline)
- Student: [Nova Lite via Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html) (Sonnet 4.5 → Nova Lite), **~$1,700–2,700 per run**

---

## 1. Executive summary

Version A is the AWS-BAA-native option for hospitals that require AWS contractual coverage and want [Anthropic Claude](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html) or [Amazon Nova](https://aws.amazon.com/bedrock/nova/) as the chat family. Primary chat runs in Singapore via AWS's global inference profiles (`global.anthropic.*`, `apac.amazon.*`) — Anthropic and Nova models are reachable in SG even though some adjunct services (embeddings, rerank, multimodal embeddings, fine-tuning, Bedrock Data Automation) are not.

Two flavors are offered. **A1+** uses Nova Micro + Nova Pro — the cheapest SG-native AWS option. **A2** uses Claude Haiku 4.5 + Claude Sonnet 4.5 — matches the running EC2 demo and is quality-first. Choice depends on clinical benchmark: if Nova Pro clears the complex-lane rubric, A1+ is the obvious pick at ~40% of A2's cost.

Every capability listed below is **active on day one**. Training for the Nova Lite student happens pre-launch.

| Scenario requirement | How Version A meets it |
|---|---|
| Complex medical Q&A | Sonnet 4.5 (or Nova Pro) + agentic RAG + managed GraphRAG |
| Ground in internal trials + WHO + external sources | Hybrid retrieval on [OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector.html) + ICD-11 API tool + PubMed E-utilities tool |
| Auditable, compliant | CloudTrail → [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) 6-year; [Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/); [Comprehend Medical](https://aws.amazon.com/comprehend/medical/) PHI mask |
| Fast enough for diagnosis (≤ 2 s emergency) | Pure if/else toggle + Haiku 4.5 (or Nova Micro) + Nova Lite student + Bedrock Prompt Caching + ElastiCache semantic cache |
| Monthly WHO refresh | [EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html) cron → [Step Functions](https://aws.amazon.com/step-functions/) → Bedrock KB incremental sync |
| Patient-sensitive trial data | Comprehend Medical DetectPHI + reversible tokenization + in-region KMS BYOK |
| Consistent tone | Fixed system prompt + `temperature=0.1` + distillation on approved answers |
| Legacy PDF ingestion | Bedrock Data Automation (Sydney) advanced parsing |
| Structured WHO ICD-11 API | Daily delta pull + runtime `icd11_lookup` tool + query expansion |

---

## 2. Region and data residency

| | Setting |
|---|---|
| Primary region | Singapore `ap-southeast-1` |
| Chat (Haiku 4.5, Sonnet 4.5) | SG via `global.anthropic.*` inference profiles |
| Chat (Nova Micro, Nova Lite, Nova Pro) | SG via `apac.amazon.*` inference profiles |
| Text embeddings ([Titan v2](https://aws.amazon.com/bedrock/titan/)) | **Tokyo** — not in SG |
| Rerank ([Amazon Rerank 1.0](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html)) | **Tokyo** — single-region Tokyo + us-west-2 only; co-located with Titan to minimize round-trips |
| Multimodal embeddings ([Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html)) | **us-east-1** — single-region only; cross-border tax accepted for general case; emergency bypasses RAG so the delay never affects emergency SLA |
| Bedrock Data Automation (PDF parsing) | **Sydney** — not in SG; ingestion-time only (one-off per document) |
| Bedrock Model Distillation (Nova Lite training) | **us-east-1 / us-west-2** — pre-launch + quarterly retrain; trained model serves back to SG |
| Comprehend Medical | **Sydney** (nearest to SG; not in SG itself) |
| Audit retention | CloudTrail → S3 Object Lock in SG, **6 years** per [HIPAA §164.530(j)](https://www.hipaajournal.com/hipaa-retention-requirements/) |
| PDPA posture | Patient data stays in SG. Adjunct services (embed, rerank, multimodal embed, BDA, distillation) accept ephemeral cross-border for indexing — [PDPA transfer-limitation](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers) compliant via comparable-protection contract clauses |

**No Outposts, no Direct Connect.** Hospital connects over [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html) (IPsec IKEv2, AES-256-GCM, dual-tunnel HA).

Full regional verification in [`../regional_services.md` §AWS](../regional_services.md#1-aws--where-each-service-actually-lives).

---

## 3. Component diagram

```
              ┌──────────────────────────────────────────────────────────────┐
              │   Hospital network (clinician workstations + EHR systems)    │
              └──┬──────────────────────────────────────────────┬────────────┘
                 │                                              │
         AI chat │ HTTPS                          Internal mgmt │ HTTPS over
                 │                                               │ Site-to-Site VPN
                 ▼                                               ▼
     ┌──────────────────────┐                      ┌──────────────────────────┐
     │ CloudFront + WAF     │                      │ Customer Gateway on-prem │
     └──────┬───────────────┘                      └──────────┬───────────────┘
            │                                                 │
     ┌──────▼──────────┐   ──────── Site-to-Site VPN ───────► │ VPN GW / TGW
     │ API Gateway     │                                      │  (private side)
     │  (public, REST) │                                      └──────────┬───────────┘
     │  + Cognito JWT  │                                                 │
     │   authorizer    │                                                 │
     └──────┬──────────┘                                                 ▼
            │                                                 ┌──────────────────────┐
            │                                                 │ Private ALB + Cognito│
            │                                                 │ OIDC/SAML ← EntraID  │
            │                                                 │                      │
            │                                                 │ ECS Fargate:         │
            │                                                 │  Upload Portal       │
            │                                                 └──────────┬───────────┘
            │                                                            │
            ▼                                                            ▼
   ┌──────────────────────────────┐                        ┌──────────────────────────┐
   │ Lambda /chat (VPC)           │                        │ S3 raw bucket             │
   │  0. Cognito JWT check        │◄──── semantic cache ──┤ /raw/scheduled/...        │
   │  1. Comprehend Medical PHI    │     hit returns early │ /raw/manual/...           │
   │  2. if/else on emergency      │                       │ /raw/icd11/...            │
   │     toggle (pure, no LLM)     │                       │ /raw/who/...              │
   │  3. Bedrock Agent invoke      │                       └──────────┬───────────────┘
   │  4. Guardrails + citation     │                                  │ ObjectCreated
   │     validator                 │                                  ▼
   └─────┬──────────────┬──────────┘                       ┌──────────────────────────┐
         │              │                                  │ Step Functions pipeline  │
 Layer 1 │    Layer 2   │  Generation via Bedrock          │  BDA (Sydney) parse →    │
 Elasti- │    Bedrock   │   Haiku 4.5 / Nova Micro (fast,  │  chunk → Titan v2 embed  │
 Cache   │    Prompt    │     router, Emergency agent)     │  (Tokyo) → Bedrock KB    │
 Redis   │    Caching   │   Sonnet 4.5 / Nova Pro (complex │  + GraphRAG extraction   │
 OSS     │  (Claude 4.x │     + teacher + 39 specialists)  │                          │
 semantic│   + Nova)    │   Sonnet 4.5 vision (Radiology)  │ + GuardDuty Malware scan │
 cache   │              │   Nova Lite student (~40% of     │ + Macie PHI scan         │
         │              │     complex traffic)             │                          │
         │              │   + Bedrock Guardrails           │                          │
         │              │                                  └──────────┬───────────────┘
         │              │                                             ▼
         │              │                             ┌────────────────────────────┐
         │              │                             │ Bedrock Knowledge Bases    │
         │              │                             │  kb-who-guidelines         │
         │              │                             │  kb-internal-trials        │
         │              │                             │  kb-treatment-protocols    │
         │              │                             │  kb-icd11                  │
         │              │                             │  on OpenSearch Serverless  │
         │              │                             │  (hybrid kNN + BM25)       │
         │              │                             │  + Titan Embed v2 (Tokyo)  │
         │              │                             │  + Nova Multimodal Emb     │
         │              │                             │    (us-east-1, figures)    │
         │              │                             ├────────────────────────────┤
         │              │                             │ Bedrock KB GraphRAG on     │
         │              │                             │  Neptune Analytics (SG)    │
         │              │                             └────────────────────────────┘
         ▼              ▼
  All traffic → CloudTrail → S3 Object Lock (WORM, 6-year retention) → Security Lake
```

---

## 4. Data pipeline

Shared design in [`../rag_and_pipelines.md`](../rag_and_pipelines.md). Version A specifics:

### 4.1 Ingestion sources and schedule

| Source | Cadence | Trigger | Service |
|---|---|---|---|
| WHO ICD-11 API | Daily 02:00 SGT | [EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-scheduled-rule-pattern.html) cron | Lambda |
| WHO guideline PDFs | Monthly day 1 02:30 SGT + RSS webhook | EventBridge + API GW | Lambda + BDA |
| Internal clinical trial reports (SharePoint) | Weekly Sun 03:00 SGT + [Graph subscription](https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions) | EventBridge + API GW | Lambda |
| Manual upload | Any time | Upload Portal over VPN | ECS Fargate → S3 |
| Monthly full reconciliation | Day 1 04:00 SGT | EventBridge | Step Functions |

### 4.2 Parsing — Bedrock Data Automation (Sydney)

[Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) with advanced parsing handles 100+ page PDFs with horizontal and vertical tables and text-based flowcharts. BDA is not available in Singapore — parse jobs run in Sydney, output (structured JSON + text chunks) returns to SG S3. One-off cross-region tax per document, not per query.

### 4.3 Embeddings and rerank

| Use | Model | Region | Pricing | Notes |
|---|---|---|---|---|
| Text chunks | [Amazon Titan Embed Text v2](https://aws.amazon.com/bedrock/titan/) | **Tokyo** | ~$0.02 / 1M | Singapore has no Titan Embed; Tokyo is the nearest region |
| Figure-bearing chunks | [Amazon Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html) | **us-east-1** | per call | Single-region only. Emergency bypasses RAG so never calls this. |
| Rerank top-20 | [Amazon Rerank 1.0 (`amazon.rerank-v1:0`)](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html) | **Tokyo** (co-located) | $1/1k queries | Single-region Tokyo + us-west-2 only |

**Amazon-only AI stack** — no Cohere. Cost tables and architecture adjusted accordingly vs the running EC2 demo (which uses Cohere Embed v4).

### 4.4 Vector store

[**OpenSearch Serverless**](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector.html) vector collection in Singapore. Hybrid BM25 + HNSW kNN in one index. Metadata: `source`, `document_id`, `revision`, `document_type`, `publication_date`, `review_date`, `specialty`, `evidence_grade`, `page`, `section_heading`, `has_table`, `has_figure`.

### 4.5 Managed GraphRAG

[**Bedrock Knowledge Bases GraphRAG on Amazon Neptune Analytics**](https://aws.amazon.com/blogs/machine-learning/announcing-general-availability-of-amazon-bedrock-knowledge-bases-graphrag-with-amazon-neptune-analytics/) — GA March 2025, available in Singapore. Managed entity/relation extraction; no self-hosted Neo4j.

- 1 m-NCU Neptune Analytics minimum ($0.16/hr × 720 ≈ $115/mo)
- Graph extraction LLM calls on Sonnet 4.5 at ingest (~$80 one-time per WHO refresh)
- Graph-traversal LLM calls amortized ~$0.0005/query × 30% of complex traffic

### 4.6 Retrieval

- **Emergency lane** — hybrid one-pass: BM25 + kNN HNSW → top-20 → Amazon Rerank → top-5
- **Complex lane** — hybrid + agentic + graph: `kb_retrieve` / `graph_retrieve` / `icd11_lookup` / `pubmed_search` tools on a [Bedrock Agent](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)

---

## 5. Model orchestration

### 5.1 Framework — Bedrock Agents + Knowledge Bases

[Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) + Bedrock Knowledge Bases are the primary runtime. Agent tools are Lambda functions exposed via OpenAPI. LangChain is used only for the Layer-1 semantic cache (`RedisSemanticCache`) and per-session chat memory.

### 5.2 Routing — two steps

**Step 1 — Lane selection (pure if/else).** Matches [`aws-demo/ec2/app/graph.py`](../../aws-demo/ec2/app/graph.py) `_route_next`. No classifier LLM call — saves ~300 ms.

**Step 2 — Department selection (router agent, complex lane only).** Nova Micro with structured output picks one of 40 departments. Emergency lane bypasses this.

### 5.3 Lane models and hyperparameters

#### A1+ variant (Nova Micro + Nova Pro)

| Class | Model | Hyperparameters | Latency target |
|---|---|---|---|
| Emergency | **Nova Micro** (`apac.amazon.nova-micro-v1:0`) | `temperature=0.1, max_tokens=700` | ≤ 2 s |
| Router | Nova Micro | `temperature=0, max_tokens=150` (JSON only) | ~150 ms |
| Complex | **Nova Pro** (`apac.amazon.nova-pro-v1:0`) | `temperature=0.2, max_tokens=1500` | 3–6 s |
| Vision (Radiology) | Nova Pro vision | `temperature=0.2, max_tokens=1500` | 3–6 s |
| Literature/citation | Nova Micro, grounded-only | `temperature=0.1` | 1.5–2 s |

#### A2 variant (Haiku 4.5 + Sonnet 4.5)

| Class | Model | Hyperparameters | Latency target |
|---|---|---|---|
| Emergency | **Claude Haiku 4.5** (`global.anthropic.claude-haiku-4-5-20251001-v1:0`) | `temperature=0.1, max_tokens=700` — Claude rejects both temperature and top_p together | ≤ 2 s |
| Router | Nova Micro | `temperature=0, max_tokens=150` | ~150 ms |
| Complex | **Claude Sonnet 4.5** (`global.anthropic.claude-sonnet-4-5-20250929-v1:0`) | `temperature=0.2, max_tokens=1500` | 3–6 s |
| Vision (Radiology) | Claude Sonnet 4.5 (native vision) | `temperature=0.2, max_tokens=1500` | 3–6 s |
| Literature/citation | Haiku 4.5, grounded-only | `temperature=0.1` | 1.5–2 s |

**Claude Opus is not used** — overkill, priced out for Nova's volume.

### 5.4 Multi-agent department topology

40 specialty agents mirroring a Vietnamese tertiary hospital. **UI never exposes the list.** Full Vietnamese → English mapping in [`../rag_and_pipelines.md` §Multi-agent topology](../rag_and_pipelines.md#3-multi-agent-topology-vietnamese-tertiary-hospital).

- **Emergency toggle ON → Emergency Medicine agent** (bypass router)
- **Image attached → Radiology agent on vision-capable model** (Sonnet 4.5 or Nova Pro vision)
- **Prescribing question → Clinical Pharmacy auto-invoked as side-channel**
- **Router confidence < 0.6 → General Medicine / Triage with banner**

Per-tenant config enables a subset of the 40.

### 5.5 Agent tools (Bedrock Agent action groups, all read-only)

- `retrieve_guideline(topic, source=WHO, max_age_days=90)` — Bedrock KB retrieval
- `retrieve_trial(doc_id)` — internal KB
- `graph_retrieve(entity, relation?, hops=2)` — Bedrock KB GraphRAG on Neptune Analytics
- `icd11_lookup(term, mode)` — Lambda → live WHO ICD-11 API
- `pubmed_search(query, max_results)` — Lambda → [NCBI E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25500/)
- `icd11_expand_query(term)` — silent query expansion for retrieval

---

## 6. Fine-tuning and distillation

Detailed technique catalog in [`../customization.md`](../customization.md). Version A specifics:

### 6.1 The Claude Haiku 4.5 constraint

**Claude Haiku 4.5 is NOT fine-tunable on Bedrock.** [Only Claude 3 Haiku (2024-03-07)](https://docs.aws.amazon.com/bedrock/latest/userguide/custom-model-supported.html) is fine-tunable — and using it would lose all the Haiku 4.5 quality gains. The production path is therefore **Bedrock Model Distillation**: Sonnet 4.5 as teacher → Nova Lite as student.

### 6.2 [Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html)

Managed end-to-end. You provide prompts (or invocation-log seeds), Bedrock asks the teacher, trains the student, exposes a custom-model endpoint. Available in us-east-1 / us-west-2. Trained model invocable via Bedrock from SG.

| Item | Cost |
|---|---|
| Teacher generation (80M in + 6M out on Sonnet batch) | `(80 × $1.50) + (6 × $7.50)` ≈ **$165** |
| Training job (managed) | **$1,500–2,500** |
| Clinician review (~15% sample, in-house) | $0 |
| **Total per run** | **~$1,700–2,700** |

Quarterly cadence.

### 6.3 Training pipeline

```
1. Seed prompts
   (a) de-identified clinician questions from invocation logs
       (Comprehend Medical DetectPHI masks before logging)
   (b) teacher-paraphrases of WHO / protocol chunks
   target: 10k–30k prompts

2. Bedrock Model Distillation job
   - teacher: Sonnet 4.5
   - student: Nova Lite
   - dataset: seed prompts + optional "golden examples"
   - training region: us-east-1 or us-west-2 (de-identified data only crosses the Pacific)

3. Eval harness
   Sonnet 4.5 as LLM-judge on: accuracy, citation coverage, PHI leakage, tone, emergency-appropriateness

4. Promote to production
   gate: student ≥ 95% of teacher on holdout + zero regression on safety suite
   launch-day: 100% on fast lane (A2 variant)
   post-launch retrains: 5% canary for 72 hours
```

### 6.4 Serving the student

Nova Lite custom model ID replaces base Haiku 4.5 on the fast lane in the A2 variant at launch. A2 after distillation: Nova Lite takes ~40% of complex-lane traffic too, saving ~$2,200/mo.

### 6.5 Optional fallback — Claude 3 Haiku custom SFT

If the client demands a Claude-family student, Claude 3 Haiku (2024-03-07) custom SFT is available on us-west-2 only. Hyperparameters:

```
epochCount:             2     (default, range 1–10)
batchSize:              32    (default, range 4–256)
learningRateMultiplier: 1.0   (default, range 0.1–2.0)
earlyStoppingThreshold: 0.001
earlyStoppingPatience:  2
```

Trade-off: lose Haiku 4.5 quality gains. Only used when client mandates Claude branding for the student.

---

## 7. Security architecture

Full mapping in [`../compliance.md`](../compliance.md). Summary:

| Layer | Control |
|---|---|
| Account isolation | [AWS Organizations](https://aws.amazon.com/organizations/); one account per environment in `ap-southeast-1` |
| Network | Lambdas in private VPC; Bedrock + S3 + OpenSearch via [VPC endpoints](https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html); zero Internet egress from chat Lambda |
| Identity — clinicians | [Cognito user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-pools-identity-federation.html) federated via SAML/OIDC to hospital IdP |
| Identity — Nova staff | [IAM Identity Center](https://aws.amazon.com/iam/identity-center/) federated to Nova EntraID |
| Hospital ↔ cloud | [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html) — IKEv2 + AES-256-GCM + SHA-2, dual-tunnel HA |
| Data at rest | S3, OpenSearch, ElastiCache, Secrets Manager — all on customer-managed KMS keys |
| Data in transit | TLS 1.3 everywhere |
| PHI handling | [Comprehend Medical DetectPHI](https://docs.aws.amazon.com/comprehend/latest/dg/how-medical-phi.html) on every inbound message → reversible KMS-backed tokenization → model never sees raw PHI. [Macie](https://aws.amazon.com/macie/) weekly on `raw/` |
| LLM safety | [Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/): denied topics (`self-diagnosis without clinician`, `dosing override`, `illegal drug synthesis`), PHI filter, grounding ≥ 0.7, prompt-injection filter |
| Audit | CloudTrail → [S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) **6-year retention** + [Security Lake](https://aws.amazon.com/security-lake/) |
| Ingestion safety | [GuardDuty Malware Protection for S3](https://docs.aws.amazon.com/guardduty/latest/ug/malware-protection-s3.html); Macie PHI scan |
| Secrets | [Secrets Manager](https://aws.amazon.com/secrets-manager/) with KMS + rotation Lambda |
| BAA | AWS BAA signed and scoped to all Bedrock + adjunct services in `ap-southeast-1` |

---

## 8. Cost — monthly pilot (600k calls, 30/70 emergency/complex)

Assumptions shared in [`../overview.md`](../overview.md). All list prices, USD, early 2026.

### 8.1 A1+ — Nova Micro (fast) + Nova Pro (complex), all-Nova, SG-native

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Nova Micro | 180k × 65% × $0.0006 | ~$70 |
| Complex lane — Nova Pro | 420k × $0.0035 | ~$1,470 |
| Titan Embed Text v2 (Tokyo) | ~500M tokens | ~$10 |
| Amazon Rerank 1.0 (Tokyo, 10% of complex) | | ~$45 |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless (1+1 OCU) | 720 hr × $0.24 × 2 | ~$350 |
| Bedrock KB GraphRAG on Neptune Analytics (1 m-NCU + extraction LLM calls + traversal LLM calls) | | ~$200 |
| Comprehend Medical | per 100-char unit | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Redis OSS (2-AZ cache.t4g.small) | | ~$80 |
| Site-to-Site VPN (dual tunnel) | | ~$80 |
| **A1+ total** | | **~$2,955** |

### 8.2 A2 — Haiku 4.5 (fast) + Sonnet 4.5 (complex)

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Haiku 4.5 | 180k × 65% × $0.003 | ~$350 |
| Complex lane — Sonnet 4.5 | 420k × $0.013 | ~$5,460 |
| Everything else same as A1+ (includes $200 GraphRAG) | | ~$1,485 |
| **A2 base** | | **~$7,295** |
| + Distillation amortized ($2,000 per run / 3 mo) | | +$670 |
| − Nova Lite replaces Sonnet on ~40% of complex traffic | | −$2,200 |
| **A2 with trained Nova Lite student** | | **~$5,765** |

### 8.3 Per-call cost

| Variant | Emergency | Complex |
|---|---|---|
| A1+ (Nova Micro / Nova Pro) | ~$0.0006 | ~$0.0035 |
| A2 (Haiku 4.5 / Sonnet 4.5) | ~$0.003 | ~$0.013 |

### 8.4 [Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/) (Layer 2)

Claude 4.x + Nova families both supported. Up to 90% off cached input + ~85% TTFT cut. Cache-point placement is explicit via `<cachePoint/>` on the prefix. 5-minute TTL.

Composed emergency p95 (A2):

```
 20 ms   ElastiCache semantic cache hit (Layer 1; 30–45% of queries)
100 ms   Cognito auth + PHI mask
 60 ms   Hybrid retrieval (metadata pre-filter, top-20, rerank to 5)
400 ms   Haiku 4.5 first-token (Bedrock Prompt Cache hit on static prefix)
1,200 ms Haiku 4.5 full answer (250 tokens, streaming)
120 ms   Guardrail + grounding + citation validation
──────
≤ 1,900 ms  p95
```

---

## 9. Performance budget

| Traffic class | p50 | p95 | SLA |
|---|---|---|---|
| Emergency (cached) | 300–500 ms | 900 ms | ≤ 2 s |
| Emergency (cold, A2 Haiku 4.5) | 700–1,200 ms | 1,900 ms | ≤ 2 s |
| Emergency (cold, A1+ Nova Micro) | 500–900 ms | 1,500 ms | ≤ 2 s |
| Complex (cached prefix) | 1,500–3,000 ms | 4,500 ms | ≤ 6 s |
| Complex (cold, A2 Sonnet 4.5) | 3,000–5,000 ms | 6,000 ms | ≤ 6 s |

Latency levers:
1. Pure if/else emergency routing saves ~300 ms
2. ElastiCache Redis OSS semantic cache (30–45% hit rate)
3. Bedrock Prompt Caching (~50% input token reduction + 85% TTFT cut)
4. Nova Lite student (smaller = faster on ~40% of complex traffic)
5. Bedrock Reserved Tier on emergency lane (Layer 3, peak only)
6. Streaming via Converse API — first token ~300–400 ms

---

## 10. Continuous operations (post-launch)

| Cadence | Action |
|---|---|
| Daily 02:00 SGT | WHO ICD-11 delta; semantic-cache invalidation for `source:icd11` tags |
| Weekly Sun 03:00 SGT | SharePoint / trial reconciliation |
| Monthly day 1 02:30 SGT | WHO guideline PDF refresh + incremental Neptune Analytics graph re-index |
| Monthly | DPO micro-run (limited on Claude family; Nova Lite distillation re-run with fresh preference data) |
| Quarterly | Full Nova Lite student retrain via Bedrock Model Distillation; re-qualify on eval harness; 5% canary 72 hours |
| Event-driven | Red-team re-run after any guardrail incident |

---

## 11. Flagged limitations and mitigations

| Limitation | Mitigation |
|---|---|
| Titan Embed Text v2 not in SG | Tokyo (~30 ms RTT); only hit at ingest + at query-time embedding (small latency cost) |
| Amazon Rerank 1.0 single-region Tokyo + us-west-2 | Co-locate with Titan in Tokyo so embed+rerank is one round-trip |
| Nova Multimodal Embeddings single-region us-east-1 | Emergency bypasses RAG so never touches this. For general case: accept ~180 ms cross-Pacific tax or omit multimodal embed (text-only recall still works, figure-heavy queries lose some precision) |
| Bedrock Data Automation not in SG | Sydney for one-off parsing at ingest; output returns to SG |
| Claude Haiku 4.5 NOT fine-tunable | Use Bedrock Model Distillation (Sonnet → Nova Lite) instead, or Claude 3 Haiku (2024-03-07) SFT fallback |
| Bedrock Model Distillation / RFT / custom SFT all US-only | Acceptable — de-identified training data only; trained model invocable from SG |
| Comprehend Medical not in SG | Sydney (nearest) for PHI masking |
| Claude API rejects temperature + top_p together | Use temperature alone |
| Bedrock Prompt Caching 5-minute TTL | System prefix gets refreshed on every first-call burst; caveat accepted |

Full regional detail in [`../regional_services.md` §AWS — critical callouts](../regional_services.md#aws--critical-callouts).

---

## 12. Deployment approach

Single-region primary in Singapore; adjunct services in nearest AWS regions:

- Chat + retrieval + guardrails + audit + hospital VPN all in `ap-southeast-1`
- Embed + rerank in Tokyo (single round-trip from SG)
- Multimodal embed in us-east-1 (general case only; emergency bypasses)
- BDA parsing in Sydney (ingest-time only)
- Distillation training in us-east-1 / us-west-2 (pre-launch + quarterly)

DR: cross-AZ within `ap-southeast-1`. Warm-standby in Jakarta or Tokyo is a roadmap item pending PDPA review.

### Launch scope — everything on day one

| Capability | State at launch |
|---|---|
| Scheduled ingestion + Upload Portal over Site-to-Site VPN | ✅ |
| Hybrid retrieval (BM25 + kNN on OpenSearch Serverless + Amazon Rerank) | ✅ |
| Managed GraphRAG on Neptune Analytics | ✅ |
| Emergency toggle + if/else router | ✅ |
| Haiku 4.5 / Nova Micro fast lane + Sonnet 4.5 / Nova Pro complex lane | ✅ |
| Nova Lite student trained pre-launch via Bedrock Model Distillation (A2 variant) | ✅ |
| 40-department multi-agent topology | ✅ (configurable subset per tenant) |
| ElastiCache Redis OSS semantic cache + Bedrock Prompt Caching | ✅ |
| Bedrock Reserved Tier on emergency lane | ✅ (sized to peak TPM) |
| Bedrock Guardrails + Comprehend Medical + grounding + citation validator | ✅ |
| CloudTrail → S3 Object Lock 6-year | ✅ |
| [EHR SMART App Launch v2](http://docs.smarthealthit.org/) on FHIR R4 | ✅ per tenant |

### Corporate integration

Full design in [`../rag_and_pipelines.md` §Corporate integration](../rag_and_pipelines.md#6-corporate-integration). Summary:

- **EHR** via SMART App Launch v2 against Epic / Cerner / Allscripts on FHIR R4. Lambda de-identifies the patient slice (Comprehend Medical) before calling Bedrock. Read-only scopes only.
- **SharePoint / OneDrive** — Microsoft Graph subscriptions with `Sites.Selected`. Webhook → API Gateway → Lambda → S3 → Step Functions ingestion.
- **Clinician SSO** — Cognito federation per hospital tenant.
- **Admin SSO** — IAM Identity Center → Nova EntraID.
- **Audit export** — CloudWatch Logs → S3 → hospital SIEM via cross-account role.

---

## 13. Pre-launch build (before cut-over)

| Week | Activity |
|---|---|
| 1–2 | Provision SG resources; ingest WHO + ICD-11; BDA (Sydney) parse + Titan (Tokyo) embed + Neptune graph extraction |
| 3–4 | Train Nova Lite student via Bedrock Model Distillation (us-west-2); eval harness green |
| 5–6 | EHR integration (SMART on FHIR sandboxes); SharePoint Graph; Cognito federation per hospital |
| 7–8 | Red team 200+ adversarial prompts; tune Bedrock Guardrails; Reserved Tier sizing |
| Launch | Cut-over; all capabilities active |

---

## 14. When Version A is the right choice

| Client profile | Pick |
|---|---|
| Cost-sensitive AWS client, Nova quality acceptable | **A1+** — ~$2,955/mo, cheapest fully-AWS-SG-native option |
| US hospital with Anthropic brand preference; AWS BAA mandatory | **A2** — Haiku 4.5 + Sonnet 4.5, quality-first, SG-native for chat |
| PDPA-strict, open to Alibaba | See [Version C](version_c_alibaba_qwen.md) — cheaper and zero cross-region hops |
| Open-weights mandate under AWS BAA | See [Version B](version_b_aws_qwen.md) |

---

## 15. References

- [Amazon Bedrock model IDs](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)
- [Amazon Nova](https://aws.amazon.com/bedrock/nova/) · [Anthropic Claude on Bedrock](https://www.anthropic.com/news/amazon-bedrock)
- [Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/)
- [Bedrock Model Distillation](https://docs.aws.amazon.com/bedrock/latest/userguide/model-distillation.html)
- [Bedrock Knowledge Bases GraphRAG on Neptune Analytics — GA](https://aws.amazon.com/blogs/machine-learning/announcing-general-availability-of-amazon-bedrock-knowledge-bases-graphrag-with-amazon-neptune-analytics/)
- [Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/)
- [Amazon Rerank 1.0](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html)
- [Amazon Comprehend Medical](https://aws.amazon.com/comprehend/medical/)
- [Bedrock Guardrails](https://aws.amazon.com/bedrock/guardrails/)
- [AWS HIPAA compliance](https://aws.amazon.com/compliance/hipaa-compliance/)
- [AWS Services in Scope](https://aws.amazon.com/compliance/services-in-scope/)
- [AWS Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html)
- [Singapore PDPA — cross-border transfers](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers)

*Content above is rephrased for compliance with licensing restrictions.*
