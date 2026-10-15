DROP VIEW IF EXISTS vw_delivery_performance;
DROP VIEW IF EXISTS vw_monthly_demand;
DROP VIEW IF EXISTS vw_category_performance;

CREATE VIEW vw_delivery_performance AS
SELECT
    shipping_mode,
    market,
    order_region,
    COUNT(*) AS order_items,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(AVG(days_for_shipping_real)::NUMERIC, 2) AS avg_actual_shipping_days,
    ROUND(AVG(days_for_shipping_scheduled)::NUMERIC, 2) AS avg_scheduled_shipping_days,
    ROUND(AVG(shipping_delay_days)::NUMERIC, 2) AS avg_shipping_delay_days,
    ROUND(AVG(is_late_delivery::NUMERIC) * 100, 2) AS late_delivery_rate_pct,
    ROUND(SUM(sales)::NUMERIC, 2) AS total_sales,
    ROUND(SUM(order_profit_per_order)::NUMERIC, 2) AS total_profit
FROM stg_supply_chain_orders
WHERE is_delivery_observation = 1
GROUP BY
    shipping_mode,
    market,
    order_region;


CREATE VIEW vw_monthly_demand AS
SELECT
    order_month_start,
    order_year,
    order_month,
    COUNT(*) AS order_items,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(order_item_quantity) AS units,
    ROUND(SUM(sales)::NUMERIC, 2) AS total_sales,
    ROUND(SUM(order_profit_per_order)::NUMERIC, 2) AS total_profit
FROM stg_supply_chain_orders
GROUP BY
    order_month_start,
    order_year,
    order_month;


CREATE VIEW vw_category_performance AS
SELECT
    category_name,
    department_name,
    COUNT(*) AS order_items,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(order_item_quantity) AS units,
    ROUND(SUM(sales)::NUMERIC, 2) AS total_sales,
    ROUND(SUM(order_profit_per_order)::NUMERIC, 2) AS total_profit,
    ROUND(AVG(is_late_delivery::NUMERIC) * 100, 2)
        AS late_delivery_rate_pct
FROM stg_supply_chain_orders
WHERE is_delivery_observation = 1
GROUP BY
    category_name,
    department_name;