import pandas as pd

from src.statistics.demand_statistics import (
    summarize_monthly_demand,
    calculate_sales_order_correlation,
    calculate_profit_sales_correlation,
    monthly_sales_trend_test,
)


def test_summarize_monthly_demand():
    df = pd.DataFrame({
        "orders": [100, 120, 110],
        "units": [200, 240, 220],
        "total_sales": [1000, 1200, 1100],
        "total_profit": [100, 120, 110],
    })

    result = summarize_monthly_demand(df)

    assert "orders" in result.index
    assert "total_sales" in result.index


def test_sales_order_correlation():
    df = pd.DataFrame({
        "orders": [1, 2, 3, 4],
        "total_sales": [10, 20, 30, 40],
    })

    result = calculate_sales_order_correlation(df)

    assert round(result, 5) == 1.0


def test_profit_sales_correlation():
    df = pd.DataFrame({
        "total_sales": [10, 20, 30, 40],
        "total_profit": [1, 2, 3, 4],
    })

    result = calculate_profit_sales_correlation(df)

    assert round(result, 5) == 1.0


def test_monthly_sales_trend_test():
    df = pd.DataFrame({
        "order_month_start": pd.date_range(
            "2020-01-01",
            periods=5,
            freq="MS",
        ),
        "total_sales": [100, 200, 300, 400, 500],
    })

    result = monthly_sales_trend_test(df)

    assert result["slope"] > 0
    assert result["r_squared"] > 0.99