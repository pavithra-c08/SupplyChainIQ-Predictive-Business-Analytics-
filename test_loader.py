import pandas as pd
import pytest

from src.data.loader import (
    COLUMN_MAPPING,
    prepare_data,
)


def test_column_mapping_is_not_empty():
    assert len(COLUMN_MAPPING) > 0


def test_column_mapping_has_unique_target_names():
    target_columns = list(COLUMN_MAPPING.values())

    assert len(target_columns) == len(set(target_columns))


def test_prepare_data_selects_expected_columns():
    source_data = {
        column: [1]
        for column in COLUMN_MAPPING
    }

    source_data["order date (DateOrders)"] = [
        "2015-01-01 10:00:00"
    ]

    source_data["shipping date (DateOrders)"] = [
        "2015-01-03 10:00:00"
    ]

    df = pd.DataFrame(source_data)

    result = prepare_data(df)

    assert len(result) == 1
    assert len(result.columns) == len(COLUMN_MAPPING)


def test_prepare_data_renames_columns():
    source_data = {
        column: [1]
        for column in COLUMN_MAPPING
    }

    source_data["order date (DateOrders)"] = [
        "2015-01-01 10:00:00"
    ]

    source_data["shipping date (DateOrders)"] = [
        "2015-01-03 10:00:00"
    ]

    df = pd.DataFrame(source_data)

    result = prepare_data(df)

    for target_column in COLUMN_MAPPING.values():
        assert target_column in result.columns


def test_prepare_data_converts_dates():
    source_data = {
        column: [1]
        for column in COLUMN_MAPPING
    }

    source_data["order date (DateOrders)"] = [
        "2015-01-01 10:00:00"
    ]

    source_data["shipping date (DateOrders)"] = [
        "2015-01-03 10:00:00"
    ]

    df = pd.DataFrame(source_data)

    result = prepare_data(df)

    assert pd.api.types.is_datetime64_any_dtype(
        result["order_date"]
    )

    assert pd.api.types.is_datetime64_any_dtype(
        result["shipping_date"]
    )


def test_prepare_data_preserves_row_count():
    source_data = {
        column: [1, 2, 3]
        for column in COLUMN_MAPPING
    }

    source_data["order date (DateOrders)"] = [
        "2015-01-01 10:00:00",
        "2015-01-02 10:00:00",
        "2015-01-03 10:00:00",
    ]

    source_data["shipping date (DateOrders)"] = [
        "2015-01-03 10:00:00",
        "2015-01-04 10:00:00",
        "2015-01-05 10:00:00",
    ]

    df = pd.DataFrame(source_data)

    result = prepare_data(df)

    assert len(result) == 3


def test_prepare_data_rejects_missing_columns():
    source_data = {
        column: [1]
        for column in COLUMN_MAPPING
    }

    source_data.pop("Order Id")

    source_data["order date (DateOrders)"] = [
        "2015-01-01 10:00:00"
    ]

    source_data["shipping date (DateOrders)"] = [
        "2015-01-03 10:00:00"
    ]

    df = pd.DataFrame(source_data)

    with pytest.raises(ValueError, match="Missing source columns"):
        prepare_data(df)


def test_prepare_data_rejects_invalid_dates():
    source_data = {
        column: [1]
        for column in COLUMN_MAPPING
    }

    source_data["order date (DateOrders)"] = [
        "not-a-date"
    ]

    source_data["shipping date (DateOrders)"] = [
        "2015-01-03 10:00:00"
    ]

    df = pd.DataFrame(source_data)

    with pytest.raises(ValueError):
        prepare_data(df)