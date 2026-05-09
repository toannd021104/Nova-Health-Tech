################################################################################
# KMS Keys — one per data classification level
################################################################################
resource "aws_kms_key" "public_content" {
  description             = "${var.project}-${var.environment} public clinical content encryption key"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "RootAccess"
        Effect = "Allow"
        Principal = { AWS = "arn:aws:iam::${var.aws_account_id}:root" }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "S3Service"
        Effect = "Allow"
        Principal = { Service = "s3.amazonaws.com" }
        Action   = ["kms:GenerateDataKey", "kms:Decrypt"]
        Resource = "*"
      },
      {
        Sid    = "CloudTrailService"
        Effect = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt"]
        Resource = "*"
      },
      {
        Sid    = "ConfigService"
        Effect = "Allow"
        Principal = { Service = "config.amazonaws.com" }
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt"]
        Resource = "*"
      },
      {
        Sid    = "OpenSearchServerlessService"
        Effect = "Allow"
        Principal = { Service = "aoss.amazonaws.com" }
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt", "kms:CreateGrant", "kms:DescribeKey"]
        Resource = "*"
      }
    ]
  })

  tags = merge(var.tags, {
    Name               = "${var.project}-${var.environment}-kms-public"
    DataClassification = "Public"
  })
}

resource "aws_kms_alias" "public_content" {
  name          = "alias/${var.project}-${var.environment}-public"
  target_key_id = aws_kms_key.public_content.key_id
}

resource "aws_kms_key" "phi" {
  description             = "${var.project}-${var.environment} PHI encryption key — HIPAA restricted"
  deletion_window_in_days = 30
  enable_key_rotation     = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "RootAccess"
        Effect = "Allow"
        Principal = { AWS = "arn:aws:iam::${var.aws_account_id}:root" }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "S3Service"
        Effect = "Allow"
        Principal = { Service = "s3.amazonaws.com" }
        Action   = ["kms:GenerateDataKey", "kms:Decrypt"]
        Resource = "*"
      },
      {
        Sid    = "OpenSearchServerlessService"
        Effect = "Allow"
        Principal = { Service = "aoss.amazonaws.com" }
        Action   = ["kms:GenerateDataKey*", "kms:Decrypt", "kms:CreateGrant", "kms:DescribeKey"]
        Resource = "*"
      },
      {
        Sid    = "DenyNonPHIRoles"
        Effect = "Deny"
        Principal = { AWS = "*" }
        Action   = ["kms:Decrypt", "kms:GenerateDataKey"]
        Resource = "*"
        Condition = {
          StringNotLike = {
            "aws:PrincipalArn" = [
              "arn:aws:iam::${var.aws_account_id}:role/${var.project}-${var.environment}-phi-researcher-role",
              "arn:aws:iam::${var.aws_account_id}:role/${var.project}-${var.environment}-lambda-pipeline-role",
              "arn:aws:iam::${var.aws_account_id}:root"
            ]
          }
        }
      }
    ]
  })

  tags = merge(var.tags, {
    Name               = "${var.project}-${var.environment}-kms-phi"
    DataClassification = "PHI"
    Compliance         = "HIPAA"
  })
}

resource "aws_kms_alias" "phi" {
  name          = "alias/${var.project}-${var.environment}-phi"
  target_key_id = aws_kms_key.phi.key_id
}

################################################################################
# S3 — Public Clinical Content Bucket (WHO, protocols, PubMed)
################################################################################
resource "aws_s3_bucket" "public_content" {
  bucket        = "${var.project}-${var.environment}-public-content-${var.aws_account_id}"
  force_destroy = var.environment == "dev" ? true : false

  tags = merge(var.tags, {
    Name               = "${var.project}-${var.environment}-public-content"
    DataClassification = "Internal"
  })
}

resource "aws_s3_bucket_versioning" "public_content" {
  bucket = aws_s3_bucket.public_content.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "public_content" {
  bucket = aws_s3_bucket.public_content.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.public_content.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "public_content" {
  bucket                  = aws_s3_bucket.public_content.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "public_content" {
  bucket = aws_s3_bucket.public_content.id

  rule {
    id     = "archive-old-versions"
    status = "Enabled"

    filter {}

    noncurrent_version_transition {
      noncurrent_days = 90
      storage_class   = "STANDARD_IA"
    }

    noncurrent_version_expiration {
      noncurrent_days = 365
    }
  }
}

################################################################################
# S3 — PHI Bucket (clinical trial reports — isolated)
################################################################################
resource "aws_s3_bucket" "phi" {
  bucket        = "${var.project}-${var.environment}-phi-${var.aws_account_id}"
  force_destroy = false

  tags = merge(var.tags, {
    Name               = "${var.project}-${var.environment}-phi"
    DataClassification = "PHI"
    Compliance         = "HIPAA"
  })
}

resource "aws_s3_bucket_versioning" "phi" {
  bucket = aws_s3_bucket.phi.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "phi" {
  bucket = aws_s3_bucket.phi.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.phi.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "phi" {
  bucket                  = aws_s3_bucket.phi.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "phi" {
  bucket = aws_s3_bucket.phi.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "DenyNonHTTPS"
        Effect = "Deny"
        Principal = "*"
        Action   = "s3:*"
        Resource = [
          "${aws_s3_bucket.phi.arn}",
          "${aws_s3_bucket.phi.arn}/*"
        ]
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      },
      {
        Sid    = "DenyNonPHIRoles"
        Effect = "Deny"
        Principal = "*"
        Action   = ["s3:GetObject", "s3:PutObject"]
        Resource = "${aws_s3_bucket.phi.arn}/*"
        Condition = {
          StringNotLike = {
            "aws:PrincipalArn" = [
              "arn:aws:iam::${var.aws_account_id}:role/${var.project}-${var.environment}-phi-researcher-role",
              "arn:aws:iam::${var.aws_account_id}:role/${var.project}-${var.environment}-lambda-pipeline-role",
              "arn:aws:iam::${var.aws_account_id}:root"
            ]
          }
        }
      }
    ]
  })
}

################################################################################
# S3 — Audit Log Bucket (immutable, long-retention)
################################################################################
resource "aws_s3_bucket" "audit_logs" {
  bucket        = "${var.project}-${var.environment}-audit-logs-${var.aws_account_id}"
  force_destroy = false

  tags = merge(var.tags, {
    Name       = "${var.project}-${var.environment}-audit-logs"
    Compliance = "HIPAA"
  })
}

resource "aws_s3_bucket_versioning" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = aws_kms_key.public_content.arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "audit_logs" {
  bucket                  = aws_s3_bucket.audit_logs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Object Lock (WORM) for prod audit logs — HIPAA 7-year retention
resource "aws_s3_bucket_object_lock_configuration" "audit_logs" {
  count  = var.enable_object_lock ? 1 : 0
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    default_retention {
      mode  = "COMPLIANCE"
      years = 7
    }
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "audit_logs" {
  bucket = aws_s3_bucket.audit_logs.id

  rule {
    id     = "transition-to-glacier"
    status = "Enabled"

    filter {}

    transition {
      days          = 90
      storage_class = "GLACIER_IR"
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"
    }
  }
}

################################################################################
# DynamoDB — Document metadata table
################################################################################
resource "aws_dynamodb_table" "document_metadata" {
  name           = "${var.project}-${var.environment}-document-metadata"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "document_id"
  range_key      = "version"

  attribute {
    name = "document_id"
    type = "S"
  }

  attribute {
    name = "version"
    type = "S"
  }

  attribute {
    name = "source_type"
    type = "S"
  }

  attribute {
    name = "ingested_at"
    type = "S"
  }

  global_secondary_index {
    name            = "source-type-index"
    hash_key        = "source_type"
    range_key       = "ingested_at"
    projection_type = "ALL"
  }

  point_in_time_recovery {
    enabled = true
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = aws_kms_key.public_content.arn
  }

  ttl {
    attribute_name = "expires_at"
    enabled        = false
  }

  tags = merge(var.tags, {
    Name = "${var.project}-${var.environment}-document-metadata"
  })
}
