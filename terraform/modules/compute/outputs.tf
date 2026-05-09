output "ecr_repository_url" {
  value = aws_ecr_repository.rag_service.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_cluster_arn" {
  value = aws_ecs_cluster.main.arn
}

output "ecs_service_name" {
  value = aws_ecs_service.rag_service.name
}

output "alb_internal_arn" {
  value = aws_lb.internal.arn
}

output "alb_internal_dns" {
  value = aws_lb.internal.dns_name
}

output "alb_listener_arn" {
  value = aws_lb_listener.http.arn
}

output "target_group_arn" {
  value = aws_lb_target_group.rag_service.arn
}
