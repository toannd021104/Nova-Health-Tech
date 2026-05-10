# End-to-end Workflow (AWS Singapore Production)

Matches the numbered steps on `diagrams/aws_workflow.svg`.

## A. Runtime path (single clinical question)

### Step 1 — Browser to edge (≈20 ms)

- Clinician clicks "Ask Nova" in the hospital web app or in the EHR iframe (SMART App Launch v2).
- Request hits **CloudFront** in the nearest edge location; AWS WAF applies geo + OWASP + rate rules.
- Payload `{ "message": "...", "emergency": true|false }` — the emergency flag is the user's explicit toggle on the chat panel.

### Step 2 — API Gateway + Cognito (≈100 ms)

- **API Gateway** REST endpoint `POST /api/chat`.
- **Cognito** authorizer validates the JWT:
  - For clinicians — token issued by Cognito user pool federated (SAML/OIDC) to the hospital IdP (EntraID / Okta / ADFS).
  - For demo users — the demo OIDC flow with Nova's own EntraID tenant.
- JWT claims extracted: `sub` (user id), `hospital_id`, `specialty`, `scope`.

### Step 3 — Lambda `/chat` preflight, PHI mask + cache check (≈80 ms)

- Lambda runs inside the **VPC**; only egress is to VPC endpoints for Bedrock, OpenSearch, S3, ElastiCache.
- **Comprehend Medical** DetectPHI on the message → reversible KMS-backed tokenization. The model never sees raw names, MRNs, DOBs.
- **Semantic response cache** lookup in ElastiCache Valkey (LangChain `RedisSemanticCache`): hash of normalized + tokenized question + emergency flag + model id. Hit → jump straight to Step 7 with `cache_hit=true`. Miss → continue.

### Step 4 — Hybrid retrieval from Bedrock Knowledge Bases (≈60–100 ms)

- LangGraph `retrieve` node runs a hybrid **BM25 + kNN HNSW** query against the `kb-who-guidelines`, `kb-internal-trials`, `kb-treatment-protocols`, `kb-icd11` indexes on **OpenSearch Serverless**.
- Pre-filter by metadata: `review_date >= NOW-18m`, `specialty IN (...)`, `document_type`, hospital tenant if applicable.
- **Cohere Embed v4** (`global.cohere.embed-v4:0`) embeds the query (text-only) at 1024 dims; all text chunks are embedded the same way at ingest time, so queries and chunks live in the same vector space.
- **Amazon Nova Multimodal Embeddings** — used at ingest time for figure-bearing chunks, stored in a **separate vector field** (`chunk_mm_vec`) alongside the text field (`chunk_text_vec`). Retrieval runs two parallel kNN searches (text + multimodal) and merges results at rerank time, rather than sharing one combined vector space. The running demo on EC2 uses Cohere v4 only (text-only corpus); Nova Multimodal is wired in the production plan for figure-heavy documents.
- Top-20 by kNN → **Cohere Rerank** on Bedrock → keep top-5 chunks with `{source, page, section}` metadata preserved.

### Step 5 — Route (pure if/else, no LLM call)

The LangGraph `_route_next` node reads `state.emergency` from the request body. No classifier LLM call here — that was deliberately removed to save ~300 ms.

```python
def _route_next(state):
    return "answer_fast" if state["emergency"] else "answer_complex"
```

### Step 5a — Emergency lane → **Claude Haiku 4.5** (target ≤ 2 s)

- `global.anthropic.claude-haiku-4-5-20251001-v1:0` via the **Bedrock Converse streaming API**.
- Hyperparameters: `temperature=0.1`, `max_tokens=700`. (Claude rejects sending both `temperature` and `top_p`; temperature alone is enough for tone consistency.)
- Prompt structure (from `graph.py`): the Nova system prompt + retrieved context with `[1], [2]` source tokens + the user's question. The first ~2-3 KB of the prompt is static and cached via **Bedrock Prompt Caching** (90% off on cached input tokens).
- **Production serving**: the fast lane calls the **fine-tuned Nova Lite student distilled from Sonnet 4.5** via Bedrock's custom-model endpoint. Same streaming Converse API surface as base Haiku. Base Haiku 4.5 stays registered as the same-API fallback when the custom endpoint is unavailable.

### Step 5b — Complex lane → **Claude Sonnet 4.5** (target 3–6 s)

- `global.anthropic.claude-sonnet-4-5-20250929-v1:0`, same streaming Converse pattern.
- `temperature=0.2`, `max_tokens=1500` — longer answers, slightly more flexible phrasing, deeper differential reasoning.
- Used for non-emergency clinical questions, literature synthesis, multi-step reasoning.

### Step 6 — Guardrails + citation check (≈100 ms)

- **Bedrock Guardrails** policy checks:
  - PHI filter (belts-and-suspenders layer after Comprehend Medical).
  - Denied topics: self-diagnosis without clinician, dosing override, illegal drug synthesis.
  - Contextual grounding score ≥ 0.7 — ungrounded answers blocked.
  - Prompt-injection filter on the user message.
- **Citation validator** (custom) confirms every `[N]` in the answer maps to a retrieved chunk. A fail → block the response, return a friendly "I cannot answer this from the retrieved context" message, and log the attempt.

### Step 7 — Stream response back + cache write (concurrent with generation)

- Server-Sent Events from Bedrock bubble up through API Gateway to the browser — first token in ~300–400 ms for Haiku, ~800 ms for Sonnet. Clinician starts reading while generation finishes.
- Successful answers written to the semantic cache with `TTL=10 min` for emergency, `TTL=24 hr` for general.
- Answer payload includes `{route, model_id, latency_ms, citations[]}` for the UI to render the route badge and source list.

### Step 8 — Audit trail (async)

Structured log written to CloudWatch Logs + CloudTrail, then pushed to S3 with **Object Lock** (WORM) for 6-year retention:

```
{
  "ts": "...",
  "user_id": "<hashed>",
  "hospital_id": "...",
  "question_hash": "sha256(...)",
  "emergency": true,
  "route": "emergency",
  "model_version": "global.anthropic.claude-haiku-4-5-20251001-v1:0",
  "retrieved_chunk_ids": ["..."],
  "citations": ["..."],
  "guardrail_verdict": "pass",
  "answer_hash": "sha256(...)",
  "latency_ms": 1642,
  "cache_hit": false
}
```

No raw PHI is logged; only hashes and tokenized stand-ins.

---

## B. Ingestion path (asynchronous, scheduled)

### Step 9 — Scheduled polls + webhooks

Event sources that drop new objects into `s3://nova-raw/`:

| Cadence | Source | Where |
|---|---|---|
| Daily 02:00 SGT | **WHO ICD-11 API** delta | `raw/scheduled/icd11/` |
| Monthly day 1 02:30 SGT + RSS webhook | **WHO guideline PDFs** | `raw/scheduled/who/` |
| Weekly Sun 03:00 SGT | Internal trial reports (pull over VPN) | `raw/scheduled/trials/` |
| Weekly Sun 03:30 SGT | Treatment protocols (pull over VPN) | `raw/scheduled/protocols/` |
| Real-time webhook | **Microsoft Graph** subscription on SharePoint site(s) | `raw/sharepoint/<tenant>/` |
| Any time | **Internal Upload Portal** manual upload over VPN | `raw/manual/` |

EventBridge cron rules fire Step Functions workflows; Graph webhooks hit API Gateway → a dedicated FC function that validates `clientState` and writes to S3.

### Step 10 — Parse + chunk + embed + index

On every S3 `ObjectCreated` event:

1. **Amazon Bedrock Data Automation** advanced parsing: text + tables (2-D preserved) + figures + layout metadata.
2. **Macie** PHI scan — quarantine + notify admin on a hit; the document never reaches the index until reviewed.
3. **GuardDuty Malware Protection** for S3 — rejects infected uploads before parsing.
4. **Lambda chunker**: hierarchical 1500/300 tokens, 15% overlap, section-aware. Figure-bearing chunks flagged for the multimodal embedding.
5. **Embedding**: text chunks → `global.cohere.embed-v4:0` into `chunk_text_vec`; figure-bearing chunks also get Amazon Nova Multimodal Embeddings into a separate `chunk_mm_vec` field on the same document (not concatenated into one vector space). OpenSearch Serverless stores both vector fields per chunk.
6. **Bedrock Knowledge Base sync** (incremental upsert by `document_id + revision_hash` — unchanged chunks are free).
7. On completion, publish to SNS → Lambda flushes semantic-cache keys tagged with the changed `source:*` so stale answers disappear.

---

## C. Failure handling

| Failure | Response |
|---|---|
| Guardrail fail (ungrounded / PHI / injection) | Return templated "I cannot answer this from the current context" + log + alert |
| EHR unreachable | Degrade gracefully — answer without patient context, show banner |
| Bedrock throttled | Retry with exponential backoff; fall back from Sonnet to Haiku for complex questions if the retry exceeds 4 s; never fall back *from* Haiku (already fastest) |
| OpenSearch retrieval empty | Answer from generic model knowledge with a visible "no internal source matched" warning |
| Cache miss on a slow network | Cold path ~1800 ms (p95) — still inside the SLA when running in-region |
| WHO API / Graph subscription lost | Lifecycle webhook auto-renews; if missed, weekly reconciliation cron catches it |

---

## D. Notes on the emergency toggle

The user toggles the switch in the chat panel before sending. The frontend adds `"emergency": true` to the request body. The server treats it as authoritative — no LLM classifier — so:

- **Deterministic**: same question + same toggle always routes to the same model.
- **Faster**: no extra model call before routing.
- **Lower cost**: one fewer token charge per query.
- **Fallback safety**: if the toggle is somehow missing, the graph defaults to `emergency=false` (Sonnet, the safer "take your time and reason" path).

A later phase could still layer a passive classifier in parallel to warn the clinician if the toggle looks wrong ("this looks like an emergency — consider enabling the fast lane"), but the routing itself stays a simple if/else.
