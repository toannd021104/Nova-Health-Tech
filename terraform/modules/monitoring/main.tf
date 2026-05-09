################################################################################
# CloudWatch Dashboard — operational overview
################################################################################
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project}-${var.environment}-operations"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "API Latency P50/P95/P99 (ms) — ≤2s SLA target"
          period = 60
          stat   = "p95"
          metrics = [
            ["AWS/ApiGateway", "IntegrationLatency", "ApiId", var.api_gateway_id, { stat = "p50", label = "P50" }],
            [".", ".", ".", ".", { stat = "p95", label = "P95" }],
            [".", ".", ".", ".", { stat = "p99", label = "P99" }]
          ]
          annotations = {
            horizontal = [{
              label = "2s SLA"
              value = 2000
              color = "#ff0000"
            }]
          }
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "API Error Rate (5xx)"
          period = 60
          metrics = [
            ["AWS/ApiGateway", "5XXError", "ApiId", var.api_gateway_id],
            [".", "Count", ".", "."]
          ]
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "ECS Task Count & CPU/Memory"
          period = 60
          metrics = [
            ["ECS/ContainerInsights", "RunningTaskCount", "ClusterName", var.ecs_cluster_name, "ServiceName", var.ecs_service_name],
            [".", "CpuUtilized", ".", ".", ".", "."],
            [".", "MemoryUtilized", ".", ".", ".", "."]
          ]
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "Bedrock Token Usage"
          period = 300
          metrics = [
            ["AWS/Bedrock", "InputTokenCount", "ModelId", "anthropic.claude-3-5-sonnet-20241022-v2:0"],
            [".", "OutputTokenCount", ".", "."],
            [".", "InvocationLatency", ".", "."]
          ]
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "Redis Cache Hit Rate"
          period = 60
          metrics = [
            ["AWS/ElastiCache", "CacheHits"],
            [".", "CacheMisses"],
            [{
              expression = "hits/(hits+misses)*100"
              label      = "Hit Rate %"
              id         = "e1"
            }]
          ]
        }
      }
    ]
  })
}

################################################################################
# CloudWatch Alarms
################################################################################

# P95 Latency > 2s
resource "aws_cloudwatch_metric_alarm" "api_p95_latency" {
  alarm_name          = "${var.project}-${var.environment}-api-p95-latency-breach"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = var.p95_latency_threshold_ms
  alarm_description   = "API P95 latency exceeds 2s SLA threshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [var.alert_topic_arn]
  ok_actions          = [var.alert_topic_arn]

  metric_query {
    id          = "m1"
    return_data = true

    metric {
      metric_name = "IntegrationLatency"
      namespace   = "AWS/ApiGateway"
      period      = 60
      stat        = "p95"
      dimensions  = { ApiId = var.api_gateway_id }
    }
  }

  tags = var.tags
}

# 5xx error rate > 1%
resource "aws_cloudwatch_metric_alarm" "api_error_rate" {
  alarm_name          = "${var.project}-${var.environment}-api-5xx-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  threshold           = var.error_rate_threshold_pct
  alarm_description   = "API 5xx error rate exceeded threshold"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [var.alert_topic_arn]

  metric_query {
    id = "error_rate"
    expression = "(errors / total) * 100"
    label       = "Error Rate %"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "5XXError"
      namespace   = "AWS/ApiGateway"
      period      = 60
      stat        = "Sum"
      dimensions  = { ApiId = var.api_gateway_id }
    }
  }

  metric_query {
    id = "total"
    metric {
      metric_name = "Count"
      namespace   = "AWS/ApiGateway"
      period      = 60
      stat        = "Sum"
      dimensions  = { ApiId = var.api_gateway_id }
    }
  }

  tags = var.tags
}

# ECS task CPU > 85% sustained — scale already triggered but alert if persists
resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${var.project}-${var.environment}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 5
  metric_name         = "CpuUtilized"
  namespace           = "ECS/ContainerInsights"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "ECS CPU utilization sustained above 85% for 5 minutes"
  treat_missing_data  = "notBreaching"
  alarm_actions       = [var.alert_topic_arn]

  dimensions = {
    ClusterName = var.ecs_cluster_name
    ServiceName = var.ecs_service_name
  }

  tags = var.tags
}

################################################################################
# X-Ray — Distributed tracing
################################################################################
resource "aws_xray_sampling_rule" "clinical_query" {
  rule_name      = "${var.project}-${var.environment}-clinical-query"
  priority       = 1000
  reservoir_size = 10
  fixed_rate     = 0.05
  url_path       = "/v1/query"
  host           = "*"
  http_method    = "POST"
  service_name   = "*"
  service_type   = "*"
  resource_arn   = "*"
  version        = 1

  tags = var.tags
}

# Sample 100% of requests that are slow (>1.5s) — catches latency regressions
resource "aws_xray_sampling_rule" "slow_requests" {
  rule_name      = "${var.project}-${var.environment}-slow-requests"
  priority       = 999
  reservoir_size = 50
  fixed_rate     = 1.0
  url_path       = "*"
  host           = "*"
  http_method    = "*"
  service_name   = "*"
  service_type   = "*"
  resource_arn   = "*"
  version        = 1

  attributes = {
    "x-nova-latency-tier" = "slow"
  }

  tags = var.tags
}
