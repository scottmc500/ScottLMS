# ScottLMS Kubernetes Resources
# This file manages all Kubernetes resources for the ScottLMS application

# Kubernetes Namespace
resource "kubernetes_namespace" "scottlms" {
  metadata {
    name = "scottlms"
    labels = {
      app = "scottlms"
    }
  }
}

# ConfigMap
resource "kubernetes_config_map" "app_config" {
  metadata {
    name      = "scottlms-config"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }

  data = {
    API_PORT      = "8000"
    FRONTEND_PORT = "8501"
    API_BASE_URL  = "http://scottlms-api-loadbalancer:8000"
  }
}

# Secrets
resource "kubernetes_secret" "app_secrets" {
  metadata {
    name      = "scottlms-secrets"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }
  type = "Opaque"
  data = {
    MONGODB_URL = local.mongodb_url
  }
}

resource "kubernetes_secret" "docker_hub_credentials" {
  metadata {
    name      = "docker-hub-credentials"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
  }

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

  type = "kubernetes.io/dockerconfigjson"
}

# API Deployment
resource "kubernetes_deployment" "scottlms_api" {
  metadata {
    name      = "scottlms-api"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    labels = {
      app = "scottlms-api"
    }
  }

  timeouts {
    create = "3m"
    update = "3m"
    delete = "3m"
  }

         spec {
           replicas = 2
           progress_deadline_seconds = 600

           selector {
             match_labels = {
               app = "scottlms-api"
             }
           }

    template {
      metadata {
        labels = {
          app = "scottlms-api"
        }
      }

      spec {
        image_pull_secrets {
          name = kubernetes_secret.docker_hub_credentials.metadata[0].name
        }

        container {
          name  = "scottlms-api"
          image = "smchenry2014/scottlms-api:${var.app_image_tag}"

          port {
            container_port = 8000
          }

          env {
            name = "MONGODB_URL"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.app_secrets.metadata[0].name
                key  = "MONGODB_URL"
              }
            }
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          resources {
            requests = {
              memory = "256Mi"
              cpu    = "250m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "500m"
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

# Frontend Deployment
resource "kubernetes_deployment" "scottlms_frontend" {
  metadata {
    name      = "scottlms-frontend"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    labels = {
      app = "scottlms-frontend"
    }
  }

  timeouts {
    create = "3m"
    update = "3m"
    delete = "3m"
  }

  spec {
    replicas = 2

    selector {
      match_labels = {
        app = "scottlms-frontend"
      }
    }

    template {
      metadata {
        labels = {
          app = "scottlms-frontend"
        }
      }

      spec {
        image_pull_secrets {
          name = kubernetes_secret.docker_hub_credentials.metadata[0].name
        }

        container {
          name  = "scottlms-frontend"
          image = "smchenry2014/scottlms-ui:${var.app_image_tag}"

          port {
            container_port = 8501
          }

          env_from {
            config_map_ref {
              name = kubernetes_config_map.app_config.metadata[0].name
            }
          }

          resources {
            requests = {
              memory = "256Mi"
              cpu    = "250m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "500m"
            }
          }

          liveness_probe {
            http_get {
              path = "/"
              port = 8501
            }
            initial_delay_seconds = 30
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/"
              port = 8501
            }
            initial_delay_seconds = 5
            period_seconds        = 5
          }
        }
      }
    }
  }
}

# Services - LoadBalancers for external access
resource "kubernetes_service" "scottlms_api_loadbalancer" {
  count = 1
  metadata {
    name      = "scottlms-api-loadbalancer"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    labels = {
      app = "scottlms-api"
    }
  }

  spec {
    type = "LoadBalancer"
    port {
      port        = 8000
      target_port = 8000
      protocol    = "TCP"
      name        = "http"
    }
    selector = {
      app = "scottlms-api"
    }
  }
}

resource "kubernetes_service" "scottlms_frontend_loadbalancer" {
  count = 1
  metadata {
    name      = "scottlms-frontend-loadbalancer"
    namespace = kubernetes_namespace.scottlms.metadata[0].name
    labels = {
      app = "scottlms-frontend"
    }
  }

  spec {
    type = "LoadBalancer"
    port {
      port        = 80
      target_port = 8501
      protocol    = "TCP"
      name        = "http"
    }
    selector = {
      app = "scottlms-frontend"
    }
  }
}
