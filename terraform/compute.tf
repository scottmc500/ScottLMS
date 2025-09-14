# ECS Cluster
resource "aws_ecs_cluster" "scottlms" {
  name = local.name

  configuration {
    execute_command_configuration {
      logging = "DEFAULT"
    }
  }

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = local.common_tags
}

# ECS Cluster Capacity Providers
resource "aws_ecs_cluster_capacity_providers" "scottlms" {
  cluster_name = aws_ecs_cluster.scottlms.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE_SPOT"
  }
}

# ECS Task Definition for API
resource "aws_ecs_task_definition" "scottlms_api" {
  family                   = "scottlms-api"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256  # 0.25 vCPU
  memory                   = 512  # 512 MB
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "scottlms-api"
      image = "${aws_ecr_repository.scottlms.repository_url}:${var.image_tag}"
      
      portMappings = [
        {
          containerPort = 8000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ENVIRONMENT"
          value = "production"
        },
        {
          name  = "LOG_LEVEL"
          value = "info"
        },
        {
          name  = "DATABASE_NAME"
          value = "scottlms"
        }
      ]

      secrets = [
        {
          name      = "MONGODB_URL"
          valueFrom = aws_secretsmanager_secret.documentdb_url.arn
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.scottlms_api.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = local.common_tags
}

# ECS Task Definition for Frontend
resource "aws_ecs_task_definition" "scottlms_frontend" {
  family                   = "scottlms-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256  # 0.25 vCPU
  memory                   = 512  # 512 MB
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "scottlms-frontend"
      image = "${aws_ecr_repository.scottlms_frontend.repository_url}:${var.image_tag}"
      
      portMappings = [
        {
          containerPort = 8501
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "API_BASE_URL"
          value = "http://${aws_lb.scottlms.dns_name}"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.scottlms_frontend.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = local.common_tags
}

# ECS Service for API
resource "aws_ecs_service" "scottlms_api" {
  name            = "scottlms-api"
  cluster         = aws_ecs_cluster.scottlms.id
  task_definition = aws_ecs_task_definition.scottlms_api.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = module.vpc.private_subnets
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.scottlms_api.arn
    container_name   = "scottlms-api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.scottlms_api]

  tags = local.common_tags
}

# ECS Service for Frontend
resource "aws_ecs_service" "scottlms_frontend" {
  name            = "scottlms-frontend"
  cluster         = aws_ecs_cluster.scottlms.id
  task_definition = aws_ecs_task_definition.scottlms_frontend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets          = module.vpc.private_subnets
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.scottlms_frontend.arn
    container_name   = "scottlms-frontend"
    container_port   = 8501
  }

  depends_on = [aws_lb_listener.scottlms_frontend]

  tags = local.common_tags
}

# ECS Execution Role
resource "aws_iam_role" "ecs_execution_role" {
  name = "${local.name}-ecs-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_execution_role" {
  role       = aws_iam_role.ecs_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Additional policy for ECS execution role to access Secrets Manager
resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${local.name}-ecs-execution-secrets"
  role = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.documentdb_url.arn
        ]
      }
    ]
  })
}

# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name = "${local.name}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "scottlms_api" {
  name              = "/ecs/scottlms-api"
  retention_in_days = 7

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "scottlms_frontend" {
  name              = "/ecs/scottlms-frontend"
  retention_in_days = 7

  tags = local.common_tags
}