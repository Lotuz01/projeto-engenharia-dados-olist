-- Staging Customers
DROP TABLE IF EXISTS stg.customers;
CREATE TABLE stg.customers AS
SELECT DISTINCT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    LOWER(customer_city) as customer_city,
    UPPER(customer_state) as customer_state
FROM raw.customers;

-- Staging Sellers
DROP TABLE IF EXISTS stg.sellers;
CREATE TABLE stg.sellers AS
SELECT DISTINCT
    seller_id,
    seller_zip_code_prefix,
    LOWER(seller_city) as seller_city,
    UPPER(seller_state) as seller_state
FROM raw.sellers;

-- Staging Orders
DROP TABLE IF EXISTS stg.orders;
CREATE TABLE stg.orders AS
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp,
    order_approved_at,
    order_delivered_carrier_date,
    order_delivered_customer_date,
    order_estimated_delivery_date
FROM raw.orders
WHERE order_id IS NOT NULL;

-- Staging Order Items
DROP TABLE IF EXISTS stg.order_items;
CREATE TABLE stg.order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,
    shipping_limit_date,
    price,
    freight_value
FROM raw.order_items
WHERE order_id IS NOT NULL;
