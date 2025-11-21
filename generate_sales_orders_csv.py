#!/usr/bin/env python3
"""
Generate sales orders for AutoCorp and export to CSV files.
Uses generators for memory efficiency.
Configurable hyperparameters for order distribution.
"""

import random
import csv
import os
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

# ============================================================================
# HYPERPARAMETERS
# ============================================================================

# Order generation settings
TOTAL_ORDERS = 791532  # Total number of sales orders to generate
OUTPUT_DIR = "."  # Directory for CSV output files

# Order type distribution (must sum to 1.0)
ORDER_TYPE_DISTRIBUTION = {
    'Parts': 0.82,      # 82% parts-only orders
    'Service': 0.09,    # 9% service-only orders
    'Mixed': 0.09       # 9% mixed (parts + service) orders
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
# MOCK DATA GENERATORS
# ============================================================================

def generate_mock_customers():
    """Generate mock customer IDs."""
    return list(range(1, 1150))  # 1149 customers

def generate_mock_parts():
    """Generate mock parts data."""
    parts = []
    for i in range(1, 401):  # 400 parts
        parts.append({
            'sku': f'PART-{i:04d}',
            'name': f'Auto Part {i}',
            'price': round(random.uniform(5.0, 500.0), 2)
        })
    return parts

def generate_mock_services():
    """Generate mock services data."""
    services = []
    for i in range(1, 111):  # 110 services
        labor_cost = round(random.uniform(50.0, 500.0), 2)
        services.append({
            'serviceid': f'SVC-{i:03d}',
            'service': f'Service {i}',
            'labor_minutes': random.randint(30, 480),
            'labor_cost': labor_cost
        })
    return services

# ============================================================================
# ORDER GENERATORS
# ============================================================================

def generate_invoice_number(year_counters, order_date):
    """Generate unique invoice number and increment the counter for that year."""
    year = order_date.year
    year_counters[year] += 1
    return f"INV-{year}-{year_counters[year]:06d}"

def generate_parts_order(order_id, customer_ids, parts, year_counters):
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
            'order_id': order_id,
            'sku': part['sku'],
            'part_description': part['name'],
            'quantity': quantity,
            'unit_price': unit_price,
            'line_total': line_total
        })
    
    tax = subtotal * Decimal(str(TAX_RATE))
    total = subtotal + tax
    
    order_date = random_date(ORDER_DATE_START, ORDER_DATE_END)
    order = {
        'order_id': order_id,
        'customer_id': random.choice(customer_ids),
        'order_date': order_date,
        'invoice_number': generate_invoice_number(year_counters, order_date),
        'payment_method': weighted_choice(PAYMENT_METHODS),
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total,
        'order_type': 'Parts',
        'status': 'Completed',
        'parts': line_items,
        'services': []
    }
    
    return order

def generate_service_order(order_id, customer_ids, services, year_counters):
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
            'order_id': order_id,
            'serviceid': service['serviceid'],
            'service_description': service['service'],
            'quantity': quantity,
            'labor_minutes': service['labor_minutes'],
            'labor_cost': labor_cost,
            'parts_cost': parts_cost,
            'line_total': line_total,
            'vehicle_id': random.randint(10000, 99999),
            'technician_id': random.randint(1, 50),
            'service_status': 'Completed'
        })
    
    tax = subtotal * Decimal(str(TAX_RATE))
    total = subtotal + tax
    
    order_date = random_date(ORDER_DATE_START, ORDER_DATE_END)
    order = {
        'order_id': order_id,
        'customer_id': random.choice(customer_ids),
        'order_date': order_date,
        'invoice_number': generate_invoice_number(year_counters, order_date),
        'payment_method': weighted_choice(PAYMENT_METHODS),
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total,
        'order_type': 'Service',
        'status': 'Completed',
        'parts': [],
        'services': line_items
    }
    
    return order

def generate_mixed_order(order_id, customer_ids, parts, services, year_counters):
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
            'order_id': order_id,
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
            'order_id': order_id,
            'serviceid': service['serviceid'],
            'service_description': service['service'],
            'quantity': quantity,
            'labor_minutes': service['labor_minutes'],
            'labor_cost': labor_cost,
            'parts_cost': parts_cost,
            'line_total': line_total,
            'vehicle_id': random.randint(10000, 99999),
            'technician_id': random.randint(1, 50),
            'service_status': 'Completed'
        })
    
    tax = subtotal * Decimal(str(TAX_RATE))
    total = subtotal + tax
    
    order_date = random_date(ORDER_DATE_START, ORDER_DATE_END)
    order = {
        'order_id': order_id,
        'customer_id': random.choice(customer_ids),
        'order_date': order_date,
        'invoice_number': generate_invoice_number(year_counters, order_date),
        'payment_method': weighted_choice(PAYMENT_METHODS),
        'subtotal': subtotal,
        'tax': tax,
        'total_amount': total,
        'order_type': 'Mixed',
        'status': 'Completed',
        'parts': parts_items,
        'services': service_items
    }
    
    return order

def order_generator(customer_ids, parts, services, total_orders, year_counters):
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
    for order_id, order_type in enumerate(order_types, start=1):
        if order_type == 'Parts':
            yield generate_parts_order(order_id, customer_ids, parts, year_counters)
        elif order_type == 'Service':
            yield generate_service_order(order_id, customer_ids, services, year_counters)
        else:  # Mixed
            yield generate_mixed_order(order_id, customer_ids, parts, services, year_counters)

# ============================================================================
# CSV EXPORT FUNCTIONS
# ============================================================================

def write_orders_to_csv(orders, output_file):
    """Write orders to CSV file (append mode)."""
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['order_id', 'customer_id', 'order_date', 'invoice_number', 
                      'payment_method', 'subtotal', 'tax', 'total_amount', 
                      'order_type', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        for order in orders:
            writer.writerow({
                'order_id': order['order_id'],
                'customer_id': order['customer_id'],
                'order_date': order['order_date'].strftime('%Y-%m-%d %H:%M:%S'),
                'invoice_number': order['invoice_number'],
                'payment_method': order['payment_method'],
                'subtotal': f"{order['subtotal']:.2f}",
                'tax': f"{order['tax']:.2f}",
                'total_amount': f"{order['total_amount']:.2f}",
                'order_type': order['order_type'],
                'status': order['status']
            })

def write_parts_to_csv(parts_items, output_file):
    """Write parts line items to CSV file (append mode)."""
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['order_id', 'sku', 'part_description', 'quantity', 
                      'unit_price', 'line_total']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        for item in parts_items:
            writer.writerow({
                'order_id': item['order_id'],
                'sku': item['sku'],
                'part_description': item['part_description'],
                'quantity': item['quantity'],
                'unit_price': f"{item['unit_price']:.2f}",
                'line_total': f"{item['line_total']:.2f}"
            })

def write_services_to_csv(service_items, output_file):
    """Write service line items to CSV file (append mode)."""
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['order_id', 'serviceid', 'service_description', 'quantity',
                      'labor_minutes', 'labor_cost', 'parts_cost', 'line_total',
                      'vehicle_id', 'technician_id', 'service_status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        for item in service_items:
            writer.writerow({
                'order_id': item['order_id'],
                'serviceid': item['serviceid'],
                'service_description': item['service_description'],
                'quantity': item['quantity'],
                'labor_minutes': item['labor_minutes'],
                'labor_cost': f"{item['labor_cost']:.2f}",
                'parts_cost': f"{item['parts_cost']:.2f}",
                'line_total': f"{item['line_total']:.2f}",
                'vehicle_id': item['vehicle_id'],
                'technician_id': item['technician_id'],
                'service_status': item['service_status']
            })

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 70)
    print("Sales Order Generator (CSV Export)")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Total Orders: {TOTAL_ORDERS:,}")
    print(f"  Order Type Distribution:")
    for order_type, pct in ORDER_TYPE_DISTRIBUTION.items():
        count = int(TOTAL_ORDERS * pct)
        print(f"    {order_type:12s}: {pct:5.1%} ({count:,} orders)")
    print(f"  Date Range: {ORDER_DATE_START.date()} to {ORDER_DATE_END.date()}")
    print(f"  Tax Rate: {TAX_RATE:.1%}")
    print(f"  Output Directory: {OUTPUT_DIR}")
    
    try:
        # Generate mock reference data
        print("\n" + "-" * 70)
        print("Generating reference data...")
        customer_ids = generate_mock_customers()
        parts = generate_mock_parts()
        services = generate_mock_services()
        print(f"✓ Generated {len(customer_ids)} customer IDs")
        print(f"✓ Generated {len(parts)} parts")
        print(f"✓ Generated {len(services)} services")
        
        # Initialize year counters (starting from 0 for new data)
        year_counters = defaultdict(int)
        print(f"✓ Starting invoice numbers from scratch")
        
        # Generate orders and collect data
        print("\n" + "-" * 70)
        print("Generating orders...")
        
        orders_batch = []
        parts_items = []
        services_items = []
        total_generated = 0
        
        for order in order_generator(customer_ids, parts, services, TOTAL_ORDERS, year_counters):
            orders_batch.append(order)
            parts_items.extend(order['parts'])
            services_items.extend(order['services'])
            
            total_generated += 1
            if total_generated % 1000 == 0:
                print(f"  Generated {total_generated:,} / {TOTAL_ORDERS:,} orders...", end='\r')
        
        print(f"\n✓ Successfully generated {total_generated:,} orders")
        print(f"✓ Total parts line items: {len(parts_items):,}")
        print(f"✓ Total service line items: {len(services_items):,}")
        
        # Write to CSV files
        print("\n" + "-" * 70)
        print("Writing to CSV files...")
        
        orders_file = f"{OUTPUT_DIR}/sales_orders.csv"
        parts_file = f"{OUTPUT_DIR}/sales_order_parts.csv"
        services_file = f"{OUTPUT_DIR}/sales_order_services.csv"
        
        write_orders_to_csv(orders_batch, orders_file)
        print(f"✓ Written {orders_file}")
        
        write_parts_to_csv(parts_items, parts_file)
        print(f"✓ Written {parts_file}")
        
        write_services_to_csv(services_items, services_file)
        print(f"✓ Written {services_file}")
        
        # Calculate statistics
        print("\n" + "-" * 70)
        print("Statistics:")
        
        order_type_counts = defaultdict(int)
        for order in orders_batch:
            order_type_counts[order['order_type']] += 1
        
        print("\nOrder counts by type:")
        for order_type, count in sorted(order_type_counts.items()):
            print(f"  {order_type:12s}: {count:,} orders")
        
        total_revenue = sum(order['total_amount'] for order in orders_batch)
        avg_order_value = total_revenue / len(orders_batch)
        min_order = min(order['total_amount'] for order in orders_batch)
        max_order = max(order['total_amount'] for order in orders_batch)
        
        print(f"\nRevenue statistics:")
        print(f"  Total Revenue: ${total_revenue:,.2f}")
        print(f"  Avg Order Value: ${avg_order_value:,.2f}")
        print(f"  Min Order: ${min_order:,.2f}")
        print(f"  Max Order: ${max_order:,.2f}")
        
        print("\n" + "=" * 70)
        print("CSV generation completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
