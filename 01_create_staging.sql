DROP TABLE IF EXISTS stg_supply_chain_orders;

CREATE TABLE stg_supply_chain_orders AS
SELECT
    order_item_id,
    order_id,
    customer_id,
    order_customer_id,

    order_date,
    shipping_date,

    shipping_mode,

    days_for_shipping_real,
    days_for_shipping_scheduled,

    delivery_status,

    /*
        Original dataset flag.

        Retained for comparison and analysis only.
        It will NOT be used as an ML feature.
    */
    late_delivery_risk,

    /*
        Operational metric:
        difference between actual and scheduled shipping duration.

        Positive  -> exceeded schedule
        Zero      -> exactly on schedule
        Negative  -> shipped faster than scheduled
    */
    days_for_shipping_real
        - days_for_shipping_scheduled
        AS shipping_delay_days,

    /*
        Operational indicator:
        did actual shipping duration exceed scheduled duration?
    */
    CASE
        WHEN days_for_shipping_real > days_for_shipping_scheduled
            THEN 1
        ELSE 0
    END AS exceeded_schedule,

    /*
        ML target:

        1 = order was classified as a late delivery
        0 = advance shipping or shipping on time

        Canceled shipments are therefore not positive late-delivery
        observations.
    */
    CASE
        WHEN delivery_status = 'Late delivery'
            THEN 1
        ELSE 0
    END AS is_late_delivery,

    /*
        Identifies records belonging to the delivery prediction
        population.

        Canceled shipments are excluded from the ML population.
    */
    CASE
        WHEN delivery_status <> 'Shipping canceled'
            THEN 1
        ELSE 0
    END AS is_delivery_observation,

    /*
        Order calendar features
    */
    EXTRACT(YEAR FROM order_date)::INTEGER
        AS order_year,

    EXTRACT(MONTH FROM order_date)::INTEGER
        AS order_month,

    DATE_TRUNC('month', order_date)::DATE
        AS order_month_start,

    TO_CHAR(order_date, 'YYYY-MM')
        AS order_year_month,

    EXTRACT(DOW FROM order_date)::INTEGER
        AS order_day_of_week,

    /*
        Commercial metrics
    */
    category_id,
    category_name,

    product_card_id,
    product_category_id,
    product_name,

    product_price,
    order_item_product_price,

    order_item_quantity,

    order_item_discount,
    order_item_discount_rate,

    /*
        Explicit calculated discount amount.
    */
    order_item_product_price
        * order_item_quantity
        * order_item_discount_rate
        AS calculated_discount_amount,

    sales,
    order_item_total,

    order_profit_per_order,
    order_item_profit_ratio,

    customer_segment,

    department_id,
    department_name,

    market,

    order_city,
    order_country,
    order_region,
    order_state,

    order_status,

    transaction_type

FROM supply_chain_orders;


CREATE INDEX idx_stg_order_date
    ON stg_supply_chain_orders(order_date);

CREATE INDEX idx_stg_customer_id
    ON stg_supply_chain_orders(customer_id);

CREATE INDEX idx_stg_order_id
    ON stg_supply_chain_orders(order_id);

CREATE INDEX idx_stg_late_delivery
    ON stg_supply_chain_orders(is_late_delivery);

CREATE INDEX idx_stg_delivery_observation
    ON stg_supply_chain_orders(is_delivery_observation);

CREATE INDEX idx_stg_category
    ON stg_supply_chain_orders(category_name);

CREATE INDEX idx_stg_market
    ON stg_supply_chain_orders(market);

CREATE INDEX idx_stg_order_month
    ON stg_supply_chain_orders(order_month_start);