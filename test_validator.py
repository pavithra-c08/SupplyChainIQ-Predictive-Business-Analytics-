import pandas as pd
import pytest

from src.data.validator import (
    validate_required_columns,
    validate_row_count,
    validate_no_duplicate_rows,
    validate_customer_ids,
    validate_order_ids,
    validate_quantities,
    validate_prices,
    validate_discount_rate,
    validate_late_delivery_flag,
    validate_dates,
    validate_shipping_days,
)


@pytest.fixture
def valid_data():
    return pd.DataFrame({
        "Type": ["DEBIT", "TRANSFER"],
        "Days for shipping (real)": [2, 4],
        "Days for shipment (scheduled)": [2, 3],
        "Delivery Status": ["Advance shipping", "Late delivery"],
        "Late_delivery_risk": [0, 1],
        "Category Id": [1, 2],
        "Category Name": ["Category A", "Category B"],
        "Customer Id": [101, 102],
        "Customer Segment": ["Consumer", "Corporate"],
        "Department Id": [1, 2],
        "Department Name": ["Dept A", "Dept B"],
        "Market": ["USCA", "Europe"],
        "Order Customer Id": [101, 102],
        "order date (DateOrders)": [
            "2015-01-01 10:00:00",
            "2015-01-02 10:00:00",
        ],
        "Order Id": [1001, 1002],
        "Order Item Id": [1, 2],
        "Order Item Discount": [10.0, 5.0],
        "Order Item Discount Rate": [0.10, 0.05],
        "Order Item Product Price": [100.0, 200.0],
        "Order Item Profit Ratio": [0.20, 0.15],
        "Order Item Quantity": [1, 2],
        "Sales": [90.0, 380.0],
        "Order Item Total": [90.0, 380.0],
        "Order Profit Per Order": [18.0, 57.0],
        "Order Region": ["Region A", "Region B"],
        "Order Status": ["COMPLETE", "PENDING"],
        "Product Card Id": [1, 2],
        "Product Category Id": [1, 2],
        "Product Name": ["Product A", "Product B"],
        "Product Price": [100.0, 200.0],
        "Product Status": [0, 0],
        "shipping date (DateOrders)": [
            "2015-01-03 10:00:00",
            "2015-01-06 10:00:00",
        ],
        "Shipping Mode": ["Standard Class", "Second Class"],
    })


def test_required_columns(valid_data):
    validate_required_columns(valid_data)


def test_row_count(valid_data):
    validate_row_count(valid_data)


def test_no_duplicate_rows(valid_data):
    validate_no_duplicate_rows(valid_data)


def test_customer_ids(valid_data):
    validate_customer_ids(valid_data)


def test_order_ids(valid_data):
    validate_order_ids(valid_data)


def test_quantities(valid_data):
    validate_quantities(valid_data)


def test_prices(valid_data):
    validate_prices(valid_data)


def test_discount_rate(valid_data):
    validate_discount_rate(valid_data)


def test_late_delivery_flag(valid_data):
    validate_late_delivery_flag(valid_data)


def test_dates(valid_data):
    validate_dates(valid_data)


def test_shipping_days(valid_data):
    validate_shipping_days(valid_data)


def test_negative_quantity_rejected(valid_data):
    valid_data.loc[0, "Order Item Quantity"] = -1

    with pytest.raises(AssertionError):
        validate_quantities(valid_data)


def test_negative_price_rejected(valid_data):
    valid_data.loc[0, "Order Item Product Price"] = -10

    with pytest.raises(AssertionError):
        validate_prices(valid_data)


def test_invalid_discount_rate_rejected(valid_data):
    valid_data.loc[0, "Order Item Discount Rate"] = 1.5

    with pytest.raises(AssertionError):
        validate_discount_rate(valid_data)


def test_invalid_late_delivery_flag_rejected(valid_data):
    valid_data.loc[0, "Late_delivery_risk"] = 2

    with pytest.raises(AssertionError):
        validate_late_delivery_flag(valid_data)


def test_shipping_before_order_rejected(valid_data):
    valid_data.loc[0, "shipping date (DateOrders)"] = "2014-12-31 10:00:00"

    with pytest.raises(AssertionError):
        validate_dates(valid_data)


def test_negative_shipping_days_rejected(valid_data):
    valid_data.loc[0, "Days for shipping (real)"] = -1

    with pytest.raises(AssertionError):
        validate_shipping_days(valid_data)