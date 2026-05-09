################################################################################
# ElastiCache Serverless — Redis compatible
# Scales from 0 to var.max_cache_gb automatically.
# Used for: (1) semantic query cache, (2) RAG response cache, (3) session tokens
################################################################################
resource "aws_elasticache_serverless_cache" "redis" {
  engine = "redis"
  name   = "${var.project}-${var.environment}-cache"

  cache_usage_limits {
    data_storage {
      maximum = var.max_cache_gb
      unit    = "GB"
    }
    ecpu_per_second {
      maximum = var.environment == "prod" ? 5000 : 1000
    }
  }

  description            = "Nova Health Tech semantic + RAG response cache"
  kms_key_id             = var.kms_key_arn
  major_engine_version   = "7"
  security_group_ids     = [var.redis_sg_id]
  subnet_ids             = var.private_subnet_ids

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-redis"
  })
}
