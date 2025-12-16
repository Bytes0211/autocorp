# DMS Module - Database Migration Service
# Creates DMS replication infrastructure for PostgreSQL CDC

# Create VPC for DMS (simplified for dev environment)
resource "aws_vpc" "dms" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-dms-vpc-${var.environment}"
  }
}

# Internet Gateway for public access
resource "aws_internet_gateway" "dms" {
  vpc_id = aws_vpc.dms.id

  tags = {
    Name = "${var.project_name}-dms-igw-${var.environment}"
  }
}

# Public Subnets in 2 AZs (required for DMS)
resource "aws_subnet" "dms_public_a" {
  vpc_id                  = aws_vpc.dms.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-dms-subnet-a-${var.environment}"
  }
}

resource "aws_subnet" "dms_public_b" {
  vpc_id                  = aws_vpc.dms.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = data.aws_availability_zones.available.names[1]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-dms-subnet-b-${var.environment}"
  }
}

# Route Table
resource "aws_route_table" "dms_public" {
  vpc_id = aws_vpc.dms.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.dms.id
  }

  tags = {
    Name = "${var.project_name}-dms-rt-${var.environment}"
  }
}

# Route Table Associations
resource "aws_route_table_association" "dms_a" {
  subnet_id      = aws_subnet.dms_public_a.id
  route_table_id = aws_route_table.dms_public.id
}

resource "aws_route_table_association" "dms_b" {
  subnet_id      = aws_subnet.dms_public_b.id
  route_table_id = aws_route_table.dms_public.id
}

# Security Group for DMS
resource "aws_security_group" "dms" {
  name        = "${var.project_name}-dms-sg-${var.environment}"
  description = "Security group for DMS replication instance"
  vpc_id      = aws_vpc.dms.id

  # Outbound PostgreSQL connection
  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "PostgreSQL outbound"
  }

  # HTTPS for AWS services
  egress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS outbound"
  }

  tags = {
    Name = "${var.project_name}-dms-sg-${var.environment}"
  }
}

# Data source for availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

# DMS Replication Subnet Group
resource "aws_dms_replication_subnet_group" "main" {
  replication_subnet_group_id          = "${var.project_name}-dms-subnet-group-${var.environment}"
  replication_subnet_group_description = "DMS replication subnet group for ${var.project_name}"
  subnet_ids                           = [
    aws_subnet.dms_public_a.id,
    aws_subnet.dms_public_b.id
  ]

  tags = {
    Name = "${var.project_name}-dms-subnet-group-${var.environment}"
  }
}

# DMS Replication Instance
resource "aws_dms_replication_instance" "main" {
  replication_instance_id      = "${var.project_name}-dms-instance-${var.environment}"
  replication_instance_class   = var.replication_instance_class
  allocated_storage            = var.allocated_storage
  engine_version               = "3.5.2"
  multi_az                     = false  # Single AZ for dev
  publicly_accessible          = true   # Required to reach on-prem PostgreSQL
  replication_subnet_group_id  = aws_dms_replication_subnet_group.main.id
  vpc_security_group_ids       = [aws_security_group.dms.id]

  tags = {
    Name = "${var.project_name}-dms-instance-${var.environment}"
  }
}

# Source Endpoint - PostgreSQL
resource "aws_dms_endpoint" "postgres_source" {
  endpoint_id   = "${var.project_name}-postgres-source-${var.environment}"
  endpoint_type = "source"
  engine_name   = "postgres"

  server_name = var.postgres_host
  port        = var.postgres_port
  database_name = var.postgres_database
  username    = var.postgres_username
  password    = var.postgres_password
  ssl_mode    = "none"  # Adjust if SSL is required

  tags = {
    Name = "${var.project_name}-postgres-source-${var.environment}"
  }
}

# Target Endpoint - S3
resource "aws_dms_endpoint" "s3_target" {
  endpoint_id   = "${var.project_name}-s3-target-${var.environment}"
  endpoint_type = "target"
  engine_name   = "s3"

  s3_settings {
    bucket_name             = split(":::", var.target_bucket_arn)[1]
    bucket_folder           = "raw/database"
    compression_type        = "GZIP"
    data_format             = "parquet"
    service_access_role_arn = var.dms_role_arn
    timestamp_column_name   = "dms_timestamp"
    parquet_timestamp_in_millisecond = true
  }

  tags = {
    Name = "${var.project_name}-s3-target-${var.environment}"
  }
}

# Replication Task - Full Load
resource "aws_dms_replication_task" "full_load" {
  replication_task_id      = "${var.project_name}-full-load-${var.environment}"
  migration_type           = "full-load"
  replication_instance_arn = aws_dms_replication_instance.main.replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.postgres_source.endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.s3_target.endpoint_arn
  table_mappings           = file("${path.module}/table_mappings.json")

  replication_task_settings = jsonencode({
    TargetMetadata = {
      TargetSchema = ""
      SupportLobs = true
      FullLobMode = false
      LobChunkSize = 64
      LimitedSizeLobMode = true
      LobMaxSize = 32
    }
    FullLoadSettings = {
      TargetTablePrepMode = "DO_NOTHING"
      CreatePkAfterFullLoad = false
      StopTaskCachedChangesApplied = false
      StopTaskCachedChangesNotApplied = false
      MaxFullLoadSubTasks = 8
      TransactionConsistencyTimeout = 600
    }
    Logging = {
      EnableLogging = true
      LogComponents = [{
        Id = "TRANSFORMATION"
        Severity = "LOGGER_SEVERITY_DEFAULT"
      },
      {
        Id = "SOURCE_UNLOAD"
        Severity = "LOGGER_SEVERITY_DEFAULT"
      },
      {
        Id = "TARGET_LOAD"
        Severity = "LOGGER_SEVERITY_DEFAULT"
      }]
    }
  })

  tags = {
    Name = "${var.project_name}-full-load-${var.environment}"
  }
}

# Replication Task - CDC
resource "aws_dms_replication_task" "cdc" {
  replication_task_id      = "${var.project_name}-cdc-${var.environment}"
  migration_type           = "cdc"
  replication_instance_arn = aws_dms_replication_instance.main.replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.postgres_source.endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.s3_target.endpoint_arn
  table_mappings           = file("${path.module}/table_mappings.json")
  cdc_start_position       = ""  # Set after full load completes

  replication_task_settings = jsonencode({
    TargetMetadata = {
      TargetSchema = ""
      SupportLobs = true
      FullLobMode = false
      LobChunkSize = 64
      LimitedSizeLobMode = true
      LobMaxSize = 32
    }
    ChangeProcessingDdlHandlingPolicy = {
      HandleSourceTableDropped = true
      HandleSourceTableTruncated = true
    }
    ChangeProcessingTuning = {
      BatchApplyPreserveTransaction = true
      BatchApplyTimeoutMin = 1
      BatchApplyTimeoutMax = 30
      BatchApplyMemoryLimit = 500
      BatchSplitSize = 0
      MinTransactionSize = 1000
      CommitTimeout = 1
      MemoryLimitTotal = 1024
      MemoryKeepTime = 60
      StatementCacheSize = 50
    }
    Logging = {
      EnableLogging = true
      LogComponents = [{
        Id = "SOURCE_CAPTURE"
        Severity = "LOGGER_SEVERITY_DEFAULT"
      },
      {
        Id = "TARGET_APPLY"
        Severity = "LOGGER_SEVERITY_DEFAULT"
      }]
    }
  })

  tags = {
    Name = "${var.project_name}-cdc-${var.environment}"
  }
}
