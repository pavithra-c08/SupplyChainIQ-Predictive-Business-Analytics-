import pandas as pd
from scipy import stats


def summarize_monthly_demand(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate descriptive statistics for monthly demand metrics.
    """
    metrics = [
        "orders",
        "units",
        "total_sales",
        "total_profit",
    ]

    return df[metrics].describe().T


def calculate_sales_order_correlation(df: pd.DataFrame) -> float:
    """
    Calculate Pearson correlation between monthly orders and sales.
    """
    return df["orders"].corr(df["total_sales"])


def calculate_profit_sales_correlation(df: pd.DataFrame) -> float:
    """
    Calculate Pearson correlation between monthly sales and profit.
    """
    return df["total_sales"].corr(df["total_profit"])


def monthly_sales_trend_test(df: pd.DataFrame) -> dict:
    """
    Test whether monthly sales show a statistically significant
    linear trend over time.
    """
    ordered = df.sort_values("order_month_start").reset_index(drop=True)

    x = range(len(ordered))
    y = ordered["total_sales"]

    result = stats.linregress(x, y)

    return {
        "slope": result.slope,
        "r_value": result.rvalue,
        "p_value": result.pvalue,
        "r_squared": result.rvalue ** 2,
    }