DROP TABLE IF EXISTS ml_delivery_dataset;

CREATE TABLE ml_delivery_dataset AS
SELECT
    order_item_id,
    order_id,

    -- Keep original timestamp for chronological modeling
    order_date,

    -- Target
    is_late_delivery AS target_late_delivery,

    -- Order-time categorical features
    shipping_mode,
    market,
    order_region,
    order_state,
    category_name,
    department_name,
    customer_segment,
    transaction_type,

    -- Order-time product/commercial features
    product_price,
    order_item_product_price,
    order_item_quantity,
    order_item_discount,
    order_item_discount_rate,

    -- Calendar features
    order_year,
    order_month,
    order_day_of_week,

    EXTRACT(DAY FROM order_date)::INTEGER AS order_day,

    CASE
        WHEN EXTRACT(DOW FROM order_date) IN (0, 6)
        THEN 1
        ELSE 0
    END AS is_weekend

FROM stg_supply_chain_orders
WHERE is_delivery_observation = 1;