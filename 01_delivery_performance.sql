DROP TABLE IF EXISTS delivery_performance;

CREATE TABLE delivery_performance AS
SELECT
    shipping_mode,

    market,

    order_region,

    department_name,

    category_name,

    customer_segment,

    COUNT(*) AS order_items,

    COUNT(DISTINCT order_id) AS orders,

    COUNT(DISTINCT customer_id) AS customers,

    SUM(order_item_quantity) AS units,

    ROUND(
        AVG(days_for_shipping_real)::NUMERIC,
        2
    ) AS avg_actual_shipping_days,

    ROUND(
        AVG(days_for_shipping_scheduled)::NUMERIC,
        2
    ) AS avg_scheduled_shipping_days,

    ROUND(
        AVG(shipping_delay_days)::NUMERIC,
        2
    ) AS avg_shipping_delay_days,

    ROUND(
        AVG(exceeded_schedule::NUMERIC) * 100,
        2
    ) AS schedule_exceeded_rate_pct,

    ROUND(
        AVG(is_late_delivery::NUMERIC) * 100,
        2
    ) AS late_delivery_rate_pct,

    ROUND(
        SUM(sales)::NUMERIC,
        2
    ) AS total_sales,

    ROUND(
        SUM(order_profit_per_order)::NUMERIC,
        2
    ) AS total_profit,

    ROUND(
        AVG(order_profit_per_order)::NUMERIC,
        2
    ) AS avg_profit_per_order

FROM stg_supply_chain_orders

GROUP BY
    shipping_mode,
    market,
    order_region,
    department_name,
    category_name,
    customer_segment;