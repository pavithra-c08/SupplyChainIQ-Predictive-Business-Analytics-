import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


load_dotenv()


def get_engine():
    """
    Create a PostgreSQL SQLAlchemy engine.

    URL.create() safely handles special characters
    such as '@' in the database password.
    """

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


def test_staging_table_exists(engine):
    with engine.connect() as connection:
        result = connection.execute(
            text(
                """
                SELECT to_regclass(
                    'public.stg_supply_chain_orders'
                )
                """
            )
        ).scalar_one()

    assert result == "stg_supply_chain_orders"


def test_staging_row_count_matches_source(engine):
    with engine.connect() as connection:
        source_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM supply_chain_orders
                """
            )
        ).scalar_one()

        staging_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                """
            )
        ).scalar_one()

    assert staging_count == source_count


def test_order_item_ids_are_unique(engine):
    with engine.connect() as connection:
        total_count = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                """
            )
        ).scalar_one()

        distinct_count = connection.execute(
            text(
                """
                SELECT COUNT(DISTINCT order_item_id)
                FROM stg_supply_chain_orders
                """
            )
        ).scalar_one()

    assert total_count == distinct_count


def test_is_late_delivery_definition(engine):
    """
    is_late_delivery must be 1 only for
    Delivery Status = 'Late delivery'.
    """

    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE is_late_delivery != CASE
                    WHEN delivery_status = 'Late delivery'
                        THEN 1
                    ELSE 0
                END
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_exceeded_schedule_definition(engine):
    """
    exceeded_schedule must be 1 only when
    actual shipping duration exceeds scheduled duration.
    """

    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE exceeded_schedule != CASE
                    WHEN days_for_shipping_real
                         > days_for_shipping_scheduled
                        THEN 1
                    ELSE 0
                END
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_shipping_delay_calculation(engine):
    """
    shipping_delay_days must equal:

    actual shipping days - scheduled shipping days
    """

    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE shipping_delay_days
                    != (
                        days_for_shipping_real
                        - days_for_shipping_scheduled
                    )
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_delivery_observation_definition(engine):
    """
    Canceled shipments are excluded from the
    delivery prediction population.
    """

    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE is_delivery_observation != CASE
                    WHEN delivery_status <> 'Shipping canceled'
                        THEN 1
                    ELSE 0
                END
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_calendar_features(engine):
    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE order_year
                      != EXTRACT(YEAR FROM order_date)::INTEGER

                   OR order_month
                      != EXTRACT(MONTH FROM order_date)::INTEGER

                   OR order_month_start
                      != DATE_TRUNC(
                           'month',
                           order_date
                       )::DATE
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_late_delivery_flag_contains_only_binary_values(engine):
    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE is_late_delivery NOT IN (0, 1)
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_delivery_observation_flag_contains_only_binary_values(engine):
    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE is_delivery_observation NOT IN (0, 1)
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_exceeded_schedule_flag_contains_only_binary_values(engine):
    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE exceeded_schedule NOT IN (0, 1)
                """
            )
        ).scalar_one()

    assert invalid_rows == 0


def test_canceled_shipments_are_not_late_delivery_observations(engine):
    """
    Every canceled shipment must have:
        is_delivery_observation = 0
        is_late_delivery = 0
    """

    with engine.connect() as connection:
        invalid_rows = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM stg_supply_chain_orders
                WHERE delivery_status = 'Shipping canceled'
                  AND (
                      is_delivery_observation != 0
                      OR is_late_delivery != 0
                  )
                """
            )
        ).scalar_one()

    assert invalid_rows == 0