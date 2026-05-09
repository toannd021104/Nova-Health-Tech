output "public_collection_arn" {
  description = "ARN of the public OpenSearch Serverless collection"
  value       = aws_opensearchserverless_collection.public.arn
}

output "public_collection_endpoint" {
  description = "Endpoint URL for the public collection"
  value       = aws_opensearchserverless_collection.public.collection_endpoint
}

output "phi_collection_arn" {
  description = "ARN of the PHI OpenSearch Serverless collection"
  value       = aws_opensearchserverless_collection.phi.arn
}

output "phi_collection_endpoint" {
  description = "Endpoint URL for the PHI collection"
  value       = aws_opensearchserverless_collection.phi.collection_endpoint
}
