output "api_invoke_url" {
  description = "API Gateway invocation URL"
  value       = module.api.api_gateway_invoke_url
}

output "ecr_repository_url" {
  description = "ECR repository URL for the RAG service image"
  value       = module.compute.ecr_repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = module.compute.ecs_cluster_name
}

output "redis_endpoint" {
  description = "Redis cache endpoint"
  value       = module.cache.redis_endpoint
  sensitive   = true
}

output "opensearch_public_endpoint" {
  description = "OpenSearch public collection endpoint"
  value       = module.opensearch.public_collection_endpoint
  sensitive   = true
}

output "opensearch_phi_endpoint" {
  description = "OpenSearch PHI collection endpoint"
  value       = module.opensearch.phi_collection_endpoint
  sensitive   = true
}

output "cognito_auth_domain" {
  description = "Cognito hosted UI auth domain"
  value       = module.cognito.auth_domain
}

output "cognito_user_pool_id" {
  description = "Cognito user pool ID"
  value       = module.cognito.user_pool_id
}

output "cognito_app_client_id" {
  description = "Cognito app client ID"
  value       = module.cognito.app_client_id
}

output "cloudtrail_arn" {
  description = "CloudTrail ARN for audit verification"
  value       = module.security.cloudtrail_arn
}

output "guardduty_detector_id" {
  description = "GuardDuty detector ID"
  value       = module.security.guardduty_detector_id
}

output "phi_bucket_id" {
  description = "PHI S3 bucket name"
  value       = module.storage.phi_bucket_id
  sensitive   = true
}

output "public_content_bucket_id" {
  description = "Public content S3 bucket name"
  value       = module.storage.public_content_bucket_id
}

output "provisioned_model_arn" {
  description = "Bedrock Provisioned Throughput model ARN"
  value       = module.bedrock.provisioned_model_arn
}
