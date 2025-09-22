# ScottLMS Terraform Main Configuration
# Provider configurations and module calls

# Configure Terraform version and backend
terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "scottmc500"  # Replace with your Terraform Cloud organization name
    
    workspaces {
      name = "scottlms-production"  # Replace with your desired workspace name
    }
  }
  
  required_providers {
    # Kubernetes provider for managing K8s resources
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }
    
    # MongoDB Atlas provider for database resources
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.0"
    }
    
    # Random provider for generating random values
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Configure Kubernetes Provider
provider "kubernetes" {
  # For Terraform Cloud, we'll use environment variables or host configuration
  # The kubeconfig will be provided via environment variables in Terraform Cloud
  # or configured directly in the workspace settings
}

# Configure MongoDB Atlas Provider
provider "mongodbatlas" {
  public_key  = var.atlas_public_key
  private_key = var.atlas_private_key
}

# Local values for computed resources
locals {
  # Project configuration
  project_name = "scottlms"
  environment  = "production"
  region       = "us-east"
  
  # Common tags for all resources
  common_tags = {
    Project     = local.project_name
    Environment = local.environment
    ManagedBy   = "terraform"
    CreatedBy   = "scottlms"
  }
  
  # Naming convention
  name_prefix = "${local.project_name}-${local.environment}"
  
  # MongoDB Atlas configuration with defaults
  mongodb_config = {
    cluster_name           = "${local.project_name}-cluster"
    provider_name          = "AWS"
    provider_region_name   = "US_WEST_2"
    database_name          = local.project_name
  }
  
  # Kubernetes configuration with defaults
  k8s_config = {
    namespace = local.project_name
  }
  
  # Application configuration with defaults
  app_config = {
    cpu_request    = "100m"
    memory_request = "256Mi"
    cpu_limit      = "500m"
    memory_limit   = "512Mi"
    log_level      = "info"
  }
  
  # Security and monitoring defaults
  security_config = {
    enable_rbac             = true
    enable_network_policies = true
    enable_monitoring       = true
    enable_backups          = true
    backup_retention_days   = 7
    ssl_enabled            = true
  }
}
