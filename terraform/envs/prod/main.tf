terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
  }

  backend "s3" {
    # Set via -backend-config or CI/CD pipeline environment variables
    # bucket         = "nova-terraform-state-<account-id>"
    # key            = "prod/terraform.tfstate"
    # region         = "us-east-1"
    # dynamodb_table = "nova-terraform-locks"
    # encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

locals {
  project     = "nova"
  environment = "prod"

  common_tags = {
    Project     = "nova-health-tech"
    Environment = local.environment
    ManagedBy   = "terraform"
    Compliance  = "HIPAA"
    DataClass   = "Sensitive"
  }
}

################################################################################
# Networking — 3 AZs for full HA in prod
################################################################################
module "networking" {
  source = "../../modules/networking"

  project     = local.project
  environment = local.environment

  vpc_cidr             = "10.10.0.0/16"
  availability_zones   = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnet_cidrs = ["10.10.1.0/24", "10.10.2.0/24", "10.10.3.0/24"]
  public_subnet_cidrs  = ["10.10.101.0/24", "10.10.102.0/24", "10.10.103.0/24"]
  tags                 = local.common_tags
}

################################################################################
# Storage — Object Lock enabled for HIPAA 7-year audit retention
################################################################################
module "storage" {
  source = "../../modules/storage"

  project        = local.project
  environment    = local.environment
  aws_account_id = var.aws_account_id
  aws_region     = var.aws_region

  enable_object_lock = true
  log_retention_days = 2555
  tags               = local.common_tags
}

################################################################################
# IAM Roles
################################################################################
module "iam" {
  source = "../../modules/iam"

  project        = local.project
  environment    = local.environment
  aws_account_id = var.aws_account_id
  aws_region     = var.aws_region

  phi_bucket_arn            = module.storage.phi_bucket_arn
  public_bucket_arn         = module.storage.public_content_bucket_arn
  phi_kms_key_arn           = module.storage.phi_kms_key_arn
  public_kms_key_arn        = module.storage.public_kms_key_arn
  opensearch_collection_arn = module.opensearch.public_collection_arn

  tags = local.common_tags
}

################################################################################
# OpenSearch Serverless — standby replicas enabled for HA
################################################################################
module "opensearch" {
  source = "../../modules/opensearch"

  project        = local.project
  environment    = local.environment
  aws_account_id = var.aws_account_id

  phi_researcher_role_arn  = module.iam.phi_researcher_role_arn
  lambda_pipeline_role_arn = module.iam.lambda_pipeline_role_arn
  ecs_task_role_arn        = module.iam.ecs_task_role_arn
  public_kms_key_arn       = module.storage.public_kms_key_arn
  phi_kms_key_arn          = module.storage.phi_kms_key_arn

  tags = local.common_tags
}

################################################################################
# Bedrock — Provisioned Throughput for ≤2s SLA guarantee
################################################################################
module "bedrock" {
  source = "../../modules/bedrock"

  project        = local.project
  environment    = local.environment
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id

  enable_provisioned_throughput = true
  model_units                   = var.bedrock_model_units
  tags                          = local.common_tags
}

################################################################################
# Cognito — MFA enforced for all prod users
################################################################################
module "cognito" {
  source = "../../modules/cognito"

  project     = local.project
  environment = local.environment
  aws_region  = var.aws_region

  callback_urls           = var.callback_urls
  logout_urls             = var.logout_urls
  mfa_configuration       = "ON"
  password_minimum_length = 16

  tags = local.common_tags
}

################################################################################
# ElastiCache Redis — higher ECPU for prod query volume
################################################################################
module "cache" {
  source = "../../modules/cache"

  project            = local.project
  environment        = local.environment
  private_subnet_ids = module.networking.private_subnet_ids
  redis_sg_id        = module.networking.sg_redis_id
  kms_key_arn        = module.storage.public_kms_key_arn
  max_cache_gb       = 50

  tags = local.common_tags
}

################################################################################
# Data Pipeline — higher Lambda memory for large clinical PDFs
################################################################################
module "data_pipeline" {
  source = "../../modules/data_pipeline"

  project        = local.project
  environment    = local.environment
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id

  lambda_role_arn         = module.iam.lambda_pipeline_role_arn
  step_functions_role_arn = module.iam.step_functions_role_arn
  scheduler_role_arn      = module.iam.scheduler_role_arn

  public_bucket_id           = module.storage.public_content_bucket_id
  phi_bucket_id              = module.storage.phi_bucket_id
  public_collection_endpoint = module.opensearch.public_collection_endpoint
  phi_collection_endpoint    = module.opensearch.phi_collection_endpoint
  document_metadata_table_name = module.storage.document_metadata_table_name
  app_config_secret_arn      = module.bedrock.app_config_secret_arn

  private_subnet_ids = module.networking.private_subnet_ids
  lambda_sg_id       = module.networking.sg_lambda_id

  lambda_memory_mb   = 2048
  lambda_timeout_sec = 900

  tags = local.common_tags
}

################################################################################
# Compute — 2 always-on tasks, scales to 20, 4 vCPU each
################################################################################
module "compute" {
  source = "../../modules/compute"

  project        = local.project
  environment    = local.environment
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id

  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids
  public_subnet_ids  = module.networking.public_subnet_ids

  ecs_task_role_arn      = module.iam.ecs_task_role_arn
  ecs_execution_role_arn = module.iam.ecs_execution_role_arn
  sg_ecs_tasks_id        = module.networking.sg_ecs_tasks_id
  sg_alb_id              = module.networking.sg_alb_id

  opensearch_public_endpoint = module.opensearch.public_collection_endpoint
  opensearch_phi_endpoint    = module.opensearch.phi_collection_endpoint
  redis_endpoint             = module.cache.redis_endpoint
  redis_port                 = module.cache.redis_port

  app_config_secret_arn = module.bedrock.app_config_secret_arn
  guardrail_id          = module.bedrock.guardrail_id
  guardrail_version     = module.bedrock.guardrail_version

  container_image    = var.container_image
  task_cpu           = 4096
  task_memory_mb     = 8192
  min_capacity       = 2
  max_capacity       = 20
  log_retention_days = 2555

  tags = local.common_tags
}

################################################################################
# API Gateway + WAF — higher throughput for prod
################################################################################
module "api" {
  source = "../../modules/api"

  project        = local.project
  environment    = local.environment
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id

  cognito_user_pool_arn = module.cognito.user_pool_arn
  alb_internal_dns      = module.compute.alb_internal_dns
  alb_listener_arn      = module.compute.alb_listener_arn

  vpc_id             = module.networking.vpc_id
  private_subnet_ids = module.networking.private_subnet_ids

  throttle_burst_limit = 500
  throttle_rate_limit  = 200

  tags = local.common_tags
}

################################################################################
# Security — Macie enabled, multi-region CloudTrail
################################################################################
module "security" {
  source = "../../modules/security"

  project        = local.project
  environment    = local.environment
  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id

  audit_bucket_arn   = module.storage.audit_logs_bucket_arn
  audit_bucket_id    = module.storage.audit_logs_bucket_id
  public_kms_key_arn = module.storage.public_kms_key_arn
  phi_bucket_id      = module.storage.phi_bucket_id
  public_bucket_id   = module.storage.public_content_bucket_id
  enable_macie       = true
  alert_email        = var.alert_email

  tags = local.common_tags
}

################################################################################
# Monitoring — tighter SLA thresholds for prod
################################################################################
module "monitoring" {
  source = "../../modules/monitoring"

  project     = local.project
  environment = local.environment
  aws_region  = var.aws_region

  ecs_cluster_name         = module.compute.ecs_cluster_name
  ecs_service_name         = module.compute.ecs_service_name
  api_gateway_id           = module.api.api_gateway_id
  alert_topic_arn          = module.security.security_alerts_topic_arn
  p95_latency_threshold_ms = 2000
  error_rate_threshold_pct = 1

  tags = local.common_tags
}
