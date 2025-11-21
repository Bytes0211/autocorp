-- Create unified sales system (Option A)
-- This replaces the existing sales table structure with a more flexible approach

-- Drop existing tables if they exist (for clean recreation)
DROP VIEW IF EXISTS v_sales_order_summary CASCADE;
DROP VIEW IF EXISTS v_service_with_parts CASCADE;
DROP TABLE IF EXISTS sales_order_services CASCADE;
DROP TABLE IF EXISTS sales_order_parts CASCADE;
DROP TABLE IF EXISTS sales_order CASCADE;
DROP TABLE IF EXISTS service_parts CASCADE;

-- 1. Create service_parts junction table (maps which parts are used in each service)
CREATE TABLE service_parts (
    service_part_id SERIAL PRIMARY KEY,
    serviceid VARCHAR(50) NOT NULL REFERENCES service(serviceid),
    sku VARCHAR(50) NOT NULL,
    quantity INTEGER DEFAULT 1,
    UNIQUE(serviceid, sku),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Main sales order header table
CREATE TABLE sales_order (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,  -- References customer(customer_id) when customer table exists
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

-- 3. Line items for parts sold directly (not as part of a service)
CREATE TABLE sales_order_parts (
    line_item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sales_order(order_id) ON DELETE CASCADE,
    part_id INTEGER,  -- References autoparts(part_id) when autoparts table exists
    sku VARCHAR(50),
    part_description VARCHAR(200),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    line_total DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Line items for services (labor + associated parts)
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

-- Create indexes for performance
CREATE INDEX idx_service_parts_serviceid ON service_parts(serviceid);
CREATE INDEX idx_service_parts_sku ON service_parts(sku);

CREATE INDEX idx_sales_order_customer ON sales_order(customer_id);
CREATE INDEX idx_sales_order_date ON sales_order(order_date);
CREATE INDEX idx_sales_order_invoice ON sales_order(invoice_number);
CREATE INDEX idx_sales_order_status ON sales_order(status);

CREATE INDEX idx_sales_order_parts_order ON sales_order_parts(order_id);
CREATE INDEX idx_sales_order_parts_part ON sales_order_parts(part_id);
CREATE INDEX idx_sales_order_parts_sku ON sales_order_parts(sku);

CREATE INDEX idx_sales_order_services_order ON sales_order_services(order_id);
CREATE INDEX idx_sales_order_services_service ON sales_order_services(serviceid);
CREATE INDEX idx_sales_order_services_vehicle ON sales_order_services(vehicle_id);
CREATE INDEX idx_sales_order_services_technician ON sales_order_services(technician_id);

-- Create a view for easy querying of complete orders
-- Note: customer join will work once customer table is created
CREATE VIEW v_sales_order_summary AS
SELECT 
    so.order_id,
    so.invoice_number,
    so.order_date,
    so.customer_id,
    so.order_type,
    so.subtotal,
    so.tax,
    so.total_amount,
    so.payment_method,
    so.status,
    COUNT(DISTINCT sop.line_item_id) as parts_line_items,
    COUNT(DISTINCT sos.line_item_id) as service_line_items
FROM sales_order so
LEFT JOIN sales_order_parts sop ON so.order_id = sop.order_id
LEFT JOIN sales_order_services sos ON so.order_id = sos.order_id
GROUP BY so.order_id, so.invoice_number, so.order_date, so.customer_id, 
         so.order_type, so.subtotal, so.tax, so.total_amount, 
         so.payment_method, so.status;

-- Create a view for service details with parts breakdown
CREATE VIEW v_service_with_parts AS
SELECT 
    s.serviceid,
    s.service,
    s.category,
    s.labor_minutes,
    s.labor_cost,
    COUNT(sp.service_part_id) as parts_count,
    SUM(sp.quantity) as total_parts_quantity
FROM service s
LEFT JOIN service_parts sp ON s.serviceid = sp.serviceid
GROUP BY s.serviceid, s.service, s.category, s.labor_minutes, s.labor_cost;
