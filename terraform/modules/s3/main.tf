# S3 Module - Data Lake Storage
# Creates S3 buckets for raw, curated, and logs with lifecycle policies

# Data Lake Bucket
resource "aws_s3_bucket" "data_lake" {
  bucket = "${var.project_name}-datalake-${var.environment}"

  tags = {
    Name        = "${var.project_name}-datalake-${var.environment}"
    Description = "AutoCorp data lake for raw curated and logs"
  }
}

# Enable versioning for data protection
resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = var.enable_versioning ? "Enabled" : "Suspended"
  }
}

# Server-side encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # Use SSE-S3 (can upgrade to SSE-KMS)
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lifecycle policy: raw/ → Glacier after specified days
resource "aws_s3_bucket_lifecycle_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  # Archive raw zone data to Glacier
  rule {
    id     = "archive-raw-zone"
    status = "Enabled"

    filter {
      prefix = "raw/"
    }

    transition {
      days          = var.lifecycle_days
      storage_class = "GLACIER"
    }

    # Expire old data after 1 year in Glacier
    expiration {
      days = var.lifecycle_days + 365
    }
  }

  # Delete logs after 90 days
  rule {
    id     = "expire-logs"
    status = "Enabled"

    filter {
      prefix = "logs/"
    }

    expiration {
      days = 90
    }
  }
}

# Create folder structure via S3 objects (empty files)
resource "aws_s3_object" "folder_structure" {
  for_each = toset([
    "raw/database/.keep",
    "raw/csv/.keep",
    "curated/hudi/.keep",
    "logs/dms/.keep",
    "logs/glue/.keep",
    "logs/datasync/.keep",
  ])

  bucket  = aws_s3_bucket.data_lake.id
  key     = each.value
  content = ""
}
