# Nova Health Tech — AWS GenAI Clinical Assistant

HIPAA-compliant RAG system for clinical staff. Answers complex medical questions with source citations, stays current with monthly protocol updates, and meets ≤2s response time for emergency care.

**Stack:** Claude 3.5 Sonnet (Bedrock) · OpenSearch Serverless · ECS Fargate (LangChain) · ElastiCache Redis · Cognito · Step Functions · Terraform

---

## Prerequisites

| Tool | Version |
|------|---------|
| Terraform | ≥ 1.6 |
| AWS CLI | ≥ 2.x, configured with credentials |
| Docker | For building the RAG service image |

Bedrock model access must be enabled manually in the AWS console before applying:
- `anthropic.claude-3-5-sonnet-20241022-v2:0`
- `amazon.titan-embed-text-v2:0`

> Console → Bedrock → Model access → Request access

---

## Quickstart

### 1. Bootstrap backend + init Terraform

```bash
chmod +x scripts/init.sh

# Set your AWS profile in the environment (never hardcode in code)
export AWS_PROFILE=<your-profile>

# dev
./scripts/init.sh dev <aws_account_id> us-east-1

# prod
./scripts/init.sh prod <aws_account_id> us-east-1
```

This creates the S3 state bucket (`nova-terraform-state-<account_id>`), the DynamoDB lock table (`nova-terraform-locks`), and runs `terraform init` + `terraform validate`.

**Bootstrap output:**
```
========================================================
 Nova Health Tech — Terraform Bootstrap
 Environment   : dev
 AWS Account   : 123456789012
 AWS Region    : us-east-1
 State Bucket  : nova-terraform-state-123456789012
 Lock Table    : nova-terraform-locks
========================================================
Checking AWS credentials... OK.
Creating Terraform state bucket: s3://nova-terraform-state-123456789012
  Bucket created and configured.
Creating DynamoDB lock table: nova-terraform-locks
  Waiting for table to become active...
  Lock table created.

Initializing Terraform in .../terraform/envs/dev...
Initializing modules...
Initializing the backend...
Terraform has been successfully initialized!

Running terraform validate...
Success! The configuration is valid.

========================================================
 Bootstrap complete for environment: dev
 ...
========================================================
```

---

### 2. Create `terraform.tfvars`

**`terraform/envs/dev/terraform.tfvars`**
```hcl
aws_account_id = "123456789012"
aws_region     = "us-east-1"
alert_email    = "oncall@your-org.com"
# container_image defaults to amazonlinux placeholder for first apply
```

**`terraform/envs/prod/terraform.tfvars`**
```hcl
aws_account_id  = "123456789012"
aws_region      = "us-east-1"
alert_email     = "oncall@your-org.com"
container_image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/nova-rag-api:v1.0.0"
callback_urls   = ["https://app.nova-health.com/callback"]
logout_urls     = ["https://app.nova-health.com/logout"]
```

---

### 3. Plan

```bash
cd terraform/envs/dev
terraform plan -var-file=terraform.tfvars
```

### 4. Apply

```bash
terraform apply -var-file=terraform.tfvars
```

Type `yes` when prompted. First apply takes ~15–20 minutes (OpenSearch Serverless collection creation is the long pole).

---

## Terraform Outputs

After a successful apply, Terraform prints the following:

### dev

```
Outputs:

api_invoke_url           = "https://<id>.execute-api.us-east-1.amazonaws.com/dev"
cognito_auth_domain      = "nova-dev-<hash>.auth.us-east-1.amazoncognito.com"
cognito_app_client_id    = "abc123xyz"
ecr_repository_url       = "123456789012.dkr.ecr.us-east-1.amazonaws.com/nova-rag-api-dev"
ecs_cluster_name         = "nova-dev-cluster"
public_content_bucket_id = "nova-public-content-dev-123456789012"

# sensitive — retrieve with:
#   terraform output redis_endpoint
#   terraform output opensearch_public_endpoint
#   terraform output phi_bucket_id
redis_endpoint             = <sensitive>
opensearch_public_endpoint = <sensitive>
phi_bucket_id              = <sensitive>
```

### prod (additional outputs)

```
cloudtrail_arn           = "arn:aws:cloudtrail:us-east-1:123456789012:trail/nova-prod-trail"
guardduty_detector_id    = "abc1234567890"
cognito_user_pool_id     = "us-east-1_XXXXXXXXX"
opensearch_phi_endpoint  = <sensitive>
provisioned_model_arn    = "arn:aws:bedrock:us-east-1::provisioned-model/..."
```

Retrieve sensitive outputs:
```bash
terraform output -raw redis_endpoint
terraform output -raw opensearch_public_endpoint
terraform output -raw phi_bucket_id
```

---

## Environments

| Setting | dev | prod |
|---------|-----|------|
| OpenSearch OCU | 1 | 4 |
| ECS min / max tasks | 1 / 3 | 2 / 20 |
| Bedrock throughput | on-demand | provisioned |
| Redis min cache | 0 GB | reserved |
| S3 Object Lock | off | on (WORM, 7 yr) |
| CloudTrail | single-region | multi-region |
| Macie | off | on |
| Log retention | 30 days | 7 years |
| API throttle | 20 rps / 50 burst | 200 rps / 500 burst |

---

## Project Structure

```
.
├── docs/
│   ├── architecture.md      # Full architecture + component decisions
│   └── decisions.md         # Decision log (all 15 choices resolved)
├── envs/                    # Env-specific var files (gitignored secrets)
│   ├── dev/
│   └── prod/
├── modules/                 # Reusable Terraform modules
│   ├── api/                 # API Gateway + WAF
│   ├── bedrock/             # Guardrails + Provisioned Throughput + Secrets
│   ├── cache/               # ElastiCache Redis Serverless
│   ├── cognito/             # User pool + RBAC groups
│   ├── compute/             # ECS Fargate + ALB + ECR
│   ├── data_pipeline/       # Lambda + Step Functions + EventBridge
│   ├── iam/                 # All IAM roles and policies
│   ├── monitoring/          # CloudWatch dashboards + alarms + X-Ray
│   ├── networking/          # VPC + subnets + security groups
│   ├── opensearch/          # Serverless collections (public + PHI)
│   ├── security/            # CloudTrail + GuardDuty + Macie + Config + Security Hub
│   └── storage/             # S3 buckets + KMS CMKs + DynamoDB metadata table
├── scripts/
│   └── init.sh              # Bootstrap script (backend bucket + lock table + tf init)
└── terraform/
    └── envs/
        ├── dev/             # Dev root module (main.tf, variables.tf, outputs.tf)
        └── prod/            # Prod root module
```

---

## Destroy

```bash
# dev only — never run destroy on prod without explicit sign-off
cd terraform/envs/dev
terraform destroy -var-file=terraform.tfvars
```

> **Note:** OpenSearch Serverless collections and S3 buckets with versioning may require manual cleanup if non-empty.
