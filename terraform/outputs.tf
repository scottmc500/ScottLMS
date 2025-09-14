# Outputs for ScottLMS AWS Infrastructure

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = module.vpc.vpc_cidr_block
}

output "private_subnets" {
  description = "List of IDs of private subnets"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of IDs of public subnets"
  value       = module.vpc.public_subnets
}

# ECS Outputs
output "ecs_cluster_id" {
  description = "ECS cluster ID"
  value       = aws_ecs_cluster.scottlms.id
}

output "ecs_cluster_arn" {
  description = "ECS cluster ARN"
  value       = aws_ecs_cluster.scottlms.arn
}

output "ecs_cluster_name" {
  description = "ECS cluster name"
  value       = aws_ecs_cluster.scottlms.name
}

# Load Balancer Outputs
output "alb_dns_name" {
  description = "DNS name of the Application Load Balancer"
  value       = aws_lb.scottlms.dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value       = aws_lb.scottlms.zone_id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value       = aws_lb.scottlms.arn
}

# ECR Outputs
output "ecr_repository_url" {
  description = "URL of the ECR repository for API"
  value       = aws_ecr_repository.scottlms.repository_url
}

output "ecr_frontend_repository_url" {
  description = "URL of the ECR repository for Frontend"
  value       = aws_ecr_repository.scottlms_frontend.repository_url
}

# SSL Certificate Outputs
# output "certificate_arn" {
#   description = "ARN of the SSL certificate"
#   value       = aws_acm_certificate.scottlms.arn
# }

# Route53 Outputs
output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = aws_route53_zone.scottlms.zone_id
}

# DocumentDB Outputs
output "documentdb_endpoint" {
  description = "DocumentDB cluster endpoint"
  value       = aws_docdb_cluster.scottlms.endpoint
}

output "documentdb_port" {
  description = "DocumentDB cluster port"
  value       = aws_docdb_cluster.scottlms.port
}

output "documentdb_connection_string" {
  description = "DocumentDB connection string"
  value       = "mongodb://${aws_docdb_cluster.scottlms.master_username}:${random_password.documentdb_password.result}@${aws_docdb_cluster.scottlms.endpoint}:27017/scottlms?ssl=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"
  sensitive   = true
}

# Application URLs
output "api_url" {
  description = "URL of the API service"
  value       = "http://${aws_lb.scottlms.dns_name}"
}

output "frontend_url" {
  description = "URL of the Frontend service"
  value       = "http://${aws_lb.scottlms.dns_name}:8080"
}