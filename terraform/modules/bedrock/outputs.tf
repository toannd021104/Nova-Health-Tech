output "guardrail_id" {
  description = "ID of the Bedrock clinical safety guardrail"
  value       = aws_bedrock_guardrail.clinical.guardrail_id
}

output "guardrail_arn" {
  description = "ARN of the Bedrock clinical safety guardrail"
  value       = aws_bedrock_guardrail.clinical.guardrail_arn
}

output "guardrail_version" {
  description = "Published version of the guardrail"
  value       = aws_bedrock_guardrail_version.clinical.version
}

output "provisioned_model_arn" {
  description = "ARN of the Bedrock Provisioned Throughput model (empty if not enabled)"
  value       = var.enable_provisioned_throughput ? aws_bedrock_provisioned_model_throughput.claude[0].provisioned_model_arn : ""
}

output "app_config_secret_arn" {
  description = "ARN of the Secrets Manager secret containing app config"
  value       = aws_secretsmanager_secret.app_config.arn
}
