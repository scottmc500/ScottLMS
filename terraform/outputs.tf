# ScottLMS Infrastructure Outputs
# MongoDB Atlas and Linode cluster information

# === MONGODB ATLAS OUTPUTS ===

output "mongodb_cluster_id" {
  description = "MongoDB Atlas cluster ID"
  value       = mongodbatlas_cluster.main.id
}

output "mongodb_debug_info" {
  description = "Debug information for MongoDB URL construction"
  value       = local.mongodb_debug
  sensitive   = true
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

output "linode_cluster_kubeconfig" {
  description = "Linode LKE cluster kubeconfig"
  value       = yamldecode(base64decode(linode_lke_cluster.scottlms_cluster.kubeconfig))
  sensitive   = true
}

output "linode_cluster_kube_token" {
  description = "Linode LKE cluster kube token"
  value       = yamldecode(base64decode(linode_lke_cluster.scottlms_cluster.kubeconfig)).users[0].user.token
  sensitive   = true
}

output "linode_cluster_kube_certificate" {
  description = "Linode LKE cluster kube certificate"
  value       = yamldecode(base64decode(linode_lke_cluster.scottlms_cluster.kubeconfig)).clusters[0].cluster.certificate-authority-data
  sensitive   = true
}

# === KUBERNETES NAMESPACE ===

output "kubernetes_namespace" {
  description = "Kubernetes namespace name"
  value       = kubernetes_namespace.scottlms.metadata[0].name
}

# === APPLICATION SERVICES ===

output "application_service" {
  description = "Application service endpoint for external access"
  value = {
    api_service = {
      name      = kubernetes_service.scottlms_api_loadbalancer[0].metadata[0].name
      namespace = kubernetes_service.scottlms_api_loadbalancer[0].metadata[0].namespace
      type      = kubernetes_service.scottlms_api_loadbalancer[0].spec[0].type
    }
    frontend_service = {
      name      = kubernetes_service.scottlms_frontend_loadbalancer[0].metadata[0].name
      namespace = kubernetes_service.scottlms_frontend_loadbalancer[0].metadata[0].namespace
      type      = kubernetes_service.scottlms_frontend_loadbalancer[0].spec[0].type
    }
  }
}

output "api_service_name" {
  description = "API service name"
  value       = kubernetes_service.scottlms_api_loadbalancer[0].metadata[0].name
}

output "frontend_external_ip" {
  description = "Frontend service external IP"
  value       = kubernetes_service.scottlms_frontend_loadbalancer[0].status[0].load_balancer[0].ingress[0].ip
}

output "api_external_ip" {
  description = "API service external IP"
  value       = kubernetes_service.scottlms_api_loadbalancer[0].status[0].load_balancer[0].ingress[0].ip
}