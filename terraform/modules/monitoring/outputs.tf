output "dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}

output "latency_alarm_arn" {
  value = aws_cloudwatch_metric_alarm.api_p95_latency.arn
}

output "error_rate_alarm_arn" {
  value = aws_cloudwatch_metric_alarm.api_error_rate.arn
}
