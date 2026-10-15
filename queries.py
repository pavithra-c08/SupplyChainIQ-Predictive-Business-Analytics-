DELIVERY_SUMMARY_QUERY = """
SELECT
    total_order_items,
    total_orders,
    total_customers,
    total_units,
    avg_actual_shipping_days,
    avg_scheduled_shipping_days,
    avg_shipping_delay_days,
    late_delivery_rate_pct,
    total_sales,
    total_profit,
    avg_profit_per_order_item
FROM delivery_summary;
"""


MONTHLY_DEMAND_QUERY = """
SELECT
    order_month_start,
    orders,
    units,
    total_sales,
    total_profit
FROM monthly_demand_analysis
ORDER BY order_month_start;
"""


SHIPPING_MODE_QUERY = """
SELECT *
FROM shipping_mode_analysis
ORDER BY late_delivery_rate_pct DESC;
"""


CATEGORY_QUERY = """
SELECT *
FROM category_delivery_exposure
ORDER BY total_sales DESC;
"""