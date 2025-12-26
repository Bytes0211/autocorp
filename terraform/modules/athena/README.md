# Athena Terraform Module

This module creates AWS Athena resources for querying the AutoCorp data lake.

## Resources Created

- **Athena Workgroup**: Isolated environment for running queries with cost controls
- **Named Queries**: Pre-defined SQL queries for common analytics tasks
- **Query Result Configuration**: S3 location and encryption for query outputs

## Named Queries Included

1. **sales_summary** - Daily sales metrics (order count, revenue, avg order value)
2. **top_parts_by_revenue** - Top 20 auto parts by total revenue
3. **customer_order_history** - Customer lifetime value and order patterns
4. **service_performance** - Service catalog performance metrics
5. **hudi_time_travel_example** - Example of point-in-time Hudi queries

## Usage

```hcl
module "athena" {
  source = "./modules/athena"

  project_name         = "autocorp"
  environment          = "dev"
  query_results_bucket = module.s3.datalake_bucket_id
  glue_database_name   = "autocorp_curated"
}
```

## Querying Hudi Tables

Athena Engine Version 3 supports Apache Hudi tables natively. To query Hudi tables:

1. Ensure Glue Crawler has registered the Hudi tables in the Data Catalog
2. Use the Athena workgroup created by this module
3. Query tables normally - Hudi metadata is handled automatically

### Example Queries

**Basic Query:**
```sql
SELECT * FROM sales_order LIMIT 10;
```

**Time-Travel Query (Point-in-Time):**
```sql
SELECT * FROM sales_order
WHERE _hoodie_commit_time <= '20250101000000000';
```

**Incremental Query (Changes Since):**
```sql
SELECT * FROM sales_order
WHERE _hoodie_commit_time > '20241220000000000';
```

## Outputs

- `workgroup_id` - ID of the Athena workgroup
- `workgroup_arn` - ARN of the Athena workgroup
- `workgroup_name` - Name of the Athena workgroup
- `query_results_location` - S3 path for query results
- `named_queries` - Map of named query IDs

## Cost Optimization

- Queries are charged $5 per TB scanned
- Use partitioning to reduce data scanned
- Enable result caching in workgroup settings (24 hours by default)
- Use columnar formats (Parquet) - already implemented via Hudi

## Monitoring

CloudWatch metrics are published for:
- Query execution time
- Data scanned per query
- Query failures
- Concurrent query count

Access metrics in CloudWatch under namespace: `AWS/Athena`
