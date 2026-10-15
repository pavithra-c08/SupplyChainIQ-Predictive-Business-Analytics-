import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, URL
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"

RESULTS_DIR.mkdir(exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")

db_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(db_url)


exports = {
    "delivery_summary.csv": """
        SELECT *
        FROM delivery_summary
    """,

    "shipping_mode_analysis.csv": """
        SELECT *
        FROM shipping_mode_analysis
        ORDER BY late_delivery_rate_pct DESC
    """,

    "monthly_demand_analysis.csv": """
        SELECT *
        FROM monthly_demand_analysis
        ORDER BY order_month_start
    """,

    "category_delivery_exposure.csv": """
        SELECT *
        FROM category_delivery_exposure
        ORDER BY sales_exposure_to_late_delivery DESC
    """,

    "ml_dataset_summary.csv": """
        SELECT
            COUNT(*) AS observations,
            SUM(target_late_delivery) AS late_deliveries,
            ROUND(
                AVG(target_late_delivery::numeric) * 100,
                2
            ) AS late_delivery_rate_pct
        FROM ml_delivery_dataset
    """,
}


for filename, query in exports.items():
    df = pd.read_sql(query, engine)
    output_path = RESULTS_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"Exported: {output_path}")


print("All result exports completed.")