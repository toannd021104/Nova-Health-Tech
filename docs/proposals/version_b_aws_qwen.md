# Version B — AWS + Qwen (Bedrock Sydney)

All-Qwen on AWS Bedrock. Primary inference runs in **Sydney `ap-southeast-2`** because Qwen is not available on Singapore Bedrock. Fine-tuning via [Bedrock Reinforcement Fine-Tuning](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html) on Qwen3-32B (us-west-2).

- Primary chat region: **Sydney `ap-southeast-2`** (Bedrock Qwen)
- SG tenant: S3 raw, OpenSearch Serverless, ElastiCache, audit, VPN endpoint all in `ap-southeast-1`
- Fast lane: **Qwen3 Next 80B A3B** (MoE, 3B active) · Complex lane: **Qwen3 VL 235B A22B**
- Student (optional): Qwen3-32B via Bedrock RFT (us-west-2, $80/hr)
- Monthly cost: **~$2,967 base** / ~$3,240 with custom Qwen3-32B

---

## 1. Executive summary

Version B is the **open-weights-on-AWS-BAA** option. [Bedrock now hosts four Qwen3 models managed-serverless](https://aws.amazon.com/bedrock/qwen/), so Version B needs no self-hosted GPU for base inference — the entire SageMaker path that earlier drafts proposed is reduced to an optional alternative when the client requires the student model physically in Singapore.

The catch: **Qwen on Bedrock is not in Singapore** (DNS-verified 10 May 2026). Sydney (`ap-southeast-2`) is the nearest APAC region. PDPA-strict clients will need comparable-protection contract clauses for the SG→Sydney transfer. Clients who can accept that trade-off get Qwen-quality reasoning at Bedrock-managed ops complexity.

Every capability listed below is **active on day one**. If a custom student is desired, [Bedrock RFT](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html) training on Qwen3-32B runs pre-launch in us-west-2.

| Scenario requirement | How Version B meets it |
|---|---|
| Complex medical Q&A | [Qwen3 VL 235B A22B](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-vl-235b-a22b.html) (22B active, vision-capable) |
| Ground in internal trials + WHO + external sources | Hybrid retrieval on OpenSearch Serverless (SG) + ICD-11 API + PubMed tools |
| Auditable, compliant | CloudTrail → S3 Object Lock 6-year; Bedrock Guardrails; Comprehend Medical PHI mask |
| Fast enough for diagnosis (≤ 2 s emergency) | Pure if/else toggle + [Qwen3 Next 80B A3B](https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/model-card-qwen-qwen3-next-80b-a3b.html) MoE (3B active) + ElastiCache semantic cache |
| Monthly WHO refresh | EventBridge cron → Step Functions → Bedrock KB incremental sync |
| Patient-sensitive trial data | Comprehend Medical PHI mask + reversible tokenization + KMS BYOK |
| Consistent tone | Fixed system prompt + `temperature=0.1` + optional RFT on Qwen3-32B |
| Legacy PDF ingestion | Bedrock Data Automation (Sydney) advanced parsing |
| Structured WHO ICD-11 API | Daily delta pull + runtime `icd11_lookup` tool + query expansion |

---

## 2. Region and data residency

| | Setting |
|---|---|
| Tenant region (raw storage, vector store, audit) | **Singapore `ap-southeast-1`** |
| Bedrock Qwen inference | **Sydney `ap-southeast-2`** — nearest APAC region with Qwen; not in SG |
| Embeddings ([Titan v2](https://aws.amazon.com/bedrock/titan/)) | **Tokyo `ap-northeast-1`** |
| Rerank ([Amazon Rerank 1.0](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html)) | **Tokyo** (co-located with Titan) |
| Multimodal embeddings ([Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html)) | **us-east-1** (single-region) |
| Bedrock Data Automation | **Sydney** |
| Bedrock Reinforcement Fine-Tuning (path B-1) | **us-west-2 only** for Qwen3-32B |
| SageMaker (path B-2, optional) | Singapore — if SG residency for student is mandatory |
| Audit retention | CloudTrail → S3 Object Lock in SG, **6 years** |
| PDPA posture | Ephemeral prompt + response tokens transit SG→Sydney per query. Permanent patient data never leaves SG. Comparable-protection contract clause covers the Sydney hop. |

**No Outposts, no Direct Connect.** Hospital connects over [Site-to-Site VPN](https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html).

### Residency callout

The SG→Sydney round trip adds ~90 ms each way to the emergency-lane budget. This is the price of Qwen on Bedrock. If a client cannot accept this, either **Version A** (Claude/Nova SG-native) or **Version C** (Alibaba Qwen SG-native) is the better fit.

---

## 3. Available Qwen models on Bedrock (verified 10 May 2026)

From [`aws bedrock list-foundation-models`](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html) + [Bedrock pricing page](https://aws.amazon.com/bedrock/pricing/):

| Model | Total / Active params | Input $/1M (Sydney) | Output $/1M (Sydney) | Role |
|---|---|---|---|---|
| **[Qwen3 Next 80B A3B](https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/model-card-qwen-qwen3-next-80b-a3b.html)** | 80B / **3B active (MoE)** | **$0.1545** | **$1.2360** | **Emergency fast lane** — fastest Qwen on Bedrock via MoE routing |
| [Qwen3 32B dense](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-32b.html) | 32B dense | $0.1545 | $0.6180 | Alternative fast lane — cheaper output, slower per-token |
| **[Qwen3 VL 235B A22B](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-vl-235b-a22b.html)** | 235B / 22B active | **$0.5459** | **$2.7398** | **Complex lane + distillation teacher** — includes vision |
| Qwen3 235B A22B 2507 | 235B / 22B active | $0.2266 | $0.9064 | Text-only alternative — **60% cheaper than VL** when no figures |
| Qwen3 Coder Next | — | $0.5150 | $1.2360 | Not used (coding specialist) |

Batch: 50% off. Flex: 50% off. Priority: 75% premium.

### Regional availability

| Region | Qwen3 Next 80B | Qwen3 VL 235B | Qwen3 32B | Notes |
|---|---|---|---|---|
| Singapore `ap-southeast-1` | ❌ | ❌ | ❌ | No Qwen on SG Bedrock (verified) |
| **Sydney `ap-southeast-2`** | ✅ | ✅ | ✅ | **baseline region for Version B** |
| Tokyo `ap-northeast-1` | ✅ | ✅ | ✅ | Higher pricing |
| Mumbai `ap-south-1` | ✅ | ✅ | ✅ | Similar pricing to Sydney |
| us-west-2 / us-east-1 | ✅ | ✅ | ✅ | Cheapest; + Bedrock RFT endpoint |

---

## 4. Component diagram

```
 Clinician browser
      │ HTTPS + Cognito OIDC
      ▼
 CloudFront + WAF + API Gateway (SG)
      │
      ▼
 Lambda /chat (SG, VPC)
      ├─ Comprehend Medical (Sydney) PHI mask
      ├─ Layer-1 ElastiCache Redis OSS semantic cache (SG)
      ├─ if/else route on emergency flag
      │
      ├────── retrieval ──────► Bedrock Knowledge Bases on OpenSearch Serverless (SG)
      │                          + Titan Embed Text v2 (Tokyo)
      │                          + Amazon Rerank 1.0 (Tokyo)
      │                          + Nova Multimodal Embeddings (us-east-1, figures)
      │
      ├─── emergency=true ────► Bedrock (Sydney)
      │                          qwen.qwen3-next-80b-a3b  (3B active, ~250 tok/s)
      │                          OR custom RFT'd Qwen3-32B (us-west-2 custom model)
      │
      └─── emergency=false ───► Bedrock (Sydney)
                                  qwen.qwen3-vl-235b-a22b  (vision path)
                                  OR qwen.qwen3-235b-a22b-2507 (text-only, cheaper)
      │
      ▼
 Bedrock Guardrails + citation validator
      │
      ▼
 Stream response back to client

Ingestion (SG tenant):
 S3 raw (SG) → EventBridge → Step Functions → BDA (Sydney) parse → chunk
             → Titan v2 (Tokyo) embed → Bedrock KB sync (SG)
             → Bedrock KB GraphRAG on Neptune Analytics (SG) extraction

Optional customization (path B-1, quarterly):
 Bedrock RFT endpoint (us-west-2) on Qwen3-32B with Lambda grader
```

---

## 5. Data pipeline

Shared design in [`../rag_and_pipelines.md`](../rag_and_pipelines.md). Same parsing / chunking / embed strategy as Version A. Services and regions:

| Component | Service | Region |
|---|---|---|
| Raw storage | S3 with [Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) | SG |
| Parser | [Bedrock Data Automation](https://aws.amazon.com/bedrock/bda/) | Sydney (BDA not in SG) |
| Text embeddings | [Titan Embed Text v2](https://aws.amazon.com/bedrock/titan/) | Tokyo |
| Multimodal embeddings | [Nova Multimodal Embeddings](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-amazon-amazon-nova-multimodal-embeddings.html) | us-east-1 (single-region) |
| Rerank | [Amazon Rerank 1.0](https://docs.aws.amazon.com/bedrock/latest/userguide/rerank.html) | Tokyo |
| Vector store | [OpenSearch Serverless](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-vector.html) | SG |
| Managed GraphRAG | [Bedrock KB GraphRAG on Neptune Analytics](https://aws.amazon.com/blogs/machine-learning/announcing-general-availability-of-amazon-bedrock-knowledge-bases-graphrag-with-amazon-neptune-analytics/) | SG |

### Retrieval

- **Emergency lane** — hybrid BM25 + kNN HNSW → top-20 → Amazon Rerank → top-5
- **Complex lane** — hybrid + agentic + graph: `kb_retrieve` / `graph_retrieve` / `icd11_lookup` / `pubmed_search` tools

---

## 6. Model orchestration

### 6.1 Framework

Bedrock Agents + Bedrock Knowledge Bases as primary runtime — same as Version A. Qwen on Bedrock speaks the Converse API, so the same Agent machinery works. LangChain only for Layer-1 semantic cache + chat memory.

### 6.2 Routing — two steps

**Step 1 — Lane selection (pure if/else).** Matches [`aws-demo/ec2/app/graph.py`](../../aws-demo/ec2/app/graph.py). No classifier LLM call.

**Step 2 — Department selection (router agent, complex lane only).** Qwen3 32B with structured output picks one of 40 departments. Emergency bypasses this.

### 6.3 Lane models and hyperparameters

| Class | Model | Hyperparameters | Latency target |
|---|---|---|---|
| Emergency | **Qwen3 Next 80B A3B** (`qwen.qwen3-next-80b-a3b`) | `temperature=0.1, max_tokens=700` | ≤ 2 s |
| Router | Qwen3 32B, JSON mode | `temperature=0, max_tokens=150` | ~200 ms |
| Complex — with figures | **Qwen3 VL 235B A22B** (`qwen.qwen3-vl-235b-a22b`) | `temperature=0.2, max_tokens=1500` | 3–6 s |
| Complex — text-only | **Qwen3 235B A22B 2507** | `temperature=0.2, max_tokens=1500` | 3–6 s (60% cheaper) |
| Radiology (image attachment) | Qwen3 VL 235B A22B (native vision) | `temperature=0.2, max_tokens=1500` | 3–6 s |

**Splitting the complex lane** — routing text-only questions to Qwen3 235B A22B 2507 ($0.2266 in / $0.9064 out) and reserving Qwen3 VL for figure-bearing chunks cuts complex-lane cost ~60%.

### 6.4 Multi-agent department topology

40 specialty agents mirroring a Vietnamese tertiary hospital. Full mapping in [`../rag_and_pipelines.md` §Multi-agent topology](../rag_and_pipelines.md#3-multi-agent-topology-vietnamese-tertiary-hospital). UI never exposes the list. Emergency toggle bypasses the router. Image attachments force Radiology agent on vision-capable Qwen3 VL.

### 6.5 Agent tools (all read-only)

- `retrieve_guideline(topic, source=WHO, max_age_days=90)` — Bedrock KB
- `retrieve_trial(doc_id)` — internal KB
- `graph_retrieve(entity, relation?, hops=2)` — Bedrock KB GraphRAG on Neptune Analytics
- `icd11_lookup(term, mode)` — Lambda → live WHO ICD-11 API
- `pubmed_search(query, max_results)` — Lambda → NCBI E-utilities
- `icd11_expand_query(term)` — silent query expansion

---

## 7. Fine-tuning

Detailed technique catalog in [`../customization.md`](../customization.md). Version B specifics:

### 7.1 Path B-1 — Bedrock Reinforcement Fine-Tuning on Qwen3-32B (preferred)

[Bedrock RFT](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html) — fully managed. Provide prompts + Lambda reward function, Bedrock runs the training loop.

| Item | Price |
|---|---|
| Training hours (us-west-2 only) | **$80/hr** |
| Post-training inference input | $0.20 / 1M tokens |
| Post-training inference output | $0.78 / 1M tokens |
| Trained-model storage | $1.95 / month |

Typical clinical-domain run: 6–12 hours × $80 = **~$500–$1,000 per retrain**. Much simpler than SageMaker + TRL.

**Bonus**: the custom model's output pricing ($0.78/1M) is **cheaper than the base Qwen3 Next 80B A3B output ($1.24/1M)** — running the fast lane on the RFT'd custom model saves money as well as improves quality.

### 7.2 Path B-2 — SageMaker + Hugging Face TRL GRPO on Qwen3-4B (optional)

Kept as an alternative for clients who need the student physically in Singapore:

- `ml.g6e.8xlarge` training at ~$5.74/hr × 10–15 hr ≈ **$70–$100 per run** (matches [AWS Builder GRPO recipe](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai))
- SageMaker endpoint `ml.g5.2xlarge` in SG: ~$1.52/hr always-on (~$1,095/mo)
- GRPO via [TRL `GRPOTrainer`](https://huggingface.co/docs/trl/main/en/grpo_trainer)

Hyperparameters (from [`../customization.md`](../customization.md)):

```
LoRA rank 16, alpha 32, dropout 0.05
learning_rate 2e-4, epochs 3, warmup_ratio 0.03
bf16, batch_size 4 per device, grad_accum 4
```

### 7.3 When to use which

| Choose... | ...if |
|---|---|
| No fine-tuning (base Qwen3 Next 80B + Qwen3 VL 235B) | RAG + prompt engineering + caching alone clear the clinical-quality rubric. Simplest ops. |
| **Path B-1 (Bedrock RFT on Qwen3-32B)** | Want a clinical-domain-tuned student without managing GPU infra; willing to serve from us-west-2 custom-model endpoint. **Cheapest at steady state** because custom-model output pricing is lower. |
| **Path B-2 (SageMaker GRPO on Qwen3-4B)** | Student must physically live in Singapore for PDPA; or need sub-4B for tightest latency; or need weights portable off AWS |

---

## 8. Security architecture

Full mapping in [`../compliance.md`](../compliance.md). Same controls as Version A with these Version B deltas:

- **Qwen inference calls from SG Lambda → Sydney Bedrock** — TLS 1.3 over AWS backbone; no public Internet transit
- **Cross-region IAM** — Lambda execution role includes `bedrock:InvokeModel` scoped to `arn:aws:bedrock:ap-southeast-2:*:inference-profile/qwen.*`
- **PDPA transfer-limitation clause** signed with AWS for SG→Sydney prompt-token flow
- **Bedrock Guardrails** in Sydney co-located with the models

---

## 9. Cost — monthly pilot (600k calls, 30/70 emergency/complex)

Assumptions shared in [`../overview.md`](../overview.md). All list prices, USD, early 2026.

### 9.1 Base — Bedrock-only, no fine-tuning

| Item | Calc | Cost |
|---|---|---|
| Fast lane — Qwen3 Next 80B A3B (Bedrock Sydney) | 180k × 65% × (3k in + 350 out) × $0.1545/$1.236 per 1M | ~$105 |
| Complex lane — Qwen3 VL 235B A22B (Bedrock Sydney) | 420k × (3k in + 600 out) × $0.5459/$2.7398 per 1M | ~$1,377 |
| Titan Embed Text v2 (Tokyo) | ~500M tokens | ~$10 |
| Amazon Rerank 1.0 (Tokyo, 10% of complex) | | ~$45 |
| Bedrock Guardrails | per call | ~$180 |
| OpenSearch Serverless (SG) | baseline | ~$350 |
| **Bedrock KB GraphRAG on Neptune Analytics** | same pattern as Version A | ~$200 |
| Comprehend Medical | | ~$180 |
| Lambda + API GW + CloudFront + WAF | serverless | ~$150 |
| S3 + CloudTrail Object Lock + Macie | | ~$120 |
| ElastiCache Redis OSS | | ~$80 |
| Site-to-Site VPN | dual tunnel | ~$80 |
| **Base total** | | **~$2,967** |

### 9.2 With custom Qwen3-32B via Bedrock RFT (path B-1)

| Item | Delta |
|---|---|
| RFT training run, amortized (quarterly ~$800) | +$270 |
| Fast lane switches to custom Qwen3-32B: 117k calls × (3k + 350) × $0.20/$0.78 | replaces $105, costs ~$100 |
| Model storage | +$2 |
| **B-1 total** | **~$3,240** |

Note: output pricing on the custom model ($0.78) is lower than base ($1.24), so at scale the custom model actually saves on output tokens.

### 9.3 Complex-lane split (route text-only to cheaper model)

| Split variant | Complex-lane cost |
|---|---|
| 100% Qwen3 VL 235B | ~$1,377 |
| 80% text-only Qwen3 235B 2507 / 20% VL | ~$400 + ~$275 = **~$675** |

**Using the split, B base drops to ~$2,265/mo** — below Version C base. This is the strongest Version B configuration.

### 9.4 Path B-2 — SG-hosted SageMaker student (optional)

| Item | Cost |
|---|---|
| GRPO training on `ml.g6e.8xlarge` (quarterly ~$100) | +$35 amortized |
| SageMaker endpoint `ml.g5.2xlarge` SG, always-on | +$1,095 |
| Savings on fast-lane Qwen3 Next calls | −$95 |
| **B-2 total** | **~$4,000** |

Use Path B-2 only when client mandates SG residency for the student.

### 9.5 Per-call cost

| Variant | Emergency | Complex (VL) | Complex (text-only) |
|---|---|---|---|
| B base | ~$0.0009 | ~$0.0033 | ~$0.0012 |
| B-1 with custom Qwen3-32B | ~$0.0009 | ~$0.0033 | ~$0.0012 |

---

## 10. Performance budget (emergency lane, Qwen3 Next 80B A3B)

```
  25 ms   ElastiCache Redis OSS semantic cache hit (Layer 1; skip to step 7 if hit)
 100 ms   Cognito auth + PHI mask (Lambda in SG)
  70 ms   Retrieval (OpenSearch Serverless SG)
  90 ms   cross-region SG → Sydney (Bedrock)
 500 ms   Qwen3 Next first-token (MoE; NO prompt cache — Qwen3 not supported on Bedrock Prompt Caching, verified May 2026)
1,100 ms  Full answer (250 tokens @ ~250 tok/s via MoE)
 110 ms   Bedrock Guardrails + citation validation
───────
≤ 1,995 ms  p95
```

### Bedrock Prompt Caching — NOT available for Qwen3

[Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/) supports Claude 4.x and Amazon Nova. **Qwen3 is not on the supported-models list** (verified May 2026). Consequences:

- No TTFT reduction on the static prefix
- No input-token discount on repeated context
- Version A (Claude) saves ~300–400 ms on TTFT via prompt caching; Version B cannot replicate this on Bedrock today

**Mitigation if the 2-second SLA becomes tight**: pivot the fast lane to a self-hosted vLLM/SGLang endpoint on SageMaker (Path B-2). [vLLM Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html) and [SGLang RadixAttention](https://docs.sglang.ai/backend/server_arguments.html) both deliver prompt-cache equivalents without Bedrock's constraints (no `<cachePoint/>`, no 5-min TTL, no cache-write premium).

### Latency levers available

1. Pure if/else emergency routing saves ~300 ms
2. ElastiCache Redis OSS semantic cache (Layer 1, 30–45% hit rate)
3. Qwen3 Next MoE (3B active) fast first-token
4. RFT'd Qwen3-32B student (optional, path B-1) can replace base Qwen3 Next
5. Bedrock Reserved Tier on emergency lane (Layer 3, peak only)
6. Streaming via Converse API

---

## 11. Continuous operations (post-launch)

| Cadence | Action |
|---|---|
| Daily 02:00 SGT | WHO ICD-11 delta; semantic-cache invalidation |
| Weekly Sun 03:00 SGT | SharePoint reconciliation |
| Monthly day 1 02:30 SGT | WHO guideline PDF refresh + incremental Neptune graph re-index |
| Monthly | DPO micro-run on clinician preference pairs (if on path B-2 SageMaker) |
| Quarterly | Full RFT retrain on Qwen3-32B (path B-1) or full GRPO retrain on Qwen3-4B (path B-2); 5% canary 72 hours |
| Event-driven | Red-team re-run after any guardrail incident |

---

## 12. Flagged limitations and mitigations

| Limitation | Mitigation |
|---|---|
| Qwen NOT on Bedrock Singapore | Sydney cross-region (~90 ms RTT); PDPA comparable-protection contract clause |
| Bedrock Prompt Caching not supported for Qwen3 | Accept no Layer-2 on Bedrock; or pivot fast lane to self-hosted vLLM APC on SageMaker |
| Bedrock RFT pinned to us-west-2 | De-identified training data only; one-time US residency for the training process |
| Titan Embed Text v2 not in SG | Tokyo (~30 ms) |
| Amazon Rerank 1.0 Tokyo + us-west-2 only | Co-locate with Titan in Tokyo |
| Nova Multimodal Embeddings us-east-1 only | Emergency bypasses RAG so no impact; general case accepts ~180 ms cross-Pacific at query time |
| BDA not in SG | Sydney for one-off parse at ingest |
| Qwen3 VL pricing ~4× text-only 235B 2507 | Split complex lane — route text-only questions to cheaper model |
| No prompt-cache `<cachePoint/>` placement for Qwen on Bedrock | Trade-off accepted; or pivot to self-hosted |

Full regional detail in [`../regional_services.md` §AWS](../regional_services.md#1-aws--where-each-service-actually-lives).

---

## 13. Deployment approach

Tenant storage + retrieval + audit + VPN all in Singapore. Qwen inference in Sydney. Ingest-time services (BDA, Titan embed, Rerank, Nova Multimodal) in their native regions.

- Raw storage + vector store + ElastiCache + CloudTrail Object Lock — Singapore
- Qwen chat inference — Sydney
- Titan Embed + Amazon Rerank — Tokyo (co-located)
- Nova Multimodal Embeddings — us-east-1 (general case only)
- Bedrock Data Automation — Sydney (ingest-time)
- Bedrock RFT training (path B-1) — us-west-2

### Launch scope — everything on day one

| Capability | State at launch |
|---|---|
| Scheduled ingestion + Upload Portal over Site-to-Site VPN | ✅ |
| Hybrid retrieval on OpenSearch Serverless SG + Amazon Rerank (Tokyo) | ✅ |
| Managed GraphRAG on Neptune Analytics (SG) | ✅ |
| Emergency toggle + if/else router | ✅ |
| Qwen3 Next 80B A3B fast lane + Qwen3 VL 235B complex lane + Qwen3 235B 2507 text-only split | ✅ |
| Custom Qwen3-32B via Bedrock RFT (path B-1, trained pre-launch) | ✅ if customization chosen |
| 40-department multi-agent topology | ✅ (configurable subset per tenant) |
| ElastiCache Redis OSS semantic cache (Layer 1) | ✅ |
| Bedrock Reserved Tier on emergency | ✅ (sized to peak TPM) |
| Bedrock Guardrails + Comprehend Medical + grounding + citation validator | ✅ |
| CloudTrail → S3 Object Lock 6-year | ✅ |
| EHR SMART App Launch v2 on FHIR R4 | ✅ per tenant |

### Corporate integration

Full design in [`../rag_and_pipelines.md` §Corporate integration](../rag_and_pipelines.md#6-corporate-integration). Same as Version A:

- EHR via SMART App Launch v2 on FHIR R4
- SharePoint via Microsoft Graph `Sites.Selected` subscriptions
- Cognito federation for clinicians, IAM Identity Center for staff
- Audit export nightly to hospital SIEM

---

## 14. Pre-launch build (before cut-over)

| Week | Activity |
|---|---|
| 1–2 | Provision SG + Sydney resources; ingest WHO + ICD-11; BDA parse + Titan embed + Neptune graph extraction |
| 3–4 | Train Qwen3-32B student via Bedrock RFT (us-west-2) if path B-1; eval harness green |
| 5–6 | EHR integration (SMART on FHIR sandboxes); SharePoint Graph; Cognito federation per hospital |
| 7–8 | Red team 200+ adversarial prompts; tune Bedrock Guardrails; Reserved Tier sizing |
| Launch | Cut-over; all capabilities active |

---

## 15. When Version B is the right choice

- Hospital needs **open-weights** under AWS BAA
- Client willing to accept **Sydney residency** for inference (ephemeral prompt/response tokens only)
- Willing to run Bedrock RFT for a cost-effective custom student
- Bedrock-managed ops preferred over SageMaker complexity

If the client can't accept Sydney residency, pick [Version A](version_a_aws_claude.md) (AWS-BAA SG-native) or [Version C](version_c_alibaba_qwen.md) (Alibaba SG-native, zero cross-region hops).

---

## 16. References

- [Amazon Bedrock pricing — Qwen section](https://aws.amazon.com/bedrock/pricing/)
- [Qwen3 VL 235B A22B model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-vl-235b-a22b.html)
- [Qwen3 Next 80B A3B model card](https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/model-card-qwen-qwen3-next-80b-a3b.html)
- [Qwen3 32B model card](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-qwen-qwen3-32b.html)
- [OpenAI-compatible fine-tuning APIs (Reinforcement Fine-Tuning) in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/fine-tuning-openai-apis.html)
- [AWS Builder — GRPO tool-calling on Hugging Face TRL + SageMaker](https://builder.aws.com/content/35x6VR6kZYSn3JgNQmcNmIVK32Y/fine-tune-small-language-models-for-production-grade-tool-calling-with-grpo-using-hugging-face-trl-on-amazon-sagemaker-ai)
- [TRL GRPO Trainer](https://huggingface.co/docs/trl/main/en/grpo_trainer)
- [vLLM Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
- [SGLang RadixAttention](https://docs.sglang.ai/backend/server_arguments.html)
- [Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/)
- [Singapore PDPA — cross-border transfers](https://www.pdpc.gov.sg/organisations/resources/guidance-by-topic/guide-to-cross-border-data-transfers)

*Content above is rephrased for compliance with licensing restrictions.*
