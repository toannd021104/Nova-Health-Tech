# Resource Naming Map

All resources are named `HA-<base64url(logical-name)>` (padding stripped). This lets anyone trace a console-visible name back to its purpose.

## PoC Version A — AWS + Claude (EC2 + Bedrock KB)

| Logical name | Encoded tag | AWS resource | Region |
|---|---|---|---|
| `vpc-nova` | `HA-dnBjLW5vdmE` | VPC (10.20.0.0/16) | ap-southeast-1 |
| `subnet-pub` | `HA-c3VibmV0LXB1Yg` | Public subnet (10.20.1.0/24) | ap-southeast-1a |
| `igw-nova` | `HA-aWd3LW5vdmE` | Internet Gateway | - |
| `rt-pub` | `HA-cnQtcHVi` | Public route table | - |
| `sg-web` | `HA-c2ctd2Vi` | Security Group (SSH 22 + HTTP 80 + HTTPS 443) | - |
| `ec2-bedrock` | `HA-ZWMyLWJlZHJvY2s` | IAM role attached to EC2 (Bedrock + S3 read) | global |
| `s3-bucket` | `ha-czmtynvja2v0-<acct>` (lowercased, suffixed) | S3 bucket for RAG source docs | ap-southeast-1 |
| `kb-src` | `HA-a2Itc3Jj` | S3 prefix for RAG ingestion (inside the bucket) | - |
| `ec2-nova` | `HA-ZWMyLW5vdmE` | EC2 instance (t4g.small) | ap-southeast-1a |
| `eip-nova` | `HA-ZWlwLW5vdmE` | Elastic IP attached to the instance | ap-southeast-1 |

## PoC Version B — AWS + Qwen (SageMaker Fine-tuning)

| Logical name | Encoded tag | AWS resource | Region |
|---|---|---|---|
| `sm-training-phase1` | `HA-c20tdHJhaW5pbmctcGhhc2Ux` | SageMaker Training Job — Phase 1 (200 steps, ~30 min, ml.g4dn.2xlarge) | ap-southeast-1 |
| `sm-training-phase2` | `HA-c20tdHJhaW5pbmctcGhhc2Uy` | SageMaker Training Job — Phase 2 (3 epochs, full, ml.g4dn.2xlarge) | ap-southeast-1 |
| `qwen-ft-data-p1` | `HA-cXdlbi1mdC1kYXRhLXAx` | S3 prefix: distillation JSONL phase 1 (inside existing bucket) | ap-southeast-1 |
| `qwen-ft-data-p2` | `HA-cXdlbi1mdC1kYXRhLXAy` | S3 prefix: distillation JSONL phase 2 (inside existing bucket) | ap-southeast-1 |
| `qwen-ft-source` | `HA-cXdlbi1mdC1zb3VyY2U` | S3 prefix: training entry script tarball | ap-southeast-1 |
| `qwen-ft-output-p1` | `HA-cXdlbi1mdC1vdXRwdXQtcDE` | S3 prefix: trained model artifact phase 1 | ap-southeast-1 |
| `qwen-ft-output-p2` | `HA-cXdlbi1mdC1vdXRwdXQtcDI` | S3 prefix: trained model artifact phase 2 | ap-southeast-1 |
| `sm-exec-role` | `HA-c20tZXhlYy1yb2xl` | IAM role: AmazonSageMaker-ExecutionRole-20260313T100722 (existing, reused) | global |
| `cw-sm-training` | `HA-Y3ctc20tdHJhaW5pbmc` | CloudWatch log group: /aws/sagemaker/TrainingJobs (auto-created by SM) | ap-southeast-1 |
| `ec2-qwen` | `HA-ZWMyLXF3ZW4` | EC2 instance (t4g.small) — Qwen PoC web server | ap-southeast-1a |
| `eip-qwen` | `HA-ZWlwLXF3ZW4` | Elastic IP: 54.179.152.27 | ap-southeast-1 |
| `sm-student-model` | `HA-c20tc3R1ZGVudC1tb2RlbA` | SageMaker Model (Qwen3-4B + LoRA adapter) | ap-southeast-1 |
| `sm-student-epc` | `HA-c20tc3R1ZGVudC1lcGM` | SageMaker EndpointConfig (ml.g4dn.xlarge) | ap-southeast-1 |
| `sm-student-ep` | `HA-c20tc3R1ZGVudC1lcA` | SageMaker Endpoint — student inference ($0.74/hr) | ap-southeast-1 |

## How to reproduce the names

```python
import base64
def tag(name: str) -> str:
    return "HA-" + base64.urlsafe_b64encode(name.encode()).decode().rstrip("=")
```

`tag("vpc-nova")` → `HA-dnBjLW5vdmE`.
`tag("sm-training-phase1")` → `HA-c20tdHJhaW5pbmctcGhhc2Ux`.

## What isn't created (per user request — "no log, firewall, VPN, DR")

- No CloudTrail, CloudWatch alarms, or log aggregation.
- No AWS WAF (only a simple Security Group restricts inbound).
- No Site-to-Site VPN.
- No DR region / snapshot.
- No OpenSearch Serverless (to avoid its cost floor). We use a local FAISS index in the EC2 instance instead — fine for demo.
