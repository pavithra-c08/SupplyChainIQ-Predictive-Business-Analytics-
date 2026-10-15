DROP TABLE IF EXISTS supply_chain_orders;

CREATE TABLE supply_chain_orders (
    order_item_id BIGINT PRIMARY KEY,
    order_id BIGINT NOT NULL,

    customer_id BIGINT NOT NULL,
    order_customer_id BIGINT NOT NULL,

    order_date TIMESTAMP NOT NULL,
    shipping_date TIMESTAMP NOT NULL,

    shipping_mode VARCHAR(50) NOT NULL,

    days_for_shipping_real INTEGER NOT NULL,
    days_for_shipping_scheduled INTEGER NOT NULL,

    delivery_status VARCHAR(50) NOT NULL,
    late_delivery_risk SMALLINT NOT NULL,

    category_id INTEGER,
    category_name VARCHAR(150),

    product_card_id INTEGER,
    product_category_id INTEGER,
    product_name VARCHAR(255),

    product_price NUMERIC(12, 2),
    order_item_product_price NUMERIC(12, 2),

    order_item_quantity INTEGER NOT NULL,

    order_item_discount NUMERIC(12, 2),
    order_item_discount_rate NUMERIC(8, 6),

    sales NUMERIC(14, 2),
    order_item_total NUMERIC(14, 2),

    order_profit_per_order NUMERIC(14, 2),
    order_item_profit_ratio NUMERIC(8, 6),

    customer_segment VARCHAR(50),

    department_id INTEGER,
    department_name VARCHAR(100),

    market VARCHAR(50),

    order_city VARCHAR(150),
    order_country VARCHAR(100),
    order_region VARCHAR(100),
    order_state VARCHAR(150),

    order_status VARCHAR(50),

    transaction_type VARCHAR(50)
);

CREATE INDEX idx_supply_chain_order_id
    ON supply_chain_orders(order_id);

CREATE INDEX idx_supply_chain_customer_id
    ON supply_chain_orders(customer_id);

CREATE INDEX idx_supply_chain_order_date
    ON supply_chain_orders(order_date);

CREATE INDEX idx_supply_chain_shipping_date
    ON supply_chain_orders(shipping_date);

CREATE INDEX idx_supply_chain_category
    ON supply_chain_orders(category_name);

CREATE INDEX idx_supply_chain_market
    ON supply_chain_orders(market);

CREATE INDEX idx_supply_chain_delivery_status
    ON supply_chain_orders(delivery_status);

CREATE INDEX idx_supply_chain_order_region
    ON supply_chain_orders(order_region);