from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "DataCoSupplyChainDataset.csv"
)


REQUIRED_COLUMNS = [
    "Type",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Delivery Status",
    "Late_delivery_risk",
    "Category Id",
    "Category Name",
    "Customer Id",
    "Customer Segment",
    "Department Id",
    "Department Name",
    "Market",
    "Order Customer Id",
    "order date (DateOrders)",
    "Order Id",
    "Order Item Id",
    "Order Item Discount",
    "Order Item Discount Rate",
    "Order Item Product Price",
    "Order Item Profit Ratio",
    "Order Item Quantity",
    "Sales",
    "Order Item Total",
    "Order Profit Per Order",
    "Order Region",
    "Order Status",
    "Product Card Id",
    "Product Category Id",
    "Product Name",
    "Product Price",
    "Product Status",
    "shipping date (DateOrders)",
    "Shipping Mode",
]


def load_data() -> pd.DataFrame:
    return pd.read_csv(
        RAW_FILE,
        encoding="latin1"
    )


def validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    assert not missing_columns, (
        f"Missing required columns: {missing_columns}"
    )


def validate_row_count(df: pd.DataFrame) -> None:
    assert len(df) > 0, "Dataset is empty"


def validate_no_duplicate_rows(df: pd.DataFrame) -> None:
    duplicates = df.duplicated().sum()

    assert duplicates == 0, (
        f"Found {duplicates:,} duplicate rows"
    )


def validate_customer_ids(df: pd.DataFrame) -> None:
    assert (
        df["Customer Id"].notna().all()
    ), "Customer Id contains missing values"

    assert (
        df["Order Customer Id"].notna().all()
    ), "Order Customer Id contains missing values"


def validate_order_ids(df: pd.DataFrame) -> None:
    assert (
        df["Order Id"].notna().all()
    ), "Order Id contains missing values"

    assert (
        df["Order Item Id"].notna().all()
    ), "Order Item Id contains missing values"


def validate_quantities(df: pd.DataFrame) -> None:
    assert (
        df["Order Item Quantity"] > 0
    ).all(), "Quantity contains non-positive values"


def validate_prices(df: pd.DataFrame) -> None:
    assert (
        df["Order Item Product Price"] >= 0
    ).all(), "Product price contains negative values"

    assert (
        df["Product Price"] >= 0
    ).all(), "Product Price contains negative values"


def validate_discount_rate(df: pd.DataFrame) -> None:
    assert (
        df["Order Item Discount Rate"].between(0, 1).all()
    ), "Discount rate contains values outside [0, 1]"


def validate_late_delivery_flag(df: pd.DataFrame) -> None:
    assert set(
        df["Late_delivery_risk"].unique()
    ).issubset({0, 1}), (
        "Late_delivery_risk must contain only 0/1"
    )


def validate_dates(df: pd.DataFrame) -> None:
    order_dates = pd.to_datetime(
        df["order date (DateOrders)"],
        errors="coerce"
    )

    shipping_dates = pd.to_datetime(
        df["shipping date (DateOrders)"],
        errors="coerce"
    )

    assert order_dates.notna().all(), (
        "Invalid order dates found"
    )

    assert shipping_dates.notna().all(), (
        "Invalid shipping dates found"
    )

    assert (
        shipping_dates >= order_dates
    ).all(), (
        "Shipping date occurs before order date"
    )


def validate_shipping_days(df: pd.DataFrame) -> None:
    assert (
        df["Days for shipping (real)"] >= 0
    ).all()

    assert (
        df["Days for shipment (scheduled)"] >= 0
    ).all()


def validate(df: pd.DataFrame) -> None:
    validate_required_columns(df)
    validate_row_count(df)
    validate_no_duplicate_rows(df)
    validate_customer_ids(df)
    validate_order_ids(df)
    validate_quantities(df)
    validate_prices(df)
    validate_discount_rate(df)
    validate_late_delivery_flag(df)
    validate_dates(df)
    validate_shipping_days(df)


def main() -> None:
    print("Loading dataset...")

    df = load_data()

    print(f"Rows loaded: {len(df):,}")

    validate(df)

    print("All validation checks passed.")


if __name__ == "__main__":
    main()