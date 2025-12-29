"""
Glue ETL Job: Analytics Sales Order Line Items Table
Creates unified line-item fact table combining parts and services with full
order and customer context for granular analytics.

Reads from:
  - curated/hudi/sales_order/
  - curated/hudi/customers/
  - curated/hudi/sales_order_parts/
  - curated/hudi/sales_order_services/
  - curated/hudi/auto_parts/
  - curated/hudi/service/

Writes to:
  - curated/analytics/sales_order_line_items/
"""
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Get job parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'DATA_LAKE_BUCKET'])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Configuration
data_lake_bucket = args['DATA_LAKE_BUCKET']
curated_path = f"s3://{data_lake_bucket}/curated/hudi"
analytics_path = f"s3://{data_lake_bucket}/curated/analytics/sales_order_line_items/"

print(f"Reading from curated zone: {curated_path}")
print(f"Writing to analytics zone: {analytics_path}")

# Read from Hudi curated tables
print("Reading source tables...")
df_sales_order = spark.read.format("hudi").load(f"{curated_path}/sales_order/")
df_customers = spark.read.format("hudi").load(f"{curated_path}/customers/")
df_parts_lines = spark.read.format("hudi").load(f"{curated_path}/sales_order_parts/")
df_services_lines = spark.read.format("hudi").load(f"{curated_path}/sales_order_services/")
df_auto_parts = spark.read.format("hudi").load(f"{curated_path}/auto_parts/")
df_service = spark.read.format("hudi").load(f"{curated_path}/service/")

print(f"Source records - Parts lines: {df_parts_lines.count()}, Services lines: {df_services_lines.count()}")

# Build parts line items with full context
df_parts_denorm = df_parts_lines.alias("sop") \
    .join(df_sales_order.alias("so"), "order_id", "inner") \
    .join(df_customers.alias("c"), col("so.customer_id") == col("c.customer_id"), "inner") \
    .join(df_auto_parts.alias("ap"), col("sop.sku") == col("ap.sku"), "inner") \
    .select(
        lit("PART").alias("line_item_type"),
        col("sop.line_item_id"),
        col("sop.order_id"),
        col("so.invoice_number"),
        col("so.order_date"),
        col("so.status").alias("order_status"),
        
        # Customer dimensions
        col("c.customer_id"),
        concat(col("c.first_name"), lit(" "), col("c.last_name")).alias("customer_name"),
        col("c.email").alias("customer_email"),
        col("c.city"),
        col("c.state"),
        
        # Line item details
        col("sop.sku").alias("item_code"),
        col("ap.name").alias("item_name"),
        col("ap.description").alias("item_description"),
        col("sop.quantity"),
        col("sop.unit_price"),
        col("sop.line_total"),
        
        # Parts-specific fields
        col("ap.vendor"),
        lit(None).cast(IntegerType()).alias("labor_minutes"),
        lit(None).cast(DecimalType(10,2)).alias("labor_cost"),
        lit(None).cast(DecimalType(10,2)).alias("parts_cost")
    )

# Build services line items with full context
df_services_denorm = df_services_lines.alias("sos") \
    .join(df_sales_order.alias("so"), "order_id", "inner") \
    .join(df_customers.alias("c"), col("so.customer_id") == col("c.customer_id"), "inner") \
    .join(df_service.alias("s"), col("sos.serviceid") == col("s.serviceid"), "inner") \
    .select(
        lit("SERVICE").alias("line_item_type"),
        col("sos.line_item_id"),
        col("sos.order_id"),
        col("so.invoice_number"),
        col("so.order_date"),
        col("so.status").alias("order_status"),
        
        # Customer dimensions
        col("c.customer_id"),
        concat(col("c.first_name"), lit(" "), col("c.last_name")).alias("customer_name"),
        col("c.email").alias("customer_email"),
        col("c.city"),
        col("c.state"),
        
        # Line item details
        col("sos.serviceid").alias("item_code"),
        col("s.service").alias("item_name"),
        col("s.category").alias("item_description"),
        col("sos.quantity"),
        (col("sos.line_total") / when(col("sos.quantity") == 0, 1).otherwise(col("sos.quantity"))).cast(DecimalType(10,2)).alias("unit_price"),
        col("sos.line_total"),
        
        # Service-specific fields
        lit(None).cast(StringType()).alias("vendor"),
        col("sos.labor_minutes"),
        col("sos.labor_cost"),
        col("sos.parts_cost")
    )

# Union parts and services into single line items table
df_line_items = df_parts_denorm.unionAll(df_services_denorm) \
    .withColumn("etl_timestamp", current_timestamp()) \
    .withColumn("year", year(col("order_date"))) \
    .withColumn("month", month(col("order_date")))

print(f"Unified line items records: {df_line_items.count()}")

# Hudi configuration for analytics table
hudi_options = {
    'hoodie.table.name': 'sales_order_line_items',
    'hoodie.datasource.write.recordkey.field': 'line_item_id',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.table.name': 'sales_order_line_items',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'etl_timestamp',
    'hoodie.datasource.hive_sync.enable': 'false',
    'hoodie.upsert.shuffle.parallelism': 10,
    'hoodie.insert.shuffle.parallelism': 20,
    'hoodie.datasource.write.hive_style_partitioning': 'true'
}

# Write to Hudi in analytics zone
print("Writing unified line items table to Hudi...")
df_line_items.write \
    .format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save(analytics_path)

print(f"Successfully wrote {df_line_items.count()} records to sales_order_line_items analytics table")

# Validation metrics
print("\n=== Validation Metrics ===")
df_line_items.groupBy("line_item_type").agg(
    count("*").alias("row_count"),
    sum("line_total").alias("total_revenue")
).show()

job.commit()
