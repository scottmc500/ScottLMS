# ScottLMS Infrastructure Outputs
# Only outputs needed for Kubernetes deployment

# === DEPLOYMENT OUTPUTS ===

output "mongodb_url" {
  description = "Base64 encoded MongoDB connection string for Kubernetes secrets"
  value       = local.mongodb_url
  sensitive   = true
}

# === CLUSTER ACCESS OUTPUTS ===

output "linode_cluster_kubeconfig" {
  description = "Linode LKE cluster kubeconfig for kubectl access"
  value       = base64decode(linode_lke_cluster.scottlms_cluster.kubeconfig)
  sensitive   = true
}

# === LOAD BALANCER IP OUTPUTS ===

output "api_external_ip" {
  description = "External IP address of the API LoadBalancer service"
  value       = data.external.loadbalancer_ips.result.api_ip
}

output "frontend_external_ip" {
  description = "External IP address of the Frontend LoadBalancer service"
  value       = data.external.loadbalancer_ips.result.frontend_ip
}