# ScottLMS Terraform Main Configuration
# Provider configurations and module calls

# Configure Terraform version and backend
terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "scottmc500"
    workspaces {
      name = "scottlms-production"
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
  # Disable TLS verification for Terraform Cloud (Linode clusters use self-signed certs)
  insecure = true
}

# Configure MongoDB Atlas Provider
provider "mongodbatlas" {
  public_key  = var.atlas_public_key
  private_key = var.atlas_private_key
}

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

# Local values for computed resources that are used in multiple places
locals {
  # Complete MongoDB connection URL
  mongodb_url = "mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${mongodbatlas_cluster.main.connection_strings[0].standard_srv}"
}