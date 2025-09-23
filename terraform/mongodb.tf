# ScottLMS MongoDB Atlas Resources
# MongoDB Atlas cluster and database configuration

resource "mongodbatlas_cluster" "main" {
  project_id   = var.atlas_project_id
  name         = "scottlms-cluster"
  
  # Provider settings - Free tier configuration
  provider_name         = "TENANT"
  backing_provider_name = "AWS"
  provider_instance_size_name = "M0"
  provider_region_name  = "US_EAST_1"
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
