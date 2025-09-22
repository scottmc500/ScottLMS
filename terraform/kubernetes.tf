# ScottLMS Kubernetes Resources
# Kubernetes deployments, services, and configurations

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

# Kubernetes Namespace for the application
resource "kubernetes_namespace" "scottlms" {
  metadata {
    name = local.k8s_config.namespace
    
    labels = {
      app         = local.project_name
      environment = local.environment
      managed-by  = "terraform"
    }
  }
}

# ConfigMap for application configuration
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "${local.project_name}-config"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  data = {
    ENVIRONMENT     = local.environment
    LOG_LEVEL       = local.app_config.log_level
    API_BASE_URL    = "http://${local.project_name}-api:8000"
    MONGODB_URL     = "mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${mongodbatlas_cluster.main.connection_strings[0].standard_srv}"
  }
}

# Secret for sensitive configuration
resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "${local.project_name}-secrets"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  type = "Opaque"
  
  data = {
    mongodb-uri = base64encode("mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${mongodbatlas_cluster.main.connection_strings[0].standard_srv}")
  }
}

# ConfigMap for MongoDB initialization script
resource "kubernetes_config_map" "mongo_init_script" {
  metadata {
    name      = "${local.project_name}-mongo-init"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  data = {
    "init-script.js" = file("${path.module}/mongo-init-atlas.js")
  }
}

# Kubernetes Job to initialize MongoDB
resource "kubernetes_job" "mongo_init" {
  metadata {
    name      = "${local.project_name}-mongo-init"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  spec {
    template {
      metadata {
        labels = {
          app = "${local.project_name}-mongo-init"
        }
      }
      
      spec {
        restart_policy = "OnFailure"
        
        container {
          name  = "mongo-init"
          image = "mongo:7.0"
          
          command = ["mongosh"]
          args = [
            "${mongodbatlas_cluster.main.connection_strings[0].standard_srv}",
            "--username", random_string.mongodb_username.result,
            "--password", random_password.mongodb_user_password.result,
            "--authenticationDatabase", "admin",
            "--file", "/scripts/init-script.js"
          ]
          
          volume_mount {
            name       = "init-script"
            mount_path = "/scripts"
            read_only  = true
          }
          
          env {
            name  = "MONGODB_URI"
            value = "mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${mongodbatlas_cluster.main.connection_strings[0].standard_srv}"
          }
        }
        
        volume {
          name = "init-script"
          config_map {
            name = kubernetes_config_map.mongo_init_script.metadata[0].name
          }
        }
      }
    }
    
    backoff_limit = 3
  }
  
  depends_on = [
    mongodbatlas_cluster.main,
    mongodbatlas_database_user.scottlms_user,
    kubernetes_namespace.scottlms
  ]
}
