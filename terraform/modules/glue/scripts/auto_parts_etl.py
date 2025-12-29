"""
Glue ETL Job: auto_parts - Reference data with Hudi upserts
Reads from raw/database/auto_parts/ and writes to curated/hudi/auto_parts/
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
raw_path = f"s3://{data_lake_bucket}/raw/database/auto_parts/"
curated_path = f"s3://{data_lake_bucket}/curated/hudi/auto_parts/"

print(f"Reading from: {raw_path}")
print(f"Writing to: {curated_path}")

# Read from raw zone
df = spark.read.parquet(raw_path)

print(f"Raw records read: {df.count()}")

# Data quality checks and transformations
df_clean = df \
    .dropDuplicates(["sku"]) \
    .filter(col("price") > 0) \
    .filter(col("sku").isNotNull()) \
    .withColumn("etl_timestamp", current_timestamp()) \
    .withColumn("vendor_partition", coalesce(col("vendor"), lit("UNKNOWN")))

print(f"Clean records: {df_clean.count()}")

# Hudi configuration for Merge-on-Read (batch updates)
hudi_options = {
    'hoodie.table.name': 'auto_parts',
    'hoodie.datasource.write.recordkey.field': 'sku',
    'hoodie.datasource.write.partitionpath.field': 'vendor_partition',
    'hoodie.datasource.write.table.name': 'auto_parts',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'inventory_date',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    'hoodie.datasource.hive_sync.enable': 'false',
    'hoodie.upsert.shuffle.parallelism': 10,
    'hoodie.insert.shuffle.parallelism': 10,
    'hoodie.datasource.write.hive_style_partitioning': 'true'
}

# Write to Hudi
print("Writing to Hudi table...")
df_clean.write \
    .format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save(curated_path)

print(f"Successfully wrote {df_clean.count()} records to Hudi table")

job.commit()
