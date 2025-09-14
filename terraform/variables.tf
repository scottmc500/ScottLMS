# Variables for ScottLMS AWS Infrastructure

# Core Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "scottlms"
}


variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "scottlms.local"
}

# DocumentDB Configuration (Optional - uses defaults if not specified)
# documentdb_instance_class = "db.t3.medium"
# documentdb_instance_count = 1

# Application Configuration
variable "image_tag" {
  description = "Docker image tag for the application"
  type        = string
  default     = "latest"
}