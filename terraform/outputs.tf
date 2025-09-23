# ScottLMS Terraform Outputs
# Outputs for Kubernetes cluster and MongoDB Atlas resources

# Kubernetes Cluster Outputs
output "kubernetes_namespace" {
  description = "Kubernetes namespace where the application is deployed"
  value       = kubernetes_namespace.scottlms.metadata[0].name
}

# MongoDB Atlas Outputs
output "mongodb_cluster_id" {
  description = "ID of the MongoDB Atlas cluster"
  value       = mongodbatlas_cluster.main.id
}

output "mongodb_cluster_connection_string_srv" {
  description = "SRV connection string for the MongoDB Atlas cluster"
  value       = mongodbatlas_cluster.main.connection_strings[0].standard_srv
  sensitive   = true
}

output "mongodb_database_name" {
  description = "Name of the MongoDB database"
  value       = "scottlms"
}

output "mongodb_username" {
  description = "MongoDB database username"
  value       = random_string.mongodb_username.result
  sensitive   = true
}

output "mongodb_complete_url" {
  description = "Complete MongoDB connection URL with credentials"
  value       = local.mongodb_url
  sensitive   = true
}

# Application Outputs
output "application_namespace" {
  description = "Kubernetes namespace where the application is deployed"
  value       = kubernetes_namespace.scottlms.metadata[0].name
}

output "application_service" {
  description = "Kubernetes service name for the application"
  value       = kubernetes_service.scottlms_api.metadata[0].name
}

output "frontend_loadbalancer_ip" {
  description = "External IP address of the frontend LoadBalancer service"
  value       = var.domain_name == "" ? kubernetes_service.scottlms_frontend_loadbalancer[0].status[0].load_balancer[0].ingress[0].ip : null
}

output "api_loadbalancer_ip" {
  description = "External IP address of the API LoadBalancer service"
  value       = var.domain_name == "" ? kubernetes_service.scottlms_api_loadbalancer[0].status[0].load_balancer[0].ingress[0].ip : null
}

# Security Outputs
output "rbac_enabled" {
  description = "Whether RBAC is enabled on the cluster"
  value       = true
}

output "network_policies_enabled" {
  description = "Whether network policies are enabled"
  value       = true
}

# Backup Outputs
output "backup_enabled" {
  description = "Whether automated backups are enabled"
  value       = true
}

output "backup_retention_days" {
  description = "Number of days backups are retained"
  value       = 7
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = "production"
}

output "project_name" {
  description = "Project name"
  value       = "scottlms"
}

output "region" {
  description = "Primary region"
  value       = "us-east"
}

# Quick Access Commands
output "view_pods_command" {
  description = "Command to view application pods"
  value       = "kubectl get pods -n ${kubernetes_namespace.scottlms.metadata[0].name}"
}

output "view_logs_command" {
  description = "Command to view application logs"
  value       = "kubectl logs -l app=scottlms-api -n ${kubernetes_namespace.scottlms.metadata[0].name}"
}

output "view_config_command" {
  description = "Command to view application configuration"
  value       = "kubectl get configmap scottlms-config -n ${kubernetes_namespace.scottlms.metadata[0].name} -o yaml"
}

output "view_frontend_pods_command" {
  description = "Command to view frontend pods"
  value       = "kubectl get pods -l app=scottlms-frontend -n ${kubernetes_namespace.scottlms.metadata[0].name}"
}

output "view_frontend_logs_command" {
  description = "Command to view frontend logs"
  value       = "kubectl logs -l app=scottlms-frontend -n ${kubernetes_namespace.scottlms.metadata[0].name}"
}

# Resource Summary
output "infrastructure_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    mongodb_cluster = {
      id     = mongodbatlas_cluster.main.id
      tier   = var.atlas_cluster_tier
      region = "US_EAST_1"
      name   = mongodbatlas_cluster.main.name
    }
    application = {
      replicas  = var.app_replicas
      namespace = "scottlms"  # Will be created when Kubernetes resources are enabled
    }
  }
  sensitive = true
}