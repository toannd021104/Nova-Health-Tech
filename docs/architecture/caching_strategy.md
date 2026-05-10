# Caching Strategy — Hitting the 2-Second Emergency SLA Cost-Effectively

Three layers of cache, each saving latency and cost in a different place. All three apply on both AWS and Alibaba Cloud.

## Layer 1 — Semantic response cache (LangChain pattern, hosting-independent)

What it does: when a clinician asks a question whose embedding is very close to a recent cached question, return the previous answer directly without calling the LLM. Layer 1 works identically against Bedrock, Model Studio, a SageMaker endpoint, or a self-hosted vLLM server — LangChain sits above the model layer.

- **AWS** — `langchain.cache.RedisSemanticCache` backed by **ElastiCache for Redis (Valkey)** with RediSearch. Hit time: single-digit milliseconds. Expected hit rate for emergency protocols that repeat across shifts: 30–45%.
- **Alibaba** — same pattern with **Tair** (Redis-compatible) and its built-in vector search (TairVector). `langchain_community.cache.RedisSemanticCache` works against Tair unchanged. LangChain-native Qwen integrations (`langchain_dashscope`) also exist, so the whole chain looks identical.

Tunables (applies to both):

- Similarity threshold: 0.95 (anything below goes to the LLM).
- TTL: **10 minutes for emergency-care answers** so that a mid-shift WHO update can invalidate them quickly; 24 hours for general clinical questions.
- Invalidation trigger: whenever the Knowledge Base reindex job completes, flush keys with matching `source:*` tags.

This cache goes in front of both the teacher and student lanes.

## Layer 2 — Prefix / KV cache on the LLM (cuts both latency and cost)

The RAG system prompt + retrieved chunks for a given clinical question are often ~3–5k tokens. Most of that is repeated verbatim across many calls — the system prompt, the tone template, the recent-WHO-updates preface, sometimes the same top chunks. Layer 2 avoids re-processing those tokens end-to-end: on a provider-managed endpoint this is "prompt caching"; on a self-hosted engine it is the inference engine's built-in KV-cache reuse (vLLM APC, SGLang RadixAttention).

Important: **LangChain cannot implement Layer 2.** LangChain hashes the prompt string and looks up a cached *final response* — that's Layer 1. Reusing the transformer's attention KV tensors across requests has to happen inside the model server. Trying to do "prompt caching" in LangChain is just a coarser semantic cache with a different key.

**Availability by version:**

| Version | Layer 2 cache | Where it lives | Notes |
|---|---|---|---|
| **Ver A** — AWS + Claude | ✅ Bedrock Prompt Caching | Bedrock | Claude + Nova families supported; `<cachePoint/>` in Converse API |
| **Ver B (Bedrock default)** — Qwen on Bedrock | ❌ Not available | — | Qwen3 models on Bedrock do not support prompt caching (verified May 2026); `<cachePoint/>` is a no-op |
| **Ver B (self-hosted path)** — Qwen on vLLM / SGLang | ✅ vLLM APC or SGLang RadixAttention | Our own endpoint | Zero code; enable once on the server; caches any shared prefix across any two calls |
| **Ver C** — Alibaba + Qwen | ✅ Qwen Context Cache | Model Studio | Implicit (auto) + Explicit modes |

### Ver A — Amazon Bedrock Prompt Caching

- **Savings** — up to **90% off input tokens** on cache hits; **up to 85% latency reduction** for the cached portion of a prompt. Must place the static content at the *start* of the prompt and mark it as `<cachePoint/>` in the Converse API.
- **Supported models** — Claude 4.x family, Amazon Nova family. Qwen3 on Bedrock is explicitly not supported.
- **How it fits** — cache the system prompt + tone template + top-N most-frequent WHO guideline chunks. Emergency-care answers sharing the "sepsis bundle" context become near-free on input tokens after the first hit.

### Ver B (Bedrock default) — No Layer 2 cache

Qwen3 models (`qwen3-next-80b-a3b`, `qwen3-vl-235b-a22b`) on Bedrock do not appear in the AWS prompt-caching supported-models list. The `<cachePoint/>` marker and `cache_control` field have no effect. With the Bedrock default, Ver B relies entirely on Layer 1 (semantic cache) and Layer 3 (reserved throughput) to hit the 2-second SLA. The cold-path latency budget for Ver B is therefore higher than Ver A at equal token counts — partially offset by Qwen's lower per-token price.

### Ver B (self-hosted path) — vLLM / SGLang prefix caching

If Ver B self-hosts Qwen (SageMaker endpoint, EKS on g5/g6e, or a dedicated EC2 GPU), the inference engine provides Layer 2 natively:

- **vLLM Automatic Prefix Caching (APC)** — flag `--enable-prefix-caching` on server start. Any request whose prompt shares a prefix with a cached prior request reuses that prefix's KV tensors. No code change in the caller, no explicit cache markers, no per-request config. Shares are block-aligned (default 16 tokens).
- **SGLang RadixAttention** — radix-tree–indexed KV cache with the same "prefix match anywhere" behavior; often higher hit rate than vLLM APC for chat-style workloads, at slightly higher memory.

Hit behavior on the emergency lane: the 2–3 k system-prompt + tone-template prefix is identical across every call, so it hits every time after the first. Typical first-token latency drops from ~500 ms to ~80–120 ms for the cached-prefix portion. This is *cheaper* and *more flexible* than Bedrock Prompt Caching because (a) no `<cachePoint/>` placement, (b) no 5-minute TTL, (c) no per-token premium for cache writes.

Hosting modes where this applies:
- SageMaker endpoint running vLLM (LMI container) — Layer 2 active on each instance, not shared across instances.
- EKS / ECS on g5 or g6e — same, Layer 2 per pod.
- EC2 single-instance demo — full Layer 2 benefit.

Cache is process-local; scale-out across replicas loses some hit rate unless we use a sticky-session load balancer or a shared KV store (SGLang supports disaggregated prefill-decode with a shared cache server, overkill for Nova's scale).

### Ver C — Alibaba Qwen Context Cache

- **Two modes**:
  - **Implicit cache** — automatic, zero config, active from Phase 1 (no code change needed). The system detects repeated prefixes; cache hits bill **20% of standard input price**.
  - **Explicit cache** — create a named cache ID for a prompt prefix and reference it per call; guaranteed discount on that prefix.
- **How it fits** — put the system prompt, tone template, and hot RAG chunks in the prefix; call with the per-query chunks + the user's question as the suffix. Implicit mode is free upside from day 1 — do not defer to Phase 3.

### Batch inference — for training data generation and eval

Both clouds charge **50% of on-demand price** for batch inference. We use this for:

- Teacher-model generation of the distillation dataset (tens of thousands of answers, offline, 50% off).
- Nightly LLM-as-judge evaluation runs (offline, 50% off).

## Layer 3 — Reserved throughput for the production peak (removes cold-start and queueing)

- **AWS — Bedrock Reserved Tier** for Claude Sonnet/Haiku and the Nova family. Fixed $/1K tokens-per-minute, billed monthly. Economical above a threshold of sustained TPM; for Nova's ER peak hours, typically pays off on the emergency (Haiku) lane.
- **Alibaba — Qwen Provisioned Throughput Units (PTU)** on Model Studio. Same idea — pay for reserved tokens-per-minute; Guarantees consistent latency when traffic spikes.

We turn on reserved capacity only for the small-model emergency lane at first; the complex/teacher lane stays on-demand until traffic justifies reservation.

## Composed budget (emergency lane, AWS example)

```
Layer 1 hit  (semantic cache)    →     ~20 ms                   (30–45% of queries)
Layer 2 hit  (prompt cache)      →  1100 ms, 90% cheaper input  (bulk of remaining)
No cache     (cold path)         →  1800 ms, full price         (rare)
```

Production expectation: blended p50 around 600–900 ms for cached-hot emergency queries, blended p95 under 2000 ms. The fine-tuned student model is what makes the non-cached path also fit the SLA.

## Invalidation rules

| Event | What gets invalidated |
|---|---|
| WHO monthly refresh job succeeds | Semantic cache keys with tag `source:who`; prompt-cache entries referencing WHO chunks are rebuilt on next call |
| Internal trial PDF upload | Semantic cache keys with tag `document_id:<id>`; prompt-cache entries touched |
| ICD-11 daily delta | Semantic cache keys with tag `source:icd11` |
| Model version bump (student or teacher) | Full flush — answers are model-specific |
| Guardrail policy change | Full flush |

## References

- [Cache Prompts Between Requests — AWS Bedrock Prompt Caching](https://aws.amazon.com/bedrock/prompt-caching/)
- [Effectively use prompt caching on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/effectively-use-prompt-caching-on-amazon-bedrock/)
- [Context Cache feature for Qwen models — Alibaba Cloud](https://www.alibabacloud.com/help/en/model-studio/context-cache)
- [vLLM — Automatic Prefix Caching](https://docs.vllm.ai/en/latest/features/automatic_prefix_caching.html)
- [SGLang — RadixAttention for reusing KV cache across prompts](https://docs.sglang.ai/backend/server_arguments.html)
- [Optimize LLM response costs and latency with effective caching — AWS](https://aws.amazon.com/blogs/database/optimize-llm-response-costs-and-latency-with-effective-caching/)

*Content above is rephrased for compliance with licensing restrictions.*
