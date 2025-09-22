# ScottLMS Terraform Outputs
# Outputs for Kubernetes cluster and MongoDB Atlas resources

# Kubernetes Cluster Outputs
# output "kubernetes_namespace" {
#   description = "Kubernetes namespace where the application is deployed"
#   value       = kubernetes_namespace.scottlms.metadata[0].name
# }

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
  value       = local.mongodb_config.database_name
}

output "mongodb_username" {
  description = "MongoDB database username"
  value       = random_string.mongodb_username.result
  sensitive   = true
}

# Application Outputs
# output "application_namespace" {
#   description = "Kubernetes namespace where the application is deployed"
#   value       = kubernetes_namespace.scottlms.metadata[0].name
# }

# Security Outputs
output "rbac_enabled" {
  description = "Whether RBAC is enabled on the cluster"
  value       = local.security_config.enable_rbac
}

output "network_policies_enabled" {
  description = "Whether network policies are enabled"
  value       = local.security_config.enable_network_policies
}

# Backup Outputs
output "backup_enabled" {
  description = "Whether automated backups are enabled"
  value       = local.security_config.enable_backups
}

output "backup_retention_days" {
  description = "Number of days backups are retained"
  value       = local.security_config.backup_retention_days
}

# Environment Information
output "environment" {
  description = "Environment name"
  value       = local.environment
}

output "project_name" {
  description = "Project name"
  value       = local.project_name
}

output "region" {
  description = "Primary region"
  value       = local.region
}

# Quick Access Commands
# output "view_pods_command" {
#   description = "Command to view application pods"
#   value       = "kubectl get pods -n ${kubernetes_namespace.scottlms.metadata[0].name}"
# }
# 
# output "view_logs_command" {
#   description = "Command to view application logs"
#   value       = "kubectl logs -l app=scottlms-api -n ${kubernetes_namespace.scottlms.metadata[0].name}"
# }
# 
# output "view_config_command" {
#   description = "Command to view application configuration"
#   value       = "kubectl get configmap ${local.project_name}-config -n ${kubernetes_namespace.scottlms.metadata[0].name} -o yaml"
# }

# Resource Summary
output "infrastructure_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    mongodb_cluster = {
      id     = mongodbatlas_cluster.main.id
      tier   = var.atlas_cluster_tier
      region = local.mongodb_config.provider_region_name
      name   = mongodbatlas_cluster.main.name
    }
    application = {
      replicas  = var.app_replicas
      namespace = "scottlms"  # Will be created when Kubernetes resources are enabled
    }
  }
  sensitive = true
}