# Athena Workgroup for AutoCorp data analytics
resource "aws_athena_workgroup" "autocorp" {
  name        = "${var.project_name}-workgroup-${var.environment}"
  description = "Athena workgroup for ${var.project_name} analytics queries"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${var.query_results_bucket}/athena-results/"

      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }

    engine_version {
      selected_engine_version = "Athena engine version 3"
    }
  }

  tags = {
    Name        = "${var.project_name}-athena-workgroup-${var.environment}"
    Environment = var.environment
    Project     = var.project_name
    ManagedBy   = "Terraform"
  }
}

# Named Query: Sales Summary
resource "aws_athena_named_query" "sales_summary" {
  name        = "sales_summary_${var.environment}"
  workgroup   = aws_athena_workgroup.autocorp.id
  database    = var.glue_database_name
  description = "Summary of sales orders by date"

  query = <<-EOT
    SELECT 
      order_date,
      COUNT(*) as order_count,
      SUM(total_cost) as total_revenue,
      AVG(total_cost) as avg_order_value
    FROM sales_order
    GROUP BY order_date
    ORDER BY order_date DESC
    LIMIT 30;
  EOT
}

# Named Query: Top Parts by Revenue
resource "aws_athena_named_query" "top_parts" {
  name        = "top_parts_by_revenue_${var.environment}"
  workgroup   = aws_athena_workgroup.autocorp.id
  database    = var.glue_database_name
  description = "Top 20 auto parts by revenue"

  query = <<-EOT
    SELECT 
      ap.sku,
      ap.part_name,
      ap.category,
      COUNT(sop.sku) as times_sold,
      SUM(sop.extended_cost) as total_revenue
    FROM sales_order_parts sop
    JOIN auto_parts ap ON sop.sku = ap.sku
    GROUP BY ap.sku, ap.part_name, ap.category
    ORDER BY total_revenue DESC
    LIMIT 20;
  EOT
}

# Named Query: Customer Order History
resource "aws_athena_named_query" "customer_orders" {
  name        = "customer_order_history_${var.environment}"
  workgroup   = aws_athena_workgroup.autocorp.id
  database    = var.glue_database_name
  description = "Customer order history with lifetime value"

  query = <<-EOT
    SELECT 
      c.customerid,
      c.firstname,
      c.lastname,
      c.email,
      COUNT(so.invoice_number) as total_orders,
      SUM(so.total_cost) as lifetime_value,
      AVG(so.total_cost) as avg_order_value,
      MIN(so.order_date) as first_order_date,
      MAX(so.order_date) as last_order_date
    FROM customers c
    JOIN sales_order so ON c.customerid = so.customerid
    GROUP BY c.customerid, c.firstname, c.lastname, c.email
    ORDER BY lifetime_value DESC
    LIMIT 100;
  EOT
}

# Named Query: Service Performance
resource "aws_athena_named_query" "service_performance" {
  name        = "service_performance_${var.environment}"
  workgroup   = aws_athena_workgroup.autocorp.id
  database    = var.glue_database_name
  description = "Service catalog performance metrics"

  query = <<-EOT
    SELECT 
      s.serviceid,
      s.service_name,
      s.category,
      s.labor_cost,
      COUNT(sos.serviceid) as times_performed,
      SUM(sos.extended_cost) as total_revenue,
      AVG(sos.extended_cost) as avg_service_revenue
    FROM service s
    JOIN sales_order_services sos ON s.serviceid = sos.serviceid
    GROUP BY s.serviceid, s.service_name, s.category, s.labor_cost
    ORDER BY total_revenue DESC
    LIMIT 20;
  EOT
}

# Named Query: Hudi Time Travel Example
resource "aws_athena_named_query" "hudi_time_travel" {
  name        = "hudi_time_travel_example_${var.environment}"
  workgroup   = aws_athena_workgroup.autocorp.id
  database    = var.glue_database_name
  description = "Example of Hudi time-travel query (point-in-time snapshot)"

  query = <<-EOT
    -- Query data as of a specific timestamp
    -- Replace timestamp with desired point in time
    SELECT 
      invoice_number,
      customerid,
      order_date,
      total_cost,
      _hoodie_commit_time
    FROM sales_order
    WHERE _hoodie_commit_time <= '20250101000000000'
    ORDER BY order_date DESC
    LIMIT 10;
  EOT
}

# Data Catalog permissions (if needed)
resource "aws_lakeformation_permissions" "athena_access" {
  count = var.enable_lakeformation ? 1 : 0

  principal   = var.athena_execution_role_arn
  permissions = ["SELECT", "DESCRIBE"]

  table {
    database_name = var.glue_database_name
    wildcard      = true
  }
}
