DROP TABLE IF EXISTS monthly_demand_analysis;

CREATE TABLE monthly_demand_analysis AS
SELECT
    order_month_start,
    order_year,
    order_month,

    COUNT(*) AS order_items,
    COUNT(DISTINCT order_id) AS orders,
    COUNT(DISTINCT customer_id) AS customers,
    SUM(order_item_quantity) AS units,

    ROUND(SUM(sales)::NUMERIC, 2) AS total_sales,
    ROUND(SUM(order_profit_per_order)::NUMERIC, 2) AS total_profit,

    ROUND(
        AVG(order_item_quantity)::NUMERIC,
        2
    ) AS avg_units_per_item,

    ROUND(
        AVG(sales)::NUMERIC,
        2
    ) AS avg_sales_per_item

FROM stg_supply_chain_orders
GROUP BY
    order_month_start,
    order_year,
    order_month
ORDER BY
    order_month_start;