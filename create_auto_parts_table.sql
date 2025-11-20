-- Create auto_parts table
CREATE TABLE auto_parts (
    sku VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    inventory_date DATE,
    vendor VARCHAR(255),
    price DECIMAL(10, 2)
);
