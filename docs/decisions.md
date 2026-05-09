# Nova Health Tech — Architecture Decision Log

**Project:** AWS GenAI Clinical Assistant
**Date:** 2026-05-09
**Status:** All decisions resolved ✓

---

| # | Decision | Chosen | Rejected | Why |
|---|----------|--------|----------|-----|
| 1 | **Cloud provider** | AWS | Azure, GCP | HIPAA BAA covers 170+ services incl. Bedrock; HealthLake for FHIR; Macie + GuardDuty native |
| 2 | **LLM** | Claude 3.5 Sonnet (Bedrock) | GPT-4o, Gemini 1.5 Pro, Llama 3 | Best medical reasoning; Bedrock = HIPAA-eligible; no customer data training; 200K ctx; Provisioned Throughput |
| 3 | **Knowledge strategy** | RAG | Fine-tune, LoRA, in-context only | WHO updates monthly (RAG = hours, fine-tune = weeks); source citations required for compliance; PHI never enters training data |
| 4 | **Vector DB** | OpenSearch Serverless | Pinecone, Weaviate, pgvector | Native hybrid BM25+kNN; IAM RBAC at index level; no extra vendor BAA; scales to zero in dev |
| 5 | **Embedding model** | Titan Embeddings v2 (Bedrock) | OpenAI text-embedding-3, Cohere Embed v3 | Same HIPAA boundary as inference; no extra vendor; 1536-dim; 8K token chunks |
| 6 | **PDF extraction** | AWS Textract | PDFBox Lambda, pdfminer | Handles scanned/OCR PDFs; async API for large docs; Textract Medical for entity detection |
| 7 | **Pipeline orchestration** | Step Functions | Airflow (MWAA), Glue Workflows | Visual audit trail per document; native retry/error handling; serverless; auditable by compliance teams |
| 8 | **Inference compute** | ECS Fargate | Lambda, EKS, EC2 ASG | No 15-min timeout (Lambda fails for complex chains); no EC2 mgmt; reproducible containers; scales to zero |
| 9 | **Response cache** | ElastiCache Redis Serverless | DynamoDB DAX, app-layer cache | Sub-ms reads; semantic cache (hash embedding → response); TTL aligned to update cadence; no capacity planning |
| 10 | **Auth & RBAC** | Cognito + IAM roles | Custom auth, Auth0 | Cognito groups → IAM role assumption → OpenSearch index-level access; native AWS integration |
| 11 | **PHI isolation** | Separate S3 bucket + KMS CMK + OpenSearch index | Single bucket with prefix | Separate KMS key (CMK-B); Macie scans PHI bucket; index-level RBAC; blast radius contained |
| 12 | **API layer** | API Gateway (REST) + WAF | AppSync (GraphQL), ALB direct | Per-client throttling; WAF integration; Cognito authorizer; request validation; usage plans per hospital |
| 13 | **Audit logging** | CloudTrail + S3 Object Lock | Third-party SIEM | Immutable WORM log storage; 7-year retention (HIPAA); log file validation; all API calls captured |
| 14 | **EHR integration** | Amazon HealthLake (FHIR R4) | Custom FHIR server, HL7 v2 | Managed HIPAA-eligible FHIR R4 datastore; no custom ETL; native AWS IAM |
| 15 | **CI/CD** | GitHub Actions + CodePipeline | Jenkins, CircleCI | tfsec in PR gate; manual approval for prod apply; auto-rollback on CloudWatch alarm spike |

---

## PHI Data Boundary

```
PHI path:  S3 (CMK-B) → Macie scan → Step Functions → Titan Embed → OpenSearch phi-index
                                                                              ↑
                                                              IAM: role/phi-researcher only

Public path: S3 (CMK-A) → Textract → Step Functions → Titan Embed → OpenSearch public-index
                                                                              ↑
                                                              IAM: all authenticated roles
```

## ≤2s SLA Budget (resolved)

| Path | Latency |
|------|---------|
| Cache hit | ~50ms |
| Cache miss p50 | ~1,000ms |
| Cache miss p95 | ~1,800ms |

Achieved via: Provisioned Throughput + Redis semantic cache + OpenSearch k=5 + ECS min 2 tasks + Bedrock streaming.
