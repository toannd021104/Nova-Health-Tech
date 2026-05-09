# Nova Health Tech — GenAI Clinical Assistant: Architecture Document

**Version:** 1.0
**Date:** 2026-05-09
**Author:** Cloud Architecture Team

---

## 1. Executive Summary

Nova Health Tech requires a GenAI assistant for clinical staff and hospital clients that can answer complex medical questions with citations, stay current with monthly protocol updates (WHO, internal trials), meet ≤2-second response times for emergency care, and remain fully HIPAA-compliant with complete audit trails.

**Core architectural choices:**
- **Cloud:** AWS (HIPAA BAA, Bedrock, HealthLake, mature compliance tooling)
- **LLM:** Claude 3.5 Sonnet via Amazon Bedrock (HIPAA-eligible, no customer data training)
- **Knowledge retrieval:** RAG (not fine-tuning) — auditability, monthly update cadence, source citations
- **Vector DB:** Amazon OpenSearch Serverless with vector engine
- **Orchestration:** LangChain on ECS Fargate + Step Functions for the data pipeline
- **Performance:** ElastiCache Redis + Bedrock Provisioned Throughput + hybrid BM25+vector retrieval

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          NOVA HEALTH TECH — AWS CLOUD                           │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                        DATA INGESTION PIPELINE                           │   │
│  │                                                                          │   │
│  │  Legacy PDFs          WHO API (monthly)    Internal Clinical Trials      │   │
│  │      │                     │                        │                    │   │
│  │      ▼                     ▼                        ▼                    │   │
│  │  S3 Raw Bucket        EventBridge             S3 PHI Bucket              │   │
│  │  (KMS-CMK-A)          Scheduler               (KMS-CMK-B, isolated)     │   │
│  │      │                     │                        │                    │   │
│  │      ▼                     ▼                        ▼                    │   │
│  │  AWS Textract         Lambda WHO             Lambda PDF (Textract)       │   │
│  │  (PDF→text)           Ingestor               with Macie scan             │   │
│  │      │                     │                        │                    │   │
│  │      └──────────┬──────────┘                        │                    │   │
│  │                 ▼                                    ▼                    │   │
│  │         Step Functions                    Step Functions (PHI)           │   │
│  │         (chunk→embed→index)               (chunk→embed→PHI index)       │   │
│  │                 │                                    │                    │   │
│  │                 ▼                                    ▼                    │   │
│  │         Titan Embed v2                    Titan Embed v2                 │   │
│  │         (via Bedrock)                     (via Bedrock)                  │   │
│  │                 │                                    │                    │   │
│  │                 ▼                                    ▼                    │   │
│  │       OpenSearch: public-index              OpenSearch: phi-index        │   │
│  │       (protocols, WHO, PubMed)              (clinical trials — RBAC)    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                       QUERY / INFERENCE PATH                             │   │
│  │                                                                          │   │
│  │  EHR System / Clinical UI                                               │   │
│  │         │                                                                │   │
│  │         ▼                                                                │   │
│  │  CloudFront + WAF                                                       │   │
│  │         │                                                                │   │
│  │         ▼                                                                │   │
│  │  API Gateway (REST)  ─── Cognito Authorizer (RBAC) ───┐                 │   │
│  │         │                                              │                 │   │
│  │         ▼                                             IAM Role           │   │
│  │  ECS Fargate                                    (controls phi-index      │   │
│  │  (LangChain RAG)                                 access by role)        │   │
│  │         │                                                                │   │
│  │    ┌────┴─────────────────────┐                                          │   │
│  │    ▼                          ▼                                          │   │
│  │  ElastiCache Redis      OpenSearch                                       │   │
│  │  (response cache)       Hybrid Search                                   │   │
│  │  (query cache)          (BM25 + kNN)                                    │   │
│  │                               │                                          │   │
│  │                         [retrieved chunks]                               │   │
│  │                               │                                          │   │
│  │                               ▼                                          │   │
│  │                    Amazon Bedrock                                        │   │
│  │                    Claude 3.5 Sonnet                                     │   │
│  │                    (Provisioned Throughput)                              │   │
│  │                    + Bedrock Guardrails                                  │   │
│  │                               │                                          │   │
│  │                      [streamed response]                                 │   │
│  │                               │                                          │   │
│  │                    CloudWatch + X-Ray                                    │   │
│  │                    + Audit Log (S3)                                      │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │                       SECURITY & COMPLIANCE                              │   │
│  │  CloudTrail  │  GuardDuty  │  Macie  │  AWS Config  │  Security Hub     │   │
│  │  KMS CMK (per data class)  │  VPC Private Subnets  │  PrivateLink       │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Component Decisions

### 3.1 Cloud Provider

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| AWS | Azure, GCP | AWS offers HIPAA BAA for 170+ services including Bedrock. Amazon HealthLake provides native FHIR R4 for EHR integration. Macie for automated PHI/PII detection in S3. GuardDuty for threat detection. Bedrock provides Claude models (best medical reasoning) without data leaving the AWS environment. Mature CloudTrail audit logging. |

**Why not Azure?** Azure has strong healthcare compliance but lacks a comparable managed LLM service with Claude models and has weaker vector search integration. Azure OpenAI has HIPAA support but requires more custom integration.

**Why not GCP?** Vertex AI Gemini is capable but GCP's HIPAA service scope is narrower, and HealthLake/Macie equivalents require more custom work.

---

### 3.2 LLM Choice

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| Claude 3.5 Sonnet via Amazon Bedrock | GPT-4o (Azure OpenAI), Gemini 1.5 Pro, Llama 3 (self-hosted), Mistral | Claude 3.5 Sonnet has best-in-class medical reasoning and instruction following. Bedrock is HIPAA-eligible — AWS does NOT train on customer prompts/completions. 200K token context window handles long clinical documents. Bedrock Guardrails blocks harmful medical advice. Provisioned Throughput gives deterministic low-latency. |

**Why not self-hosted Llama?** Would require GPU instances (p4d/p3), complex MLOps, no HIPAA BAA for model weights, harder to maintain medical accuracy, significant Ops overhead.

**Why not fine-tuning?** See Section 3.3.

---

### 3.3 RAG vs Fine-Tuning

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| RAG (Retrieval-Augmented Generation) | Full fine-tune, LoRA fine-tune, in-context learning only | RAG wins on all key criteria: (1) WHO updates monthly — fine-tune retraining cycle is weeks, RAG index update is hours; (2) Auditability — RAG returns source citations per answer, essential for clinical compliance; (3) PHI isolation — PHI-containing trial data never enters training data, only accessed at query time with RBAC; (4) Consistent tone achieved via prompt templates (Bedrock Prompt Management) without retraining; (5) Lower cost and ops burden. |

**Fine-tuning tradeoff documented:** Fine-tuning would improve domain vocabulary adaptation and reduce prompt length. If future benchmarks show RAG accuracy below threshold, a LoRA adapter on a small model could be combined with RAG (RAG+FT hybrid). Not implemented now — premature optimization.

---

### 3.4 Vector Database

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| Amazon OpenSearch Serverless (vector engine) | Pinecone, Weaviate, pgvector (RDS), Qdrant on EC2 | OpenSearch Serverless: zero infrastructure management, auto-scales to zero in dev, native AWS IAM integration for RBAC at index level, hybrid BM25+kNN search in a single query (critical for medical term precision), KMS encryption, VPC endpoint support, no separate vendor HIPAA BAA needed. |

**Why not Pinecone?** Excellent vector DB but requires a separate HIPAA BAA, adds a vendor, and doesn't support hybrid keyword+vector search natively.

**Why not pgvector?** Requires RDS instance management, poor horizontal scaling for large embedding datasets, no native hybrid search.

---

### 3.5 Embedding Model

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| Amazon Titan Embeddings v2 (1536-dim) via Bedrock | OpenAI text-embedding-3-large, Cohere Embed v3 | Titan Embeddings v2 runs within the same Bedrock HIPAA-eligible boundary — embeddings are generated without data leaving AWS. No additional vendor contract. 1536 dimensions balance quality and storage cost. Supports chunk sizes up to 8192 tokens. |

---

### 3.6 PDF Extraction (Legacy Documents)

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| AWS Textract | Apache PDFBox (custom Lambda), pdfminer, Azure Document Intelligence | Textract handles inconsistent tagging, scanned PDFs (OCR), tables, and forms — common in legacy clinical PDFs. Managed service with async job API for large documents. No server to manage. Textract Medical can additionally identify medical entities. |

---

### 3.7 Pipeline Orchestration

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| AWS Step Functions | Apache Airflow (MWAA), AWS Glue Workflows, EventBridge Pipes | Step Functions provides visual audit trail per document ingestion — each state transition is logged. Native retry logic, error handling, and parallel processing. Serverless. Visual state machine is auditable by compliance teams. EventBridge Scheduler triggers monthly WHO polling. |

---

### 3.8 Inference Compute

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| ECS Fargate (containers) | Lambda, EKS, EC2 ASG | Fargate: no EC2 management, per-second billing, containers for reproducible LangChain environment, scales to zero. Lambda has 15-min timeout (too short for complex RAG chains), cold-start latency issues for ≤2s requirement. EKS is over-engineered for this workload size. |

---

### 3.9 Caching (≤2s SLA)

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| ElastiCache Redis (Serverless) | DynamoDB DAX, in-memory application cache, CloudFront caching | Redis: sub-millisecond reads, semantic query caching (hash query embedding → cached response), TTL-based expiry aligned to update schedules. Emergency queries (e.g. "sepsis protocol") pre-warmed. Redis Serverless eliminates capacity planning. |

**Performance budget for ≤2s:**
- Redis cache hit: ~50ms total (cache lookup + response)
- Cache miss path: Embedding (100ms) + OpenSearch hybrid query (200ms) + Bedrock streaming first-token (800ms) + network (100ms) = ~1.2s for p50, ~1.8s for p95 with Provisioned Throughput
- Bedrock streaming: tokens stream to client as generated, perceived latency < actual completion time

---

### 3.10 Security & Compliance

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| KMS CMK per data class + VPC PrivateLink + Cognito RBAC + CloudTrail + Macie + GuardDuty + Security Hub + AWS Config | Bring-your-own HSM, third-party SIEM | Full AWS-native security stack keeps everything within the HIPAA BAA boundary. Two KMS CMKs: one for public clinical content (WHO, protocols) and one for PHI data (clinical trials). Separate S3 buckets and OpenSearch indexes per data class. Cognito groups map to IAM roles that control which OpenSearch indexes are queried. All API calls logged to CloudTrail with S3 immutable storage. Macie scans S3 for PHI/PII drift. |

---

### 3.11 API & EHR Integration

| Chosen | Alternatives Considered | Rationale |
|--------|------------------------|-----------|
| API Gateway (REST) + Amazon HealthLake (FHIR R4) | GraphQL (AppSync), custom FHIR server, HL7 v2 | REST API Gateway provides throttling, WAF integration, request validation, and usage plans per client (hospital). HealthLake provides a HIPAA-eligible FHIR R4 datastore for EHR patient context enrichment without custom ETL. |

---

## 4. Summary Table

| Component | Service/Tool | Terraform Resource | Rationale |
|-----------|-------------|-------------------|-----------|
| Cloud provider | AWS | `provider "aws"` | HIPAA BAA, Bedrock, HealthLake |
| VPC & networking | AWS VPC | `aws_vpc`, `aws_subnet` | Network isolation, private subnets |
| LLM inference | Amazon Bedrock (Claude 3.5 Sonnet) | `aws_bedrock_*` | HIPAA-eligible, no data training, best medical reasoning |
| Embeddings | Amazon Titan Embeddings v2 | Bedrock API call | Same HIPAA boundary as inference |
| Vector DB | OpenSearch Serverless | `aws_opensearchserverless_collection` | Hybrid search, IAM RBAC, managed |
| PDF extraction | AWS Textract | `aws_iam_role` (Lambda calls Textract API) | Handles legacy/scanned PDFs |
| Pipeline orchestration | AWS Step Functions | `aws_sfn_state_machine` | Visual audit trail, retry logic |
| WHO ingestion trigger | EventBridge Scheduler | `aws_scheduler_schedule` | Monthly cron, serverless |
| RAG orchestration | LangChain on ECS Fargate | `aws_ecs_task_definition` | Stateless containers, scales |
| Response cache | ElastiCache Redis Serverless | `aws_elasticache_serverless_cache` | Sub-ms reads, TTL expiry |
| Auth & RBAC | Amazon Cognito | `aws_cognito_user_pool` | User groups → IAM roles |
| API layer | API Gateway + WAF | `aws_api_gateway_rest_api`, `aws_wafv2_web_acl` | Throttling, auth, WAF |
| CDN | CloudFront | `aws_cloudfront_distribution` | Low-latency UI delivery |
| PHI storage | S3 (isolated bucket) | `aws_s3_bucket` + `aws_kms_key` | Separate KMS CMK, Macie-scanned |
| Public content storage | S3 (standard bucket) | `aws_s3_bucket` | Protocols, WHO, PubMed |
| Audit logging | CloudTrail | `aws_cloudtrail` | Immutable API audit trail |
| PHI/PII detection | Amazon Macie | `aws_macie2_account` | Automated PHI drift detection |
| Threat detection | GuardDuty | `aws_guardduty_detector` | ML-based threat detection |
| Compliance rules | AWS Config | `aws_config_configuration_recorder` | Continuous compliance checks |
| Security posture | Security Hub | `aws_securityhub_account` | Aggregated findings |
| Observability | CloudWatch + X-Ray | `aws_cloudwatch_dashboard` | Latency tracking, tracing |
| CI/CD | GitHub Actions + CodePipeline | `aws_codepipeline` | GitOps workflow |
| EHR integration | Amazon HealthLake (FHIR R4) | `aws_healthlake_fhir_datastore` | Native FHIR, HIPAA-eligible |
| Secrets | AWS Secrets Manager | `aws_secretsmanager_secret` | API keys, DB credentials |

---

## 5. Data Flow Narratives

### 5.1 Document Ingestion (PDF)
1. Clinical staff uploads PDF to `s3://nova-raw-{env}` (public-content bucket)
2. S3 event triggers Step Functions state machine
3. State 1: Lambda calls Textract `start_document_analysis` → async job
4. State 2: Lambda polls Textract job → extracts text + structure
5. State 3: Lambda chunks text (512 tokens, 50-token overlap)
6. State 4: Lambda calls Bedrock Titan Embeddings for each chunk
7. State 5: Lambda indexes chunk + embedding into OpenSearch `nova-public` collection
8. State 6: Lambda writes metadata + audit record to DynamoDB

### 5.2 WHO API Ingestion (Monthly)
1. EventBridge Scheduler fires on 1st of each month at 02:00 UTC
2. Lambda `who-ingestor` calls WHO API, paginates all updated protocols
3. Diffs against DynamoDB metadata table (last-seen hashes)
4. New/updated documents enter same chunking→embedding→indexing pipeline
5. Deleted protocols tombstoned in OpenSearch (not deleted — audit requirement)

### 5.3 Clinical Trial Ingestion (PHI path)
1. Upload to `s3://nova-phi-{env}` (PHI-isolated bucket, separate KMS CMK)
2. Macie job scans upload for PHI classification
3. Step Functions PHI pipeline: Textract → chunk → embed → index into `nova-phi` OpenSearch index
4. OpenSearch index-level access policy restricts to `role/phi-researcher` IAM role only

### 5.4 Query Path (Emergency Care ≤2s)
1. Clinical user authenticates via Cognito → JWT token with group claims
2. Request hits CloudFront → WAF inspection → API Gateway
3. Cognito Lambda authorizer validates JWT, maps group to IAM role
4. ECS Fargate RAG container:
   a. Hash query → check Redis cache → **cache hit: return in ~50ms**
   b. Cache miss: call Bedrock Titan Embeddings to embed query (~100ms)
   c. OpenSearch hybrid BM25+kNN query (public index + phi index if authorized) (~200ms)
   d. Build prompt with top-k chunks + system prompt (tone template)
   e. Call Bedrock Claude 3.5 Sonnet with streaming enabled
   f. First token returns ~800ms → stream to client → cache full response in Redis
5. Response includes source citations (document ID, chunk ID, confidence score)
6. All interactions logged: CloudWatch Logs → CloudTrail → S3 audit bucket

---

## 6. Compliance & HIPAA Controls

| Control | Implementation |
|---------|----------------|
| Data encryption at rest | KMS CMK for all S3, OpenSearch, ElastiCache, CloudTrail |
| Data encryption in transit | TLS 1.3 enforced at API Gateway, CloudFront, all VPC endpoints |
| PHI isolation | Separate S3 bucket, OpenSearch index, KMS key, IAM role for PHI data |
| Access control | Cognito → IAM role assumption, least-privilege policies |
| Audit logging | CloudTrail (all API calls), CloudWatch Logs (all application events) |
| Audit log integrity | CloudTrail log file validation enabled, S3 Object Lock (WORM) |
| PHI detection | Amazon Macie on all S3 buckets with automated alerting |
| Threat detection | GuardDuty with findings routed to Security Hub |
| Vulnerability management | ECR image scanning, Inspector for ECS tasks |
| Business Associate Agreement | AWS BAA covers all services used |
| Minimum necessary | RBAC ensures clinical staff only access their authorized data subset |
| Breach notification support | CloudTrail + Macie findings enable 60-day HIPAA breach notification |

---

## 7. Performance Architecture (≤2s SLA)

```
P50 Response Time Budget (cache miss, emergency query):
├── DNS + TLS handshake (CloudFront):      30ms
├── WAF inspection:                         10ms
├── API Gateway + authorizer:              50ms
├── ECS Fargate (LangChain overhead):      20ms
├── Redis cache check (miss):              5ms
├── Bedrock Titan Embeddings (query):     100ms
├── OpenSearch hybrid query (top-5):      150ms
├── Prompt construction:                    10ms
├── Bedrock Claude first token:            600ms  ← streaming starts here
├── Network transmission:                  25ms
└── TOTAL to first token:                ~1000ms ✓

P95 with Provisioned Throughput:          ~1800ms ✓
Cache hit path:                            ~50ms  ✓
```

**Optimizations:**
- Bedrock Provisioned Throughput: guaranteed tokens/minute, no throttling
- Redis semantic cache: hash(embedding) → cached response, 1-hour TTL for stable protocols
- OpenSearch: pre-warmed collection, optimized k=5 retrieval (not k=20)
- ECS task pre-scaling: min 2 tasks always running (no cold start)
- Streaming: client receives tokens as generated, perceived latency << actual completion

---

## 8. CI/CD Pipeline

```
GitHub PR → GitHub Actions (lint, test, tfsec) → merge to main
→ CodePipeline triggered → CodeBuild (terraform plan) → Manual approval (prod)
→ CodeBuild (terraform apply) → ECR image build + push → ECS rolling deploy
→ CloudWatch alarm check → auto-rollback if error rate spikes
```

---

## 9. Multi-Environment Strategy

| Setting | dev | prod |
|---------|-----|------|
| OpenSearch OCU | 1 | 4 |
| ECS min tasks | 1 | 2 |
| ECS max tasks | 3 | 20 |
| Bedrock throughput | on-demand | provisioned |
| Redis | serverless (min 0) | serverless (min cache units) |
| S3 versioning | enabled | enabled + Object Lock |
| CloudTrail | single-region | multi-region + org trail |
| GuardDuty | enabled | enabled + S3 protection |
| Retention (logs) | 30 days | 7 years (HIPAA) |
