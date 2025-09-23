# ScottLMS Infrastructure Outputs
# MongoDB Atlas and Linode cluster information

# === MONGODB ATLAS OUTPUTS ===

output "mongodb_cluster_id" {
  description = "MongoDB Atlas cluster ID"
  value       = mongodbatlas_cluster.main.id
}

output "mongodb_connection_string" {
  description = "MongoDB Atlas connection string"
  value       = mongodbatlas_cluster.main.connection_strings[0].standard_srv
  sensitive   = true
}

output "mongodb_database_name" {
  description = "MongoDB database name"
  value       = "scottlms"
}

output "mongodb_username" {
  description = "MongoDB Atlas database username"
  value       = random_string.mongodb_username.result
  sensitive   = true
}

output "mongodb_password" {
  description = "MongoDB Atlas database password"
  value       = random_password.mongodb_user_password.result
  sensitive   = true
}

output "mongodb_url" {
  description = "Complete MongoDB connection URL with credentials"
  value       = local.mongodb_url
  sensitive   = true
}

# === LINODE CLUSTER OUTPUTS ===

output "linode_cluster_id" {
  description = "Linode LKE cluster ID"
  value       = linode_lke_cluster.scottlms_cluster.id
}

output "linode_cluster_status" {
  description = "Linode LKE cluster status"
  value       = linode_lke_cluster.scottlms_cluster.status
}

output "linode_cluster_endpoint" {
  description = "Linode LKE cluster API endpoint"
  value       = linode_lke_cluster.scottlms_cluster.api_endpoints[0]
}

output "linode_cluster_region" {
  description = "Linode LKE cluster region"
  value       = linode_lke_cluster.scottlms_cluster.region
}

output "linode_cluster_label" {
  description = "Linode LKE cluster label"
  value       = linode_lke_cluster.scottlms_cluster.label
}

output "linode_cluster_version" {
  description = "Linode LKE cluster Kubernetes version"
  value       = linode_lke_cluster.scottlms_cluster.k8s_version
}

# === HELM DEPLOYMENT INFORMATION ===

output "helm_deployment_info" {
  description = "Information for Helm deployments"
  value = {
    cluster_endpoint = linode_lke_cluster.scottlms_cluster.api_endpoints[0]
    cluster_name     = linode_lke_cluster.scottlms_cluster.label
    mongodb_url      = local.mongodb_url
    namespace        = "scottlms"
  }
  sensitive = true
}

# === INFRASTRUCTURE SUMMARY ===

output "infrastructure_summary" {
  description = "Summary of deployed infrastructure"
  value = {
    mongodb_cluster = {
      id     = mongodbatlas_cluster.main.id
      tier   = "M0"
      region = "US_EAST_1"
      name   = mongodbatlas_cluster.main.name
    }
    kubernetes_cluster = {
      id       = linode_lke_cluster.scottlms_cluster.id
      region   = linode_lke_cluster.scottlms_cluster.region
      label    = linode_lke_cluster.scottlms_cluster.label
      version  = linode_lke_cluster.scottlms_cluster.k8s_version
    }
    deployment_method = {
      description = "Kubernetes resources managed by Helm"
      benefits = [
        "Simplified Terraform infrastructure management",
        "Flexible application deployment with Helm",
        "Easy rollbacks and updates",
        "Template-based configuration management"
      ]
    }
  }
  sensitive = true
}