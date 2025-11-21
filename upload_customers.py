#!/usr/bin/env python3
"""
Upload randomly selected customers from customers.csv to autocorp database.
Randomly selects 1,150 customers from the 1.2M customer CSV file.
"""

import csv
import random
import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_CONFIG = {
    'dbname': 'autocorp',
    'user': 'scotton',
    'host': 'localhost'
}

# File paths
CSV_FILE = '/home/scotton/dev/projects/autocorp/customers.csv'
NUM_CUSTOMERS = 1150

def create_customers_table(cursor):
    """Create the customers table if it doesn't exist."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id SERIAL PRIMARY KEY,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        email VARCHAR(200) UNIQUE NOT NULL,
        phone VARCHAR(50),
        address VARCHAR(300),
        city VARCHAR(100),
        state VARCHAR(50),
        zip_code VARCHAR(20),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Create index on email for faster lookups
    CREATE INDEX IF NOT EXISTS idx_customers_email ON customers(email);
    """
    cursor.execute(create_table_sql)
    print("✓ Customers table created/verified")

def count_csv_lines(filepath):
    """Count total lines in CSV file (excluding header)."""
    with open(filepath, 'r') as f:
        return sum(1 for _ in f) - 1  # Subtract 1 for header

def randomly_select_customers(filepath, num_to_select):
    """
    Randomly select N customers from CSV using reservoir sampling.
    This is memory efficient for large files.
    """
    print(f"Reading {filepath}...")
    
    # For files with known line count, we can use random line selection
    total_lines = count_csv_lines(filepath)
    print(f"Total customers available: {total_lines:,}")
    
    # Generate random line numbers (excluding header line 0)
    selected_line_numbers = set(random.sample(range(1, total_lines + 1), num_to_select))
    print(f"Randomly selected {num_to_select} customers")
    
    selected_customers = []
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for line_num, row in enumerate(reader, start=1):
            if line_num in selected_line_numbers:
                selected_customers.append(row)
                if len(selected_customers) == num_to_select:
                    break
    
    return selected_customers

def insert_customers(cursor, customers):
    """Insert customers into the database."""
    insert_sql = """
    INSERT INTO customers (first_name, last_name, email, phone, address, city, state, zip_code)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (email) DO NOTHING;
    """
    
    inserted = 0
    skipped = 0
    
    for customer in customers:
        try:
            cursor.execute(insert_sql, (
                customer['first_name'],
                customer['last_name'],
                customer['email'],
                customer['phone'],
                customer['address'],
                customer['city'],
                customer['state'],
                customer['zip']
            ))
            if cursor.rowcount > 0:
                inserted += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"Error inserting customer {customer['email']}: {e}")
            skipped += 1
    
    return inserted, skipped

def main():
    """Main execution function."""
    print("=" * 60)
    print("Customer Upload Script")
    print("=" * 60)
    
    try:
        # Connect to database
        print("\nConnecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected to autocorp database")
        
        # Create table
        print("\nCreating/verifying customers table...")
        create_customers_table(cursor)
        conn.commit()
        
        # Randomly select customers
        print(f"\nSelecting {NUM_CUSTOMERS} random customers...")
        customers = randomly_select_customers(CSV_FILE, NUM_CUSTOMERS)
        print(f"✓ Selected {len(customers)} customers")
        
        # Insert customers
        print("\nInserting customers into database...")
        inserted, skipped = insert_customers(cursor, customers)
        conn.commit()
        
        print(f"\n✓ Successfully inserted {inserted} customers")
        if skipped > 0:
            print(f"  ⚠ Skipped {skipped} customers (duplicates or errors)")
        
        # Verify counts
        cursor.execute("SELECT COUNT(*) FROM customers")
        total_count = cursor.fetchone()[0]
        print(f"\n✓ Total customers in database: {total_count}")
        
        # Show sample customers
        cursor.execute("SELECT customer_id, first_name, last_name, email, city, state FROM customers LIMIT 5")
        print("\nSample customers:")
        print("-" * 80)
        for row in cursor.fetchall():
            print(f"  ID: {row[0]:4d} | {row[1]} {row[2]:15s} | {row[3]:30s} | {row[4]}, {row[5]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("Upload completed successfully!")
        print("=" * 60)
        
    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return 1
    except FileNotFoundError:
        print(f"\n✗ File not found: {CSV_FILE}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
