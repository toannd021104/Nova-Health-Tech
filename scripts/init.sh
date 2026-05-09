#!/usr/bin/env bash
# =============================================================================
# Nova Health Tech — Terraform Bootstrap Script
# Creates the S3 backend bucket, DynamoDB lock table, and sets up prerequisites.
#
# Usage:
#   ./scripts/init.sh <environment> <aws_account_id> [aws_region]
#
# Example:
#   ./scripts/init.sh dev 123456789012 us-east-1
#   ./scripts/init.sh prod 123456789012 us-east-1
# =============================================================================

set -euo pipefail

# ── Args ─────────────────────────────────────────────────────────────────────
ENV="${1:?Usage: $0 <environment> <aws_account_id> [aws_region]}"
ACCOUNT_ID="${2:?AWS account ID required}"
REGION="${3:-us-east-1}"

STATE_BUCKET="nova-terraform-state-${ACCOUNT_ID}"
LOCK_TABLE="nova-terraform-locks"
PROJECT="nova"

echo "========================================================"
echo " Nova Health Tech — Terraform Bootstrap"
echo " Environment   : ${ENV}"
echo " AWS Account   : ${ACCOUNT_ID}"
echo " AWS Region    : ${REGION}"
echo " State Bucket  : ${STATE_BUCKET}"
echo " Lock Table    : ${LOCK_TABLE}"
echo "========================================================"

# ── Validate environment ──────────────────────────────────────────────────────
if [[ "${ENV}" != "dev" && "${ENV}" != "prod" ]]; then
  echo "ERROR: environment must be 'dev' or 'prod'" >&2
  exit 1
fi

# ── Check dependencies ────────────────────────────────────────────────────────
for cmd in aws terraform; do
  if ! command -v "${cmd}" &>/dev/null; then
    echo "ERROR: '${cmd}' is not installed or not in PATH" >&2
    exit 1
  fi
done

echo ""
echo "Checking AWS credentials..."
aws sts get-caller-identity --region "${REGION}" > /dev/null
echo "AWS credentials OK."

# ── Create S3 state backend bucket ───────────────────────────────────────────
echo ""
echo "Creating Terraform state bucket: s3://${STATE_BUCKET}"

if aws s3api head-bucket --bucket "${STATE_BUCKET}" --region "${REGION}" 2>/dev/null; then
  echo "  Bucket already exists — skipping creation."
else
  aws s3api create-bucket \
    --bucket "${STATE_BUCKET}" \
    --region "${REGION}" \
    $([ "${REGION}" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=${REGION}" || echo "")

  # Enable versioning
  aws s3api put-bucket-versioning \
    --bucket "${STATE_BUCKET}" \
    --versioning-configuration Status=Enabled

  # Enable server-side encryption
  aws s3api put-bucket-encryption \
    --bucket "${STATE_BUCKET}" \
    --server-side-encryption-configuration '{
      "Rules": [{
        "ApplyServerSideEncryptionByDefault": {
          "SSEAlgorithm": "aws:kms"
        },
        "BucketKeyEnabled": true
      }]
    }'

  # Block all public access
  aws s3api put-public-access-block \
    --bucket "${STATE_BUCKET}" \
    --public-access-block-configuration '{
      "BlockPublicAcls": true,
      "IgnorePublicAcls": true,
      "BlockPublicPolicy": true,
      "RestrictPublicBuckets": true
    }'

  # Enforce TLS
  aws s3api put-bucket-policy \
    --bucket "${STATE_BUCKET}" \
    --policy "{
      \"Version\": \"2012-10-17\",
      \"Statement\": [{
        \"Sid\": \"DenyNonHTTPS\",
        \"Effect\": \"Deny\",
        \"Principal\": \"*\",
        \"Action\": \"s3:*\",
        \"Resource\": [
          \"arn:aws:s3:::${STATE_BUCKET}\",
          \"arn:aws:s3:::${STATE_BUCKET}/*\"
        ],
        \"Condition\": {
          \"Bool\": { \"aws:SecureTransport\": \"false\" }
        }
      }]
    }"

  echo "  Bucket created and configured."
fi

# ── Create DynamoDB lock table ────────────────────────────────────────────────
echo ""
echo "Creating DynamoDB lock table: ${LOCK_TABLE}"

if aws dynamodb describe-table \
    --table-name "${LOCK_TABLE}" \
    --region "${REGION}" &>/dev/null; then
  echo "  Lock table already exists — skipping creation."
else
  aws dynamodb create-table \
    --table-name "${LOCK_TABLE}" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --sse-specification Enabled=true \
    --region "${REGION}"

  echo "  Waiting for table to become active..."
  aws dynamodb wait table-exists \
    --table-name "${LOCK_TABLE}" \
    --region "${REGION}"

  echo "  Lock table created."
fi

# ── Check Bedrock model access ────────────────────────────────────────────────
echo ""
echo "Checking Bedrock foundation model access..."
echo "  NOTE: Claude 3.5 Sonnet and Amazon Titan Embeddings v2 access"
echo "  must be requested manually in the AWS console:"
echo "  https://console.aws.amazon.com/bedrock/home#/modelaccess"
echo ""
echo "  Required models:"
echo "    - anthropic.claude-3-5-sonnet-20241022-v2:0"
echo "    - amazon.titan-embed-text-v2:0"

# ── Terraform init ────────────────────────────────────────────────────────────
ENV_DIR="$(cd "$(dirname "$0")/.." && pwd)/terraform/envs/${ENV}"

if [[ ! -d "${ENV_DIR}" ]]; then
  echo "ERROR: Environment directory not found: ${ENV_DIR}" >&2
  exit 1
fi

echo ""
echo "Initializing Terraform in ${ENV_DIR}..."

cd "${ENV_DIR}"

terraform init \
  -backend-config="bucket=${STATE_BUCKET}" \
  -backend-config="key=${ENV}/terraform.tfstate" \
  -backend-config="region=${REGION}" \
  -backend-config="dynamodb_table=${LOCK_TABLE}" \
  -backend-config="encrypt=true" \
  -reconfigure

echo ""
echo "Running terraform validate..."
terraform validate

echo ""
echo "========================================================"
echo " Bootstrap complete for environment: ${ENV}"
echo ""
echo " Next steps:"
echo "   1. Ensure Bedrock model access is approved (AWS console)"
echo "   2. Create terraform.tfvars in ${ENV_DIR} with:"
echo "        aws_account_id = \"${ACCOUNT_ID}\""
echo "        aws_region     = \"${REGION}\""
echo "        alert_email    = \"<your-email>\""
if [[ "${ENV}" == "prod" ]]; then
echo "        container_image = \"<ecr-uri>:<tag>\""
echo "        callback_urls   = [\"https://<your-domain>/callback\"]"
echo "        logout_urls     = [\"https://<your-domain>/logout\"]"
fi
echo ""
echo "   3. Review the plan:"
echo "        cd ${ENV_DIR}"
echo "        terraform plan -var-file=terraform.tfvars"
echo ""
echo "   4. Apply:"
echo "        terraform apply -var-file=terraform.tfvars"
echo "========================================================"
