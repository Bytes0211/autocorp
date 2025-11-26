"""
Glue ETL Job: customers - Master data with Hudi upserts
Reads from raw/database/customers/ and writes to curated/hudi/customers/
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
raw_path = f"s3://{data_lake_bucket}/raw/database/customers/"
curated_path = f"s3://{data_lake_bucket}/curated/hudi/customers/"

print(f"Reading from: {raw_path}")
print(f"Writing to: {curated_path}")

# Read from raw zone
df = spark.read.parquet(raw_path)

print(f"Raw records read: {df.count()}")

# Data quality checks and transformations
df_clean = df \
    .dropDuplicates(["customer_id"]) \
    .filter(col("email").isNotNull()) \
    .filter(col("first_name").isNotNull()) \
    .filter(col("last_name").isNotNull()) \
    .withColumn("etl_timestamp", current_timestamp()) \
    .withColumn("state_partition", coalesce(col("state"), lit("UNKNOWN")))

print(f"Clean records: {df_clean.count()}")

# Hudi configuration for Merge-on-Read (dimension data)
hudi_options = {
    'hoodie.table.name': 'customers',
    'hoodie.datasource.write.recordkey.field': 'customer_id',
    'hoodie.datasource.write.partitionpath.field': 'state_partition',
    'hoodie.datasource.write.table.name': 'customers',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'created_at',
    'hoodie.datasource.write.table.type': 'MERGE_ON_READ',
    'hoodie.datasource.hive_sync.enable': 'true',
    'hoodie.datasource.hive_sync.database': 'autocorp_dev',
    'hoodie.datasource.hive_sync.table': 'customers',
    'hoodie.datasource.hive_sync.partition_fields': 'state_partition',
    'hoodie.datasource.hive_sync.partition_extractor_class': 'org.apache.hudi.hive.SlashEncodedDayPartitionValueExtractor',
    'hoodie.datasource.hive_sync.use_jdbc': 'false',
    'hoodie.datasource.hive_sync.mode': 'hms',
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
