DROP TABLE IF EXISTS product_category_analysis;

CREATE TABLE product_category_analysis AS
SELECT
    category_name,

    department_name,

    COUNT(*) AS order_items,

    COUNT(DISTINCT order_id) AS orders,

    COUNT(DISTINCT customer_id) AS customers,

    SUM(order_item_quantity) AS units,

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
    ) AS avg_profit_per_order,

    ROUND(
        AVG(order_item_discount_rate)::NUMERIC,
        4
    ) AS avg_discount_rate,

    ROUND(
        AVG(is_late_delivery::NUMERIC) * 100,
        2
    ) AS late_delivery_rate_pct,

    ROUND(
        AVG(shipping_delay_days)::NUMERIC,
        2
    ) AS avg_shipping_delay_days,

    ROUND(
        AVG(order_item_quantity)::NUMERIC,
        2
    ) AS avg_quantity_per_item

FROM stg_supply_chain_orders

WHERE is_delivery_observation = 1

GROUP BY
    category_name,
    department_name

ORDER BY
    total_sales DESC;