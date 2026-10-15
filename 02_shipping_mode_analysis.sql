DROP TABLE IF EXISTS shipping_mode_analysis;

CREATE TABLE shipping_mode_analysis AS
SELECT
    shipping_mode,

    COUNT(*) AS order_items,

    COUNT(DISTINCT order_id) AS orders,

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
        AVG(is_late_delivery::NUMERIC) * 100,
        2
    ) AS late_delivery_rate_pct,

    ROUND(
        AVG(exceeded_schedule::NUMERIC) * 100,
        2
    ) AS schedule_exceeded_rate_pct,

    ROUND(
        SUM(sales)::NUMERIC,
        2
    ) AS total_sales,

    ROUND(
        SUM(order_profit_per_order)::NUMERIC,
        2
    ) AS total_profit

FROM stg_supply_chain_orders

WHERE is_delivery_observation = 1

GROUP BY
    shipping_mode

ORDER BY
    late_delivery_rate_pct DESC;