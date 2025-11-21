#!/usr/bin/env python3
"""
Generate sales orders for AutoCorp database.
Uses generators for memory efficiency.
Configurable hyperparameters for order distribution.
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
import psycopg2
from psycopg2.extras import execute_batch

# ============================================================================
# HYPERPARAMETERS
# ============================================================================

# Order generation settings
TOTAL_ORDERS = 1000
BATCH_SIZE = 100  # Insert orders in batches for performance

# Order type distribution (must sum to 1.0)
ORDER_TYPE_DISTRIBUTION = {
    'Parts': 0.65,      # 65% parts-only orders
    'Service': 0.25,    # 25% service-only orders
    'Mixed': 0.10       # 10% mixed (parts + service) orders
}

# Line items per order (min, max)
PARTS_PER_ORDER = (1, 5)        # 1-5 parts per parts order
SERVICES_PER_ORDER = (1, 3)     # 1-3 services per service order
MIXED_PARTS_PER_ORDER = (1, 3)  # 1-3 parts in mixed orders
MIXED_SERVICES_PER_ORDER = (1, 2)  # 1-2 services in mixed orders

# Date range for orders
ORDER_DATE_START = datetime(2021, 6, 7)
ORDER_DATE_END = datetime(2024, 12, 31)

# Tax rate
TAX_RATE = 0.08  # 8% sales tax

# Payment methods distribution
PAYMENT_METHODS = {
    'Credit Card': 0.50,
    'Cash': 0.20,
    'Debit Card': 0.20,
    'Bank Transfer': 0.10
}

# Database connection
DB_CONFIG = {
    'dbname': 'autocorp',
    'user': 'scotton',
    'host': 'localhost'
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def weighted_choice(choices_dict):
    """Select random item based on probability weights."""
    choices = list(choices_dict.keys())
    weights = list(choices_dict.values())
    return random.choices(choices, weights=weights, k=1)[0]

def random_date(start, end):
    """Generate random datetime between start and end."""
    delta = end - start
    random_days = random.randint(0, delta.days)
    random_seconds = random.randint(0, 86399)
    return start + timedelta(days=random_days, seconds=random_seconds)

def calculate_line_total(quantity, unit_price):
    """Calculate line total with proper decimal precision."""
    return Decimal(str(quantity)) * Decimal(str(unit_price))

# ============================================================================
# DATA FETCHERS
# ============================================================================

def fetch_customer_ids(cursor):
    """Fetch all customer IDs."""
    cursor.execute("SELECT customer_id FROM customers")
    return [row[0] for row in cursor.fetchall()]

def fetch_parts(cursor):
    """Fetch all parts with SKU and price."""
    cursor.execute("SELECT sku, name, price FROM auto_parts")
    return [{'sku': row[0], 'name': row[1], 'price': float(row[2])} for row in cursor.fetchall()]

def fetch_services(cursor):
    """Fetch all services with details."""
    cursor.execute("""
        SELECT serviceid, service, labor_minutes, labor_cost
        FROM service
    """)
    return [{
        'serviceid': row[0],
        'service': row[1],
        'labor_minutes': row[2],
        'labor_cost': float(row[3].replace('$', '').replace(',', ''))
    } for row in cursor.fetchall()]

# ============================================================================
# ORDER GENERATORS
# ============================================================================

def generate_invoice_number(order_num):
    """Generate unique invoice number."""
    return f"INV-2024-{order_num:06d}"

def generate_parts_order(order_num, customer_ids, parts):
    """Generate a parts-only order."""
    num_parts = random.randint(*PARTS_PER_ORDER)
    selected_parts = random.sample(parts, min(num_parts, len(parts)))
    
    line_items = []
    subtotal = Decimal('0')
    
    for part in selected_parts:
        quantity = random.randint(1, 5)
        unit_price = Decimal(str(part['price']))
        line_total = calculate_line_total(quantity, unit_price)
        subtotal += line_total
        
        line_items.append({
            'sku': part['sku'],
            'part_description': part['name'],
            'quantity': quantity,
            'unit_price': unit_price,
            'line_total': line_total
        })
    
    tax = subtotal * Decimal(str(TAX_RATE))
    total = subtotal + tax
    
    order = {
        'customer_id': random.choice(customer_ids),
        'order_date': random_date(ORDER_DATE_START, ORDER_DATE_END),
        'invoice_number': generate_invoice_number(order_num),
        'payment_method': weighted_choice(PAYMENT_METHODS),
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total,
        'order_type': 'Parts',
        'parts': line_items,
        'services': []
    }
    
    return order

def generate_service_order(order_num, customer_ids, services):
    """Generate a service-only order."""
    num_services = random.randint(*SERVICES_PER_ORDER)
    selected_services = random.sample(services, min(num_services, len(services)))
    
    line_items = []
    subtotal = Decimal('0')
    
    for service in selected_services:
        quantity = 1  # Services typically performed once
        labor_cost = Decimal(str(service['labor_cost']))
        # Estimate parts cost as 50-150% of labor cost
        parts_cost = labor_cost * Decimal(str(random.uniform(0.5, 1.5)))
        line_total = labor_cost + parts_cost
        subtotal += line_total
        
        line_items.append({
            'serviceid': service['serviceid'],
            'service_description': service['service'],
            'quantity': quantity,
            'labor_minutes': service['labor_minutes'],
            'labor_cost': labor_cost,
            'parts_cost': parts_cost,
            'line_total': line_total,
            'vehicle_id': random.randint(10000, 99999),
            'technician_id': random.randint(1, 50)
        })
    
    tax = subtotal * Decimal(str(TAX_RATE))
    total = subtotal + tax
    
    order = {
        'customer_id': random.choice(customer_ids),
        'order_date': random_date(ORDER_DATE_START, ORDER_DATE_END),
        'invoice_number': generate_invoice_number(order_num),
        'payment_method': weighted_choice(PAYMENT_METHODS),
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total,
        'order_type': 'Service',
        'parts': [],
        'services': line_items
    }
    
    return order

def generate_mixed_order(order_num, customer_ids, parts, services):
    """Generate a mixed order (parts + services)."""
    num_parts = random.randint(*MIXED_PARTS_PER_ORDER)
    num_services = random.randint(*MIXED_SERVICES_PER_ORDER)
    
    selected_parts = random.sample(parts, min(num_parts, len(parts)))
    selected_services = random.sample(services, min(num_services, len(services)))
    
    parts_items = []
    service_items = []
    subtotal = Decimal('0')
    
    # Generate parts line items
    for part in selected_parts:
        quantity = random.randint(1, 3)
        unit_price = Decimal(str(part['price']))
        line_total = calculate_line_total(quantity, unit_price)
        subtotal += line_total
        
        parts_items.append({
            'sku': part['sku'],
            'part_description': part['name'],
            'quantity': quantity,
            'unit_price': unit_price,
            'line_total': line_total
        })
    
    # Generate service line items
    for service in selected_services:
        quantity = 1
        labor_cost = Decimal(str(service['labor_cost']))
        parts_cost = labor_cost * Decimal(str(random.uniform(0.5, 1.5)))
        line_total = labor_cost + parts_cost
        subtotal += line_total
        
        service_items.append({
            'serviceid': service['serviceid'],
            'service_description': service['service'],
            'quantity': quantity,
            'labor_minutes': service['labor_minutes'],
            'labor_cost': labor_cost,
            'parts_cost': parts_cost,
            'line_total': line_total,
            'vehicle_id': random.randint(10000, 99999),
            'technician_id': random.randint(1, 50)
        })
    
    tax = subtotal * Decimal(str(TAX_RATE))
    total = subtotal + tax
    
    order = {
        'customer_id': random.choice(customer_ids),
        'order_date': random_date(ORDER_DATE_START, ORDER_DATE_END),
        'invoice_number': generate_invoice_number(order_num),
        'payment_method': weighted_choice(PAYMENT_METHODS),
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total,
        'order_type': 'Mixed',
        'parts': parts_items,
        'services': service_items
    }
    
    return order

def order_generator(customer_ids, parts, services, total_orders):
    """
    Generator function to create orders one at a time.
    Memory efficient - only holds one order in memory at a time.
    """
    # Calculate order counts for each type
    parts_count = int(total_orders * ORDER_TYPE_DISTRIBUTION['Parts'])
    service_count = int(total_orders * ORDER_TYPE_DISTRIBUTION['Service'])
    mixed_count = total_orders - parts_count - service_count
    
    # Create list of order types to generate
    order_types = (
        ['Parts'] * parts_count +
        ['Service'] * service_count +
        ['Mixed'] * mixed_count
    )
    
    # Shuffle to randomize order placement
    random.shuffle(order_types)
    
    # Generate orders
    for order_num, order_type in enumerate(order_types, start=1):
        if order_type == 'Parts':
            yield generate_parts_order(order_num, customer_ids, parts)
        elif order_type == 'Service':
            yield generate_service_order(order_num, customer_ids, services)
        else:  # Mixed
            yield generate_mixed_order(order_num, customer_ids, parts, services)

# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def insert_order_batch(cursor, orders):
    """Insert a batch of orders with their line items."""
    # Prepare order headers
    order_sql = """
        INSERT INTO sales_order (customer_id, order_date, invoice_number, payment_method,
                                 subtotal, tax, total_amount, order_type, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING order_id
    """
    
    parts_sql = """
        INSERT INTO sales_order_parts (order_id, sku, part_description, quantity,
                                        unit_price, line_total)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    services_sql = """
        INSERT INTO sales_order_services (order_id, serviceid, service_description, quantity,
                                          labor_minutes, labor_cost, parts_cost, line_total,
                                          vehicle_id, technician_id, service_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    for order in orders:
        # Insert order header
        cursor.execute(order_sql, (
            order['customer_id'],
            order['order_date'],
            order['invoice_number'],
            order['payment_method'],
            order['subtotal'],
            order['tax'],
            order['total_amount'],
            order['order_type'],
            'Completed'
        ))
        
        order_id = cursor.fetchone()[0]
        
        # Insert parts line items
        if order['parts']:
            parts_data = [
                (order_id, item['sku'], item['part_description'], item['quantity'],
                 item['unit_price'], item['line_total'])
                for item in order['parts']
            ]
            execute_batch(cursor, parts_sql, parts_data)
        
        # Insert service line items
        if order['services']:
            services_data = [
                (order_id, item['serviceid'], item['service_description'], item['quantity'],
                 item['labor_minutes'], item['labor_cost'], item['parts_cost'], item['line_total'],
                 item['vehicle_id'], item['technician_id'], 'Completed')
                for item in order['services']
            ]
            execute_batch(cursor, services_sql, services_data)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 70)
    print("Sales Order Generator")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Total Orders: {TOTAL_ORDERS:,}")
    print(f"  Order Type Distribution:")
    for order_type, pct in ORDER_TYPE_DISTRIBUTION.items():
        count = int(TOTAL_ORDERS * pct)
        print(f"    {order_type:12s}: {pct:5.1%} ({count:,} orders)")
    print(f"  Date Range: {ORDER_DATE_START.date()} to {ORDER_DATE_END.date()}")
    print(f"  Tax Rate: {TAX_RATE:.1%}")
    print(f"  Batch Size: {BATCH_SIZE}")
    
    try:
        # Connect to database
        print("\n" + "-" * 70)
        print("Connecting to database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        print("✓ Connected to autocorp database")
        
        # Fetch reference data
        print("\nFetching reference data...")
        customer_ids = fetch_customer_ids(cursor)
        parts = fetch_parts(cursor)
        services = fetch_services(cursor)
        print(f"✓ Loaded {len(customer_ids)} customers")
        print(f"✓ Loaded {len(parts)} parts")
        print(f"✓ Loaded {len(services)} services")
        
        # Generate and insert orders in batches
        print("\n" + "-" * 70)
        print("Generating and inserting orders...")
        
        batch = []
        total_inserted = 0
        parts_line_items = 0
        services_line_items = 0
        
        for order in order_generator(customer_ids, parts, services, TOTAL_ORDERS):
            batch.append(order)
            parts_line_items += len(order['parts'])
            services_line_items += len(order['services'])
            
            # Insert when batch is full
            if len(batch) >= BATCH_SIZE:
                insert_order_batch(cursor, batch)
                conn.commit()
                total_inserted += len(batch)
                print(f"  Inserted {total_inserted:,} / {TOTAL_ORDERS:,} orders...", end='\r')
                batch = []
        
        # Insert remaining orders
        if batch:
            insert_order_batch(cursor, batch)
            conn.commit()
            total_inserted += len(batch)
        
        print(f"\n✓ Successfully inserted {total_inserted:,} orders")
        print(f"✓ Total parts line items: {parts_line_items:,}")
        print(f"✓ Total service line items: {services_line_items:,}")
        
        # Verify results
        print("\n" + "-" * 70)
        print("Verifying results...")
        cursor.execute("SELECT order_type, COUNT(*) FROM sales_order GROUP BY order_type ORDER BY order_type")
        print("\nOrder counts by type:")
        for row in cursor.fetchall():
            print(f"  {row[0]:12s}: {row[1]:,} orders")
        
        cursor.execute("""
            SELECT 
                SUM(total_amount) as total_revenue,
                AVG(total_amount) as avg_order_value,
                MIN(total_amount) as min_order,
                MAX(total_amount) as max_order
            FROM sales_order
        """)
        stats = cursor.fetchone()
        print(f"\nRevenue statistics:")
        print(f"  Total Revenue: ${stats[0]:,.2f}")
        print(f"  Avg Order Value: ${stats[1]:,.2f}")
        print(f"  Min Order: ${stats[2]:,.2f}")
        print(f"  Max Order: ${stats[3]:,.2f}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("Generation completed successfully!")
        print("=" * 70)
        
    except psycopg2.Error as e:
        print(f"\n✗ Database error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        if 'conn' in locals():
            conn.rollback()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
