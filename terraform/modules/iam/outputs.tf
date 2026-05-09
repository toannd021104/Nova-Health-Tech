output "ecs_task_role_arn" {
  description = "ARN of the ECS task IAM role"
  value       = aws_iam_role.ecs_task.arn
}

output "ecs_execution_role_arn" {
  description = "ARN of the ECS task execution IAM role"
  value       = aws_iam_role.ecs_execution.arn
}

output "phi_researcher_role_arn" {
  description = "ARN of the PHI researcher IAM role (OpenSearch phi-index access)"
  value       = aws_iam_role.phi_researcher.arn
}

output "lambda_pipeline_role_arn" {
  description = "ARN of the Lambda data pipeline IAM role"
  value       = aws_iam_role.lambda_pipeline.arn
}

output "step_functions_role_arn" {
  description = "ARN of the Step Functions IAM role"
  value       = aws_iam_role.step_functions.arn
}

output "scheduler_role_arn" {
  description = "ARN of the EventBridge Scheduler IAM role"
  value       = aws_iam_role.scheduler.arn
}
