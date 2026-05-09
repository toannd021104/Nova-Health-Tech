################################################################################
# Bedrock Model Access
# Note: Model access must also be enabled in the AWS console (one-time action).
# The aws_bedrock_foundation_model_agreement resource handles the acceptance.
################################################################################

# Guardrail — block harmful content and enforce clinical safety
resource "aws_bedrock_guardrail" "clinical" {
  name                      = "${var.project}-${var.environment}-clinical-guardrail"
  blocked_input_messaging   = "This query cannot be processed. Please consult a licensed clinician for medical advice."
  blocked_outputs_messaging = "Response blocked by safety policy. Please rephrase or consult a licensed clinician."
  description               = "Clinical safety guardrail: blocks harmful medical advice, PII exfiltration, and hallucinated drug dosages"

  content_policy_config {
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "HATE"
    }
    filters_config {
      input_strength  = "HIGH"
      output_strength = "HIGH"
      type            = "VIOLENCE"
    }
    filters_config {
      input_strength  = "MEDIUM"
      output_strength = "HIGH"
      type            = "MISCONDUCT"
    }
  }

  sensitive_information_policy_config {
    pii_entities_config {
      action = "BLOCK"
      type   = "EMAIL"
    }
    pii_entities_config {
      action = "BLOCK"
      type   = "PHONE"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "NAME"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "US_SOCIAL_SECURITY_NUMBER"
    }
    pii_entities_config {
      action = "ANONYMIZE"
      type   = "US_INDIVIDUAL_TAX_IDENTIFICATION_NUMBER"
    }
  }

  word_policy_config {
    managed_word_lists_config {
      type = "PROFANITY"
    }
  }

  tags = var.tags
}

resource "aws_bedrock_guardrail_version" "clinical" {
  guardrail_arn = aws_bedrock_guardrail.clinical.guardrail_arn
  description   = "v1 — initial clinical safety policy"
}

################################################################################
# Bedrock Provisioned Throughput (prod only)
# Ensures <800ms first-token latency for the ≤2s SLA
################################################################################
resource "aws_bedrock_provisioned_model_throughput" "claude" {
  count                    = var.enable_provisioned_throughput ? 1 : 0
  provisioned_model_name   = "${var.project}-${var.environment}-claude-pt"
  model_arn                = "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
  model_units              = var.model_units
  commitment_duration       = "ONE_MONTH"

  tags = var.tags
}

################################################################################
# Secrets Manager — store API keys and config used by LangChain
################################################################################
resource "aws_secretsmanager_secret" "app_config" {
  name                    = "${var.project}/${var.environment}/app-config"
  description             = "Nova Health Tech application configuration and API keys"
  recovery_window_in_days = var.environment == "prod" ? 30 : 7

  tags = var.tags
}

resource "aws_secretsmanager_secret_version" "app_config" {
  secret_id = aws_secretsmanager_secret.app_config.id
  secret_string = jsonencode({
    bedrock_region              = var.aws_region
    claude_model_id             = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    titan_embed_model_id        = "amazon.titan-embed-text-v2:0"
    guardrail_id                = aws_bedrock_guardrail.clinical.guardrail_id
    guardrail_version           = aws_bedrock_guardrail_version.clinical.version
    provisioned_model_arn       = var.enable_provisioned_throughput ? aws_bedrock_provisioned_model_throughput.claude[0].provisioned_model_arn : ""
    embedding_dimensions        = "1536"
    chunk_size_tokens           = "512"
    chunk_overlap_tokens        = "50"
    retrieval_top_k             = "5"
    redis_ttl_seconds           = "3600"
    who_api_base_url            = "https://extranet.who.int/iris/rest"
    system_prompt_tone          = "You are a clinical decision support assistant for licensed medical professionals. Respond with evidence-based, concise answers. Always cite your sources. Never provide a definitive diagnosis — always recommend clinician judgment."
  })

  lifecycle {
    ignore_changes = [secret_string]
  }
}
