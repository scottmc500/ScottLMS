# ScottLMS Kubernetes Resources
# Kubernetes deployments, services, and configurations
# NOTE: Temporarily disabled until Kubernetes access is configured in Terraform Cloud

# Kubernetes Namespace for the application
resource "kubernetes_namespace" "scottlms" {
  metadata {
    name = "scottlms"
    
    labels = {
      app         = "scottlms"
      environment = "production"
      managed-by  = "terraform"
    }
  }
}
# ConfigMap for application configuration
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "scottlms-config"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  data = {
    ENVIRONMENT     = "production"
    LOG_LEVEL       = "info"
    API_BASE_URL    = "http://scottlms-api:8000"
    MONGODB_URL     = local.mongodb_url
  }
}
# Secret for sensitive configuration
resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "scottlms-secrets"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  type = "Opaque"
  
  data = {
    mongodb-uri = base64encode(local.mongodb_url)
  }
}

# Secret for Docker Hub credentials
resource "kubernetes_secret" "docker_hub_credentials" {
  metadata {
    name      = "docker-hub-credentials"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  type = "kubernetes.io/dockerconfigjson"
  
  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "https://index.docker.io/v1/" = {
          username = var.docker_hub_username
          password = var.docker_hub_password
          auth     = base64encode("${var.docker_hub_username}:${var.docker_hub_password}")
        }
      }
    })
  }
}

# ConfigMap for frontend configuration
resource "kubernetes_config_map" "frontend_config" {
  metadata {
    name      = "scottlms-frontend-config"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  
  data = {
    ENVIRONMENT     = "production"
    API_BASE_URL    = "http://scottlms-api:8000"
    REACT_APP_API_URL = "http://scottlms-api:8000"
  }
}

# Kubernetes Deployment for the application
resource "kubernetes_deployment" "scottlms_api" {
  metadata {
    name      = "scottlms-api"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    
    labels = {
      app         = "scottlms-api"
      environment = "production"
      managed-by  = "terraform"
    }
  }
  
  spec {
    replicas = var.app_replicas
    
    selector {
      match_labels = {
        app = "scottlms-api"
      }
    }
    
    template {
      metadata {
        labels = {
          app         = "scottlms-api"
          environment = "production"
        }
      }
      
      spec {
        image_pull_secrets {
          name = kubernetes_secret.docker_hub_credentials.metadata[0].name
        }
        
        container {
          name              = "scottlms-api"
          image             = "smchenry2014/scottlms-api:${var.app_image_tag}"
          image_pull_policy = "Always"
          
          port {
            container_port = 8000
            name          = "http"
          }
          
          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }
          
          env_from {
            secret_ref {
              name = kubernetes_secret.app_secrets.metadata[0].name
            }
          }
          
          resources {
            requests = {
              cpu    = "100m"
              memory = "256Mi"
            }
            limits = {
              cpu    = "500m"
              memory = "512Mi"
            }
          }
          
          liveness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }
          
          readiness_probe {
            http_get {
              path = "/health"
              port = 8000
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}

# Kubernetes Deployment for the frontend
resource "kubernetes_deployment" "scottlms_frontend" {
  metadata {
    name      = "scottlms-frontend"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    
    labels = {
      app         = "scottlms-frontend"
      environment = "production"
      managed-by  = "terraform"
    }
  }
  
  spec {
    replicas = var.app_replicas
    
    selector {
      match_labels = {
        app = "scottlms-frontend"
      }
    }
    
    template {
      metadata {
        labels = {
          app         = "scottlms-frontend"
          environment = "production"
        }
      }
      
      spec {
        image_pull_secrets {
          name = kubernetes_secret.docker_hub_credentials.metadata[0].name
        }
        
        container {
          name              = "scottlms-frontend"
          image             = "smchenry2014/scottlms-frontend:${var.app_image_tag}"
          image_pull_policy = "Always"
          
          port {
            container_port = 3000
            name          = "http"
          }
          
          env_from {
            config_map_ref {
              name = kubernetes_config_map.frontend_config.metadata[0].name
            }
          }
          
          resources {
            requests = {
              cpu    = "100m"
              memory = "128Mi"
            }
            limits = {
              cpu    = "200m"
              memory = "256Mi"
            }
          }
          
          liveness_probe {
            http_get {
              path = "/"
              port = 3000
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }
          
          readiness_probe {
            http_get {
              path = "/"
              port = 3000
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}

# Kubernetes Service for the application
resource "kubernetes_service" "scottlms_api" {
  metadata {
    name      = "scottlms-api"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    
    labels = {
      app         = "scottlms-api"
      environment = "production"
      managed-by  = "terraform"
    }
  }
  
  spec {
    selector = {
      app = "scottlms-api"
    }
    
    port {
      name        = "http"
      port        = 8000
      target_port = 8000
      protocol    = "TCP"
    }
    
    type = "ClusterIP"
  }
}

# Kubernetes Service for the frontend
resource "kubernetes_service" "scottlms_frontend" {
  metadata {
    name      = "scottlms-frontend"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    
    labels = {
      app         = "scottlms-frontend"
      environment = "production"
      managed-by  = "terraform"
    }
  }
  
  spec {
    selector = {
      app = "scottlms-frontend"
    }
    
    port {
      name        = "http"
      port        = 3000
      target_port = 3000
      protocol    = "TCP"
    }
    
    type = "ClusterIP"
  }
}

# Kubernetes Service for LoadBalancer (frontend external access)
resource "kubernetes_service" "scottlms_frontend_loadbalancer" {
  count = var.domain_name == "" ? 1 : 0
  
  metadata {
    name      = "scottlms-frontend-loadbalancer"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    
    labels = {
      app         = "scottlms-frontend"
      environment = "production"
      managed-by  = "terraform"
    }
  }
  
  spec {
    selector = {
      app = "scottlms-frontend"
    }
    
    port {
      name        = "http"
      port        = 80
      target_port = 3000
      protocol    = "TCP"
    }
    
    type = "LoadBalancer"
  }
}

# Kubernetes Service for LoadBalancer (API external access)
resource "kubernetes_service" "scottlms_api_loadbalancer" {
  count = var.domain_name == "" ? 1 : 0
  
  metadata {
    name      = "scottlms-api-loadbalancer"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    
    labels = {
      app         = "scottlms-api"
      environment = "production"
      managed-by  = "terraform"
    }
  }
  
  spec {
    selector = {
      app = "scottlms-api"
    }
    
    port {
      name        = "http"
      port        = 8000
      target_port = 8000
      protocol    = "TCP"
    }
    
    type = "LoadBalancer"
  }
}

