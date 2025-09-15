-- Medium complexity schema - Mix of common and specialized fields
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(150),
    phone VARCHAR(20),
    ssn CHAR(9),
    department VARCHAR(100),
    salary DECIMAL(10,2),
    hire_date DATE
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    company_name VARCHAR(100),
    contact_person VARCHAR(100),
    email VARCHAR(150),
    phone VARCHAR(20),
    billing_address TEXT,
    credit_limit DECIMAL(15,2)
);

CREATE TABLE transactions (
    txn_id BIGINT PRIMARY KEY,
    customer_id INT,
    transaction_date TIMESTAMP,
    amount DECIMAL(12,2),
    payment_method VARCHAR(50),
    merchant_category VARCHAR(100)
);
