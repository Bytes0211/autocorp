"""
Glue ETL Job: sales_order_csv - Process CSV data with Hudi upserts
Reads from Glue catalog (CSV tables) and writes to curated/hudi/sales_order/
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
curated_path = f"s3://{data_lake_bucket}/curated/hudi/sales_order/"

print(f"Reading from Glue catalog table: autocorp_dev.sales_orders")
print(f"Writing to: {curated_path}")

# Read from Glue Data Catalog (CSV table)
df = glueContext.create_dynamic_frame.from_catalog(
    database="autocorp_dev",
    table_name="sales_orders"
).toDF()

print(f"Raw CSV records read: {df.count()}")
df.printSchema()

# Data type conversions and cleaning
# Cast order_date to date type (handles both date and datetime strings)
df_typed = df \
    .withColumn("order_date", to_date(col("order_date"))) \
    .withColumn("created_at", current_timestamp()) \
    .withColumn("updated_at", current_timestamp())

# Data quality checks and transformations
df_clean = df_typed \
    .filter(col("invoice_number").isNotNull()) \
    .filter(col("total_amount") > 0) \
    .filter(col("order_date").isNotNull()) \
    .withColumn("etl_timestamp", current_timestamp()) \
    .withColumn("year", year(col("order_date"))) \
    .withColumn("month", month(col("order_date"))) \
    .withColumn("data_source", lit("csv"))

# Deduplicate by invoice_number (Hudi record key)
df_clean = df_clean.dropDuplicates(["invoice_number"])

print(f"Clean records after deduplication: {df_clean.count()}")

# Hudi configuration for Copy-on-Write (transactional data)
hudi_options = {
    'hoodie.table.name': 'sales_order',
    'hoodie.datasource.write.recordkey.field': 'invoice_number',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.table.name': 'sales_order',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.precombine.field': 'updated_at',
    'hoodie.datasource.hive_sync.enable': 'false',  # Disabled for initial load
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

print(f"Successfully wrote {df_clean.count()} unique records to Hudi table")

job.commit()
