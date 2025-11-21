-- Create sales table
CREATE TABLE sales (
    transactionid VARCHAR(50) PRIMARY KEY,
    sku VARCHAR(50) REFERENCES auto_parts(sku),
    serviceid VARCHAR(50) REFERENCES service(serviceid),
    trans_type VARCHAR(50),
    sales_date DATE,
    price DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    total DECIMAL(10, 2),
    storeid VARCHAR(50),
    customer_name VARCHAR(255),
    customer_phone VARCHAR(20),
    customer_email VARCHAR(255)
);
