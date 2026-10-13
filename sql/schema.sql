CREATE DATABASE IF NOT EXISTS retail_analytics;
USE retail_analytics;

CREATE TABLE IF NOT EXISTS customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(120) NOT NULL,
    segment VARCHAR(40) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id VARCHAR(30) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(60) NOT NULL,
    subcategory VARCHAR(60) NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id VARCHAR(30) PRIMARY KEY,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    ship_mode VARCHAR(40) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    country VARCHAR(80) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code INT NULL,
    region VARCHAR(40) NOT NULL,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT PRIMARY KEY,
    order_id VARCHAR(30) NOT NULL,
    product_id VARCHAR(30) NOT NULL,
    sales DECIMAL(12, 2) NOT NULL,
    quantity INT NOT NULL,
    discount DECIMAL(6, 4) NOT NULL,
    profit DECIMAL(12, 2) NOT NULL,
    CONSTRAINT chk_order_item_quantity CHECK (quantity > 0),
    CONSTRAINT chk_order_item_discount CHECK (discount >= 0),
    CONSTRAINT fk_items_order FOREIGN KEY (order_id) REFERENCES orders(order_id),
    CONSTRAINT fk_items_product FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_orders_region ON orders(region);
CREATE INDEX idx_items_product ON order_items(product_id);
