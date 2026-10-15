import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import pandas as pd


load_dotenv()


def get_engine():
    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(url)


@pytest.fixture(scope="module")
def engine():
    return get_engine()


@pytest.mark.parametrize(
    "table_name",
    [
        "delivery_performance",
        "delivery_summary",
        "shipping_mode_analysis",
        "monthly_delivery_trends",
    ],
)
def test_analysis_table_exists(engine, table_name):

    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT to_regclass(
                    :table_name
                )
                """
            ),
            {"table_name": f"public.{table_name}"},
        ).scalar_one()

    assert result == table_name


def test_delivery_summary_has_rows(engine):

    with engine.connect() as connection:
        count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM delivery_summary
                """
            )
        ).scalar_one()

    assert count == 1


def test_delivery_summary_excludes_canceled_shipments(engine):

    with engine.connect() as connection:
        count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM delivery_summary
                WHERE late_delivery_rate_pct < 0
                   OR late_delivery_rate_pct > 100
                """
            )
        ).scalar_one()

    assert count == 0


def test_shipping_mode_analysis_has_expected_modes(engine):

    with engine.connect() as connection:
        modes = connection.execute(
            text(
                """
                SELECT shipping_mode
                FROM shipping_mode_analysis
                ORDER BY shipping_mode
                """
            )
        ).scalars().all()

    assert set(modes) == {
        "First Class",
        "Second Class",
        "Same Day",
        "Standard Class",
    }


def test_late_delivery_rates_are_valid(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM shipping_mode_analysis
                WHERE late_delivery_rate_pct < 0
                   OR late_delivery_rate_pct > 100
                """
            )
        ).scalar_one()

    assert invalid == 0


def test_monthly_trends_are_chronological(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT
                        order_month_start,
                        LAG(order_month_start)
                        OVER (
                            ORDER BY order_month_start
                        ) AS previous_month
                    FROM monthly_delivery_trends
                ) x
                WHERE previous_month IS NOT NULL
                  AND order_month_start < previous_month
                """
            )
        ).scalar_one()

    assert invalid == 0


def test_monthly_trends_have_positive_orders(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM monthly_delivery_trends
                WHERE orders <= 0
                   OR order_items <= 0
                """
            )
        ).scalar_one()

    assert invalid == 0

def test_product_category_analysis_has_rows(engine):

    with engine.connect() as connection:
        count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM product_category_analysis
                """
            )
        ).scalar_one()

    assert count > 0


def test_product_analysis_has_rows(engine):

    with engine.connect() as connection:
        count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM product_analysis
                """
            )
        ).scalar_one()

    assert count > 0


def test_category_late_rates_are_valid(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM product_category_analysis
                WHERE late_delivery_rate_pct < 0
                   OR late_delivery_rate_pct > 100
                """
            )
        ).scalar_one()

    assert invalid == 0


def test_product_late_rates_are_valid(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM product_analysis
                WHERE late_delivery_rate_pct < 0
                   OR late_delivery_rate_pct > 100
                """
            )
        ).scalar_one()

    assert invalid == 0


def test_product_category_sales_are_non_negative(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM product_category_analysis
                WHERE total_sales < 0
                """
            )
        ).scalar_one()

    assert invalid == 0

def test_category_delivery_exposure_has_rows(engine):

    with engine.connect() as connection:
        count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM category_delivery_exposure
                """
            )
        ).scalar_one()

    assert count > 0


def test_category_delivery_exposure_is_non_negative(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM category_delivery_exposure
                WHERE total_sales < 0
                   OR total_profit < 0
                   OR sales_exposure_to_late_delivery < 0
                   OR profit_exposure_to_late_delivery < 0
                """
            )
        ).scalar_one()

    assert invalid == 0


def test_category_delivery_exposure_rate_is_valid(engine):

    with engine.connect() as connection:
        invalid = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM category_delivery_exposure
                WHERE late_delivery_rate_pct < 0
                   OR late_delivery_rate_pct > 100
                """
            )
        ).scalar_one()

    assert invalid == 0

def test_ml_dataset_has_rows(engine):
    result = pd.read_sql(
        "SELECT COUNT(*) AS count FROM ml_delivery_dataset",
        engine
    )

    assert result.loc[0, "count"] > 0


def test_ml_target_is_binary(engine):
    result = pd.read_sql(
        """
        SELECT DISTINCT target_late_delivery
        FROM ml_delivery_dataset
        ORDER BY target_late_delivery
        """,
        engine
    )

    assert set(result["target_late_delivery"]) <= {0, 1}


def test_ml_dataset_has_no_target_leakage_columns(engine):
    columns = pd.read_sql(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'ml_delivery_dataset'
        """,
        engine
    )["column_name"].tolist()

    forbidden = {
        "shipping_date",
        "days_for_shipping_real",
        "shipping_delay_days",
        "exceeded_schedule",
        "delivery_status",
        "late_delivery_risk",
        "is_late_delivery",
    }

    assert forbidden.isdisjoint(set(columns))


def test_ml_dataset_has_required_features(engine):
    columns = pd.read_sql(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'ml_delivery_dataset'
        """,
        engine
    )["column_name"].tolist()

    required = {
        "target_late_delivery",
        "shipping_mode",
        "market",
        "order_region",
        "category_name",
        "department_name",
        "customer_segment",
        "transaction_type",
        "product_price",
        "order_item_quantity",
        "order_item_discount_rate",
        "order_year",
        "order_month",
        "order_day_of_week",
    }

    assert required.issubset(set(columns))

def test_monthly_demand_analysis_has_rows(engine):
    result = pd.read_sql(
        """
        SELECT COUNT(*) AS count
        FROM monthly_demand_analysis
        """,
        engine,
    )

    assert result.loc[0, "count"] > 0


def test_monthly_demand_analysis_is_chronological(engine):
    result = pd.read_sql(
        """
        SELECT order_month_start
        FROM monthly_demand_analysis
        ORDER BY order_month_start
        """,
        engine,
    )

    dates = pd.to_datetime(result["order_month_start"])

    assert dates.is_monotonic_increasing


def test_monthly_demand_analysis_has_positive_orders(engine):
    result = pd.read_sql(
        """
        SELECT MIN(orders) AS min_orders
        FROM monthly_demand_analysis
        """,
        engine,
    )

    assert result.loc[0, "min_orders"] > 0


def test_monthly_demand_analysis_has_nonnegative_sales(engine):
    result = pd.read_sql(
        """
        SELECT MIN(total_sales) AS min_sales
        FROM monthly_demand_analysis
        """,
        engine,
    )

    assert result.loc[0, "min_sales"] >= 0

def test_monthly_demand_analysis_covers_multiple_months(engine):
    result = pd.read_sql(
        """
        SELECT COUNT(*) AS month_count
        FROM monthly_demand_analysis
        """,
        engine,
    )
    assert result.loc[0, "month_count"] > 12


def test_monthly_demand_analysis_has_positive_profit_values(engine):
    result = pd.read_sql(
        """
        SELECT MIN(total_profit) AS min_profit
        FROM monthly_demand_analysis
        """,
        engine,
    )
    assert result.loc[0, "min_profit"] >= 0


def test_monthly_demand_analysis_has_positive_units(engine):
    result = pd.read_sql(
        """
        SELECT MIN(units) AS min_units
        FROM monthly_demand_analysis
        """,
        engine,
    )
    assert result.loc[0, "min_units"] > 0