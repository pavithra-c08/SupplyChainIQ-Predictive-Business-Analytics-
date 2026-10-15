DROP TABLE IF EXISTS category_delivery_exposure;

CREATE TABLE category_delivery_exposure AS
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
        AVG(is_late_delivery::NUMERIC) * 100,
        2
    ) AS late_delivery_rate_pct,

    ROUND(
        (
            SUM(sales)
            * AVG(is_late_delivery::NUMERIC)
        )::NUMERIC,
        2
    ) AS sales_exposure_to_late_delivery,

    ROUND(
        (
            SUM(order_profit_per_order)
            * AVG(is_late_delivery::NUMERIC)
        )::NUMERIC,
        2
    ) AS profit_exposure_to_late_delivery

FROM stg_supply_chain_orders

WHERE is_delivery_observation = 1

GROUP BY
    category_name,
    department_name

ORDER BY
    sales_exposure_to_late_delivery DESC;