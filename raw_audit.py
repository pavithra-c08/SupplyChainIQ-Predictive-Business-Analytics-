from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "DataCoSupplyChainDataset.csv"


def load_raw_data() -> pd.DataFrame:
    """Load the raw DataCo supply-chain dataset."""
    return pd.read_csv(
        RAW_FILE,
        encoding="latin1"
    )


def audit_dataset(df: pd.DataFrame) -> None:
    """Print a structured audit of the raw dataset."""

    print("=" * 80)
    print("DATASET OVERVIEW")
    print("=" * 80)

    print(f"File: {RAW_FILE}")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    print("\n" + "=" * 80)
    print("COLUMN NAMES")
    print("=" * 80)

    for i, column in enumerate(df.columns, start=1):
        print(f"{i:3}. {column}")

    print("\n" + "=" * 80)
    print("DATA TYPES")
    print("=" * 80)

    print(df.dtypes)

    print("\n" + "=" * 80)
    print("MISSING VALUES")
    print("=" * 80)

    missing = (
        df.isna()
        .sum()
        .to_frame("missing_count")
    )

    missing["missing_percentage"] = (
        missing["missing_count"] / len(df) * 100
    )

    missing = missing[
        missing["missing_count"] > 0
    ].sort_values(
        "missing_count",
        ascending=False
    )

    if missing.empty:
        print("No missing values found.")
    else:
        print(missing)

    print("\n" + "=" * 80)
    print("DUPLICATE ROWS")
    print("=" * 80)

    print(f"Duplicate rows: {df.duplicated().sum():,}")

    print("\n" + "=" * 80)
    print("NUMERIC SUMMARY")
    print("=" * 80)

    print(df.describe(include="number").T)

    print("\n" + "=" * 80)
    print("CATEGORICAL SUMMARY")
    print("=" * 80)

    categorical_columns = df.select_dtypes(
        include=["object","string"]
    ).columns

    for column in categorical_columns:
        print(f"\n--- {column} ---")
        print(f"Unique values: {df[column].nunique(dropna=False):,}")

        print(
            df[column]
            .value_counts(dropna=False)
            .head(10)
        )


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {RAW_FILE}"
        )

    df = load_raw_data()
    audit_dataset(df)


if __name__ == "__main__":
    main()