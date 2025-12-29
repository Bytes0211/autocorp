"""
Glue ETL Job: Analytics Sales Order Fact Table
Creates denormalized order-level analytics table with embedded customer dimensions
and aggregated line item metrics.

Reads from:
  - curated/hudi/sales_order/
  - curated/hudi/customers/
  - curated/hudi/sales_order_parts/
  - curated/hudi/sales_order_services/

Writes to:
  - curated/analytics/sales_order_fact/
"""
import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import *

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
analytics_path = f"s3://{data_lake_bucket}/curated/analytics/sales_order_fact/"

print(f"Reading from curated zone: {curated_path}")
print(f"Writing to analytics zone: {analytics_path}")

# Read from Hudi curated tables
print("Reading sales_order table...")
df_sales_order = spark.read.format("hudi").load(f"{curated_path}/sales_order/")

print("Reading customers table...")
df_customers = spark.read.format("hudi").load(f"{curated_path}/customers/")

print("Reading sales_order_parts table...")
df_parts = spark.read.format("hudi").load(f"{curated_path}/sales_order_parts/")

print("Reading sales_order_services table...")
df_services = spark.read.format("hudi").load(f"{curated_path}/sales_order_services/")

print(f"Source records - Orders: {df_sales_order.count()}, Customers: {df_customers.count()}")
print(f"Source records - Parts: {df_parts.count()}, Services: {df_services.count()}")

# Aggregate parts line items per order
df_parts_agg = df_parts.groupBy("order_id").agg(
    count("line_item_id").alias("parts_line_count"),
    sum("quantity").alias("total_parts_quantity")
)

# Aggregate services line items per order
df_services_agg = df_services.groupBy("order_id").agg(
    count("line_item_id").alias("services_line_count"),
    sum("quantity").alias("total_services_quantity")
)

# Create denormalized fact table
# Join sales_order with customers
df_fact = df_sales_order.alias("so").join(
    df_customers.alias("c"),
    col("so.customer_id") == col("c.customer_id"),
    "inner"
).select(
    # Order identifiers and header info
    col("so.order_id"),
    col("so.invoice_number"),
    col("so.order_date"),
    col("so.order_type"),
    col("so.status"),
    col("so.payment_method"),
    
    # Customer dimensions (denormalized to avoid joins)
    col("c.customer_id"),
    col("c.first_name"),
    col("c.last_name"),
    col("c.email"),
    col("c.phone"),
    col("c.city"),
    col("c.state"),
    col("c.zip_code"),
    
    # Order financials
    col("so.subtotal"),
    col("so.tax"),
    col("so.total_amount")
)

# Left join with parts aggregations
df_fact = df_fact.join(
    df_parts_agg,
    "order_id",
    "left"
)

# Left join with services aggregations
df_fact = df_fact.join(
    df_services_agg,
    "order_id",
    "left"
)

# Fill nulls for orders with no parts or services
df_fact = df_fact \
    .fillna(0, subset=["parts_line_count", "services_line_count"]) \
    .fillna(0, subset=["total_parts_quantity", "total_services_quantity"]) \
    .withColumn("total_line_items", col("parts_line_count") + col("services_line_count")) \
    .withColumn("etl_timestamp", current_timestamp()) \
    .withColumn("year", year(col("order_date"))) \
    .withColumn("month", month(col("order_date")))

print(f"Denormalized fact table records: {df_fact.count()}")

# Hudi configuration for analytics table
hudi_options = {
    'hoodie.table.name': 'sales_order_fact',
    'hoodie.datasource.write.recordkey.field': 'order_id',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.table.name': 'sales_order_fact',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'etl_timestamp',
    'hoodie.datasource.hive_sync.enable': 'false',
    'hoodie.upsert.shuffle.parallelism': 10,
    'hoodie.insert.shuffle.parallelism': 20,
    'hoodie.datasource.write.hive_style_partitioning': 'true'
}

# Write to Hudi in analytics zone
print("Writing denormalized fact table to Hudi...")
df_fact.write \
    .format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save(analytics_path)

print(f"Successfully wrote {df_fact.count()} records to sales_order_fact analytics table")

# Validation metrics
print("\n=== Validation Metrics ===")
print(f"Total revenue: ${df_fact.agg(sum('total_amount')).collect()[0][0]:,.2f}")
print(f"Orders with parts only: {df_fact.filter((col('parts_line_count') > 0) & (col('services_line_count') == 0)).count()}")
print(f"Orders with services only: {df_fact.filter((col('parts_line_count') == 0) & (col('services_line_count') > 0)).count()}")
print(f"Orders with both: {df_fact.filter((col('parts_line_count') > 0) & (col('services_line_count') > 0)).count()}")

job.commit()
