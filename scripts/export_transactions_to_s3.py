#!/usr/bin/env python3
"""
Export transaction tables from PostgreSQL to Parquet format in S3.
This populates the raw/database/ prefix that Glue ETL jobs expect.
"""

import psycopg2
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import boto3
from io import BytesIO
import sys

# Database connection
DB_CONFIG = {
    'dbname': 'autocorp',
    'user': 'scotton',
    'host': 'localhost'
}

# S3 configuration
S3_BUCKET = 'autocorp-datalake-dev'
S3_PREFIX = 'raw/database/'

# Tables to export
TABLES = [
    'sales_order',
    'sales_order_parts',
    'sales_order_services'
]

def export_table_to_s3(cursor, s3_client, table_name):
    """Export a single table to S3 as Parquet."""
    print(f"Exporting {table_name}...")
    
    # Fetch data
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    
    if not data:
        print(f"  ⚠️  Warning: {table_name} is empty")
        return
    
    # Convert to pandas DataFrame
    df = pd.DataFrame(data, columns=columns)
    print(f"  Rows: {len(df):,}")
    
    # Convert timestamp columns to microsecond precision (not nanoseconds)
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            df[col] = df[col].astype('datetime64[us]')
    
    # Convert to PyArrow Table with timestamp(us) for datetime columns
    table = pa.Table.from_pandas(df)
    
    # Write to in-memory buffer as Parquet
    buffer = BytesIO()
    pq.write_table(table, buffer, compression='snappy')
    buffer.seek(0)
    
    # Upload to S3
    s3_key = f"{S3_PREFIX}{table_name}/{table_name}.parquet"
    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=s3_key,
        Body=buffer.getvalue()
    )
    
    print(f"  ✅ Uploaded to s3://{S3_BUCKET}/{s3_key}")

def main():
    """Export all transaction tables to S3."""
    print(f"Connecting to PostgreSQL database '{DB_CONFIG['dbname']}'...")
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Export each table
        for table_name in TABLES:
            try:
                export_table_to_s3(cursor, s3_client, table_name)
            except Exception as e:
                print(f"  ❌ Error exporting {table_name}: {e}")
                continue
        
        cursor.close()
        conn.close()
        
        print("\n✅ Export complete!")
        print(f"\nNext steps:")
        print(f"1. Run Glue Crawler to update schema:")
        print(f"   aws glue start-crawler --name autocorp-raw-database-crawler-dev")
        print(f"2. Re-run Glue ETL jobs:")
        print(f"   aws glue start-job-run --job-name autocorp-sales-order-etl-dev")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
