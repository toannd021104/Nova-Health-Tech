# Session handoff — Nova Health Tech Clinical AI proposal

Context transfer doc for continuing this work in a fresh Kiro session. Everything is already committed to `toannd021104/Nova-Health-Tech`, branch `proposal/genai-architecture`.

## TL;DR — what's on the branch as of this handoff

```
HEAD = 1373464 (or later)
Branch: proposal/genai-architecture
Remote: https://github.com/toannd021104/Nova-Health-Tech.git
```

- **Three production architecture tracks** drafted: Version A (AWS + Claude), Version B (AWS + Qwen), Version C (Alibaba + Qwen). All three are single-launch (no phase 1/2/3), multi-agent, with RAG + managed GraphRAG + 3-layer caching + SFT-or-distillation + 6-year audit.
- **Two POCs scaffolded** in `poc/`:
  - `poc/aws_claude/` — Version A, non-fine-tuned, base Claude + Amazon-only AI stack + Redis, ~$165 for 10-day / 100-question demo
  - `poc/aws_qwen/` — Version B, includes SFT training on Qwen3-4B, ~$197 for the same demo (Scenario A)
- **40-department Vietnamese-hospital topology** mapped to routing labels in `docs/rag_and_pipelines.md` §Multi-agent topology
- **36 real PDFs** downloaded into `data/clinical-trials/departments/` via `scripts/download_department_refs.py` (PubMed Central open access); gitignored but easy to re-fetch

## User's hard constraints (do not violate)

| Constraint | Why |
|---|---|
| **Region: Singapore** for both AWS (`ap-southeast-1`) and Alibaba Cloud International | PDPA data residency; no cross-border transfer by default |
| **No Outposts, no Direct Connect** | Singapore region is close enough; Site-to-Site IPsec VPN only |
| **Audit retention: 6 years** (HIPAA §164.530(j)), not 7 | Corrected earlier in the conversation |
| **Emergency routing: pure if/else on the explicit UI toggle** | No classifier LLM call — saves ~300 ms. User repeated this twice. |
| **No Claude Opus** | Overkill, price hard to justify |
| **No fine-tuning of Claude Haiku 4.5** on Bedrock | Only Claude 3 Haiku (2024-03-07) is fine-tunable. Production uses Bedrock Model Distillation Sonnet → Nova Lite instead. |
| **Amazon-only AI stack, no Cohere** | Swap Cohere Embed/Rerank for Amazon Titan Embed v2 + Amazon Rerank 1.0 |
| **Cache: Redis OSS, NOT Valkey** | User was explicit; `redis>=5.0` in requirements |
| **Secrets never committed** | `HA-sing.pem`, WHO ICD-11 creds, EntraID client secret, AWS keys |
| **One product, no staged rollout** | No "phase 1 / 2 / 3" language anywhere. Launch = all features active; what comes after is "continuous operations" (monthly DPO, quarterly SFT) |
| **Don't use subprocess + PowerShell for AWS CLI** | Use boto3 directly. PowerShell treats AWS CLI stderr as errors. |
| **No fake data** in `/data/` — use `/reference/` for the user's local copyrighted reference docs (gitignored) |
| **Multi-agent topology mirrors a Vietnamese tertiary hospital** — the UI does NOT expose the 40-department list. Router classifies the prompt. Full Vietnamese → English mapping is in `docs/rag_and_pipelines.md` §Multi-agent topology. |

## Credentials the user shared during the conversation

**Do NOT put these in plaintext anywhere in the repo — GitHub push protection will reject.** Put in env vars, AWS Secrets Manager, or the user's local `.env` (gitignored):

- **AWS** — profile `gapv50k` (access key and secret are on the user's local machine; ask the user to paste into `~/.aws/credentials` in the new session if boto3 calls are needed). Keypair `HA-sing` is already uploaded to `ap-southeast-1`.
- **WHO ICD-11 OAuth2** (free, register at https://icd.who.int/icdapi) — user shared a client ID + secret earlier. Don't echo them; reference via `WHO_ICD_CLIENT_ID` / `WHO_ICD_CLIENT_SECRET` env vars.
- **Microsoft EntraID** — tenant `e5675247-08d2-407e-98e1-f2aabf5e9b18`, client `427891a5-6075-44e0-bea4-278fa5c2eb3c`, client secret redacted (user has it locally). Auth / token URLs follow the standard EntraID pattern for that tenant.

If the new session needs any of these secrets, ask the user to paste them into the terminal environment (not into a file that will be committed).

## Running EC2 demo (separate from the POCs)

- Host: `13.213.123.169` on a `t4g.small` in ap-southeast-1
- Uses LangChain + LangGraph + FAISS + Cohere Embed v4 (before the Amazon-only decision) + Claude Haiku 4.5 + Sonnet 4.5
- This is the "Version A2" variant — not what the final Version A proposes. It's a live baseline for comparison.
- Deploy code: `aws-demo/ec2/deploy.py` + `setup_instance.py`
- Teardown: resource tagging is `HA-<base64>`; listed in `aws-demo/ec2/NAMING.md`

## Open work items for the new session

### 1. Technical proposal documents — DONE

The three per-version proposal documents are now the committed source of truth:

| Doc | Covers |
|---|---|
| `docs/proposals/version_a_aws_claude.md` | Version A — AWS + Claude. Both A1+ (Nova Micro + Nova Pro) and A2 (Haiku 4.5 + Sonnet 4.5) sub-variants. |
| `docs/proposals/version_b_aws_qwen.md` | Version B — AWS + Qwen (Bedrock Sydney). Base + path B-1 (Bedrock RFT on Qwen3-32B) + optional path B-2 (SageMaker GRPO). |
| `docs/proposals/version_c_alibaba_qwen.md` | Version C — Alibaba + Qwen (SG). Recommended default. |

Each covers: executive summary, region + residency, component diagram, data pipeline, model orchestration (40-department multi-agent), fine-tuning, security, cost, performance budget, continuous ops, flagged limitations, pre-launch build, when-to-pick.

### 2. Finish the POC deploys (parallel with the proposals)

Currently `poc/aws_qwen/deploy.py` and `poc/aws_claude/deploy.py` are `--stage build-only`. They produce the FAISS indexes + Lambda zip but don't create the AWS resources. The skeleton points at the right approach (follow `aws-demo/ec2/deploy.py`). Extend to `--stage full` that creates:
- S3 bucket (CORS, encryption)
- IAM role + policy (Lambda, Bedrock, OpenSearch, Neptune, ElastiCache read)
- OpenSearch Serverless collection (vector, 2 OCUs minimum)
- Neptune Analytics graph (1 m-NCU minimum)
- ElastiCache Redis OSS single-node
- Lambda function (from the zip, Python 3.12 arm64)
- API Gateway REST API with Lambda proxy integration
- CloudFront distribution fronting both the API and the static UI
- Resource tagging `Owner=nova-health-poc-claude` or `Owner=nova-health-poc-qwen`

Both POCs ingest the same `data/clinical-trials/departments/` corpus but each has its own FAISS indexes (embedded with Titan v2, so the vectors are interchangeable — you could share a bucket, but separate keeps the demo tidy).

### 3. Consolidation complete

All 17 original architecture + compliance + pricing docs have been consolidated into the 8 new files listed above. Deletion done. Inline citations adopted per user's request — reference links appear near the specific claim they support, not bundled at end-of-section.

### 4. A pre-launch build plan document

User said "phase 1 / 2 / 3" shouldn't appear in the production docs, but the **pre-launch build** (before cut-over) genuinely is multi-week work. A `docs/deployment/pre_launch_build_plan.md` that walks week-by-week through:
- Week 1–2: provision, ingest WHO + ICD-11, run BDA + Titan + GraphRAG extraction
- Week 3–4: train the fine-tuned student (Qwen3-4B SFT or Nova Lite distillation)
- Week 5–6: integrate EHR (SMART on FHIR sandboxes), SharePoint Graph, IdP federation
- Week 7–8: red team, eval harness, guardrail tuning
- Launch: cut-over

## Key files the new session must read

Docs consolidated from 17 files into 8. Sorted by importance:

1. `README.md` — project overview, read order, decision matrix
2. `docs/overview.md` — 3-version big picture + decision tree + common design
3. `docs/proposals/version_c_alibaba_qwen.md` — **Version C (recommended default, SG-native, zero cross-region)**
4. `docs/proposals/version_a_aws_claude.md` — Version A (AWS + Claude/Nova, SG-native chat)
5. `docs/proposals/version_b_aws_qwen.md` — Version B (AWS + Qwen, Bedrock Sydney)
6. `docs/rag_and_pipelines.md` — shared RAG + ingestion + 40-department multi-agent + framework + caching + EHR
7. `docs/customization.md` — SFT / DPO / GRPO / distillation per version
8. `docs/regional_services.md` — live-verified AWS + Alibaba service availability matrix
9. `docs/compliance.md` — PDPA / HIPAA / HCSA / FDA / EU AI Act / 6-year retention
10. `docs/architecture/diagrams/aws_workflow.svg` — architecture SVG
11. `poc/README.md` — POC overview with both variants
12. `poc/aws_claude/README.md` — Version A POC, ~$165
13. `poc/aws_qwen/README.md` — Version B POC, ~$197–$804
14. `data/clinical-trials/departments/README.md` — 36 PDFs, Vietnamese → English mapping

Reference-link style across new docs: **inline citations near the specific claim**, not bundled at end-of-section. End-of-doc references kept short (authoritative sources only).

## How to continue in a fresh Kiro session

```text
Paste this at the top of the new session:

I'm continuing work on toannd021104/Nova-Health-Tech, branch
proposal/genai-architecture. Read SESSION_HANDOFF.md first, then
README.md, then docs/overview.md.

Current task: draft the three technical proposal documents
(docs/proposals/AWS_Claude_proposal.md,
docs/proposals/AWS_Qwen_proposal.md,
docs/proposals/Alibaba_Qwen_proposal.md). See SESSION_HANDOFF.md §1
for the suggested structure.

Do not re-do work already committed. Respect every constraint in
SESSION_HANDOFF.md §"User's hard constraints".
```

## Version naming conventions (keep consistent)

- **Version A** = AWS + Claude (Singapore)
- **Version A1+** = Nova Micro (fast) + Nova Pro (complex), all-Nova SG-native variant
- **Version A2** = Haiku 4.5 + Sonnet 4.5, the running EC2 demo
- **Version B** = AWS + Qwen (Bedrock Sydney, Bedrock-only serving)
- **Version B path B-1** = Bedrock RFT on Qwen3-32B (us-west-2)
- **Version B path B-2** = SageMaker GRPO on Qwen3-4B (SG residency)
- **Version C** = Alibaba + Qwen (Singapore Model Studio)

## Verdict order (SG residency, all managed services on)

| Rank | Version | ~$/mo |
|---|---|---|
| 1 | Version C | ~$2,220 |
| 2 | Version A1+ | ~$2,955 |
| 3 | Version B | ~$2,967 |
| 4 | Version A2 | ~$7,295 |

(Post-managed-GraphRAG update. Includes Bedrock KB GraphRAG on Neptune Analytics / ADBPG GraphRAG service.)

## Do not do

- Don't propose a pilot / PoC / staged rollout language for the **production** architecture. "Phase" is banned in the production docs. Keep it for pre-launch build plans and continuous operations only.
- Don't add Cohere back. Titan Embed v2 + Amazon Rerank 1.0 is the decision.
- Don't add Valkey back. Redis OSS.
- Don't add Outposts, Direct Connect, Apsara Stack, or on-prem deployments unless the user specifically asks.
- Don't commit the HA-sing.pem file, AWS keys, WHO ICD-11 creds, or EntraID secret.
- Don't commit the `reference/` folder (user's local Alibaba docs).
- Don't claim to have done work without running the relevant tool — always read files before claiming what's in them.
