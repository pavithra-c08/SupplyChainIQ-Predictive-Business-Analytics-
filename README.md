# SupplyChainIQ — Global Supply Chain & Logistics Analytics

SupplyChainIQ is an end-to-end supply chain analytics project built around the **DataCo SMART Supply Chain for Big Data Analysis** dataset. It combines PostgreSQL, SQL, Python, statistical analysis, and machine learning to analyze logistics performance, demand patterns, product categories, profitability, and late-delivery risk.

The project is designed as a reproducible analytics workflow rather than a collection of isolated notebooks.

## Project Highlights

- **180,519** raw order-item records analyzed
- **172,765** observable order items used for delivery analysis
- **62,897** distinct orders in the observable delivery dataset
- **20,261** distinct customers in the observable delivery dataset
- **$35.21M** total sales across observable order items
- **$3.81M** total profit across observable order items
- **57.29%** late-delivery rate among observable order items
- Chronological train/test split for realistic late-delivery prediction
- Logistic Regression and HistGradientBoosting model comparison
- Reusable SQL analysis tables and PostgreSQL views
- Automated validation and analytical tests
- Reproducible Jupyter notebook

## Objectives

The project answers the following business questions:

1. How reliable is delivery performance?
2. Which shipping modes have the highest late-delivery rates?
3. How do orders, units, sales, and profit change over time?
4. Which product categories generate the most sales and profit?
5. Which categories have the greatest exposure to late deliveries?
6. Are there meaningful differences in delivery performance across markets and regions?
7. Can late deliveries be predicted using information available at order time?
8. How should the prediction threshold change depending on operational priorities?

## Dataset

**DataCo SMART SUPPLY CHAIN FOR BIG DATA ANALYSIS**

Source: Mendeley Data

Dataset page: https://data.mendeley.com/datasets/8gx2fvg2k6/5

The dataset is used under its applicable **CC BY 4.0** license.

The raw dataset is intentionally excluded from this repository through `.gitignore`.

### Data scope

The dataset contains order, product, customer-segment, geographic, transaction, sales, and shipping information.

The analytical layer intentionally excludes unnecessary customer PII such as:

- Customer email
- Customer password
- Customer first/last name
- Customer street
- Customer ZIP code

# Architecture

```text
                         DataCo Raw Dataset
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   Raw Audit     │
                         │   Validation    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │   PostgreSQL    │
                         │  Analytical DB  │
                         └────────┬────────┘
                                  │
                     ┌────────────┴────────────┐
                     ▼                         ▼
              Staging Layer              Analysis Layer
                     │                         │
                     │              ┌──────────┴──────────┐
                     │              │                     │
                     ▼              ▼                     ▼
              Delivery Logic    Demand Analysis     Category Analysis
                     │
                     ▼
              ML Dataset
                     │
                     ▼
          Chronological Train/Test Split
                     │
             ┌───────┴────────┐
             ▼                ▼
      Logistic Regression   HistGradientBoosting
             │
             ▼
       Model Evaluation
             │
             ▼
     Threshold Analysis
             │
             ▼
       Business Insights
```

# Repository Structure

```text
supply-chain-analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── sql/
│   ├── schema/
│   ├── staging/
│   ├── transformations/
│   ├── analysis/
│   └── views/
│
├── src/
│   ├── data/
│   │   ├── raw_audit.py
│   │   ├── validator.py
│   │   └── loader.py
│   ├── analysis/
│   │   └── queries.py
│   ├── statistics/
│   │   └── demand_statistics.py
│   └── modeling/
│       └── late_delivery_model.py
│
├── notebooks/
│   └── supply_chain_analysis.ipynb
│
├── results/
│   ├── delivery_summary.csv
│   ├── shipping_mode_analysis.csv
│   ├── monthly_demand_analysis.csv
│   ├── category_delivery_exposure.csv
│   └── ml_dataset_summary.csv
│
├── scripts/
│   ├── run_sql_transformations.py
│   └── export_results.py
│
├── tests/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

# Tech Stack

| Area | Technology |
|---|---|
| Database | PostgreSQL |
| SQL | PostgreSQL SQL |
| Data processing | Python, Pandas, NumPy |
| Statistics | SciPy |
| Machine Learning | Scikit-learn |
| Visualization | Matplotlib, Seaborn |
| Database connectivity | SQLAlchemy, psycopg2 |
| Configuration | python-dotenv |
| Notebook | Jupyter |
| Testing | Pytest |

# Analytical Workflow

## 1. Data Audit and Validation

The raw dataset is inspected before loading into PostgreSQL.

The audit covers:

- Row and column counts
- Data types
- Missing values
- Duplicate records
- Numeric distributions
- Categorical distributions
- Date fields
- Delivery-related fields

The raw dataset contains:

- **180,519 rows**
- **53 columns**
- **0 duplicate rows**

Notable missingness includes:

- Product Description: 100%
- Order Zipcode: approximately 86.24%
- Customer Lname: 8 rows
- Customer Zipcode: 3 rows

The analytical layer does not require the highly incomplete or unnecessary PII fields.

## 2. PostgreSQL Data Layer

The data is loaded into PostgreSQL using SQLAlchemy.

### Staging

The staging layer creates analytical fields including:

- `shipping_delay_days`
- `exceeded_schedule`
- `is_late_delivery`
- `is_delivery_observation`
- `order_year`
- `order_month`
- `order_month_start`
- `order_year_month`
- `order_day_of_week`
- `calculated_discount_amount`

### Delivery classification

```text
Late delivery      → is_late_delivery = 1
Advance shipping   → is_late_delivery = 0
Shipping on time   → is_late_delivery = 0
Shipping canceled  → excluded from delivery-observation analysis
```

Shipping-cancelled records are retained in the staging layer but excluded from delivery performance and late-delivery modeling.

# Business Analysis

## Delivery Performance

Among observable order items:

| Metric | Result |
|---|---:|
| Order items | 172,765 |
| Orders | 62,897 |
| Customers | 20,261 |
| Units | 367,591 |
| Average actual shipping time | 3.50 days |
| Average scheduled shipping time | 2.93 days |
| Average delay | 0.57 days |
| Late-delivery rate | 57.29% |
| Sales | $35,214,428.98 |
| Profit | $3,806,420.63 |
| Average profit per order item | $22.03 |

The late-delivery rate indicates that delivery reliability is a significant operational issue in the dataset.

## Shipping Mode Analysis

| Shipping Mode | Late Delivery Rate |
|---|---:|
| First Class | 100.00% |
| Second Class | 79.83% |
| Same Day | 47.93% |
| Standard Class | 39.77% |

These figures should **not** be interpreted as proof that expedited shipping is inherently worse.

Expedited services have shorter promised delivery windows. Therefore, relatively small delays can result in a late-delivery classification.

## Demand and Sales Trends

Monthly order volume and sales remain relatively stable across most of the observation period.

The final months of the dataset show a structural change in the relationship between order counts and units.

| Month | Orders | Units |
|---|---:|---:|
| Sep 2017 | 1,723 | 10,502 |
| Oct 2017 | 2,101 | 2,490 |
| Nov 2017 | 2,055 | 2,055 |
| Dec 2017 | 2,124 | 2,124 |
| Jan 2018 | 2,123 | 2,123 |

These final months should therefore be interpreted cautiously rather than being treated as straightforward evidence of a demand collapse.

## Product and Category Analysis

Product categories are evaluated using:

- Order volume
- Units
- Sales
- Profit
- Late-delivery rate
- Sales exposure to late deliveries
- Profit exposure to late deliveries

The major product categories have relatively similar late-delivery rates, generally close to the overall dataset level.

High-volume categories have greater commercial exposure because the same late-delivery rate applies to a larger sales base.

### Exposure definition

```text
Sales Exposure =
Total Category Sales × Late Delivery Rate
```

This is an **exposure metric**, not an estimate of sales actually lost because of late delivery.

## Geographic Analysis

Late-delivery rates are relatively close across the major markets.

| Market | Late Delivery Rate |
|---|---:|
| Europe | 57.69% |
| USCA | 57.41% |
| Pacific Asia | 57.38% |
| LATAM | 56.87% |
| Africa | 56.84% |

Broad market classification alone is therefore not a strong differentiator of delivery risk.

# Machine Learning — Late Delivery Prediction

## Objective

Predict whether an observable order item will be delivered late using information available at order time.

### Target

```text
target_late_delivery
```

### ML dataset

```text
172,765 observations
98,977 late deliveries
57.29% late-delivery rate
```

## Leakage Prevention

The model does not use information that becomes available after the delivery outcome.

Excluded fields include:

- `shipping_date`
- `days_for_shipping_real`
- `shipping_delay_days`
- `exceeded_schedule`
- `delivery_status`
- `late_delivery_risk`
- `is_late_delivery`

`order_date` is retained only for chronological splitting and derived calendar features.

## Features

### Numerical features

- Product price
- Order-item product price
- Order-item quantity
- Order-item discount
- Order-item discount rate
- Order year
- Order month
- Day of week
- Day of month
- Weekend indicator

### Categorical features

- Shipping mode
- Market
- Order region
- Order state
- Category
- Department
- Customer segment
- Transaction type

# Model Validation

A random train/test split is avoided because it can allow future observations to influence evaluation.

Instead, the dataset is sorted chronologically and split into:

```text
Training period:
2015-01-01 → 2017-04-22

Test period:
2017-04-22 → 2018-01-31
```

This provides a more realistic estimate of future-order performance.

# Model Comparison

| Model | ROC-AUC | PR-AUC | F1 | Precision | Recall |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | **0.7448** | **0.8351** | **0.6769** | **0.8492** | **0.5627** |
| HistGradientBoosting | 0.7391 | 0.8338 | 0.6752 | 0.8474 | 0.5612 |

Logistic Regression slightly outperforms HistGradientBoosting across the evaluated metrics.

Because the performance difference is small and Logistic Regression is simpler and more interpretable, it is selected as the final model.

# Threshold Analysis

| Threshold | Precision | Recall | F1 |
|---:|---:|---:|---:|
| 0.30 | 59.32% | **93.46%** | **0.7258** |
| 0.35 | 62.06% | 87.22% | 0.7252 |
| 0.40 | 69.26% | 72.24% | 0.7072 |
| 0.45 | 78.86% | 61.41% | 0.6905 |
| 0.50 | **84.92%** | 56.27% | 0.6769 |
| 0.55 | 86.85% | 54.60% | 0.6705 |
| 0.60 | 87.80% | 53.79% | 0.6671 |
| 0.65 | 88.24% | 52.90% | 0.6614 |
| 0.70 | 88.84% | 51.30% | 0.6504 |

Among the tested thresholds, **0.30 gives the highest F1 score** and substantially increases recall.

This does not mean 0.30 is universally optimal. The final threshold should depend on the cost of missing a risky shipment versus investigating a false positive.

# Key Business Insights

### 1. Delivery reliability is a major operational issue

Approximately 57% of observable order items are classified as late deliveries.

### 2. Expedited shipping requires closer monitoring

First Class and Second Class shipments have higher late-delivery rates because their promised delivery windows are shorter.

### 3. Major product categories have similar delivery risk

The largest categories generally have late-delivery rates close to the overall average.

### 4. High-volume categories have greater commercial exposure

Large categories can represent greater exposure to late deliveries even when their late-delivery rates are similar to other categories.

### 5. Demand is relatively stable for most of the dataset

Monthly order volume and sales remain relatively stable across most of the observation period.

### 6. The final months require caution

Late-2017 and early-2018 records show a structural change in order/unit behavior and should be investigated before being used for straightforward demand forecasting.

### 7. Late-delivery prediction is feasible

The final Logistic Regression model achieves:

```text
ROC-AUC = 0.7448
PR-AUC  = 0.8351
F1      = 0.6769
```

using order-time information.

### 8. Prediction thresholds should reflect business costs

A lower threshold can substantially improve recall when identifying potential late deliveries is more important than minimizing false positives.

# Reproducibility

## 1. Clone the repository

```bash
git clone https://github.com/Manas637/supply-chain-analytics.git
cd supply-chain-analytics
```

## 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## 3. Install dependencies

```powershell
pip install -r requirements.txt
```

## 4. Configure PostgreSQL

Create a PostgreSQL database:

```text
supply_chain_analytics
```

Create a `.env` file:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=supply_chain_analytics
DB_USER=postgres
DB_PASSWORD=your_password
```

The repository does not contain database credentials.

## 5. Add the dataset

Download the DataCo SMART Supply Chain dataset from:

https://data.mendeley.com/datasets/8gx2fvg2k6/5

Place:

```text
DataCoSupplyChainDataset.csv
```

inside:

```text
data/raw/
```

The raw dataset is ignored by Git.

## 6. Run the data audit

```powershell
python src/data/raw_audit.py
```

## 7. Validate the source data

```powershell
python src/data/validator.py
```

## 8. Load the data into PostgreSQL

```powershell
python src/data/loader.py
```

## 9. Run SQL transformations and analysis

```powershell
python scripts/run_sql_transformations.py
```

## 10. Export analytical results

```powershell
python scripts/export_results.py
```

Generated CSV outputs are stored in:

```text
results/
```

## 11. Run tests

```powershell
python -m pytest -q
```

## 12. Run the notebook

```powershell
jupyter notebook
```

Open:

```text
notebooks/supply_chain_analysis.ipynb
```

Then run all cells from a clean kernel.

# Testing

The project uses `pytest` for automated validation across:

- Source data validation
- Database loading
- Staging transformations
- Analytical tables
- Monthly demand analysis
- Statistical functions
- ML dataset construction
- Leakage prevention
- Data integrity

Run:

```powershell
python -m pytest -q
```

The final project test suite passes successfully.

# Data and Modeling Considerations

### Delivery classification

Late delivery is based on the dataset's `Delivery Status` field. Shipping-cancelled records are excluded from observable delivery performance and ML target construction.

### Dataset limitations

The selected dataset does not provide a reliable supplier-level or inventory-level representation suitable for detailed supplier or inventory optimization.

Therefore, this project focuses on:

- Logistics performance
- Delivery reliability
- Demand patterns
- Product/category performance
- Geographic analysis
- Sales and profitability
- Late-delivery prediction

### Predictive modeling limitation

The model is intended as an analytical demonstration of early risk prediction. A production deployment would require:

- Real-time operational data
- Validated intervention costs
- Monitoring for data drift
- Calibration and threshold optimization
- Business validation
- Continuous model evaluation

# Future Extensions

Potential extensions include:

- Cost-sensitive threshold optimization
- Probability calibration
- Model monitoring and drift detection
- More granular regional analysis
- Route-level or carrier-level data if available
- Forecasting with a dataset containing consistent time-series coverage
- Integration with operational alerting systems

These are intentionally outside the current project scope.

# Author

**Manas**

B.Tech Computer Science & Engineering  
IIT (ISM) Dhanbad

GitHub: https://github.com/Manas637

# License and Data Attribution

The code in this repository is intended for educational and portfolio use.

The underlying DataCo SMART Supply Chain dataset is provided by its original authors through Mendeley Data and is subject to its stated licensing and attribution requirements.

Dataset source:

https://data.mendeley.com/datasets/8gx2fvg2k6/5
