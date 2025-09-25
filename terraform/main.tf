# ScottLMS Terraform Main Configuration
# Provider configurations and module calls

# Configure Terraform version and backend
terraform {
  backend "remote" {
    hostname     = "app.terraform.io"
    organization = "scottmc500"
    workspaces {
      name = "scottlms-production"
    }
  }

  required_providers {
    # Kubernetes provider removed - using Helm for K8s deployments

    # MongoDB Atlas provider for database resources
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.0"
    }

    # Linode provider for importing existing infrastructure
    linode = {
      source  = "linode/linode"
      version = "~> 2.0"
    }

    # Kubernetes provider for managing K8s resources
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.20"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Local values for computed resources that are used in multiple places
locals {
  # === KUBECONFIG PARSING ===
  kubeconfig       = yamldecode(base64decode(linode_lke_cluster.scottlms_cluster.kubeconfig))
  kube_server      = local.kubeconfig.clusters[0].cluster.server
  kube_token       = local.kubeconfig.users[0].user.token
  kube_certificate = local.kubeconfig.clusters[0].cluster.certificate-authority-data

  # === MONGODB CONFIGURATION ===
  mongodb_hostname = replace(mongodbatlas_cluster.main.connection_strings[0].standard_srv, "mongodb+srv://", "")
  mongodb_url      = "mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${local.mongodb_hostname}/scottlms"

  # Debug: Let's see what we're actually generating
  mongodb_debug = {
    original_connection_string = mongodbatlas_cluster.main.connection_strings[0].standard_srv
    extracted_hostname         = local.mongodb_hostname
    final_url                  = local.mongodb_url
  }
}

# Configure Kubernetes Provider
provider "kubernetes" {
  host                   = local.kube_server
  token                  = local.kube_token
  cluster_ca_certificate = base64decode(local.kube_certificate)
}

# Configure MongoDB Atlas Provider
provider "mongodbatlas" {
  public_key  = var.atlas_public_key
  private_key = var.atlas_private_key
}

# Configure Linode Provider
provider "linode" {
  token = var.linode_token
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

resource "linode_lke_cluster" "scottlms_cluster" {
  label       = "scottlms-cluster"
  k8s_version = "1.33"
  region      = "us-east"
  tags        = ["scottlms"]

  pool {
    type  = "g6-standard-1"
    count = 3
  }
}

resource "mongodbatlas_cluster" "main" {
  project_id = var.atlas_project_id
  name       = "scottlms-cluster"

  # Provider settings - Free tier configuration
  provider_name               = "TENANT"
  backing_provider_name       = "AWS"
  provider_instance_size_name = "M0"
  provider_region_name        = "US_EAST_1"
}

# MongoDB Atlas Database User
resource "mongodbatlas_database_user" "scottlms_user" {
  username           = random_string.mongodb_username.result
  password           = random_password.mongodb_user_password.result
  project_id         = var.atlas_project_id
  auth_database_name = "admin"

  roles {
    role_name     = "readWrite"
    database_name = "scottlms"
  }

  scopes {
    name = mongodbatlas_cluster.main.name
    type = "CLUSTER"
  }
}

# IP Access List for MongoDB Atlas
resource "mongodbatlas_project_ip_access_list" "allow_all" {
  project_id = var.atlas_project_id
  cidr_block = "0.0.0.0/0"
  comment    = "Allow access from anywhere (restrict this in production)"
}