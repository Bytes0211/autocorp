# Unified Sales System - Usage Guide

## Overview
The unified sales system (Option A) supports both parts sales and service sales on a single invoice. This flexible approach allows:
- Direct parts sales to customers
- Service sales (which include associated parts automatically)
- Mixed invoices with both parts and services

## Database Structure

### Tables Created

1. **`service_parts`** - Junction table mapping services to parts
   - Links each service to the parts (SKUs) required
   - Contains 1,074 service-to-part mappings

2. **`sales_order`** - Main invoice/order header
   - One row per invoice
   - Tracks customer, totals, payment method, order type

3. **`sales_order_parts`** - Line items for direct parts sales
   - Parts sold individually (not as part of a service)
   - References `part_id` or uses `sku`

4. **`sales_order_services`** - Line items for services performed
   - Services include labor and associated parts
   - Tracks technician, vehicle, service status

### Views Created

1. **`v_sales_order_summary`** - Summary of all orders with line item counts
2. **`v_service_with_parts`** - Services with their parts count

## Usage Examples

### 1. Create a Parts-Only Sale

```sql
-- Insert the order header
INSERT INTO sales_order (customer_id, order_date, invoice_number, payment_method, 
                         subtotal, tax, total_amount, order_type, status)
VALUES (12345, CURRENT_TIMESTAMP, 'INV-2025-001', 'Credit Card', 
        150.00, 12.00, 162.00, 'Parts', 'Completed')
RETURNING order_id;

-- Add line items (assuming order_id = 1)
INSERT INTO sales_order_parts (order_id, sku, part_description, quantity, unit_price, line_total)
VALUES 
    (1, 'AUF1QE4EC', 'Oil Filter', 2, 25.00, 50.00),
    (1, 'ESNZDYYRH', 'Air Filter', 1, 100.00, 100.00);
```

### 2. Create a Service-Only Sale

```sql
-- Insert the order header
INSERT INTO sales_order (customer_id, order_date, invoice_number, payment_method,
                         subtotal, tax, total_amount, order_type, status)
VALUES (12345, CURRENT_TIMESTAMP, 'INV-2025-002', 'Credit Card',
        135.00, 10.80, 145.80, 'Service', 'Completed')
RETURNING order_id;

-- Add service line item (oil change)
INSERT INTO sales_order_services (order_id, serviceid, service_description, quantity,
                                   labor_minutes, labor_cost, parts_cost, line_total,
                                   vehicle_id, technician_id, service_status)
VALUES (2, '48392017', 'Oil change (engine oil & filter replacement)', 1,
        30, 45.00, 90.00, 135.00,
        77889, 42, 'Completed');
```

### 3. Create a Mixed Sale (Parts + Service)

```sql
-- Insert the order header
INSERT INTO sales_order (customer_id, order_date, invoice_number, payment_method,
                         subtotal, tax, total_amount, order_type, status)
VALUES (12345, CURRENT_TIMESTAMP, 'INV-2025-003', 'Credit Card',
        235.00, 18.80, 253.80, 'Mixed', 'Completed')
RETURNING order_id;

-- Add service line item
INSERT INTO sales_order_services (order_id, serviceid, service_description, quantity,
                                   labor_minutes, labor_cost, parts_cost, line_total,
                                   vehicle_id, technician_id)
VALUES (3, '38492059', 'Brake pad replacement', 1,
        90, 135.00, 0.00, 135.00,
        77889, 42);

-- Add direct parts line item
INSERT INTO sales_order_parts (order_id, sku, part_description, quantity, unit_price, line_total)
VALUES (3, 'AUF1QE4EC', 'Oil Filter', 4, 25.00, 100.00);
```

### 4. Query: Get Complete Order Details

```sql
-- Order summary
SELECT * FROM v_sales_order_summary WHERE invoice_number = 'INV-2025-003';

-- Get all line items for an order
SELECT 
    'Part' as item_type,
    part_description as description,
    quantity,
    unit_price,
    line_total
FROM sales_order_parts
WHERE order_id = 3
UNION ALL
SELECT 
    'Service' as item_type,
    service_description as description,
    quantity,
    labor_cost as unit_price,
    line_total
FROM sales_order_services
WHERE order_id = 3
ORDER BY item_type;
```

### 5. Query: What Parts Are Needed for a Service?

```sql
-- Get all parts needed for "Oil change"
SELECT 
    s.serviceid,
    s.service,
    sp.sku,
    sp.quantity
FROM service s
JOIN service_parts sp ON s.serviceid = sp.serviceid
WHERE s.serviceid = '48392017';

-- Count total parts across all services
SELECT * FROM v_service_with_parts
ORDER BY parts_count DESC
LIMIT 10;
```

### 6. Query: Customer Order History

```sql
-- Get all orders for a customer
SELECT 
    invoice_number,
    order_date,
    order_type,
    total_amount,
    payment_method,
    status,
    parts_line_items,
    service_line_items
FROM v_sales_order_summary
WHERE customer_id = 12345
ORDER BY order_date DESC;
```

### 7. Query: Revenue by Order Type

```sql
SELECT 
    order_type,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value
FROM sales_order
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY order_type
ORDER BY total_revenue DESC;
```

### 8. Query: Most Popular Services

```sql
SELECT 
    sos.serviceid,
    s.service,
    s.category,
    COUNT(*) as times_performed,
    SUM(sos.line_total) as total_revenue
FROM sales_order_services sos
JOIN service s ON sos.serviceid = s.serviceid
GROUP BY sos.serviceid, s.service, s.category
ORDER BY times_performed DESC
LIMIT 10;
```

### 9. Query: Technician Performance

```sql
SELECT 
    technician_id,
    COUNT(*) as services_completed,
    SUM(labor_minutes) as total_minutes,
    SUM(labor_cost) as total_labor_revenue
FROM sales_order_services
WHERE service_status = 'Completed'
GROUP BY technician_id
ORDER BY services_completed DESC;
```

### 10. Calculate Parts Cost for a Service

```sql
-- When creating a service sale, calculate parts cost from service_parts mapping
-- This would typically be done in application logic, but here's a query example:

WITH service_total_parts AS (
    SELECT 
        sp.serviceid,
        SUM(ap.unit_price * sp.quantity) as estimated_parts_cost
    FROM service_parts sp
    LEFT JOIN auto_parts ap ON sp.sku = ap.sku  -- Assumes you add auto_parts.sku
    WHERE sp.serviceid = '48392017'
    GROUP BY sp.serviceid
)
SELECT * FROM service_total_parts;
```

## Important Notes

### Foreign Key References
- `customer_id` field exists but doesn't have FK constraint yet (customer table not created)
- `part_id` field exists but doesn't have FK constraint yet (autoparts table uses different schema)
- When customer/autoparts tables are created, add constraints:
  ```sql
  ALTER TABLE sales_order ADD FOREIGN KEY (customer_id) REFERENCES customer(customer_id);
  ALTER TABLE sales_order_parts ADD FOREIGN KEY (part_id) REFERENCES autoparts(part_id);
  ```

### SKU Mapping
- `service_parts` uses SKU codes from your CSV
- Ensure these SKUs match either `auto_parts.sku` or can be mapped to `autoparts.part_number`
- May need a mapping table if SKUs differ from part numbers

### Order Type
- `'Parts'` - Only direct parts sales
- `'Service'` - Only service sales
- `'Mixed'` - Combination of both

### Best Practices
1. Always populate `order_type` based on line items added
2. Calculate `subtotal` from sum of all line items
3. Calculate `total_amount` as `subtotal + tax`
4. Use transactions when inserting order + line items
5. Service parts are tracked in `service_parts` table - don't duplicate in line items

## Example Transaction (Safe Insert)

```sql
BEGIN;

-- Insert order
INSERT INTO sales_order (customer_id, order_date, invoice_number, payment_method,
                         subtotal, tax, total_amount, order_type, status)
VALUES (12345, CURRENT_TIMESTAMP, 'INV-2025-004', 'Cash',
        45.00, 3.60, 48.60, 'Service', 'Completed')
RETURNING order_id INTO @order_id;

-- Insert service
INSERT INTO sales_order_services (order_id, serviceid, labor_minutes, labor_cost, 
                                   parts_cost, line_total, vehicle_id, technician_id)
SELECT @order_id, '48392017', 30, 45.00, 0.00, 45.00, 77889, 42;

COMMIT;
```

## Files Created
- `create_sales_system.sql` - Table and view creation script
- `load_service_parts.sql` - Service-parts mapping data
- `SALES_SYSTEM_USAGE.md` - This documentation file
