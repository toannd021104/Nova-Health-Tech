output "pdf_processor_function_arn" {
  value = aws_lambda_function.pdf_processor.arn
}

output "who_ingestor_function_arn" {
  value = aws_lambda_function.who_ingestor.arn
}

output "chunker_embedder_function_arn" {
  value = aws_lambda_function.chunker_embedder.arn
}

output "pdf_pipeline_sfn_arn" {
  value = aws_sfn_state_machine.pdf_pipeline.arn
}

output "who_scheduler_arn" {
  value = aws_scheduler_schedule.who_monthly.arn
}
