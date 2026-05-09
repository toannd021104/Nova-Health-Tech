################################################################################
# ECR Repository — RAG inference service
################################################################################
resource "aws_ecr_repository" "rag_service" {
  name                 = "${var.project}-${var.environment}-rag-service"
  image_tag_mutability = "IMMUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "KMS"
  }

  tags = var.tags
}

resource "aws_ecr_lifecycle_policy" "rag_service" {
  repository = aws_ecr_repository.rag_service.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 20 production images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["prod-"]
          countType     = "imageCountMoreThan"
          countNumber   = 20
        }
        action = { type = "expire" }
      },
      {
        rulePriority = 2
        description  = "Expire untagged images after 7 days"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 7
        }
        action = { type = "expire" }
      }
    ]
  })
}

################################################################################
# CloudWatch Log Group — ECS
################################################################################
resource "aws_cloudwatch_log_group" "rag_service" {
  name              = "/ecs/${var.project}-${var.environment}-rag-service"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

################################################################################
# ECS Cluster
################################################################################
resource "aws_ecs_cluster" "main" {
  name = "${var.project}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = var.tags
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name       = aws_ecs_cluster.main.name
  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    capacity_provider = "FARGATE"
    weight            = 1
    base              = var.min_capacity
  }
}

################################################################################
# ECS Task Definition — RAG service
################################################################################
resource "aws_ecs_task_definition" "rag_service" {
  family                   = "${var.project}-${var.environment}-rag-service"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory_mb
  task_role_arn            = var.ecs_task_role_arn
  execution_role_arn       = var.ecs_execution_role_arn

  container_definitions = jsonencode([
    {
      name      = "rag-service"
      image     = var.container_image
      essential = true

      portMappings = [{
        containerPort = 8080
        protocol      = "tcp"
      }]

      environment = [
        { name = "ENVIRONMENT", value = var.environment },
        { name = "AWS_REGION", value = var.aws_region },
        { name = "OPENSEARCH_PUBLIC_ENDPOINT", value = var.opensearch_public_endpoint },
        { name = "OPENSEARCH_PHI_ENDPOINT", value = var.opensearch_phi_endpoint },
        { name = "REDIS_HOST", value = var.redis_endpoint },
        { name = "REDIS_PORT", value = tostring(var.redis_port) },
        { name = "BEDROCK_GUARDRAIL_ID", value = var.guardrail_id },
        { name = "BEDROCK_GUARDRAIL_VERSION", value = var.guardrail_version },
        { name = "APP_CONFIG_SECRET_ARN", value = var.app_config_secret_arn }
      ]

      secrets = [
        {
          name      = "APP_CONFIG"
          valueFrom = var.app_config_secret_arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.rag_service.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "rag-service"
        }
      }

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8080/health || exit 1"]
        interval    = 15
        timeout     = 5
        retries     = 3
        startPeriod = 30
      }

      # Read-only root filesystem (security hardening)
      readonlyRootFilesystem = true
      user                   = "1000:1000"
    }
  ])

  tags = var.tags
}

################################################################################
# Network Load Balancer (internal — required for API Gateway REST VPC Link)
################################################################################
resource "aws_lb" "internal" {
  name               = "${var.project}-${var.environment}-nlb-int"
  internal           = true
  load_balancer_type = "network"
  subnets            = var.private_subnet_ids

  enable_deletion_protection = var.environment == "prod"

  access_logs {
    bucket  = "${var.project}-${var.environment}-audit-logs-${var.aws_account_id}"
    prefix  = "nlb"
    enabled = var.environment == "prod"
  }

  tags = var.tags
}

resource "aws_lb_target_group" "rag_service" {
  name        = "${var.project}-${var.environment}-rag-tg"
  port        = 8080
  protocol    = "TCP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    path                = "/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 15
  }

  deregistration_delay = 30

  tags = var.tags
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.internal.arn
  port              = 80
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.rag_service.arn
  }
}

################################################################################
# ECS Service
################################################################################
resource "aws_ecs_service" "rag_service" {
  name                               = "${var.project}-${var.environment}-rag-service"
  cluster                            = aws_ecs_cluster.main.id
  task_definition                    = aws_ecs_task_definition.rag_service.arn
  desired_count                      = var.min_capacity
  launch_type                        = "FARGATE"
  platform_version                   = "LATEST"
  health_check_grace_period_seconds  = 60
  enable_execute_command             = false
  propagate_tags                     = "TASK_DEFINITION"

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.sg_ecs_tasks_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.rag_service.arn
    container_name   = "rag-service"
    container_port   = 8080
  }

  deployment_minimum_healthy_percent = 50
  deployment_maximum_percent         = 200

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  deployment_controller {
    type = "ECS"
  }

  tags = var.tags

  lifecycle {
    ignore_changes = [desired_count, task_definition]
  }
}

################################################################################
# Auto-scaling — target tracking on CPU and request count
################################################################################
resource "aws_appautoscaling_target" "rag_service" {
  max_capacity       = var.max_capacity
  min_capacity       = var.min_capacity
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.rag_service.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "${var.project}-${var.environment}-ecs-cpu-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.rag_service.resource_id
  scalable_dimension = aws_appautoscaling_target.rag_service.scalable_dimension
  service_namespace  = aws_appautoscaling_target.rag_service.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 60.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
  }
}

resource "aws_appautoscaling_policy" "memory" {
  name               = "${var.project}-${var.environment}-ecs-memory-scaling"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.rag_service.resource_id
  scalable_dimension = aws_appautoscaling_target.rag_service.scalable_dimension
  service_namespace  = aws_appautoscaling_target.rag_service.service_namespace

  target_tracking_scaling_policy_configuration {
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60

    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageMemoryUtilization"
    }
  }
}
