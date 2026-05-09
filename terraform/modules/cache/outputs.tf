output "redis_endpoint" {
  description = "ElastiCache Serverless Redis endpoint"
  value       = aws_elasticache_serverless_cache.redis.endpoint[0].address
}

output "redis_port" {
  description = "ElastiCache Serverless Redis port"
  value       = aws_elasticache_serverless_cache.redis.endpoint[0].port
}

output "redis_arn" {
  description = "ARN of the ElastiCache Serverless cache"
  value       = aws_elasticache_serverless_cache.redis.arn
}
