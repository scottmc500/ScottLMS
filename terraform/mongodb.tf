# MongoDB Atlas Provider Configuration
terraform {
  required_providers {
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.0"
    }
  }
}

provider "mongodbatlas" {
  public_key  = var.mongodb_atlas_public_key
  private_key = var.mongodb_atlas_private_key
}

# MongoDB Atlas Project
resource "mongodbatlas_project" "scottlms" {
  name   = "ScottLMS"
  org_id = var.mongodb_atlas_project_id

  tags = [
    {
      key   = "Environment"
      value = var.environment
    },
    {
      key   = "Project"
      value = var.project_name
    }
  ]
}

# MongoDB Atlas Cluster
resource "mongodbatlas_cluster" "scottlms" {
  project_id   = mongodbatlas_project.scottlms.id
  name         = "scottlms-cluster"
  cluster_type = "REPLICASET"

  # Provider settings
  provider_name         = "AWS"
  provider_region_name  = "US_WEST_2"
  provider_instance_size_name = "M10"

  # Backup settings
  backup_enabled = true
  pit_enabled    = true

  # Security settings
  mongo_db_major_version = "7.0"

  tags = [
    {
      key   = "Environment"
      value = var.environment
    },
    {
      key   = "Project"
      value = var.project_name
    }
  ]
}

# MongoDB Atlas Database User
resource "mongodbatlas_database_user" "scottlms" {
  username           = "scottlms-user"
  password           = random_password.mongodb_password.result
  project_id         = mongodbatlas_project.scottlms.id
  auth_database_name = "admin"

  roles {
    role_name     = "readWrite"
    database_name = "scottlms"
  }

  labels = [
    {
      key   = "Environment"
      value = var.environment
    },
    {
      key   = "Project"
      value = var.project_name
    }
  ]
}

# MongoDB Atlas Network Access List
resource "mongodbatlas_network_access_list" "scottlms" {
  project_id = mongodbatlas_project.scottlms.id
  cidr_block = "0.0.0.0/0"
  comment    = "Allow access from anywhere for development"
}

# Random password for MongoDB user
resource "random_password" "mongodb_password" {
  length  = 16
  special = true
}

# Store MongoDB connection string in AWS Secrets Manager
resource "aws_secretsmanager_secret" "mongodb_connection" {
  name        = "${local.name}-mongodb-connection"
  description = "MongoDB Atlas connection string for ScottLMS"

  tags = local.common_tags
}

resource "aws_secretsmanager_secret_version" "mongodb_connection" {
  secret_id = aws_secretsmanager_secret.mongodb_connection.id
  secret_string = jsonencode({
    connection_string = mongodbatlas_cluster.scottlms.connection_strings[0].standard_srv
    username         = mongodbatlas_database_user.scottlms.username
    password         = random_password.mongodb_password.result
    database         = "scottlms"
  })
}
