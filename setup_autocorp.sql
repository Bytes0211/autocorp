-- Create autocorp schema
CREATE SCHEMA IF NOT EXISTS autocorp;

-- Set search path to use the schema
SET search_path TO autocorp;

-- Create customer table (1.1 million customers)
CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(200) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address VARCHAR(300),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create autoparts table (10k parts)
CREATE TABLE autoparts (
    part_id SERIAL PRIMARY KEY,
    part_number VARCHAR(50) UNIQUE NOT NULL,
    part_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    reorder_level INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sales table (1.5 million transactions with FK to customer)
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(customer_id),
    part_id INTEGER NOT NULL REFERENCES autoparts(part_id),
    sale_date TIMESTAMP NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    invoice_number VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50) NOT NULL
);

-- Create maintenance table (3 million transactions with FK to customer)
CREATE TABLE maintenance (
    maintenance_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customer(customer_id),
    part_id INTEGER NOT NULL REFERENCES autoparts(part_id),
    maintenance_date TIMESTAMP NOT NULL,
    vehicle_id INTEGER NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    labor_hours DECIMAL(5, 2) NOT NULL,
    labor_cost DECIMAL(10, 2) NOT NULL,
    parts_cost DECIMAL(10, 2) NOT NULL,
    total_cost DECIMAL(12, 2) NOT NULL,
    technician_id INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX idx_customer_email ON customer(email);
CREATE INDEX idx_customer_created ON customer(created_at);

CREATE INDEX idx_sales_customer_id ON sales(customer_id);
CREATE INDEX idx_sales_part_id ON sales(part_id);
CREATE INDEX idx_sales_date ON sales(sale_date);

CREATE INDEX idx_maintenance_customer_id ON maintenance(customer_id);
CREATE INDEX idx_maintenance_part_id ON maintenance(part_id);
CREATE INDEX idx_maintenance_date ON maintenance(maintenance_date);
CREATE INDEX idx_maintenance_vehicle ON maintenance(vehicle_id);

-- Insert 1.1 million customers
INSERT INTO customer (first_name, last_name, email, phone, address, city, state, zip_code)
SELECT 
    CASE (RANDOM() * 20)::INTEGER
        WHEN 0 THEN 'John' WHEN 1 THEN 'Jane' WHEN 2 THEN 'Michael' WHEN 3 THEN 'Sarah'
        WHEN 4 THEN 'David' WHEN 5 THEN 'Emily' WHEN 6 THEN 'Robert' WHEN 7 THEN 'Lisa'
        WHEN 8 THEN 'James' WHEN 9 THEN 'Mary' WHEN 10 THEN 'William' WHEN 11 THEN 'Jennifer'
        WHEN 12 THEN 'Richard' WHEN 13 THEN 'Linda' WHEN 14 THEN 'Thomas' WHEN 15 THEN 'Patricia'
        WHEN 16 THEN 'Charles' WHEN 17 THEN 'Barbara' WHEN 18 THEN 'Daniel' ELSE 'Susan'
    END,
    CASE (RANDOM() * 20)::INTEGER
        WHEN 0 THEN 'Smith' WHEN 1 THEN 'Johnson' WHEN 2 THEN 'Williams' WHEN 3 THEN 'Brown'
        WHEN 4 THEN 'Jones' WHEN 5 THEN 'Garcia' WHEN 6 THEN 'Miller' WHEN 7 THEN 'Davis'
        WHEN 8 THEN 'Rodriguez' WHEN 9 THEN 'Martinez' WHEN 10 THEN 'Hernandez' WHEN 11 THEN 'Lopez'
        WHEN 12 THEN 'Gonzalez' WHEN 13 THEN 'Wilson' WHEN 14 THEN 'Anderson' WHEN 15 THEN 'Thomas'
        WHEN 16 THEN 'Taylor' WHEN 17 THEN 'Moore' WHEN 18 THEN 'Jackson' ELSE 'Martin'
    END,
    'customer' || i || '@email.com',
    '555-' || LPAD((RANDOM() * 9999999)::INTEGER::TEXT, 7, '0'),
    (RANDOM() * 9999 + 1)::INTEGER || ' Main Street',
    CASE (RANDOM() * 10)::INTEGER
        WHEN 0 THEN 'New York' WHEN 1 THEN 'Los Angeles' WHEN 2 THEN 'Chicago'
        WHEN 3 THEN 'Houston' WHEN 4 THEN 'Phoenix' WHEN 5 THEN 'Philadelphia'
        WHEN 6 THEN 'San Antonio' WHEN 7 THEN 'San Diego' WHEN 8 THEN 'Dallas'
        ELSE 'Austin'
    END,
    CASE (RANDOM() * 10)::INTEGER
        WHEN 0 THEN 'NY' WHEN 1 THEN 'CA' WHEN 2 THEN 'IL' WHEN 3 THEN 'TX'
        WHEN 4 THEN 'AZ' WHEN 5 THEN 'PA' WHEN 6 THEN 'TX' WHEN 7 THEN 'CA'
        WHEN 8 THEN 'TX' ELSE 'TX'
    END,
    LPAD((RANDOM() * 99999)::INTEGER::TEXT, 5, '0')
FROM generate_series(1, 1100000) AS i;

-- Insert 10,000 autoparts
INSERT INTO autoparts (part_number, part_name, category, manufacturer, unit_price, stock_quantity, reorder_level)
SELECT 
    'PN-' || LPAD(i::TEXT, 6, '0'),
    CASE (i % 20)
        WHEN 0 THEN 'Oil Filter'
        WHEN 1 THEN 'Air Filter'
        WHEN 2 THEN 'Brake Pad Set'
        WHEN 3 THEN 'Spark Plug'
        WHEN 4 THEN 'Wiper Blade'
        WHEN 5 THEN 'Battery'
        WHEN 6 THEN 'Alternator'
        WHEN 7 THEN 'Starter Motor'
        WHEN 8 THEN 'Radiator'
        WHEN 9 THEN 'Fuel Pump'
        WHEN 10 THEN 'Water Pump'
        WHEN 11 THEN 'Timing Belt'
        WHEN 12 THEN 'Brake Rotor'
        WHEN 13 THEN 'Shock Absorber'
        WHEN 14 THEN 'Strut Assembly'
        WHEN 15 THEN 'CV Joint'
        WHEN 16 THEN 'Catalytic Converter'
        WHEN 17 THEN 'Muffler'
        WHEN 18 THEN 'Headlight Assembly'
        ELSE 'Tail Light'
    END || ' Model-' || (i % 100),
    CASE (i % 8)
        WHEN 0 THEN 'Engine'
        WHEN 1 THEN 'Brakes'
        WHEN 2 THEN 'Electrical'
        WHEN 3 THEN 'Suspension'
        WHEN 4 THEN 'Exhaust'
        WHEN 5 THEN 'Filters'
        WHEN 6 THEN 'Cooling'
        ELSE 'Lighting'
    END,
    CASE (i % 10)
        WHEN 0 THEN 'Bosch'
        WHEN 1 THEN 'ACDelco'
        WHEN 2 THEN 'Denso'
        WHEN 3 THEN 'Motorcraft'
        WHEN 4 THEN 'NGK'
        WHEN 5 THEN 'Delphi'
        WHEN 6 THEN 'Continental'
        WHEN 7 THEN 'Moog'
        WHEN 8 THEN 'Monroe'
        ELSE 'Wagner'
    END,
    (RANDOM() * 500 + 10)::DECIMAL(10, 2),
    (RANDOM() * 500 + 10)::INTEGER,
    (RANDOM() * 50 + 5)::INTEGER
FROM generate_series(1, 10000) AS i;

-- Insert 1.5 million sales transactions (with duplicate customer_ids as FK)
INSERT INTO sales (customer_id, part_id, sale_date, quantity, unit_price, total_amount, invoice_number, payment_method)
SELECT 
    (RANDOM() * 1099999 + 1)::INTEGER,  -- Random customer_id (creates duplicates)
    (RANDOM() * 9999 + 1)::INTEGER,      -- Random part_id
    TIMESTAMP '2020-01-01' + (RANDOM() * (TIMESTAMP '2024-12-31' - TIMESTAMP '2020-01-01')),
    (RANDOM() * 10 + 1)::INTEGER,
    (RANDOM() * 500 + 10)::DECIMAL(10, 2),
    (RANDOM() * 10 + 1)::INTEGER * (RANDOM() * 500 + 10)::DECIMAL(10, 2),
    'INV-' || LPAD(i::TEXT, 10, '0'),
    CASE (RANDOM() * 4)::INTEGER
        WHEN 0 THEN 'Cash'
        WHEN 1 THEN 'Credit Card'
        WHEN 2 THEN 'Debit Card'
        ELSE 'Bank Transfer'
    END
FROM generate_series(1, 1500000) AS i;

-- Insert 3 million maintenance transactions (with duplicate customer_ids as FK)
INSERT INTO maintenance (customer_id, part_id, maintenance_date, vehicle_id, service_type, labor_hours, labor_cost, parts_cost, total_cost, technician_id, status)
SELECT 
    (RANDOM() * 1099999 + 1)::INTEGER,  -- Random customer_id (creates duplicates)
    (RANDOM() * 9999 + 1)::INTEGER,      -- Random part_id
    TIMESTAMP '2020-01-01' + (RANDOM() * (TIMESTAMP '2024-12-31' - TIMESTAMP '2020-01-01')),
    (RANDOM() * 100000 + 1)::INTEGER,
    CASE (RANDOM() * 10)::INTEGER
        WHEN 0 THEN 'Oil Change'
        WHEN 1 THEN 'Brake Service'
        WHEN 2 THEN 'Tire Rotation'
        WHEN 3 THEN 'Engine Tune-up'
        WHEN 4 THEN 'Transmission Service'
        WHEN 5 THEN 'Coolant Flush'
        WHEN 6 THEN 'Belt Replacement'
        WHEN 7 THEN 'Battery Replacement'
        WHEN 8 THEN 'Suspension Repair'
        ELSE 'Electrical Repair'
    END,
    (RANDOM() * 8 + 0.5)::DECIMAL(5, 2),
    (RANDOM() * 8 + 0.5)::DECIMAL(5, 2) * 85.00,
    (RANDOM() * 500 + 10)::DECIMAL(10, 2),
    ((RANDOM() * 8 + 0.5)::DECIMAL(5, 2) * 85.00) + (RANDOM() * 500 + 10)::DECIMAL(10, 2),
    (RANDOM() * 50 + 1)::INTEGER,
    CASE (RANDOM() * 3)::INTEGER
        WHEN 0 THEN 'Completed'
        WHEN 1 THEN 'In Progress'
        ELSE 'Scheduled'
    END
FROM generate_series(1, 3000000) AS i;

-- Display summary statistics
SELECT 
    'customer' as table_name,
    COUNT(*) as row_count
FROM customer
UNION ALL
SELECT 
    'autoparts' as table_name,
    COUNT(*) as row_count
FROM autoparts
UNION ALL
SELECT 
    'sales' as table_name,
    COUNT(*) as row_count
FROM sales
UNION ALL
SELECT 
    'maintenance' as table_name,
    COUNT(*) as row_count
FROM maintenance;
