output "public_content_bucket_id" {
  value = aws_s3_bucket.public_content.id
}

output "public_content_bucket_arn" {
  value = aws_s3_bucket.public_content.arn
}

output "phi_bucket_id" {
  value = aws_s3_bucket.phi.id
}

output "phi_bucket_arn" {
  value = aws_s3_bucket.phi.arn
}

output "audit_logs_bucket_id" {
  value = aws_s3_bucket.audit_logs.id
}

output "audit_logs_bucket_arn" {
  value = aws_s3_bucket.audit_logs.arn
}

output "public_kms_key_arn" {
  value = aws_kms_key.public_content.arn
}

output "public_kms_key_id" {
  value = aws_kms_key.public_content.key_id
}

output "phi_kms_key_arn" {
  value = aws_kms_key.phi.arn
}

output "phi_kms_key_id" {
  value = aws_kms_key.phi.key_id
}

output "document_metadata_table_name" {
  value = aws_dynamodb_table.document_metadata.name
}

output "document_metadata_table_arn" {
  value = aws_dynamodb_table.document_metadata.arn
}
