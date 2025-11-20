-- Create service table
CREATE TABLE service (
    serviceid VARCHAR(50) PRIMARY KEY,
    service VARCHAR(200),
    category VARCHAR(50),
    labor_minutes INTEGER,
    labor_cost MONEY
);
