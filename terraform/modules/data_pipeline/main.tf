################################################################################
# CloudWatch Log Groups — Lambda & Step Functions
################################################################################
resource "aws_cloudwatch_log_group" "lambda_pdf_processor" {
  name              = "/aws/lambda/${var.project}-${var.environment}-pdf-processor"
  retention_in_days = var.environment == "prod" ? 2555 : 30
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_who_ingestor" {
  name              = "/aws/lambda/${var.project}-${var.environment}-who-ingestor"
  retention_in_days = var.environment == "prod" ? 2555 : 30
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "lambda_chunker_embedder" {
  name              = "/aws/lambda/${var.project}-${var.environment}-chunker-embedder"
  retention_in_days = var.environment == "prod" ? 2555 : 30
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "sfn_pipeline" {
  name              = "/aws/states/${var.project}-${var.environment}-pipeline"
  retention_in_days = var.environment == "prod" ? 2555 : 30
  tags              = var.tags
}

################################################################################
# Lambda — PDF Processor (calls Textract, triggers Step Functions)
################################################################################
resource "aws_lambda_function" "pdf_processor" {
  function_name = "${var.project}-${var.environment}-pdf-processor"
  description   = "Triggered by S3 upload; calls Textract and starts the ingestion Step Functions pipeline"
  role          = var.lambda_role_arn
  runtime       = var.lambda_runtime
  handler       = "pdf_processor.handler"
  timeout       = var.lambda_timeout_sec
  memory_size   = var.lambda_memory_mb

  # Placeholder code — replaced by CI/CD on first deploy
  filename         = "${path.module}/placeholder.zip"
  source_code_hash = filebase64sha256("${path.module}/placeholder.zip")

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.lambda_sg_id]
  }

  environment {
    variables = {
      ENVIRONMENT              = var.environment
      PUBLIC_BUCKET            = var.public_bucket_id
      PHI_BUCKET               = var.phi_bucket_id
      OPENSEARCH_PUBLIC_ENDPOINT = var.public_collection_endpoint
      OPENSEARCH_PHI_ENDPOINT  = var.phi_collection_endpoint
      METADATA_TABLE           = var.document_metadata_table_name
      APP_CONFIG_SECRET_ARN    = var.app_config_secret_arn
      AWS_REGION_NAME          = var.aws_region
      SFN_ARN                  = aws_sfn_state_machine.pdf_pipeline.arn
    }
  }

  tracing_config {
    mode = "Active"
  }

  depends_on = [aws_cloudwatch_log_group.lambda_pdf_processor]

  tags = var.tags
}

# S3 trigger for public content bucket
resource "aws_lambda_permission" "pdf_s3_trigger" {
  statement_id  = "AllowS3Invoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pdf_processor.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = "arn:aws:s3:::${var.public_bucket_id}"
}

resource "aws_s3_bucket_notification" "pdf_upload" {
  bucket = var.public_bucket_id

  lambda_function {
    lambda_function_arn = aws_lambda_function.pdf_processor.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".pdf"
  }

  depends_on = [aws_lambda_permission.pdf_s3_trigger]
}

################################################################################
# Lambda — Chunker & Embedder (called from Step Functions)
################################################################################
resource "aws_lambda_function" "chunker_embedder" {
  function_name = "${var.project}-${var.environment}-chunker-embedder"
  description   = "Chunks extracted text and generates Titan Embeddings, stores in OpenSearch"
  role          = var.lambda_role_arn
  runtime       = var.lambda_runtime
  handler       = "chunker_embedder.handler"
  timeout       = var.lambda_timeout_sec
  memory_size   = var.lambda_memory_mb

  filename         = "${path.module}/placeholder.zip"
  source_code_hash = filebase64sha256("${path.module}/placeholder.zip")

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.lambda_sg_id]
  }

  environment {
    variables = {
      ENVIRONMENT              = var.environment
      OPENSEARCH_PUBLIC_ENDPOINT = var.public_collection_endpoint
      OPENSEARCH_PHI_ENDPOINT  = var.phi_collection_endpoint
      METADATA_TABLE           = var.document_metadata_table_name
      APP_CONFIG_SECRET_ARN    = var.app_config_secret_arn
      AWS_REGION_NAME          = var.aws_region
    }
  }

  tracing_config {
    mode = "Active"
  }

  depends_on = [aws_cloudwatch_log_group.lambda_chunker_embedder]

  tags = var.tags
}

################################################################################
# Lambda — WHO API Ingestor (called from EventBridge Scheduler)
################################################################################
resource "aws_lambda_function" "who_ingestor" {
  function_name = "${var.project}-${var.environment}-who-ingestor"
  description   = "Polls WHO API monthly for protocol updates and triggers ingestion pipeline"
  role          = var.lambda_role_arn
  runtime       = var.lambda_runtime
  handler       = "who_ingestor.handler"
  timeout       = var.lambda_timeout_sec
  memory_size   = 512

  filename         = "${path.module}/placeholder.zip"
  source_code_hash = filebase64sha256("${path.module}/placeholder.zip")

  vpc_config {
    subnet_ids         = var.private_subnet_ids
    security_group_ids = [var.lambda_sg_id]
  }

  environment {
    variables = {
      ENVIRONMENT           = var.environment
      PUBLIC_BUCKET         = var.public_bucket_id
      METADATA_TABLE        = var.document_metadata_table_name
      APP_CONFIG_SECRET_ARN = var.app_config_secret_arn
      AWS_REGION_NAME       = var.aws_region
      SFN_ARN               = aws_sfn_state_machine.pdf_pipeline.arn
    }
  }

  tracing_config {
    mode = "Active"
  }

  depends_on = [aws_cloudwatch_log_group.lambda_who_ingestor]

  tags = var.tags
}

resource "aws_lambda_permission" "scheduler_invoke_who" {
  statement_id  = "AllowSchedulerInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.who_ingestor.function_name
  principal     = "scheduler.amazonaws.com"
}

################################################################################
# Step Functions — PDF Ingestion State Machine
################################################################################
resource "aws_sfn_state_machine" "pdf_pipeline" {
  name     = "${var.project}-${var.environment}-pdf-pipeline"
  role_arn = var.step_functions_role_arn
  type     = "STANDARD"

  definition = jsonencode({
    Comment = "Nova Health Tech: PDF ingestion pipeline — extract → chunk → embed → index"
    StartAt = "StartTextractJob"
    States = {
      StartTextractJob = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = "${aws_lambda_function.pdf_processor.arn}:$LATEST"
          "Payload.$"  = "$"
        }
        ResultPath = "$.textract_job"
        Retry = [{
          ErrorEquals     = ["Lambda.ServiceException", "Lambda.AWSLambdaException", "Lambda.SdkClientException"]
          IntervalSeconds = 2
          MaxAttempts     = 3
          BackoffRate     = 2
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next        = "PipelineFailed"
          ResultPath  = "$.error"
        }]
        Next = "WaitForTextract"
      }
      WaitForTextract = {
        Type    = "Wait"
        Seconds = 30
        Next    = "CheckTextractStatus"
      }
      CheckTextractStatus = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = "${aws_lambda_function.pdf_processor.arn}:$LATEST"
          Payload = {
            action    = "check_textract_status"
            "job_id.$" = "$.textract_job.Payload.job_id"
            "s3_key.$" = "$.s3_key"
          }
        }
        ResultPath = "$.textract_status"
        Next       = "IsTextractComplete"
      }
      IsTextractComplete = {
        Type = "Choice"
        Choices = [{
          Variable     = "$.textract_status.Payload.status"
          StringEquals = "SUCCEEDED"
          Next         = "ChunkAndEmbed"
        }, {
          Variable     = "$.textract_status.Payload.status"
          StringEquals = "FAILED"
          Next         = "PipelineFailed"
        }]
        Default = "WaitForTextract"
      }
      ChunkAndEmbed = {
        Type     = "Task"
        Resource = "arn:aws:states:::lambda:invoke"
        Parameters = {
          FunctionName = "${aws_lambda_function.chunker_embedder.arn}:$LATEST"
          "Payload.$"  = "$"
        }
        ResultPath = "$.embed_result"
        Retry = [{
          ErrorEquals     = ["Lambda.ServiceException", "Lambda.AWSLambdaException"]
          IntervalSeconds = 5
          MaxAttempts     = 2
          BackoffRate     = 2
        }]
        Catch = [{
          ErrorEquals = ["States.ALL"]
          Next        = "PipelineFailed"
          ResultPath  = "$.error"
        }]
        Next = "PipelineSucceeded"
      }
      PipelineSucceeded = {
        Type = "Succeed"
      }
      PipelineFailed = {
        Type  = "Fail"
        Error = "PipelineError"
        Cause = "Document ingestion pipeline failed — check CloudWatch logs for details"
      }
    }
  })

  logging_configuration {
    log_destination        = "${aws_cloudwatch_log_group.sfn_pipeline.arn}:*"
    include_execution_data = true
    level                  = "ALL"
  }

  tracing_configuration {
    enabled = true
  }

  tags = var.tags
}

################################################################################
# EventBridge Scheduler — monthly WHO API ingestion
################################################################################
resource "aws_scheduler_schedule" "who_monthly" {
  name                         = "${var.project}-${var.environment}-who-monthly"
  description                  = "Trigger WHO API ingestion on the 1st of every month at 02:00 UTC"
  schedule_expression          = var.who_schedule_cron
  schedule_expression_timezone = "UTC"

  flexible_time_window {
    mode                      = "FLEXIBLE"
    maximum_window_in_minutes = 60
  }

  target {
    arn      = aws_lambda_function.who_ingestor.arn
    role_arn = var.scheduler_role_arn

    input = jsonencode({
      source  = "EventBridgeScheduler"
      trigger = "monthly-who-update"
    })
  }
}

################################################################################
# Placeholder ZIP — required for Terraform to create Lambda functions.
# Real code is deployed by CI/CD pipeline (CodePipeline).
################################################################################
data "archive_file" "placeholder" {
  type        = "zip"
  output_path = "${path.module}/placeholder.zip"

  source {
    content  = "def handler(event, context): return {'statusCode': 200, 'body': 'placeholder'}"
    filename = "placeholder.py"
  }
}
