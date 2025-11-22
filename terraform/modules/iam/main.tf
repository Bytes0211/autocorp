# IAM Module - Service Roles and Policies
# Creates IAM roles for Glue, DMS, and DataSync with least privilege

# Glue Service Role
resource "aws_iam_role" "glue" {
  name = "${var.project_name}-glue-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "glue.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-glue-role-${var.environment}"
  }
}

# Glue Policy - S3 and Catalog access
resource "aws_iam_role_policy" "glue_s3_catalog" {
  name = "glue-s3-catalog-policy"
  role = aws_iam_role.glue.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          "arn:aws:s3:::${var.data_lake_bucket_id}/*",
          "arn:aws:s3:::${var.data_lake_bucket_id}"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "glue:*",
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}

# DMS Service Role
resource "aws_iam_role" "dms" {
  name = "${var.project_name}-dms-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "dms.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-dms-role-${var.environment}"
  }
}

# DMS Policy - S3 write access (raw/ only)
resource "aws_iam_role_policy" "dms_s3" {
  name = "dms-s3-policy"
  role = aws_iam_role.dms.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:PutObjectTagging"
      ]
      Resource = "arn:aws:s3:::${var.data_lake_bucket_id}/raw/database/*"
    },
    {
      Effect = "Allow"
      Action = ["s3:ListBucket"]
      Resource = "arn:aws:s3:::${var.data_lake_bucket_id}"
    }]
  })
}

# DataSync Service Role
resource "aws_iam_role" "datasync" {
  name = "${var.project_name}-datasync-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "datasync.amazonaws.com"
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-datasync-role-${var.environment}"
  }
}

# DataSync Policy - S3 write access (raw/csv/ only)
resource "aws_iam_role_policy" "datasync_s3" {
  name = "datasync-s3-policy"
  role = aws_iam_role.datasync.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetObject",
        "s3:ListBucket",
        "s3:GetBucketLocation"
      ]
      Resource = [
        "arn:aws:s3:::${var.data_lake_bucket_id}/raw/csv/*",
        "arn:aws:s3:::${var.data_lake_bucket_id}"
      ]
    }]
  })
}
