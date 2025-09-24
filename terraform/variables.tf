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

# === APPLICATION CONFIGURATION ===

variable "app_image_tag" {
  description = "Docker image tag for the application"
  type        = string
  default     = "latest"
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

# === LINODE IMPORT CONFIGURATION ===

variable "linode_token" {
  description = "Linode API token for importing existing infrastructure"
  type        = string
  sensitive   = true
}

variable "linode_cluster_id" {
  description = "ID of the existing Linode LKE cluster to import"
  type        = number
}
