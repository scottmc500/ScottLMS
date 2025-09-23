# ScottLMS Terraform Variables - Streamlined for CI/CD
# Only essential variables that need to be passed from CI/CD pipeline

# === ESSENTIAL VARIABLES (Must be set in CI/CD) ===
variable "atlas_public_key" {
  description = "MongoDB Atlas public API key"
  type        = string
  sensitive   = true
}

variable "atlas_private_key" {
  description = "MongoDB Atlas private API key"
  type        = string
  sensitive   = true
}

variable "atlas_org_id" {
  description = "MongoDB Atlas organization ID"
  type        = string
}

variable "atlas_project_id" {
  description = "MongoDB Atlas project ID (optional - leave empty to create new)"
  type        = string
  default     = ""
}

# === OPTIONAL OVERRIDES (Can be set in CI/CD) ===

variable "app_image_tag" {
  description = "Docker image tag for the application"
  type        = string
  default     = "latest"
}

variable "atlas_cluster_tier" {
  description = "MongoDB Atlas cluster tier (M0=Free, M2, M5, M10, etc.)"
  type        = string
  default     = "M0"
}

variable "app_replicas" {
  description = "Number of application replicas"
  type        = number
  default     = 2
}

variable "domain_name" {
  description = "Domain name for the application (optional - leave empty for LoadBalancer)"
  type        = string
  default     = ""
}

# === DOCKER HUB CREDENTIALS (Required for private images) ===

variable "docker_hub_username" {
  description = "Docker Hub username for pulling images"
  type        = string
  sensitive   = true
}

variable "docker_hub_password" {
  description = "Docker Hub password or access token for pulling images"
  type        = string
  sensitive   = true
}