-- KPI: Delivery Performance by State
CREATE OR REPLACE VIEW marts.kpi_delivery_performance_by_state AS
SELECT
    c.customer_state,
    COUNT(f.order_id) as total_orders,
    AVG(f.is_late) as late_rate,
    AVG(f.lead_time_days) as avg_lead_time,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY f.lead_time_days) as p90_lead_time
FROM marts.fct_deliveries f
JOIN marts.dim_customers c ON f.customer_id = c.customer_id
GROUP BY 1;

-- KPI: Freight Analysis by State
CREATE OR REPLACE VIEW marts.kpi_freight_by_state AS
SELECT
    c.customer_state,
    AVG(f.freight_value) as avg_freight,
    SUM(f.freight_value) as total_freight
FROM marts.fct_deliveries f
JOIN marts.dim_customers c ON f.customer_id = c.customer_id
GROUP BY 1;

-- KPI: Freight Analysis by Seller
CREATE OR REPLACE VIEW marts.kpi_freight_by_seller AS
SELECT
    f.seller_id,
    s.seller_state,
    AVG(f.freight_value) as avg_freight,
    COUNT(f.order_id) as total_orders
FROM marts.fct_deliveries f
JOIN marts.dim_sellers s ON f.seller_id = s.seller_id
GROUP BY 1, 2;
