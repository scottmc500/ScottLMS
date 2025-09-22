# ScottLMS Kubernetes Resources
# Kubernetes deployments, services, and configurations
# NOTE: Temporarily disabled until Kubernetes access is configured in Terraform Cloud

# Generate random password for MongoDB Atlas user
resource "random_password" "mongodb_user_password" {
  length  = 16
  special = true
}

# Generate random database username
resource "random_string" "mongodb_username" {
  length  = 8
  special = false
  upper   = false
}

# TODO: Uncomment these resources once Kubernetes access is configured in Terraform Cloud
# 
# # Kubernetes Namespace for the application
# resource "kubernetes_namespace" "scottlms" {
#   metadata {
#     name = local.k8s_config.namespace
#     
#     labels = {
#       app         = local.project_name
#       environment = local.environment
#       managed-by  = "terraform"
#     }
#   }
# }
# 
# # ConfigMap for application configuration
# resource "kubernetes_config_map" "app_config" {
#   metadata {
#     name      = "${local.project_name}-config"
#     namespace = kubernetes_namespace.scottlms.metadata[0].name
#   }
#   
#   data = {
#     ENVIRONMENT     = local.environment
#     LOG_LEVEL       = local.app_config.log_level
#     API_BASE_URL    = "http://${local.project_name}-api:8000"
#     MONGODB_URL     = "mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${mongodbatlas_cluster.main.connection_strings[0].standard_srv}"
#   }
# }
# 
# # Secret for sensitive configuration
# resource "kubernetes_secret" "app_secrets" {
#   metadata {
#     name      = "${local.project_name}-secrets"
#     namespace = kubernetes_namespace.scottlms.metadata[0].name
#   }
#   
#   type = "Opaque"
#   
#   data = {
#     mongodb-uri = base64encode("mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${mongodbatlas_cluster.main.connection_strings[0].standard_srv}")
#   }
# }

