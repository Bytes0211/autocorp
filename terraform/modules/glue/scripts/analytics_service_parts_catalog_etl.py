"""
Glue ETL Job: Analytics Service Parts Catalog Table
Creates denormalized service-to-parts reference table for inventory planning
and cost analysis.

Reads from:
  - curated/hudi/service/
  - curated/hudi/service_parts/
  - curated/hudi/auto_parts/

Writes to:
  - curated/analytics/service_parts_catalog/
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
analytics_path = f"s3://{data_lake_bucket}/curated/analytics/service_parts_catalog/"

print(f"Reading from curated zone: {curated_path}")
print(f"Writing to analytics zone: {analytics_path}")

# Read from Hudi curated tables
print("Reading source tables...")
df_service = spark.read.format("hudi").load(f"{curated_path}/service/")
df_service_parts = spark.read.format("hudi").load(f"{curated_path}/service_parts/")
df_auto_parts = spark.read.format("hudi").load(f"{curated_path}/auto_parts/")

print(f"Source records - Services: {df_service.count()}, Service-Parts: {df_service_parts.count()}")

# Create denormalized service parts catalog
df_catalog = df_service.alias("s") \
    .join(df_service_parts.alias("sp"), "serviceid", "inner") \
    .join(df_auto_parts.alias("ap"), col("sp.sku") == col("ap.sku"), "inner") \
    .select(
        # Service information
        col("s.serviceid"),
        col("s.service"),
        col("s.category"),
        col("s.labor_minutes"),
        col("s.labor_cost"),
        
        # Parts information
        col("sp.sku"),
        col("ap.name").alias("part_name"),
        col("ap.description").alias("part_description"),
        col("sp.quantity").alias("parts_quantity_required"),
        col("ap.price").alias("part_unit_price"),
        
        # Calculated costs
        (col("sp.quantity") * col("ap.price")).alias("total_parts_cost"),
        col("ap.vendor"),
        
        # Metadata
        current_timestamp().alias("etl_timestamp")
    )

print(f"Service parts catalog records: {df_catalog.count()}")

# Hudi configuration for analytics table (no partitioning for reference table)
hudi_options = {
    'hoodie.table.name': 'service_parts_catalog',
    'hoodie.datasource.write.recordkey.field': 'serviceid,sku',
    'hoodie.datasource.write.table.name': 'service_parts_catalog',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'etl_timestamp',
    'hoodie.datasource.hive_sync.enable': 'true',
    'hoodie.datasource.hive_sync.database': 'autocorp_dev_analytics',
    'hoodie.datasource.hive_sync.table': 'service_parts_catalog',
    'hoodie.datasource.hive_sync.use_jdbc': 'false',
    'hoodie.datasource.hive_sync.mode': 'hms',
    'hoodie.upsert.shuffle.parallelism': 10,
    'hoodie.insert.shuffle.parallelism': 10
}

# Write to Hudi in analytics zone
print("Writing service parts catalog to Hudi...")
df_catalog.write \
    .format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save(analytics_path)

print(f"Successfully wrote {df_catalog.count()} records to service_parts_catalog analytics table")

# Validation metrics
print("\n=== Validation Metrics ===")
print(f"Total unique services: {df_catalog.select('serviceid').distinct().count()}")
print(f"Total unique parts: {df_catalog.select('sku').distinct().count()}")
print(f"Average parts per service: {df_catalog.groupBy('serviceid').count().agg(avg('count')).collect()[0][0]:.2f}")

# Show top services by parts cost
print("\nTop 10 services by total parts cost:")
df_catalog.groupBy("serviceid", "service", "category") \
    .agg(sum("total_parts_cost").alias("total_cost")) \
    .orderBy(desc("total_cost")) \
    .limit(10) \
    .show(truncate=False)

job.commit()
