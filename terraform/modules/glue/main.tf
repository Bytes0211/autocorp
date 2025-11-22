# Glue Module - Data Catalog and ETL Jobs
# TODO: Implement Glue crawlers, jobs, and catalog

# Glue Data Catalog Database
resource "aws_glue_catalog_database" "autocorp" {
  name        = "${var.project_name}_${var.environment}"
  description = "AutoCorp data lake catalog"
}

# Glue Crawler for raw/database zone
resource "aws_glue_crawler" "raw_database" {
  count = var.enable_crawlers ? 1 : 0

  name          = "${var.project_name}-raw-database-crawler-${var.environment}"
  role          = var.glue_role_arn
  database_name = aws_glue_catalog_database.autocorp.name

  s3_target {
    path = "s3://${var.data_lake_bucket_id}/raw/database/"
  }

  schedule = var.crawler_schedule

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }
}

# Glue Crawler for raw/csv zone
resource "aws_glue_crawler" "raw_csv" {
  count = var.enable_crawlers ? 1 : 0

  name          = "${var.project_name}-raw-csv-crawler-${var.environment}"
  role          = var.glue_role_arn
  database_name = aws_glue_catalog_database.autocorp.name

  s3_target {
    path = "s3://${var.data_lake_bucket_id}/raw/csv/"
  }

  schedule = var.crawler_schedule

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }
}

# TODO: Add Glue ETL jobs for Hudi transformations
# See terraform/modules/glue/scripts/ for PySpark ETL code
