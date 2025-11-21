# AutoCorp Database - Current Status

**Last Updated:** 2025-11-21  
**Database:** `autocorp`  
**User:** `scotton`

---

## Database Tables Summary

| Table Name | Rows | Columns | Description |
|------------|------|---------|-------------|
| `auto_parts` | 400 | 6 | Auto parts inventory |
| `customers` | 1,149 | 10 | Customer information (randomly selected) |
| `service` | 110 | 5 | Service catalog with labor costs |
| `service_parts` | 1,074 | 5 | Service-to-parts mapping (which parts each service needs) |
| `sales_order` | 0 | 13 | Order/invoice headers |
| `sales_order_parts` | 0 | 9 | Line items for direct parts sales |
| `sales_order_services` | 0 | 13 | Line items for service sales |

**Total Tables:** 7  
**Total Data Rows:** 2,733

---

## Table Schemas

### 1. `customers`
Primary customer table with randomly selected 1,149 customers from 1.2M available.

```sql
CREATE TABLE customers (
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
```

**Indexes:**
- Primary key on `customer_id`
- Unique index on `email`
- Index on `email` (`idx_customers_email`)

### 2. `auto_parts`
Auto parts inventory catalog.

**Columns:**
- `part_id` (Primary Key)
- `sku` (Unique identifier)
- `name`
- `category`
- `price`
- `created_at`

### 3. `service`
Service catalog with labor rates.

```sql
CREATE TABLE service (
    serviceid VARCHAR(50) PRIMARY KEY,
    service VARCHAR(200),
    category VARCHAR(50),
    labor_minutes INTEGER,
    labor_cost MONEY
);
```

**Categories:**
- Engine & Powertrain
- Transmission & Drivetrain
- Tires & Wheels
- Brakes
- Cooling System
- Electrical System
- HVAC
- Suspension & Steering
- General Preventive Maintenance
- Exhaust & Emissions
- Fluids & Filters

### 4. `service_parts`
Junction table linking services to required parts.

```sql
CREATE TABLE service_parts (
    service_part_id SERIAL PRIMARY KEY,
    serviceid VARCHAR(50) NOT NULL REFERENCES service(serviceid),
    sku VARCHAR(50) NOT NULL,
    quantity INTEGER DEFAULT 1,
    UNIQUE(serviceid, sku),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Statistics:**
- Average parts per service: ~9.8 parts
- Service with most parts: serviceid `92038482` (27 parts)

### 5. `sales_order`
Main order/invoice header table.

```sql
CREATE TABLE sales_order (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    payment_method VARCHAR(50),
    subtotal DECIMAL(12, 2),
    tax DECIMAL(12, 2) DEFAULT 0.00,
    total_amount DECIMAL(12, 2) NOT NULL,
    order_type VARCHAR(20) CHECK (order_type IN ('Parts', 'Service', 'Mixed')),
    status VARCHAR(50) DEFAULT 'Completed',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Foreign Keys:**
- `customer_id` → `customers(customer_id)`

**Order Types:**
- `Parts` - Direct parts sales only
- `Service` - Service sales only
- `Mixed` - Combination of parts and services

### 6. `sales_order_parts`
Line items for direct parts sales (not as part of a service).

```sql
CREATE TABLE sales_order_parts (
    line_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
    part_id INTEGER,
    sku VARCHAR(50),
    part_description VARCHAR(200),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. `sales_order_services`
Line items for service sales (includes labor and parts).

```sql
CREATE TABLE sales_order_services (
    line_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
    serviceid VARCHAR(50) NOT NULL REFERENCES service(serviceid),
    service_description VARCHAR(200),
    quantity INTEGER DEFAULT 1 CHECK (quantity > 0),
    labor_minutes INTEGER NOT NULL,
    labor_cost DECIMAL(10, 2) NOT NULL,
    parts_cost DECIMAL(10, 2) DEFAULT 0.00,
    line_total DECIMAL(12, 2) NOT NULL,
    vehicle_id INTEGER,
    technician_id INTEGER,
    service_status VARCHAR(50) DEFAULT 'Completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Views

### `v_sales_order_summary`
Summarizes orders with line item counts.

### `v_service_with_parts`
Shows services with their parts counts.

---

## Data Sources

| Source File | Rows Available | Rows Loaded | Table | Selection Method |
|-------------|----------------|-------------|-------|------------------|
| `customers.csv` | 1,200,000 | 1,149 | `customers` | Random sampling |
| `auto-service.csv` | 110 | 110 | `service` | All rows |
| `service-parts.csv` | 1,074 | 1,074 | `service_parts` | All rows |
| `auto-parts.csv` | ~40,000 | 400 | `auto_parts` | Previous load |

---

## Setup Scripts

### Customer Upload
**Script:** `upload_customers.py`
- Randomly selects 1,150 customers from 1.2M available
- Uses reservoir sampling for memory efficiency
- Handles duplicates via UNIQUE constraint on email
- Loads: 1,149 customers (1 duplicate skipped)

**Usage:**
```bash
.venv/bin/python upload_customers.py
```

### Service Table
**Script:** `create_service_table.sql`
- Creates service catalog table

**Data Load:** `insert_service_data.sql` (auto-generated)

### Sales System
**Script:** `create_sales_system.sql`
- Creates unified sales order system
- Creates service_parts junction table
- Creates views

**Data Load:** `load_service_parts.sql` (auto-generated)

---

## Key Relationships

```
customers (1,149)
    ↓
sales_order (0) ← invoice/order header
    ↓
    ├─→ sales_order_parts (0) ← direct parts sales
    │       ↓
    │   auto_parts (400) via sku or part_id
    │
    └─→ sales_order_services (0) ← service sales
            ↓
        service (110)
            ↓
        service_parts (1,074) ← parts needed for service
            ↓
        auto_parts (400) via sku
```

---

## Sample Queries

### Get customer with orders
```sql
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    c.email,
    COUNT(so.order_id) as total_orders,
    SUM(so.total_amount) as total_spent
FROM customers c
LEFT JOIN sales_order so ON c.customer_id = so.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
ORDER BY total_spent DESC NULLS LAST;
```

### Get parts needed for a service
```sql
SELECT 
    s.service,
    s.category,
    s.labor_cost,
    sp.sku,
    sp.quantity
FROM service s
JOIN service_parts sp ON s.serviceid = sp.serviceid
WHERE s.serviceid = '48392017';
```

### Customer count by state
```sql
SELECT state, COUNT(*) as customer_count
FROM customers
GROUP BY state
ORDER BY customer_count DESC
LIMIT 10;
```

---

## Next Steps

1. **Generate sample sales data** - Populate sales_order tables with test transactions
2. **Add autoparts FK** - Link sales_order_parts.part_id to auto_parts.part_id
3. **Create reporting views** - Revenue reports, popular services, etc.
4. **Add vehicle table** - Track customer vehicles
5. **Add technician table** - Track technicians performing services

---

## Documentation Files

- `SALES_SYSTEM_USAGE.md` - Complete usage guide with 10+ query examples
- `DATABASE_STATUS.md` - This file
- `create_sales_system.sql` - Sales system creation script
- `create_service_table.sql` - Service table creation
- `upload_customers.py` - Customer data upload script
