"""
Glue ETL Job: sales_order_services - Service sales line items
Reads from raw/database/sales_order_services/ and writes to curated/hudi/sales_order_services/
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
raw_path = f"s3://{data_lake_bucket}/raw/database/sales_order_services/"
curated_path = f"s3://{data_lake_bucket}/curated/hudi/sales_order_services/"

print(f"Reading from: {raw_path}")
print(f"Writing to: {curated_path}")

# Read from raw zone
df = spark.read.parquet(raw_path)

print(f"Raw records read: {df.count()}")

# Data quality checks and transformations
df_clean = df \
    .dropDuplicates(["line_item_id"]) \
    .filter(col("order_id").isNotNull()) \
    .filter(col("serviceid").isNotNull()) \
    .filter(col("quantity") > 0) \
    .filter(col("line_total") > 0) \
    .withColumn("etl_timestamp", current_timestamp())

print(f"Clean records: {df_clean.count()}")

# Hudi configuration
hudi_options = {
    'hoodie.table.name': 'sales_order_services',
    'hoodie.datasource.write.recordkey.field': 'line_item_id',
    'hoodie.datasource.write.table.name': 'sales_order_services',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'created_at',
    'hoodie.datasource.hive_sync.enable': 'true',
    'hoodie.datasource.hive_sync.database': 'autocorp_dev',
    'hoodie.datasource.hive_sync.table': 'sales_order_services',
    'hoodie.datasource.hive_sync.use_jdbc': 'false',
    'hoodie.datasource.hive_sync.mode': 'hms',
    'hoodie.upsert.shuffle.parallelism': 20,
    'hoodie.insert.shuffle.parallelism': 20
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
