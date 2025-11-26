#!/usr/bin/env python3
"""
Generate sales orders for AutoCorp and export to CSV files.
Uses generators for memory efficiency.
Configurable hyperparameters for order distribution and data quality testing.

Data Quality Testing Features:
- Missing/null values injection for testing ETL null handling
- Invalid data injection (malformed dates, type mismatches, formatting issues)
- Edge case testing (duplicates, negative values, out-of-range dates)
- Data validation manifest generation for ETL pipeline verification

Designed for testing AWS DataSync -> Glue Crawler -> Data Catalog pipelines.
"""

import random
import csv
import os
import json
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

# ============================================================================
# DATA QUALITY TESTING PARAMETERS
# ============================================================================

# Missing/null value injection rates
MISSING_CUSTOMER_ID_RATE = 0.007      # 0.7% of customer_ids will be missing
MISSING_ORDER_DATE_RATE = 0.0002      # 0.02% of order_dates will be null
MISSING_TAX_RATE = 0.001              # 0.1% of tax values will be NaN
MISSING_INVOICE_NUMBER_RATE = 0.0005  # 0.05% of invoice_numbers will be missing
MISSING_PAYMENT_METHOD_RATE = 0.002   # 0.2% of payment_methods will be missing
MISSING_SUBTOTAL_RATE = 0.0003        # 0.03% of subtotals will be missing

# Invalid data injection rates
INVALID_DATE_FORMAT_RATE = 0.0008     # 0.08% invalid date formats (e.g., "2024-13-45")
WHITESPACE_CUSTOMER_ID_RATE = 0.001   # 0.1% customer_ids with leading/trailing spaces
FORMATTED_NUMBER_RATE = 0.0015        # 0.15% numbers with commas/currency symbols
CURRENCY_SYMBOL_RATE = 0.0005         # 0.05% amounts with $ symbols

# Edge case injection rates
DUPLICATE_ORDER_ID_RATE = 0.0001      # 0.01% duplicate order IDs
NEGATIVE_AMOUNT_RATE = 0.0005         # 0.05% negative amounts (business logic violation)
FUTURE_DATE_RATE = 0.001              # 0.1% dates beyond ORDER_DATE_END
PAST_DATE_RATE = 0.0008               # 0.08% dates before ORDER_DATE_START
ZERO_QUANTITY_RATE = 0.0003           # 0.03% zero quantities in line items

# Validation manifest settings
GENERATE_MANIFEST = True               # Generate data validation manifest file

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
# DATA QUALITY INJECTION FUNCTIONS
# ============================================================================

def inject_invalid_date():
    """Generate invalid date strings for testing."""
    invalid_formats = [
        "2024-13-45",           # Invalid month and day
        "2024-02-30",           # Invalid day for February
        "invalid-date",         # Non-date string
        "2024/06/15",           # Wrong delimiter
        "06-15-2024",           # Wrong order
        "2024-6-7 25:99:99",    # Invalid time
    ]
    return random.choice(invalid_formats)

def inject_whitespace(value):
    """Add leading/trailing whitespace to a value."""
    whitespace_types = [
        f" {value}",      # Leading space
        f"{value} ",      # Trailing space
        f" {value} ",     # Both
        f"  {value}  ",   # Multiple spaces
    ]
    return random.choice(whitespace_types)

def inject_formatted_number(value):
    """Format number with commas (e.g., 1,234.56)."""
    return f"{float(value):,.2f}"

def inject_currency_symbol(value):
    """Add currency symbol to number."""
    return f"${float(value):.2f}"

def generate_future_date():
    """Generate a date after ORDER_DATE_END."""
    days_ahead = random.randint(1, 365)
    return ORDER_DATE_END + timedelta(days=days_ahead)

def generate_past_date():
    """Generate a date before ORDER_DATE_START."""
    days_back = random.randint(1, 365)
    return ORDER_DATE_START - timedelta(days=days_back)

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

def write_orders_to_csv(orders, output_file, duplicate_tracker):
    """Write orders to CSV file (append mode) with comprehensive data quality injection."""
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['order_id', 'customer_id', 'order_date', 'invoice_number', 
                      'payment_method', 'subtotal', 'tax', 'total_amount', 
                      'order_type', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        for order in orders:
            # Get base values
            order_id = order['order_id']
            customer_id = order['customer_id']
            order_date_obj = order['order_date']
            invoice_number = order['invoice_number']
            payment_method = order['payment_method']
            subtotal = order['subtotal']
            tax = order['tax']
            total_amount = order['total_amount']
            
            # === DUPLICATE ORDER IDs ===
            if random.random() < DUPLICATE_ORDER_ID_RATE and duplicate_tracker['order_ids']:
                order_id = random.choice(duplicate_tracker['order_ids'])
            else:
                duplicate_tracker['order_ids'].append(order_id)
            
            # === MISSING VALUES ===
            if random.random() < MISSING_CUSTOMER_ID_RATE:
                customer_id = ''
            elif random.random() < WHITESPACE_CUSTOMER_ID_RATE:
                customer_id = inject_whitespace(customer_id)
            
            if random.random() < MISSING_INVOICE_NUMBER_RATE:
                invoice_number = ''
            
            if random.random() < MISSING_PAYMENT_METHOD_RATE:
                payment_method = ''
            
            # === DATE HANDLING ===
            if random.random() < MISSING_ORDER_DATE_RATE:
                order_date = ''
            elif random.random() < INVALID_DATE_FORMAT_RATE:
                order_date = inject_invalid_date()
            elif random.random() < FUTURE_DATE_RATE:
                order_date = generate_future_date().strftime('%Y-%m-%d %H:%M:%S')
            elif random.random() < PAST_DATE_RATE:
                order_date = generate_past_date().strftime('%Y-%m-%d %H:%M:%S')
            else:
                order_date = order_date_obj.strftime('%Y-%m-%d %H:%M:%S')
            
            # === NUMERIC VALUES ===
            # Subtotal
            if random.random() < MISSING_SUBTOTAL_RATE:
                subtotal_str = ''
            elif random.random() < NEGATIVE_AMOUNT_RATE:
                subtotal_str = f"{-abs(float(subtotal)):.2f}"
            elif random.random() < FORMATTED_NUMBER_RATE:
                subtotal_str = inject_formatted_number(subtotal)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                subtotal_str = inject_currency_symbol(subtotal)
            else:
                subtotal_str = f"{subtotal:.2f}"
            
            # Tax
            if random.random() < MISSING_TAX_RATE:
                tax_str = ''
            elif random.random() < FORMATTED_NUMBER_RATE:
                tax_str = inject_formatted_number(tax)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                tax_str = inject_currency_symbol(tax)
            else:
                tax_str = f"{tax:.2f}"
            
            # Total amount
            if random.random() < NEGATIVE_AMOUNT_RATE:
                total_amount_str = f"{-abs(float(total_amount)):.2f}"
            elif random.random() < FORMATTED_NUMBER_RATE:
                total_amount_str = inject_formatted_number(total_amount)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                total_amount_str = inject_currency_symbol(total_amount)
            else:
                total_amount_str = f"{total_amount:.2f}"
            
            writer.writerow({
                'order_id': order_id,
                'customer_id': customer_id,
                'order_date': order_date,
                'invoice_number': invoice_number,
                'payment_method': payment_method,
                'subtotal': subtotal_str,
                'tax': tax_str,
                'total_amount': total_amount_str,
                'order_type': order['order_type'],
                'status': order['status']
            })

def write_parts_to_csv(parts_items, output_file):
    """Write parts line items to CSV file (append mode) with data quality injection."""
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['order_id', 'sku', 'part_description', 'quantity', 
                      'unit_price', 'line_total']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        for item in parts_items:
            # Apply data quality issues to line items
            quantity = item['quantity']
            if random.random() < ZERO_QUANTITY_RATE:
                quantity = 0
            
            unit_price = item['unit_price']
            if random.random() < NEGATIVE_AMOUNT_RATE:
                unit_price_str = f"{-abs(float(unit_price)):.2f}"
            elif random.random() < FORMATTED_NUMBER_RATE:
                unit_price_str = inject_formatted_number(unit_price)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                unit_price_str = inject_currency_symbol(unit_price)
            else:
                unit_price_str = f"{unit_price:.2f}"
            
            line_total = item['line_total']
            if random.random() < FORMATTED_NUMBER_RATE:
                line_total_str = inject_formatted_number(line_total)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                line_total_str = inject_currency_symbol(line_total)
            else:
                line_total_str = f"{line_total:.2f}"
            
            writer.writerow({
                'order_id': item['order_id'],
                'sku': item['sku'],
                'part_description': item['part_description'],
                'quantity': quantity,
                'unit_price': unit_price_str,
                'line_total': line_total_str
            })

def write_services_to_csv(service_items, output_file):
    """Write service line items to CSV file (append mode) with data quality injection."""
    file_exists = os.path.isfile(output_file)
    with open(output_file, 'a', newline='') as csvfile:
        fieldnames = ['order_id', 'serviceid', 'service_description', 'quantity',
                      'labor_minutes', 'labor_cost', 'parts_cost', 'line_total',
                      'vehicle_id', 'technician_id', 'service_status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        
        for item in service_items:
            # Apply data quality issues
            labor_cost = item['labor_cost']
            if random.random() < FORMATTED_NUMBER_RATE:
                labor_cost_str = inject_formatted_number(labor_cost)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                labor_cost_str = inject_currency_symbol(labor_cost)
            else:
                labor_cost_str = f"{labor_cost:.2f}"
            
            parts_cost = item['parts_cost']
            if random.random() < FORMATTED_NUMBER_RATE:
                parts_cost_str = inject_formatted_number(parts_cost)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                parts_cost_str = inject_currency_symbol(parts_cost)
            else:
                parts_cost_str = f"{parts_cost:.2f}"
            
            line_total = item['line_total']
            if random.random() < FORMATTED_NUMBER_RATE:
                line_total_str = inject_formatted_number(line_total)
            elif random.random() < CURRENCY_SYMBOL_RATE:
                line_total_str = inject_currency_symbol(line_total)
            else:
                line_total_str = f"{line_total:.2f}"
            
            writer.writerow({
                'order_id': item['order_id'],
                'serviceid': item['serviceid'],
                'service_description': item['service_description'],
                'quantity': item['quantity'],
                'labor_minutes': item['labor_minutes'],
                'labor_cost': labor_cost_str,
                'parts_cost': parts_cost_str,
                'line_total': line_total_str,
                'vehicle_id': item['vehicle_id'],
                'technician_id': item['technician_id'],
                'service_status': item['service_status']
            })

def write_manifest(manifest_data, output_file):
    """Write validation manifest to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(manifest_data, f, indent=2)

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
    print(f"  Generate Manifest: {GENERATE_MANIFEST}")
    print(f"\n  Data Quality Testing Rates:")
    print(f"    Missing Values:")
    print(f"      Customer ID:     {MISSING_CUSTOMER_ID_RATE:.4%} (~{int(TOTAL_ORDERS * MISSING_CUSTOMER_ID_RATE)} orders)")
    print(f"      Order Date:      {MISSING_ORDER_DATE_RATE:.4%} (~{int(TOTAL_ORDERS * MISSING_ORDER_DATE_RATE)} orders)")
    print(f"      Tax:             {MISSING_TAX_RATE:.4%} (~{int(TOTAL_ORDERS * MISSING_TAX_RATE)} orders)")
    print(f"      Invoice Number:  {MISSING_INVOICE_NUMBER_RATE:.4%} (~{int(TOTAL_ORDERS * MISSING_INVOICE_NUMBER_RATE)} orders)")
    print(f"      Payment Method:  {MISSING_PAYMENT_METHOD_RATE:.4%} (~{int(TOTAL_ORDERS * MISSING_PAYMENT_METHOD_RATE)} orders)")
    print(f"    Invalid Data:")
    print(f"      Invalid Dates:   {INVALID_DATE_FORMAT_RATE:.4%} (~{int(TOTAL_ORDERS * INVALID_DATE_FORMAT_RATE)} orders)")
    print(f"      Formatted #s:    {FORMATTED_NUMBER_RATE:.4%} (per numeric field)")
    print(f"    Edge Cases:")
    print(f"      Duplicates:      {DUPLICATE_ORDER_ID_RATE:.4%} (~{int(TOTAL_ORDERS * DUPLICATE_ORDER_ID_RATE)} orders)")
    print(f"      Negative Amts:   {NEGATIVE_AMOUNT_RATE:.4%} (per amount field)")
    print(f"      Future Dates:    {FUTURE_DATE_RATE:.4%} (~{int(TOTAL_ORDERS * FUTURE_DATE_RATE)} orders)")
    
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
        
        # Initialize year counters and duplicate tracker
        year_counters = defaultdict(int)
        duplicate_tracker = {'order_ids': []}
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
        manifest_file = f"{OUTPUT_DIR}/data_validation_manifest.json"
        
        write_orders_to_csv(orders_batch, orders_file, duplicate_tracker)
        print(f"✓ Written {orders_file}")
        
        write_parts_to_csv(parts_items, parts_file)
        print(f"✓ Written {parts_file}")
        
        write_services_to_csv(services_items, services_file)
        print(f"✓ Written {services_file}")
        
        # Calculate statistics for manifest and reporting
        order_type_counts = defaultdict(int)
        for order in orders_batch:
            order_type_counts[order['order_type']] += 1
        
        total_revenue = sum(order['total_amount'] for order in orders_batch)
        avg_order_value = total_revenue / len(orders_batch)
        min_order = min(order['total_amount'] for order in orders_batch)
        max_order = max(order['total_amount'] for order in orders_batch)
        
        # Generate validation manifest
        if GENERATE_MANIFEST:
            manifest_data = {
                "generation_timestamp": datetime.now().isoformat(),
                "configuration": {
                    "total_orders": TOTAL_ORDERS,
                    "order_type_distribution": ORDER_TYPE_DISTRIBUTION,
                    "date_range": {
                        "start": ORDER_DATE_START.isoformat(),
                        "end": ORDER_DATE_END.isoformat()
                    },
                    "tax_rate": TAX_RATE
                },
                "data_quality_parameters": {
                    "missing_values": {
                        "customer_id_rate": MISSING_CUSTOMER_ID_RATE,
                        "order_date_rate": MISSING_ORDER_DATE_RATE,
                        "tax_rate": MISSING_TAX_RATE,
                        "invoice_number_rate": MISSING_INVOICE_NUMBER_RATE,
                        "payment_method_rate": MISSING_PAYMENT_METHOD_RATE,
                        "subtotal_rate": MISSING_SUBTOTAL_RATE
                    },
                    "invalid_data": {
                        "invalid_date_format_rate": INVALID_DATE_FORMAT_RATE,
                        "whitespace_customer_id_rate": WHITESPACE_CUSTOMER_ID_RATE,
                        "formatted_number_rate": FORMATTED_NUMBER_RATE,
                        "currency_symbol_rate": CURRENCY_SYMBOL_RATE
                    },
                    "edge_cases": {
                        "duplicate_order_id_rate": DUPLICATE_ORDER_ID_RATE,
                        "negative_amount_rate": NEGATIVE_AMOUNT_RATE,
                        "future_date_rate": FUTURE_DATE_RATE,
                        "past_date_rate": PAST_DATE_RATE,
                        "zero_quantity_rate": ZERO_QUANTITY_RATE
                    }
                },
                "expected_counts": {
                    "total_orders": total_generated,
                    "parts_line_items": len(parts_items),
                    "service_line_items": len(services_items),
                    "orders_by_type": dict(order_type_counts)
                },
                "expected_issues": {
                    "missing_customer_ids": int(TOTAL_ORDERS * MISSING_CUSTOMER_ID_RATE),
                    "missing_order_dates": int(TOTAL_ORDERS * MISSING_ORDER_DATE_RATE),
                    "missing_tax": int(TOTAL_ORDERS * MISSING_TAX_RATE),
                    "invalid_dates": int(TOTAL_ORDERS * INVALID_DATE_FORMAT_RATE),
                    "duplicate_order_ids": int(TOTAL_ORDERS * DUPLICATE_ORDER_ID_RATE),
                    "future_dates": int(TOTAL_ORDERS * FUTURE_DATE_RATE),
                    "past_dates": int(TOTAL_ORDERS * PAST_DATE_RATE)
                },
                "revenue_statistics": {
                    "total_revenue": float(total_revenue),
                    "avg_order_value": float(avg_order_value),
                    "min_order": float(min_order),
                    "max_order": float(max_order)
                },
                "files": {
                    "orders": orders_file,
                    "parts": parts_file,
                    "services": services_file
                }
            }
            write_manifest(manifest_data, manifest_file)
            print(f"✓ Written {manifest_file}")
        
        # Display statistics
        print("\n" + "-" * 70)
        print("Statistics:")
        
        print("\nOrder counts by type:")
        for order_type, count in sorted(order_type_counts.items()):
            print(f"  {order_type:12s}: {count:,} orders")
        
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
