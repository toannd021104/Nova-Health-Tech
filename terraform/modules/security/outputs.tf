output "cloudtrail_arn" {
  value = aws_cloudtrail.main.arn
}

output "guardduty_detector_id" {
  value = aws_guardduty_detector.main.id
}

output "security_alerts_topic_arn" {
  value = aws_sns_topic.security_alerts.arn
}

output "securityhub_arn" {
  value = aws_securityhub_account.main.id
}
