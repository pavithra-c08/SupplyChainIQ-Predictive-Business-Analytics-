from pathlib import Path
import os

import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    average_precision_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
    OrdinalEncoder,
)
from sklearn.ensemble import HistGradientBoostingClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(PROJECT_ROOT / ".env")


def get_engine():
    """Create a PostgreSQL SQLAlchemy engine."""

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
        database=os.getenv("DB_NAME"),
    )

    return create_engine(url)


def load_ml_dataset(engine):
    """Load the leakage-controlled ML dataset."""

    query = """
        SELECT *
        FROM ml_delivery_dataset
        ORDER BY order_date, order_id, order_item_id
    """

    return pd.read_sql(text(query), engine)


def time_based_split(
    df: pd.DataFrame,
    train_ratio: float = 0.8,
):
    """
    Split chronologically using a timestamp cutoff.

    All observations before the cutoff are training data.
    Observations at or after the cutoff are test data.
    """

    if df.empty:
        raise ValueError("Input dataframe is empty.")

    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1.")

    df = df.copy()

    df["order_date"] = pd.to_datetime(df["order_date"])

    df = df.sort_values(
        ["order_date", "order_id", "order_item_id"]
    ).reset_index(drop=True)

    cutoff_index = int(len(df) * train_ratio)
    cutoff_date = df.iloc[cutoff_index]["order_date"]

    train_df = df[df["order_date"] < cutoff_date].copy()
    test_df = df[df["order_date"] >= cutoff_date].copy()

    if train_df.empty or test_df.empty:
        raise ValueError("Train or test split is empty.")

    assert train_df["order_date"].max() < test_df["order_date"].min()

    return train_df, test_df


NUMERICAL_FEATURES = [
    "product_price",
    "order_item_product_price",
    "order_item_quantity",
    "order_item_discount",
    "order_item_discount_rate",
    "order_year",
    "order_month",
    "order_day_of_week",
    "order_day",
    "is_weekend",
]


CATEGORICAL_FEATURES = [
    "shipping_mode",
    "market",
    "order_region",
    "order_state",
    "category_name",
    "department_name",
    "customer_segment",
    "transaction_type",
]


def build_preprocessor():
    """Build preprocessing pipeline for Logistic Regression."""

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "onehot",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=True,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                NUMERICAL_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def build_tree_preprocessor():
    """Build preprocessing pipeline for HistGradientBoosting."""

    numerical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    categorical_pipeline = Pipeline(
        steps=[
            (
                "imputer",
                SimpleImputer(strategy="most_frequent"),
            ),
            (
                "ordinal",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        transformers=[
            (
                "numerical",
                numerical_pipeline,
                NUMERICAL_FEATURES,
            ),
            (
                "categorical",
                categorical_pipeline,
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def build_logistic_regression_model():
    """Build the baseline Logistic Regression pipeline."""

    preprocessor = build_preprocessor()

    model = LogisticRegression(
        max_iter=1000,
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def build_gradient_boosting_model():
    """Build the HistGradientBoosting classification pipeline."""

    preprocessor = build_tree_preprocessor()

    model = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.08,
        max_leaf_nodes=31,
        l2_regularization=1.0,
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def evaluate_model(model, X_test, y_test):
    """Evaluate classification performance."""

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]

    metrics = {
        "roc_auc": roc_auc_score(
            y_test,
            probabilities,
        ),
        "pr_auc": average_precision_score(
            y_test,
            probabilities,
        ),
        "f1": f1_score(
            y_test,
            predictions,
        ),
        "precision": precision_score(
            y_test,
            predictions,
        ),
        "recall": recall_score(
            y_test,
            predictions,
        ),
    }

    print("\nModel Performance")
    print("=================")

    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    print(f"PR-AUC:    {metrics['pr_auc']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")

    print("\nConfusion Matrix")
    print("================")

    print(
        confusion_matrix(
            y_test,
            predictions,
        )
    )

    print("\nClassification Report")
    print("====================")

    print(
        classification_report(
            y_test,
            predictions,
            digits=4,
        )
    )

    return metrics

def evaluate_thresholds(model, X_test, y_test):
    """
    Evaluate classification performance across multiple probability
    thresholds.
    """

    probabilities = model.predict_proba(X_test)[:, 1]

    thresholds = [
        0.30,
        0.35,
        0.40,
        0.45,
        0.50,
        0.55,
        0.60,
        0.65,
        0.70,
    ]

    rows = []

    for threshold in thresholds:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        rows.append(
            {
                "threshold": threshold,
                "precision": precision_score(
                    y_test,
                    predictions,
                    zero_division=0,
                ),
                "recall": recall_score(
                    y_test,
                    predictions,
                    zero_division=0,
                ),
                "f1": f1_score(
                    y_test,
                    predictions,
                    zero_division=0,
                ),
            }
        )

    results = pd.DataFrame(rows)

    print("\nThreshold Analysis")
    print("==================")

    print(
        results.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    best_row = results.loc[
        results["f1"].idxmax()
    ]

    print("\nBest F1 Threshold")
    print("=================")

    print(
        f"Threshold: {best_row['threshold']:.2f}"
    )

    print(
        f"Precision: {best_row['precision']:.4f}"
    )

    print(
        f"Recall:    {best_row['recall']:.4f}"
    )

    print(
        f"F1:        {best_row['f1']:.4f}"
    )

    return results

def show_logistic_feature_importance(model, top_n=15):
    """
    Display the strongest positive and negative Logistic Regression
    coefficients after preprocessing.
    """

    preprocessor = model.named_steps["preprocessor"]
    classifier = model.named_steps["model"]

    feature_names = preprocessor.get_feature_names_out()
    coefficients = classifier.coef_[0]

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "coefficient": coefficients,
        }
    )

    importance["abs_coefficient"] = (
        importance["coefficient"].abs()
    )

    positive = (
        importance[
            importance["coefficient"] > 0
        ]
        .sort_values(
            "coefficient",
            ascending=False,
        )
        .head(top_n)
    )

    negative = (
        importance[
            importance["coefficient"] < 0
        ]
        .sort_values(
            "coefficient",
            ascending=True,
        )
        .head(top_n)
    )

    print("\nTop Features Associated With Higher Late-Delivery Probability")
    print("==============================================================")

    print(
        positive[
            ["feature", "coefficient"]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print("\nTop Features Associated With Lower Late-Delivery Probability")
    print("===============================================================")

    print(
        negative[
            ["feature", "coefficient"]
        ].to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    return importance


def main():
    engine = get_engine()

    df = load_ml_dataset(engine)

    print(f"Dataset shape: {df.shape}")

    train_df, test_df = time_based_split(df)

    X_train = train_df[
        NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    ]

    y_train = train_df["target_late_delivery"]

    X_test = test_df[
        NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    ]

    y_test = test_df["target_late_delivery"]

    print(f"Train rows: {len(train_df):,}")
    print(f"Test rows:  {len(test_df):,}")

    print(
        f"Train late rate: "
        f"{y_train.mean() * 100:.2f}%"
    )

    print(
        f"Test late rate: "
        f"{y_test.mean() * 100:.2f}%"
    )

    # ---------------------------------------------------------
    # Logistic Regression
    # ---------------------------------------------------------

    print("\nTraining Logistic Regression...")

    logistic_model = build_logistic_regression_model()

    logistic_model.fit(
        X_train,
        y_train,
    )

    print("\nLogistic Regression Results")

    logistic_metrics = evaluate_model(
        logistic_model,
        X_test,
        y_test,
    )

    threshold_results = evaluate_thresholds(
        logistic_model,
        X_test,
        y_test,
    )

    feature_importance = show_logistic_feature_importance(
        logistic_model
    )

    # ---------------------------------------------------------
    # HistGradientBoosting
    # ---------------------------------------------------------

    print("\nTraining HistGradientBoosting...")

    gradient_boosting_model = build_gradient_boosting_model()

    gradient_boosting_model.fit(
        X_train,
        y_train,
    )

    print("\nHistGradientBoosting Results")

    gradient_boosting_metrics = evaluate_model(
        gradient_boosting_model,
        X_test,
        y_test,
    )

    # ---------------------------------------------------------
    # Model Comparison
    # ---------------------------------------------------------

    print("\nModel Comparison")
    print("================")

    comparison = pd.DataFrame(
        [
            {
                "model": "Logistic Regression",
                **logistic_metrics,
            },
            {
                "model": "HistGradientBoosting",
                **gradient_boosting_metrics,
            },
        ]
    )

    print(
        comparison.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )


if __name__ == "__main__":
    main()