#!/usr/bin/env python3
"""
Export PostgreSQL tables to Parquet format and upload to S3 raw zone
This simulates DMS output for testing Glue ETL jobs
"""
import os
import pandas as pd
import psycopg2
import boto3
from datetime import datetime

# Database connection
DB_CONFIG = {
    'host': 'localhost',
    'database': 'autocorp',
    'user': 'scotton',
    'password': os.getenv('PGPASSWORD', '')
}

# S3 configuration
S3_BUCKET = 'autocorp-datalake-dev'
S3_PREFIX = 'raw/database'

# Tables to export
TABLES = ['customers', 'auto_parts', 'service', 'service_parts']

def export_table_to_parquet(table_name):
    """Export a PostgreSQL table to Parquet format and upload to S3"""
    print(f"\n=== Processing table: {table_name} ===")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        # Read table into pandas DataFrame
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        print(f"Rows fetched: {len(df)}")
        
        # Convert timestamp columns to compatible format (milliseconds)
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = pd.to_datetime(df[col]).dt.tz_localize(None)
        
        # Create local temp file with compatible timestamp format
        local_file = f"/tmp/{table_name}.parquet"
        df.to_parquet(
            local_file, 
            engine='pyarrow', 
            index=False,
            coerce_timestamps='ms',  # Use millisecond precision for Spark compatibility
            allow_truncated_timestamps=True
        )
        print(f"Saved to local file: {local_file}")
        
        # Upload to S3
        s3_key = f"{S3_PREFIX}/{table_name}/{table_name}.parquet"
        s3_client = boto3.client('s3')
        s3_client.upload_file(local_file, S3_BUCKET, s3_key)
        print(f"Uploaded to: s3://{S3_BUCKET}/{s3_key}")
        
        # Cleanup
        os.remove(local_file)
        print(f"✅ Successfully processed {table_name}")
        
    except Exception as e:
        print(f"❌ Error processing {table_name}: {e}")
    finally:
        conn.close()

def main():
    print("=" * 60)
    print("AutoCorp Data Export to S3 Raw Zone")
    print("=" * 60)
    print(f"Target bucket: {S3_BUCKET}")
    print(f"Target prefix: {S3_PREFIX}")
    print(f"Tables to export: {', '.join(TABLES)}")
    print("=" * 60)
    
    for table in TABLES:
        export_table_to_parquet(table)
    
    print("\n" + "=" * 60)
    print("✅ Export completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run Glue crawler to discover schema")
    print("2. Run Glue ETL jobs to create Hudi tables")
    print("3. Query Hudi tables with Athena")

if __name__ == '__main__':
    main()
