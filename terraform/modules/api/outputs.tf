output "api_gateway_id" {
  value = aws_api_gateway_rest_api.main.id
}

output "api_gateway_invoke_url" {
  value = aws_api_gateway_stage.main.invoke_url
}

output "waf_web_acl_arn" {
  value = aws_wafv2_web_acl.api.arn
}

output "vpc_link_id" {
  value = aws_api_gateway_vpc_link.main.id
}
