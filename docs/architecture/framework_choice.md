# Framework Choice for the Clinical AI Assistant

The core question: do we build the assistant on a **managed cloud-native framework** (Bedrock Agents on AWS, Model Studio Application on Alibaba), or on an **open orchestration framework** (LangGraph / LangChain, LlamaIndex)?

Our answer: **managed cloud-native framework as the primary runtime, with LangChain only where the managed flow genuinely blocks us.**

## Options compared

### Option A — Managed, cloud-native (RECOMMENDED)

- **AWS**: Amazon Bedrock Agents + Amazon Bedrock Knowledge Bases + Bedrock Guardrails, wired together inside the Converse API. Agent tools are Lambda functions exposed as an OpenAPI spec the agent reads.
- **Alibaba**: Model Studio **Application** — two flavors the docs describe:
  - **Agent application** — conversational, LLM decides what tools / retrieval to call. Matches Bedrock Agents.
  - **Workflow application** — deterministic DAG of prompt + retrieval + tool nodes. Better fit when we want a fixed path per question class (e.g., the emergency lane).

  We use **Agent application** for the general clinical chat (flexible, conversational) and a **Workflow application** for the emergency lane (deterministic, short, auditable).

Why this wins:

- Compliance surface is small — all the audit trail, guardrails, PHI handling, and model invocation logging are native features of one service.
- Operationally simple — no container fleet to patch, no dependency on a specific LangChain version on the critical path.
- Matches the scenario's "must be auditable" requirement out of the box.

Costs: you pay normal token + retrieval + cache prices; there's no extra framework fee.

Trade-offs: vendor lock-in on the orchestration layer (not on models or data); harder to port the agent to a different cloud; less flexibility than writing your own graph.

### Option B — Open orchestration (LangGraph or LangChain + LlamaIndex retrievers)

Run orchestration in your own container (ECS Fargate / Alibaba SAE / ACK). LangGraph handles state and routing; LangChain or LlamaIndex handles chat memory, retrievers, and tool wiring; both clouds still serve models via Bedrock / Model Studio.

Strengths: maximum flexibility, easy to port across clouds, large ecosystem of integrations, straightforward to swap a retriever or add a custom reranker.

Weaknesses: you own another runtime and its security patching; upgrades regularly break; the semantic cache / prompt cache wiring you write is not automatically correct; audit trail needs custom plumbing; framework churn is real and costly.

### Option C — Pure SDK (Bedrock Runtime / DashScope) + your own Python

Thin Lambda / Function Compute that directly calls the model with a hand-built prompt. No framework at all.

Strengths: no abstraction tax, fastest at runtime, easiest to audit every byte.

Weaknesses: you re-implement retrieval, tool-calling, memory, routing, guardrails. For a production clinical system that reaches dozens of KLoC fast.

## Decision

| Layer | AWS choice | Alibaba Cloud choice |
|---|---|---|
| Primary orchestration (conversational, multi-tool) | **Bedrock Agents** | **Model Studio Agent application** |
| Emergency lane orchestration (deterministic, fast) | Bedrock Agents + Guardrails + pre-routed prompt | **Model Studio Workflow application** |
| RAG index + retrieval | **Bedrock Knowledge Bases** on OpenSearch Serverless | **Model Studio Knowledge Base** on OpenSearch Vector Search Edition |
| Prompt templating / chat memory glue inside Lambda/FC | **LangChain** (light — just for the semantic response cache and chat memory) | **LangChain + `langchain-dashscope`** same pattern |
| Evaluation harness | Bedrock model evaluation jobs + custom LLM-as-judge in LangChain | PAI evaluation + LangChain LLM-as-judge |

This hybrid keeps the production critical path on managed services (which handle the audit + compliance + caching primitives) and uses LangChain only for two narrow jobs:

- Semantic response cache — `RedisSemanticCache` against ElastiCache (AWS) / Tair (Alibaba). Battle-tested, two-line install.
- Short-term chat memory — `ConversationBufferWindowMemory` keyed per session.

Anything else (tool calling, retrieval, guardrails) stays in the cloud-native framework.

## What about Qwen-Agent, Spring AI Alibaba, LlamaIndex?

- **Qwen-Agent** — Alibaba's open-source agent SDK; good when you want to self-host the agent runtime alongside a self-hosted Qwen on PAI-EAS. Only used in the on-prem Apsara Stack scenario where Model Studio isn't available.
- **Spring AI Alibaba** — for Java shops. Nova's stack is Python, so not in scope.
- **LlamaIndex** — strong retriever library; we don't need it because Bedrock KB / Model Studio KB already provide production-ready retrieval with metadata filtering and hybrid search.

## References

- [Agent vs Workflow Applications in Model Studio](https://www.alibabacloud.com/help/en/model-studio/application-introduction)
- [AI Agent Architecture with LLM and Tools Overview — Alibaba](https://www.alibabacloud.com/help/en/model-studio/getting-started/application-building-instructions)
- [How Amazon Bedrock knowledge bases work](https://docs.aws.amazon.com/bedrock/latest/userguide/kb-how-it-works.html)
- [Text generation — Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/text-generation)
- [LangChain vs LlamaIndex 2026 — production comparison](https://blog.premai.io/langchain-vs-llamaindex-2026-complete-production-rag-comparison/)

*Content above is rephrased for compliance with licensing restrictions.*
