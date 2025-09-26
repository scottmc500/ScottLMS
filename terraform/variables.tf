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

# === MONGODB ACCESS CIDR BLOCKS ===

variable "api_cidr_block" {
  description = "CIDR block for API LoadBalancer MongoDB access"
  type        = string
  default     = "0.0.0.0/0"
}

variable "frontend_cidr_block" {
  description = "CIDR block for Frontend LoadBalancer MongoDB access"
  type        = string
  default     = "0.0.0.0/0"
}

# === LINODE IMPORT CONFIGURATION ===

variable "linode_token" {
  description = "Linode API token for importing existing infrastructure"
  type        = string
  sensitive   = true
}

variable "linode_cluster_id" {
  description = "ID of the existing Linode LKE cluster to import"
  type        = string
}
