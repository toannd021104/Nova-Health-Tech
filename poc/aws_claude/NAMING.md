# Resource Naming — AWS + Claude PoC

Every resource gets `HA-<base64url(logical-name)>` (padding stripped). The DynamoDB table listed last keeps a live mapping of logical → encoded → ARN so `teardown.py` can find and delete every resource in the correct order.

Encoding helper (Python):

```python
import base64
def ha(name: str) -> str:
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")
```

## Resources created by `deploy.py`

| Logical name | Encoded tag | AWS resource | Scope |
|---|---|---|---|
| `poc-claude-map` | `HA-cG9jLWNsYXVkZS1tYXA` | DynamoDB table — the resource map | `ap-southeast-1` |
| `poc-claude-vpc` | `HA-cG9jLWNsYXVkZS12cGM` | VPC (10.30.0.0/16) | `ap-southeast-1` |
| `poc-claude-subnet` | `HA-cG9jLWNsYXVkZS1zdWJuZXQ` | Public subnet (10.30.1.0/24) | `ap-southeast-1a` |
| `poc-claude-igw` | `HA-cG9jLWNsYXVkZS1pZ3c` | Internet Gateway | — |
| `poc-claude-rt` | `HA-cG9jLWNsYXVkZS1ydA` | Route table (0.0.0.0/0 → IGW) | — |
| `poc-claude-sg` | `HA-cG9jLWNsYXVkZS1zZw` | Security Group (SSH 22 + HTTP 80) | — |
| `poc-claude-role` | `HA-cG9jLWNsYXVkZS1yb2xl` | IAM role + instance profile (Bedrock + S3 + DDB) | global |
| `poc-claude-bucket` | `ha-cg9jlwnsyxvkzs1idwnrzxq-<acct>` (lowercased DNS-safe, account ID appended for uniqueness) | S3 bucket — RAG corpus | `ap-southeast-1` |
| `poc-claude-ec2` | `HA-cG9jLWNsYXVkZS1lYzI` | EC2 instance (`t4g.small`) | `ap-southeast-1a` |
| `poc-claude-eip` | `HA-cG9jLWNsYXVkZS1laXA` | Elastic IP | `ap-southeast-1` |

## Bedrock managed resources (created via console / Bedrock APIs)

These resources are not created by `deploy.py` but are part of the deployed PoC stack. IDs are recorded in `.managed_outputs.json`.

| Resource | ID | Notes |
|---|---|---|
| OpenSearch Serverless collection | `d96n0aff30z4yu7t4tea` | Collection name: `nova-health-kb`; endpoint `d96n0aff30z4yu7t4tea.ap-southeast-1.aoss.amazonaws.com` |
| Vector Knowledge Base | `MUEEBGPRSJ` | Backed by OpenSearch Serverless; embedding model: Cohere Embed Multilingual v3 |
| Neptune Analytics graph (active, with vector search) | `g-0keuwoev4a` | 32 m-NCU; `vectorSearchConfiguration` dim=1024; endpoint `g-0keuwoev4a.ap-southeast-1.neptune-graph.amazonaws.com` |
| Neptune Analytics graph (old, no vector search) | `g-zpzlbnmil3` | Superseded; no vector search config; kept for reference |
| GraphRAG Knowledge Base | `FU6SXD0B8B` | Backed by Neptune graph `g-0keuwoev4a`; data source ID `AVQ0I8AR52`; 1,863 Entity nodes + 826 Chunk nodes from WHO B09540-eng.pdf |
| Bedrock Guardrail | `azsgfl02i9gn` | Version: DRAFT; wired into Converse streaming path |
| Bedrock Agent | `ZO61TBLZNO` | Status: PREPARED; uses `global.anthropic.claude-sonnet-4-5` inference profile; InvokeAgent blocked by IAM trust chain issue — Converse streaming used directly |

S3 bucket names must be all-lowercase DNS-safe, so that resource uses a lowercase `ha-<b64>` prefix plus the account ID as a uniqueness suffix.

## Resource-map DynamoDB schema

Table: `HA-cG9jLWNsYXVkZS1tYXA` (`poc-claude-map`)

| Attribute | Type | Notes |
|---|---|---|
| `logical_name` (PK) | string | Human-friendly key — the first column in the table above |
| `encoded_name` | string | `HA-<b64>` tag value used on the actual AWS resource |
| `resource_type` | string | `vpc` / `subnet` / `igw` / `rt` / `sg` / `role` / `s3` / `ec2` / `eip` / `ddb` |
| `arn_or_id` | string | `vpc-0abc…`, `i-0abc…`, S3 bucket name, etc. |
| `region` | string | AWS region |
| `created_at` | string | ISO 8601 timestamp |
| `stack_tag` | string | Constant `poc-claude` — so one table can hold multiple stacks later if needed |

Every create operation in `deploy.py` writes to this table as soon as the resource exists. `teardown.py` reads the table to know exactly what to delete and in what order (EIP → EC2 → role → SG → RT → subnet → IGW → VPC → S3 objects → S3 bucket → DDB table last).

## Region

- **Primary:** `ap-southeast-1` Singapore (EC2, S3, DDB, VPC, Bedrock `global.anthropic.*` inference profile, OpenSearch Serverless, Neptune Analytics, Bedrock Guardrails)
- **No cross-region embed/rerank:** Cohere Embed Multilingual v3 is available natively in Singapore. Amazon Titan Embed Text v2 and Amazon Rerank 1.0 are **not** available in `ap-southeast-1`; they are not used in this PoC.
- **Profile:** `gapv50k` (override with `--profile`)

## What is intentionally omitted from this PoC

Per the user's "reduce everything" brief:
- No ElastiCache Redis OSS (≈ $4 / 10 days and adds VPC complexity) — semantic cache disabled; `REDIS_ENDPOINT` left empty
- No CloudTrail, no Macie, no WAF, no Site-to-Site VPN, no DR — these belong in production Version A (see `docs/proposals/version_a_aws_claude.md`)
- No Bedrock Data Automation parse in Sydney — `pypdf` text extraction is good enough for the reduced corpus
- No Bedrock Model Distillation run — base Claude 4.5 only, matching the PoC README's "no fine-tuning" baseline
- No Amazon Rerank — not available in `ap-southeast-1`; this is a known gap vs the production proposal
