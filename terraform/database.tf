# DocumentDB Subnet Group
resource "aws_docdb_subnet_group" "scottlms" {
  name       = "${local.name}-docdb-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = merge(local.common_tags, {
    Name = "${local.name}-docdb-subnet-group"
  })
}

# DocumentDB Parameter Group
resource "aws_docdb_cluster_parameter_group" "scottlms" {
  family      = "docdb5.0"
  name        = "${local.name}-docdb-params"
  description = "DocumentDB parameter group for ScottLMS"

  parameter {
    name  = "tls"
    value = "disabled"
  }

  tags = local.common_tags
}

# DocumentDB Cluster
resource "aws_docdb_cluster" "scottlms" {
  cluster_identifier      = local.name
  engine                  = "docdb"
  master_username         = "scottlms_admin"
  master_password         = random_password.documentdb_password.result
  backup_retention_period = 7
  preferred_backup_window = "07:00-09:00"
  skip_final_snapshot     = true
  deletion_protection     = false

  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.scottlms.name
  db_subnet_group_name           = aws_docdb_subnet_group.scottlms.name
  vpc_security_group_ids         = [aws_security_group.documentdb.id]

  enabled_cloudwatch_logs_exports = ["audit", "profiler"]

  tags = local.common_tags
}

# DocumentDB Instance
resource "aws_docdb_cluster_instance" "scottlms" {
  count              = 1
  identifier         = "${local.name}-docdb-${count.index + 1}"
  cluster_identifier = aws_docdb_cluster.scottlms.id
  instance_class     = "db.t3.medium"
  engine             = "docdb"

  tags = local.common_tags
}

# DocumentDB Security Group
resource "aws_security_group" "documentdb" {
  name_prefix = "${local.name}-documentdb-"
  vpc_id      = module.vpc.vpc_id

  ingress {
    description     = "DocumentDB from ECS"
    from_port       = 27017
    to_port         = 27017
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "${local.name}-documentdb-sg"
  })
}

# Random password for DocumentDB
resource "random_password" "documentdb_password" {
  length  = 16
  special = true
}