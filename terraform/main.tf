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

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }

    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# Local values for computed resources that are used in multiple places
locals {
  # === KUBERNETES CONFIGURATION ===
  kubernetes_kubeconfig = yamldecode(base64decode(linode_lke_cluster.scottlms_cluster.kubeconfig))
  kubernetes_token      = local.kubernetes_kubeconfig.users[0].user.token
  kubernetes_host       = local.kubernetes_kubeconfig.clusters[0].cluster.server
  kubernetes_ca_cert    = local.kubernetes_kubeconfig.clusters[0].cluster.certificate-authority-data
  kubernetes_addresses   = flatten([for node in data.kubernetes_nodes.scottlms_nodes.nodes : [for status in node.status: status.addresses]])
  kubernetes_ipv4_addresses   = [for address in local.kubernetes_addresses : address.address if address.type == "ExternalIP" && !can(regex("::", address.address))]
  # === MONGODB CONFIGURATION ===
  mongodb_hostname = replace(mongodbatlas_cluster.main.connection_strings[0].standard_srv, "mongodb+srv://", "")
  mongodb_url      = "mongodb+srv://${random_string.mongodb_username.result}:${random_password.mongodb_user_password.result}@${local.mongodb_hostname}/scottlms"
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

# Configure Kubernetes Provider
provider "kubernetes" {
  token       = local.kubernetes_token
  host        = local.kubernetes_host
  cluster_ca_certificate = base64decode(local.kubernetes_ca_cert)
}

data "kubernetes_nodes" "scottlms_nodes" {
  depends_on = [linode_lke_cluster.scottlms_cluster]
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

# IP Access List for MongoDB Atlas - Flexible cluster pod network
# This uses a broader CIDR block to accommodate current and future cluster nodes
resource "mongodbatlas_project_ip_access_list" "cluster_pods" {
  for_each = toset(local.kubernetes_ipv4_addresses)
  project_id = mongodbatlas_cluster.main.project_id
  ip_address = each.value
  comment    = "Kubernetes cluster pod network (flexible for future growth): ${each.value}"
  depends_on = [mongodbatlas_cluster.main]
}