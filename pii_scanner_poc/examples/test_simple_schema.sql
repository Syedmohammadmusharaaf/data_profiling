-- Simple schema - Basic patterns that should have high local efficiency
CREATE TABLE simple_users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(150),
    phone VARCHAR(20)
);

CREATE TABLE simple_orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    order_date DATE,
    total_amount DECIMAL(10,2)
);
