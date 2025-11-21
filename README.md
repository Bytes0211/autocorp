# AutoCorp Database Project

A PostgreSQL database system for managing auto parts sales and service operations.

## Project Overview

This project implements a unified sales system that handles:
- **Auto parts inventory** (400 parts)
- **Service catalog** (110 services across 11 categories)
- **Customer management** (1,149 customers)
- **Sales orders** (supports parts sales, service sales, and mixed orders)
- **Service-parts relationships** (1,074 mappings)

## Database Structure

**Database Name:** `autocorp`  
**Total Tables:** 7  
**Total Data Rows:** 2,733

### Tables
- `auto_parts` - Parts inventory (400 rows)
- `customers` - Customer information (1,149 rows)
- `service` - Service catalog (110 rows)
- `service_parts` - Service-to-parts mapping (1,074 rows)
- `sales_order` - Order headers (0 rows - ready for data)
- `sales_order_parts` - Parts line items (0 rows - ready for data)
- `sales_order_services` - Service line items (0 rows - ready for data)

## Project Files

### Source Data (CSV)
- `auto-parts.csv` - Auto parts inventory source data
- `auto-service.csv` - Service catalog source data
- `service-parts.csv` - Service-to-parts mapping source data
- `customers.csv` - Customer data source (1.2M records, 1,149 loaded)

### Database Scripts (SQL)
- `create_auto_parts_table.sql` - Creates auto_parts table
- `create_service_table.sql` - Creates service table
- `create_sales_system.sql` - Creates complete sales system (orders, line items, views)

### Python Scripts
- `upload_customers.py` - Randomly selects and uploads 1,150 customers from CSV
  - **Usage:** `.venv/bin/python upload_customers.py`
  - **Features:** Random sampling, duplicate handling, progress reporting

### Documentation
- `README.md` - This file
- `DATABASE_STATUS.md` - Complete database schema and statistics
- `SALES_SYSTEM_USAGE.md` - Usage guide with 10+ SQL query examples
- `developer-approach.md` - Development notes and approach

### Configuration
- `requirements.txt` - Python dependencies
- `Makefile` - Project automation commands
- `.gitignore` - Git exclusions
- `.venv/` - Python virtual environment

## Setup Instructions

### Prerequisites
- PostgreSQL installed and running
- Python 3.12+ with venv support
- Database `autocorp` created

### Initial Setup

1. **Create virtual environment and install dependencies:**
   ```bash
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   .venv/bin/pip install psycopg2-binary
   ```

2. **Create database tables:**
   ```bash
   # Auto parts table
   psql -U scotton -d autocorp -f create_auto_parts_table.sql
   
   # Service table
   psql -U scotton -d autocorp -f create_service_table.sql
   
   # Sales system (orders, line items, views)
   psql -U scotton -d autocorp -f create_sales_system.sql
   ```

3. **Load data:**
   ```bash
   # Load customers (randomly selects 1,150 from 1.2M)
   .venv/bin/python upload_customers.py
   
   # Load services and service-parts data
   # (SQL INSERT scripts would be generated from CSVs)
   ```

## Key Features

### Unified Sales System (Option A)
- Single invoice can contain parts and/or services
- Three order types: `Parts`, `Service`, `Mixed`
- Automatic tracking of service-parts relationships
- Foreign key integrity with customers

### Service-Parts Mapping
- Each service linked to required parts via `service_parts` table
- Supports multiple parts per service
- Quantity tracking for each part-service relationship

### Customer Management
- Random sampling from large dataset (1.2M → 1,149)
- Email uniqueness enforced
- Geographic distribution across 59 states

## Common Operations

### View Database Status
```bash
psql -U scotton -d autocorp -c "
  SELECT 'auto_parts' as table_name, COUNT(*) FROM auto_parts 
  UNION ALL SELECT 'customers', COUNT(*) FROM customers 
  UNION ALL SELECT 'service', COUNT(*) FROM service 
  UNION ALL SELECT 'service_parts', COUNT(*) FROM service_parts
  ORDER BY table_name;"
```

### Query Example: Get Service with Parts
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

### Create a Sample Order
```sql
-- Insert order header
INSERT INTO sales_order (customer_id, order_date, invoice_number, 
                         payment_method, total_amount, order_type)
VALUES (1, CURRENT_TIMESTAMP, 'INV-2025-001', 'Credit Card', 
        145.80, 'Service')
RETURNING order_id;

-- Insert service line item
INSERT INTO sales_order_services (order_id, serviceid, labor_minutes, 
                                   labor_cost, parts_cost, line_total)
VALUES (1, '48392017', 30, 45.00, 90.00, 135.00);
```

## Service Categories

The system includes 110 services across these categories:
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

## Data Statistics

- **Average parts per service:** ~9.8 parts
- **Service with most parts:** ID `92038482` (27 parts)
- **Customer geographic spread:** 59 different states
- **Total service-parts relationships:** 1,074

## Development Notes

See `developer-approach.md` for development approach and design decisions.

## Documentation

For detailed usage examples and query patterns, see:
- `SALES_SYSTEM_USAGE.md` - Complete usage guide
- `DATABASE_STATUS.md` - Schema details and statistics

## Project Status

**Current Phase:** Database setup complete, ready for application development

**Ready for:**
- Sales transaction generation
- Reporting and analytics
- Application integration
- Additional feature development

**Next Steps:**
1. Generate sample sales data
2. Create reporting views
3. Add vehicle tracking table
4. Add technician management table
5. Build application layer

## License

Internal project - All rights reserved

## Contact

Project Owner: scotton
