output "user_pool_id" {
  value = aws_cognito_user_pool.main.id
}

output "user_pool_arn" {
  value = aws_cognito_user_pool.main.arn
}

output "user_pool_endpoint" {
  value = aws_cognito_user_pool.main.endpoint
}

output "app_client_id" {
  value = aws_cognito_user_pool_client.clinical_app.id
}

output "identity_pool_id" {
  value = aws_cognito_identity_pool.main.id
}

output "auth_domain" {
  value = "${aws_cognito_user_pool_domain.main.domain}.auth.${var.aws_region}.amazoncognito.com"
}
