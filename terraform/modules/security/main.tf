################################################################################
# CloudTrail — Organisation-level audit trail
################################################################################
resource "aws_cloudtrail" "main" {
  name                          = "${var.project}-${var.environment}-trail"
  s3_bucket_name                = aws_s3_bucket_policy.cloudtrail_write.id
  include_global_service_events = true
  is_multi_region_trail         = var.environment == "prod"
  enable_log_file_validation    = true
  kms_key_id                    = var.public_kms_key_arn

  # Management events (all read/write)
  advanced_event_selector {
    name = "ManagementEvents"
    field_selector {
      field  = "eventCategory"
      equals = ["Management"]
    }
  }

  # S3 data events for PHI and public buckets
  advanced_event_selector {
    name = "S3DataEvents"
    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }
    field_selector {
      field  = "resources.type"
      equals = ["AWS::S3::Object"]
    }
    field_selector {
      field       = "resources.ARN"
      starts_with = ["arn:aws:s3:::${var.phi_bucket_id}/", "arn:aws:s3:::${var.public_bucket_id}/"]
    }
  }

  # Bedrock model invocation data events
  advanced_event_selector {
    name = "BedrockModelInvocationDataEvents"
    field_selector {
      field  = "eventCategory"
      equals = ["Data"]
    }
    field_selector {
      field  = "resources.type"
      equals = ["AWS::Bedrock::Model"]
    }
  }

  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.cloudtrail.arn}:*"
  cloud_watch_logs_role_arn  = aws_iam_role.cloudtrail_cw.arn

  tags = merge(var.tags, {
    Compliance = "HIPAA"
  })
}

resource "aws_cloudwatch_log_group" "cloudtrail" {
  name              = "/aws/cloudtrail/${var.project}-${var.environment}"
  retention_in_days = var.environment == "prod" ? 2555 : 90
  tags              = var.tags
}

resource "aws_iam_role" "cloudtrail_cw" {
  name = "${var.project}-${var.environment}-cloudtrail-cw-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "cloudtrail.amazonaws.com" }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "cloudtrail_cw_policy" {
  name = "cloudtrail-cw-policy"
  role = aws_iam_role.cloudtrail_cw.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["logs:CreateLogStream", "logs:PutLogEvents"]
      Resource = "${aws_cloudwatch_log_group.cloudtrail.arn}:*"
    }]
  })
}

# Bucket policy allowing CloudTrail to write
resource "aws_s3_bucket_policy" "cloudtrail_write" {
  bucket = var.audit_bucket_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AWSCloudTrailAclCheck"
        Effect = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action   = "s3:GetBucketAcl"
        Resource = var.audit_bucket_arn
      },
      {
        Sid    = "AWSCloudTrailWrite"
        Effect = "Allow"
        Principal = { Service = "cloudtrail.amazonaws.com" }
        Action   = "s3:PutObject"
        Resource = "${var.audit_bucket_arn}/AWSLogs/${var.aws_account_id}/*"
        Condition = {
          StringEquals = {
            "s3:x-amz-acl" = "bucket-owner-full-control"
          }
        }
      }
    ]
  })
}

################################################################################
# GuardDuty — Threat detection
################################################################################
resource "aws_guardduty_detector" "main" {
  enable = true

  datasources {
    s3_logs {
      enable = true
    }
    kubernetes {
      audit_logs {
        enable = false
      }
    }
    malware_protection {
      scan_ec2_instance_with_findings {
        ebs_volumes {
          enable = true
        }
      }
    }
  }

  tags = var.tags
}

################################################################################
# Amazon Macie — PHI/PII detection in S3
################################################################################
resource "aws_macie2_account" "main" {
  count                        = var.enable_macie ? 1 : 0
  finding_publishing_frequency = "FIFTEEN_MINUTES"
  status                       = "ENABLED"
}

resource "aws_macie2_classification_job" "phi_scan" {
  count      = var.enable_macie ? 1 : 0
  job_type   = "SCHEDULED"
  name       = "${var.project}-${var.environment}-phi-scan"
  depends_on = [aws_macie2_account.main]

  schedule_frequency {
    daily_schedule = true
  }

  s3_job_definition {
    bucket_definitions {
      account_id = var.aws_account_id
      buckets    = [var.phi_bucket_id, var.public_bucket_id]
    }
  }

  tags = var.tags
}

################################################################################
# AWS Config — Continuous compliance checks
################################################################################
resource "aws_config_configuration_recorder" "main" {
  name     = "${var.project}-${var.environment}-config-recorder"
  role_arn = aws_iam_role.config.arn

  recording_group {
    all_supported                 = true
    include_global_resource_types = true
  }
}

resource "aws_config_delivery_channel" "main" {
  name           = "${var.project}-${var.environment}-config-delivery"
  s3_bucket_name = var.audit_bucket_id
  s3_key_prefix  = "aws-config"

  snapshot_delivery_properties {
    delivery_frequency = "Six_Hours"
  }

  depends_on = [aws_config_configuration_recorder.main]
}

resource "aws_config_configuration_recorder_status" "main" {
  name       = aws_config_configuration_recorder.main.name
  is_enabled = true

  depends_on = [aws_config_delivery_channel.main]
}

resource "aws_iam_role" "config" {
  name = "${var.project}-${var.environment}-config-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "config.amazonaws.com" }
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "config_managed" {
  role       = aws_iam_role.config.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"
}

# Config Rules — HIPAA compliance checks
resource "aws_config_config_rule" "s3_bucket_ssl" {
  name        = "${var.project}-${var.environment}-s3-ssl-only"
  description = "Ensure S3 buckets deny HTTP access"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_SSL_REQUESTS_ONLY"
  }

  depends_on = [aws_config_configuration_recorder_status.main]
}

resource "aws_config_config_rule" "s3_bucket_encryption" {
  name        = "${var.project}-${var.environment}-s3-encrypted"
  description = "Ensure S3 buckets use server-side encryption"

  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_SERVER_SIDE_ENCRYPTION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder_status.main]
}

resource "aws_config_config_rule" "cloudtrail_enabled" {
  name        = "${var.project}-${var.environment}-cloudtrail-enabled"
  description = "Ensure CloudTrail is enabled"

  source {
    owner             = "AWS"
    source_identifier = "CLOUD_TRAIL_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder_status.main]
}

resource "aws_config_config_rule" "kms_rotation" {
  name        = "${var.project}-${var.environment}-kms-rotation"
  description = "Ensure KMS keys have automatic rotation enabled"

  source {
    owner             = "AWS"
    source_identifier = "CMK_BACKING_KEY_ROTATION_ENABLED"
  }

  depends_on = [aws_config_configuration_recorder_status.main]
}

resource "aws_config_config_rule" "guardduty_enabled" {
  name        = "${var.project}-${var.environment}-guardduty-enabled"
  description = "Ensure GuardDuty is enabled"

  source {
    owner             = "AWS"
    source_identifier = "GUARDDUTY_ENABLED_CENTRALIZED"
  }

  depends_on = [aws_config_configuration_recorder_status.main]
}

################################################################################
# Security Hub — Aggregated security findings
################################################################################
resource "aws_securityhub_account" "main" {}

resource "aws_securityhub_standards_subscription" "hipaa" {
  standards_arn = "arn:aws:securityhub:${var.aws_region}::standards/aws-foundational-security-best-practices/v/1.0.0"
  depends_on    = [aws_securityhub_account.main]
}

resource "aws_securityhub_standards_subscription" "cis" {
  standards_arn = "arn:aws:securityhub:::ruleset/cis-aws-foundations-benchmark/v/1.2.0"
  depends_on    = [aws_securityhub_account.main]
}

################################################################################
# SNS — Security alerts
################################################################################
resource "aws_sns_topic" "security_alerts" {
  name              = "${var.project}-${var.environment}-security-alerts"
  kms_master_key_id = var.public_kms_key_arn
  tags              = var.tags
}

resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch alarm — GuardDuty high-severity findings
resource "aws_cloudwatch_event_rule" "guardduty_finding" {
  name        = "${var.project}-${var.environment}-guardduty-finding"
  description = "Capture high severity GuardDuty findings"

  event_pattern = jsonencode({
    source      = ["aws.guardduty"]
    detail-type = ["GuardDuty Finding"]
    detail = {
      severity = [{ numeric = [">=", 7] }]
    }
  })

  tags = var.tags
}

resource "aws_cloudwatch_event_target" "guardduty_sns" {
  rule      = aws_cloudwatch_event_rule.guardduty_finding.name
  target_id = "SendToSNS"
  arn       = aws_sns_topic.security_alerts.arn
}

resource "aws_sns_topic_policy" "security_alerts" {
  arn = aws_sns_topic.security_alerts.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "events.amazonaws.com" }
      Action    = "sns:Publish"
      Resource  = aws_sns_topic.security_alerts.arn
    }]
  })
}
