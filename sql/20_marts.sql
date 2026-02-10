-- Dimension: Customers
DROP TABLE IF EXISTS marts.dim_customers;
CREATE TABLE marts.dim_customers AS
SELECT * FROM stg.customers;

-- Dimension: Sellers
DROP TABLE IF EXISTS marts.dim_sellers;
CREATE TABLE marts.dim_sellers AS
SELECT * FROM stg.sellers;

-- Fact: Deliveries
DROP TABLE IF EXISTS marts.fct_deliveries;
CREATE TABLE marts.fct_deliveries AS
SELECT
    o.order_id,
    o.customer_id,
    oi.seller_id,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date,
    oi.price,
    oi.freight_value,
    -- Lead Time in days
    EXTRACT(DAY FROM (o.order_delivered_customer_date - o.order_purchase_timestamp)) as lead_time_days,
    -- Is Late flag
    CASE 
        WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 
        ELSE 0 
    END as is_late
FROM stg.orders o
JOIN stg.order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL;
