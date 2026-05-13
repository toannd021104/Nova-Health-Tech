# PoC — Nova Health · AWS + Claude (Version A), reduced-data 10-day demo

Single-user, single-tenant deploy of the **Version A** architecture against AWS Singapore, with the data set deliberately trimmed so the reviewer can click through a live demo in 10 minutes.

- Profile: `gapv50k`
- Primary region: `ap-southeast-1`
- Embedding: Cohere Embed Multilingual v3 (SG-native — Titan Embed Text v2 is not available in `ap-southeast-1`)
- No cross-region hops — everything runs in Singapore
- Resource naming: `HA-<base64url(logical-name)>` — see [`NAMING.md`](NAMING.md)
- Resource map: every created resource is written to a DynamoDB table so teardown can find them again

## What got reduced vs the full proposal

The production Version A in [`../../docs/proposals/version_a_aws_claude.md`](../../docs/proposals/version_a_aws_claude.md) specifies OpenSearch Serverless + Neptune Analytics + Bedrock KB GraphRAG + ElastiCache Redis OSS + Bedrock Guardrails + Bedrock Data Automation parsing + Comprehend Medical PHI mask + CloudTrail WORM audit. The reduced PoC keeps the architecture shape but replaces some managed-service stack components to keep the 10-day cost under $20:

| Production Version A component | Reduced PoC equivalent | Why |
|---|---|---|
| OpenSearch Serverless (hybrid kNN + BM25) | **Deployed** — collection `d96n0aff30z4yu7t4tea`, KB `MUEEBGPRSJ` | Kept; semantic search only (HYBRID not used in SG) |
| Neptune Analytics + Bedrock KB GraphRAG | **Deployed** — graph `g-0keuwoev4a` (32 m-NCU), KB `FU6SXD0B8B` | Kept; 1,863 Entity + 826 Chunk nodes from WHO PDF |
| Bedrock Guardrails | **Deployed** — guardrail `azsgfl02i9gn` (DRAFT), wired into Converse streaming | Kept |
| Bedrock Agent | **Deployed** — agent `ZO61TBLZNO` (PREPARED) | InvokeAgent blocked by IAM trust chain issue; Converse streaming used directly |
| ElastiCache Redis OSS semantic cache | Cache disabled (`REDIS_ENDPOINT` unset) — `cache.get/put` no-op | Saves $0.017/hr + VPC complexity |
| Bedrock Data Automation (Sydney parse) | `pypdf.PdfReader` text extraction in-process | Reduced corpus is text-heavy, not multi-modal |
| Comprehend Medical DetectPHI | Regex `phi_mask()` in `graph.py` | Demo-grade PHI redaction only |
| Amazon Rerank 1.0 | **Not available in `ap-southeast-1`** — gap vs proposal | No rerank service in SG; production would need alternative |
| CloudTrail / Macie / Object Lock | Not attached in the PoC | Compliance stack belongs in production |

Embedding uses **Cohere Embed Multilingual v3** (SG-native). Titan Embed Text v2 is not available in `ap-southeast-1`.

## Data reduction (per the brief "just reduce the amount")

| Source | Full stack | Reduced PoC |
|---|---|---|
| WHO guidelines | 8 PDFs (all of `data/who/`) | **Only `B09540-eng.pdf`** (therapeutics & COVID-19 living guideline) |
| ICD-11 | root + 28 chapter entities + 3 search snapshots | root + first 5 entity JSON files |
| Department references | 36 PDFs (3 per department) | 12 PDFs (first one per department folder) |

Total S3 corpus footprint: ~30 MB. FAISS build time at first boot: ~60 seconds.

## Resources created

All in `ap-southeast-1`, tagged `Owner=nova-health-poc-claude`, `Stack=poc-claude`:

1. **DynamoDB table** `HA-cG9jLWNsYXVkZS1tYXA` (`poc-claude-map`) — resource map (logical → encoded → ARN)
2. **VPC** `HA-cG9jLWNsYXVkZS12cGM` (10.30.0.0/16)
3. **Subnet** `HA-cG9jLWNsYXVkZS1zdWJuZXQ` (10.30.1.0/24, AZ `ap-southeast-1a`)
4. **Internet Gateway** `HA-cG9jLWNsYXVkZS1pZ3c`
5. **Route table** `HA-cG9jLWNsYXVkZS1ydA` (0.0.0.0/0 → IGW)
6. **Security Group** `HA-cG9jLWNsYXVkZS1zZw` (SSH 22 from deployer IP + HTTP 80 public)
7. **IAM role + instance profile** `HA-cG9jLWNsYXVkZS1yb2xl` (Bedrock invoke, S3 read/write on one bucket, DynamoDB r/w on the map table)
8. **S3 bucket** `ha-cg9jlwnsyxvkzs1idwnrzxq-307711587176` — RAG corpus under `kb-who/`
9. **EC2 instance** `HA-cG9jLWNsYXVkZS1lYzI` (`t4g.small`, AL2023 arm64) — runs FastAPI + Caddy on port 80
10. **Elastic IP** `HA-cG9jLWNsYXVkZS1laXA` — public URL for the reviewer

**Bedrock managed resources** (IDs in `.managed_outputs.json`):

| Resource | ID |
|---|---|
| OpenSearch Serverless collection | `d96n0aff30z4yu7t4tea` |
| Vector Knowledge Base | `MUEEBGPRSJ` |
| Neptune Analytics graph (active) | `g-0keuwoev4a` (32 m-NCU, dim=1024) |
| Neptune Analytics graph (old, no vector search) | `g-zpzlbnmil3` |
| GraphRAG Knowledge Base | `FU6SXD0B8B` |
| Bedrock Guardrail | `azsgfl02i9gn` (DRAFT) |
| Bedrock Agent | `ZO61TBLZNO` (PREPARED) |

Full mapping in [`NAMING.md`](NAMING.md).

## Deploy + serve

```bash
# 1. Create infra + upload reduced corpus + record resources in DDB
python poc/aws_claude/deploy.py --profile gapv50k --region ap-southeast-1

# 2. Ship the app to the EC2 and start it
python poc/aws_claude/setup_instance.py

# 3. Demo URL will be printed; visit /ui/index.html for the chat UI
#    /healthz  shows the FAISS bootstrap state + bucket name
```

The deploy is idempotent — re-running it will reuse every resource by tag and only create what is missing.

## Teardown

```bash
python poc/aws_claude/teardown.py --profile gapv50k --region ap-southeast-1
```

`teardown.py` reads the DynamoDB map table as the source of truth, deletes every resource in reverse-creation order (EIP → EC2 → role → S3 empty+delete → SG → RT → subnet → IGW → VPC), then deletes the DDB table itself last.

## Model routing

Verified live against this account on 11 May 2026 (Converse smoke tests):

| Lane | Model ID | Region path |
|---|---|---|
| Emergency / router fast-path | `global.anthropic.claude-haiku-4-5-20251001-v1:0` | SG-native via the `global.*` inference profile |
| Department router (JSON classifier) | `apac.amazon.nova-micro-v1:0` | SG-native |
| Complex lane + Radiology vision | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` | SG-native via `global.*` |
| Graph construction (GraphRAG KB) | `anthropic.claude-3-haiku-20240307-v1:0` | Foundation model ARN — inference profile not supported for graph construction |
| Document embedding | Cohere Embed Multilingual v3 | SG-native — Titan Embed Text v2 not available in `ap-southeast-1` |
| Rerank | **Not available** | Amazon Rerank 1.0 not in `ap-southeast-1`; production gap |

No cross-region calls. All tokens stay in Singapore.

## What the reviewer can test

- **Emergency toggle** → bypasses router, Haiku 4.5 answer via Converse streaming with Guardrails
- **Complex case** → Nova Micro routes to one of 12 department agents; Sonnet 4.5 answers with `[1][2]` citations
- **Radiology image attach** → forces Radiology agent; Sonnet 4.5 vision describes findings and defers to a certified radiologist
- **Two KB retrieval** → Vector KB (OpenSearch, `MUEEBGPRSJ`) + GraphRAG KB (Neptune, `FU6SXD0B8B`) both queried; 5 chunks each, 10 total passed to Converse
- **Guardrails trace** → `guardrail_events` in response shows `inputAssessment` + `outputAssessments` for guardrail `azsgfl02i9gn`
- **Resource map** → `aws dynamodb scan --table-name HA-cG9jLWNsYXVkZS1tYXA` shows every created resource

## Test results summary

Results from streaming TTFT test (v3, 2026-05-13):

| Metric | Emergency (Haiku 4.5, streaming) | General (Sonnet 4.5, streaming) |
|---|---|---|
| Vector KB retrieval | ~260ms, 2 chunks | ~1,200ms, 15 chunks |
| GraphRAG retrieval | Skipped (speed) | ~400ms, 3 chunks |
| Guardrails | Skipped (speed) | Enabled |
| TTFT (avg, 10 questions) | **3,852ms** — PASS vs 5s SLA | **12,287ms** — PASS vs 15s SLA |
| Total (avg) | **3,860ms** | **12,331ms** |
| SLA pass rate | **100%** (10/10) | **100%** (10/10) |
| Input tokens (avg) | 370 | 2,500 |
| Output tokens (avg) | 295 | 400 |

**Key architecture decisions (v3):**
- Emergency: top-2 retrieval, no GraphRAG, no guardrails, short system prompt (230 chars), Haiku 4.5, max_tokens 300
- Complex: top-15 retrieval + GraphRAG top-3, guardrails enabled, full system prompt, Sonnet 4.5, max_tokens 1500
- Streaming: SSE via `/api/chat/stream`, uvicorn direct on port 80 (no Caddy proxy)
- UI shows: TTFT, total time, input/output token counts, timing breakdown (pre-gen, retrieve)

## Files in this folder

| File | Purpose |
|---|---|
| `README.md` | This doc |
| `NAMING.md` | HA-`<b64>` encoding table + DDB schema + Bedrock managed resource IDs |
| `deploy.py` | Boto3 deployer — creates infra, uploads reduced corpus, records to DDB |
| `setup_instance.py` | SSH/SCP bootstrap — ships the app tarball, sets up systemd + Caddy |
| `teardown.py` | Reads DDB map, deletes everything in the correct order |
| `requirements.txt` | Python deps installed on the EC2 (FastAPI, LangGraph, FAISS, boto3, redis) |
| `app/server.py` | FastAPI entry with startup-time S3 → FAISS bootstrap + `/healthz` |
| `app/graph.py` | LangGraph flow: PHI mask → cache → lane → router → retrieve → generate |
| `app/router.py` | Nova Micro department classifier |
| `app/rag.py` | Cohere Embed v3 + FAISS + S3 corpus bootstrap (no Amazon Rerank — not in SG) |
| `app/graphrag.py` | Bedrock KB GraphRAG — active, queries KB `FU6SXD0B8B` on Neptune `g-0keuwoev4a` |
| `app/cache.py` | Redis OSS semantic cache (disabled in reduced PoC — no-op) |
| `app/agents/__init__.py` | 12 department system prompts bound to Haiku/Sonnet/Nova Micro |
| `app/static/` | Light-theme chat UI (emergency toggle, route badge, image attach) |
| `.managed_outputs.json` | IDs for Bedrock-managed resources (KBs, Neptune graph, Guardrail, Agent) |
| `.test_results.json` | Raw test results from live PoC run (Case 1 Emergency + Case 2 Complex) |
