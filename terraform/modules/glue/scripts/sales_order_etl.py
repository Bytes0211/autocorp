"""
Glue ETL Job: sales_order - Transactional data with Hudi upserts
Reads from raw/database/sales_order/ and writes to curated/hudi/sales_order/
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
raw_path = f"s3://{data_lake_bucket}/raw/database/sales_order/"
curated_path = f"s3://{data_lake_bucket}/curated/hudi/sales_order/"

print(f"Reading from: {raw_path}")
print(f"Writing to: {curated_path}")

# Read from raw zone (Parquet from DMS)
df = spark.read.parquet(raw_path)

print(f"Raw records read: {df.count()}")

# Data quality checks and transformations
df_clean = df \
    .dropDuplicates(["order_id"]) \
    .filter(col("total_amount") > 0) \
    .filter(col("order_date").isNotNull()) \
    .withColumn("etl_timestamp", current_timestamp()) \
    .withColumn("year", year(col("order_date"))) \
    .withColumn("month", month(col("order_date")))

print(f"Clean records: {df_clean.count()}")

# Hudi configuration for Copy-on-Write (transactional data)
hudi_options = {
    'hoodie.table.name': 'sales_order',
    'hoodie.datasource.write.recordkey.field': 'order_id',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.table.name': 'sales_order',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'updated_at',
    'hoodie.datasource.hive_sync.enable': 'true',
    'hoodie.datasource.hive_sync.database': 'autocorp_dev',
    'hoodie.datasource.hive_sync.table': 'sales_order',
    'hoodie.datasource.hive_sync.partition_fields': 'year,month',
    'hoodie.datasource.hive_sync.partition_extractor_class': 'org.apache.hudi.hive.MultiPartKeysValueExtractor',
    'hoodie.datasource.hive_sync.use_jdbc': 'false',
    'hoodie.datasource.hive_sync.mode': 'hms',
    'hoodie.upsert.shuffle.parallelism': 20,
    'hoodie.insert.shuffle.parallelism': 20,
    'hoodie.datasource.write.hive_style_partitioning': 'true'
}

# Write to Hudi in curated zone
print("Writing to Hudi table...")
df_clean.write \
    .format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save(curated_path)

print(f"Successfully wrote {df_clean.count()} records to Hudi table")

job.commit()
