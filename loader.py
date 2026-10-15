from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "DataCoSupplyChainDataset.csv"
)

SCHEMA_FILE = (
    PROJECT_ROOT
    / "sql"
    / "schema"
    / "01_create_tables.sql"
)


load_dotenv(PROJECT_ROOT / ".env")


COLUMN_MAPPING = {
    "Order Item Id": "order_item_id",
    "Order Id": "order_id",
    "Customer Id": "customer_id",
    "Order Customer Id": "order_customer_id",

    "order date (DateOrders)": "order_date",
    "shipping date (DateOrders)": "shipping_date",

    "Shipping Mode": "shipping_mode",

    "Days for shipping (real)": "days_for_shipping_real",
    "Days for shipment (scheduled)": "days_for_shipping_scheduled",

    "Delivery Status": "delivery_status",
    "Late_delivery_risk": "late_delivery_risk",

    "Category Id": "category_id",
    "Category Name": "category_name",

    "Product Card Id": "product_card_id",
    "Product Category Id": "product_category_id",
    "Product Name": "product_name",

    "Product Price": "product_price",
    "Order Item Product Price": "order_item_product_price",

    "Order Item Quantity": "order_item_quantity",

    "Order Item Discount": "order_item_discount",
    "Order Item Discount Rate": "order_item_discount_rate",

    "Sales": "sales",
    "Order Item Total": "order_item_total",

    "Order Profit Per Order": "order_profit_per_order",
    "Order Item Profit Ratio": "order_item_profit_ratio",

    "Customer Segment": "customer_segment",

    "Department Id": "department_id",
    "Department Name": "department_name",

    "Market": "market",

    "Order City": "order_city",
    "Order Country": "order_country",
    "Order Region": "order_region",
    "Order State": "order_state",

    "Order Status": "order_status",

    "Type": "transaction_type",
}


def get_engine():
    """
    Create a PostgreSQL SQLAlchemy engine.

    URL.create() safely handles special characters such as
    '@' in the database password.
    """

    required_variables = [
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
    ]

    missing = [
        variable
        for variable in required_variables
        if not os.getenv(variable)
    ]

    if missing:
        raise ValueError(
            f"Missing database environment variables: {missing}"
        )

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(url)


def load_raw_data():
    """Load the original DataCo CSV without modifying it."""

    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}"
        )

    return pd.read_csv(
        RAW_FILE,
        encoding="latin1",
    )


def prepare_data(df):
    """
    Select analytical columns, rename them to SQL-friendly names,
    and convert date columns to timestamps.
    """

    missing_columns = [
        column
        for column in COLUMN_MAPPING
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing source columns: {missing_columns}"
        )

    prepared = (
        df[list(COLUMN_MAPPING.keys())]
        .rename(columns=COLUMN_MAPPING)
        .copy()
    )

    prepared["order_date"] = pd.to_datetime(
        prepared["order_date"],
        errors="raise",
    )

    prepared["shipping_date"] = pd.to_datetime(
        prepared["shipping_date"],
        errors="raise",
    )

    return prepared


def create_table(engine):
    """Create the PostgreSQL analytical table."""

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"Schema file not found: {SCHEMA_FILE}"
        )

    with open(SCHEMA_FILE, "r", encoding="utf-8") as file:
        sql = file.read()

    with engine.begin() as connection:
        connection.execute(text(sql))


def load_to_postgres(df, engine):
    """Load prepared data into PostgreSQL."""

    df.to_sql(
        "supply_chain_orders",
        engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )


def verify_load(engine, expected_rows):
    """Verify row count and primary-key uniqueness."""

    with engine.connect() as connection:

        row_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM supply_chain_orders
                """
            )
        ).scalar_one()

        distinct_items = connection.execute(
            text(
                """
                SELECT COUNT(DISTINCT order_item_id)
                FROM supply_chain_orders
                """
            )
        ).scalar_one()

    print(f"Expected rows : {expected_rows:,}")
    print(f"Loaded rows   : {row_count:,}")
    print(f"Unique items  : {distinct_items:,}")

    assert row_count == expected_rows, (
        f"Expected {expected_rows:,} rows, "
        f"found {row_count:,}"
    )

    assert distinct_items == expected_rows, (
        "order_item_id is not unique"
    )

    print("PostgreSQL load verification passed.")


def main():

    print("Loading source dataset...")

    df = load_raw_data()

    print(f"Raw rows: {len(df):,}")

    print("Preparing analytical columns...")

    prepared = prepare_data(df)

    print(f"Prepared rows: {len(prepared):,}")
    print(f"Prepared columns: {len(prepared.columns)}")

    print("Connecting to PostgreSQL...")

    engine = get_engine()

    print("Creating table...")

    create_table(engine)

    print("Loading data...")

    load_to_postgres(prepared, engine)

    print("Verifying load...")

    verify_load(
        engine,
        expected_rows=len(prepared),
    )

    print("Done.")


if __name__ == "__main__":
    main()