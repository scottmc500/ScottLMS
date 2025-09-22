# ScottLMS MongoDB Atlas Resources
# MongoDB Atlas cluster and database configuration

# MongoDB Atlas Project (if not provided)
resource "mongodbatlas_project" "scottlms" {
  count = var.atlas_project_id == "" ? 1 : 0
  
  name   = "${local.name_prefix}-project"
  org_id = var.atlas_org_id
}

# MongoDB Atlas Cluster
resource "mongodbatlas_cluster" "main" {
  project_id   = var.atlas_project_id != "" ? var.atlas_project_id : mongodbatlas_project.scottlms[0].id
  name         = local.mongodb_config.cluster_name
  
  # Cluster configuration
  cluster_type = "REPLICASET"
  cloud_backup = true
  
  # Provider settings
  provider_name         = local.mongodb_config.provider_name
  provider_instance_size_name = var.atlas_cluster_tier
  provider_region_name  = local.mongodb_config.provider_region_name
  
  # Auto-scaling
  auto_scaling_disk_gb_enabled = true
}

# MongoDB Atlas Database User
resource "mongodbatlas_database_user" "scottlms_user" {
  username           = random_string.mongodb_username.result
  password           = random_password.mongodb_user_password.result
  project_id         = var.atlas_project_id != "" ? var.atlas_project_id : mongodbatlas_project.scottlms[0].id
  auth_database_name = "admin"
  
  roles {
    role_name     = "readWrite"
    database_name = local.mongodb_config.database_name
  }
  
  scopes {
    name = mongodbatlas_cluster.main.name
    type = "CLUSTER"
  }
}

# IP Access List for MongoDB Atlas
resource "mongodbatlas_project_ip_access_list" "allow_all" {
  project_id = var.atlas_project_id != "" ? var.atlas_project_id : mongodbatlas_project.scottlms[0].id
  cidr_block = "0.0.0.0/0"
  comment    = "Allow access from anywhere (restrict this in production)"
}
