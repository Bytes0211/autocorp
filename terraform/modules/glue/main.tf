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

# S3 objects for ETL scripts
locals {
  etl_scripts = {
    sales_order          = "${path.module}/scripts/sales_order_etl.py"
    customers            = "${path.module}/scripts/customers_etl.py"
    auto_parts           = "${path.module}/scripts/auto_parts_etl.py"
    service              = "${path.module}/scripts/service_etl.py"
    service_parts        = "${path.module}/scripts/service_parts_etl.py"
    sales_order_parts    = "${path.module}/scripts/sales_order_parts_etl.py"
    sales_order_services = "${path.module}/scripts/sales_order_services_etl.py"
  }
  
  # Analytics ETL scripts (denormalized tables)
  analytics_scripts = {
    sales_order_fact      = "${path.module}/scripts/analytics_sales_order_fact_etl.py"
    line_items            = "${path.module}/scripts/analytics_sales_order_line_items_etl.py"
    service_parts_catalog = "${path.module}/scripts/analytics_service_parts_catalog_etl.py"
  }
}

resource "aws_s3_object" "etl_scripts" {
  for_each = var.enable_etl_jobs ? local.etl_scripts : {}

  bucket = var.data_lake_bucket_id
  key    = "scripts/glue/${each.key}_etl.py"
  source = each.value
  etag   = filemd5(each.value)
}

resource "aws_s3_object" "analytics_etl_scripts" {
  for_each = var.enable_etl_jobs ? local.analytics_scripts : {}

  bucket = var.data_lake_bucket_id
  key    = "scripts/glue/analytics_${each.key}_etl.py"
  source = each.value
  etag   = filemd5(each.value)
}

# Analytics Glue Catalog Database
resource "aws_glue_catalog_database" "analytics" {
  name        = "${var.project_name}_${var.environment}_analytics"
  description = "AutoCorp analytics data lake catalog with denormalized tables"
}

# Glue ETL Jobs with Hudi Connector
resource "aws_glue_job" "sales_order" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-sales-order-etl-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/sales_order_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.etl_scripts]
}

resource "aws_glue_job" "customers" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-customers-etl-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/customers_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.etl_scripts]
}

resource "aws_glue_job" "auto_parts" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-auto-parts-etl-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/auto_parts_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.etl_scripts]
}

resource "aws_glue_job" "service" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-service-etl-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/service_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.etl_scripts]
}

resource "aws_glue_job" "service_parts" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-service-parts-etl-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/service_parts_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.etl_scripts]
}

resource "aws_glue_job" "sales_order_parts" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-sales-order-parts-etl-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/sales_order_parts_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.etl_scripts]
}

# ============================================================================
# Analytics Layer ETL Jobs (Denormalized Tables)
# ============================================================================

# Analytics Job: Sales Order Fact Table
resource "aws_glue_job" "analytics_sales_order_fact" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-analytics-sales-order-fact-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/analytics_sales_order_fact_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.analytics_etl_scripts]
}

# Analytics Job: Sales Order Line Items Table
resource "aws_glue_job" "analytics_line_items" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-analytics-line-items-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/analytics_line_items_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.analytics_etl_scripts]
}

# Analytics Job: Service Parts Catalog Table
resource "aws_glue_job" "analytics_service_parts_catalog" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-analytics-service-parts-catalog-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/analytics_service_parts_catalog_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.analytics_etl_scripts]
}

# Glue Crawler for analytics zone
resource "aws_glue_crawler" "analytics" {
  count = var.enable_crawlers ? 1 : 0

  name          = "${var.project_name}-analytics-crawler-${var.environment}"
  role          = var.glue_role_arn
  database_name = aws_glue_catalog_database.analytics.name

  s3_target {
    path = "s3://${var.data_lake_bucket_id}/curated/analytics/"
  }

  schedule = var.crawler_schedule

  schema_change_policy {
    delete_behavior = "LOG"
    update_behavior = "UPDATE_IN_DATABASE"
  }
}

resource "aws_glue_job" "sales_order_services" {
  count = var.enable_etl_jobs ? 1 : 0

  name     = "${var.project_name}-sales-order-services-etl-${var.environment}"
  role_arn = var.glue_role_arn

  command {
    name            = "glueetl"
    script_location = "s3://${var.data_lake_bucket_id}/scripts/glue/sales_order_services_etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"                     = "python"
    "--job-bookmark-option"              = "job-bookmark-enable"
    "--enable-metrics"                   = "true"
    "--enable-continuous-cloudwatch-log" = "true"
    "--enable-spark-ui"                  = "true"
    "--spark-event-logs-path"            = "s3://${var.data_lake_bucket_id}/logs/glue/spark/"
    "--DATA_LAKE_BUCKET"                 = var.data_lake_bucket_id
    "--datalake-formats"                 = "hudi"
    "--conf"                             = "spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.hive.convertMetastoreParquet=false"
  }

  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 60

  depends_on = [aws_s3_object.etl_scripts]
}
