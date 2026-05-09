# Caching Strategy — Hitting the 2-Second Emergency SLA Cost-Effectively

Three layers of cache, each saving latency and cost in a different place. All three apply on both AWS and Alibaba Cloud.

## Layer 1 — Semantic response cache (LangChain / LlamaIndex pattern)

What it does: when a clinician asks a question whose embedding is very close to a recent cached question, return the previous answer directly without calling the LLM.

- **AWS** — `langchain.cache.RedisSemanticCache` backed by **ElastiCache for Redis (Valkey)** with RediSearch. Hit time: single-digit milliseconds. Expected hit rate for emergency protocols that repeat across shifts: 30–45%.
- **Alibaba** — same pattern with **Tair** (Redis-compatible) and its built-in vector search (TairVector). `langchain_community.cache.RedisSemanticCache` works against Tair unchanged. LangChain-native Qwen integrations (`langchain_dashscope`) also exist, so the whole chain looks identical.

Tunables (applies to both):

- Similarity threshold: 0.95 (anything below goes to the LLM).
- TTL: **10 minutes for emergency-care answers** so that a mid-shift WHO update can invalidate them quickly; 24 hours for general clinical questions.
- Invalidation trigger: whenever the Knowledge Base reindex job completes, flush keys with matching `source:*` tags.

This cache goes in front of both the teacher and student lanes.

## Layer 2 — Provider-managed prompt/context caching (cuts both latency and cost on the LLM)

The RAG system prompt + retrieved chunks for a given clinical question are often ~3–5k tokens. Most of that is repeated verbatim across many calls — the system prompt, the tone template, the recent-WHO-updates preface, sometimes the same top chunks. Both clouds now ship a managed cache for exactly this.

### AWS — Amazon Bedrock Prompt Caching

- **Savings** — up to **90% off input tokens** on cache hits; **up to 85% latency reduction** for the cached portion of a prompt. Must place the static content at the *start* of the prompt and mark it as `<cachePoint/>` in the Converse API.
- **Supported models** — Claude 4.x family, Amazon Nova family, and more. (Confirm current list before deployment.)
- **How it fits our design** — cache the system prompt + tone template + the top-N most-frequent WHO guideline chunks. Emergency-care answers that share the same "sepsis bundle" context see a much lower per-call cost and faster time-to-first-token.

### Alibaba — Qwen Context Cache

- **Two modes**:
  - **Implicit cache** — automatic, zero config. The system detects repeated prefixes; cache hits bill **20% of standard input price**. No guarantee of a hit, but free upside when the pattern exists.
  - **Explicit cache** — you create a named cache ID for a prompt prefix and reference it per call. Slightly lower hit-rate risk; gives you guaranteed discount on that prefix.
- **How it fits** — same shape as AWS: put the system prompt, tone template, and hot RAG chunks in the prefix; call with the per-query chunks + the user's question as the suffix.

### Batch inference — for training data generation and eval

Both clouds charge **50% of on-demand price** for batch inference. We use this for:

- Teacher-model generation of the distillation dataset (tens of thousands of answers, offline, 50% off).
- Nightly LLM-as-judge evaluation runs (offline, 50% off).

## Layer 3 — Reserved throughput for the production peak (removes cold-start and queueing)

- **AWS — Bedrock Reserved Tier** for Claude Opus/Sonnet/Haiku and Nova family. Fixed $/1K tokens-per-minute, billed monthly. Economical above a threshold of sustained TPM; for Nova's ER peak hours, typically pays off on the emergency lane.
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
- [Optimize LLM response costs and latency with effective caching — AWS](https://aws.amazon.com/blogs/database/optimize-llm-response-costs-and-latency-with-effective-caching/)

*Content above is rephrased for compliance with licensing restrictions.*
