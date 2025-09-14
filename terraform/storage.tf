# ECR Repository for ScottLMS API
resource "aws_ecr_repository" "scottlms" {
  name                 = "scottlms-api"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = local.common_tags
}

# ECR Repository for ScottLMS Frontend
resource "aws_ecr_repository" "scottlms_frontend" {
  name                 = "scottlms-frontend"
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }

  encryption_configuration {
    encryption_type = "AES256"
  }

  tags = local.common_tags
}

# ECR Lifecycle Policy for API
resource "aws_ecr_lifecycle_policy" "scottlms" {
  repository = aws_ecr_repository.scottlms.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ECR Lifecycle Policy for Frontend
resource "aws_ecr_lifecycle_policy" "scottlms_frontend" {
  repository = aws_ecr_repository.scottlms_frontend.name

  policy = jsonencode({
    rules = [
      {
        rulePriority = 1
        description  = "Keep last 10 images"
        selection = {
          tagStatus     = "tagged"
          tagPrefixList = ["v"]
          countType     = "imageCountMoreThan"
          countNumber   = 10
        }
        action = {
          type = "expire"
        }
      },
      {
        rulePriority = 2
        description  = "Delete untagged images older than 1 day"
        selection = {
          tagStatus   = "untagged"
          countType   = "sinceImagePushed"
          countUnit   = "days"
          countNumber = 1
        }
        action = {
          type = "expire"
        }
      }
    ]
  })
}

# ECR Repository Policy
resource "aws_ecr_repository_policy" "scottlms" {
  repository = aws_ecr_repository.scottlms.name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowPushPull"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability",
          "ecr:PutImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload"
        ]
      }
    ]
  })
}


# Store DocumentDB connection string in AWS Secrets Manager
resource "aws_secretsmanager_secret" "documentdb_url" {
  name        = "${local.name}-documentdb-url"
  description = "DocumentDB connection string for ScottLMS"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "documentdb_url" {
  secret_id = aws_secretsmanager_secret.documentdb_url.id
  secret_string = "mongodb://${aws_docdb_cluster.scottlms.master_username}:${random_password.documentdb_password.result}@${aws_docdb_cluster.scottlms.endpoint}:27017/scottlms?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
}
