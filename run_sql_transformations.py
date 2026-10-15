from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


PROJECT_ROOT = Path(__file__).resolve().parents[1]

load_dotenv(PROJECT_ROOT / ".env")


SQL_FILES = [
    PROJECT_ROOT
    / "sql"
    / "transformations"
    / "01_delivery_performance.sql",

    PROJECT_ROOT
    / "sql"
    / "analysis"
    / "01_delivery_summary.sql",

    PROJECT_ROOT
    / "sql"
    / "analysis"
    / "02_shipping_mode_analysis.sql",

    PROJECT_ROOT
    / "sql"
    / "analysis"
    / "03_monthly_delivery_trends.sql",

    PROJECT_ROOT
    / "sql"
    / "analysis"
    / "04_product_category_analysis.sql",

    PROJECT_ROOT
    / "sql"
    / "analysis"
    / "05_product_analysis.sql",

    PROJECT_ROOT
    / "sql"
    / "analysis"
    / "06_category_delivery_exposure.sql",

    PROJECT_ROOT 
    / "sql" 
    / "analysis" 
    / "07_ml_dataset.sql",

    PROJECT_ROOT 
    / "sql" 
    / "analysis" 
    / "08_monthly_demand_analysis.sql",

    PROJECT_ROOT 
    / "sql" 
    / "views" 
    / "01_create_views.sql",
]


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


def run_sql_file(engine, sql_file):
    print(f"Running: {sql_file.name}")

    with open(sql_file, "r", encoding="utf-8") as file:
        sql = file.read()

    with engine.begin() as connection:
        connection.execute(text(sql))

    print(f"Completed: {sql_file.name}")


def main():
    engine = get_engine()

    for sql_file in SQL_FILES:

        if not sql_file.exists():
            raise FileNotFoundError(
                f"SQL file not found: {sql_file}"
            )

        run_sql_file(engine, sql_file)

    print("\nAll SQL transformations completed successfully.")


if __name__ == "__main__":
    main()