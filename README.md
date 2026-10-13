# Retail Sales Analytics System Using SQL and Python

A local, resume-ready analytics project for the Sample Superstore dataset. It combines a normalized MySQL model, practical SQL analysis, Pandas cleaning, and reproducible Matplotlib/Seaborn reporting.

## Problem Statement

Retail transaction data contains useful sales, customer, product, geographic, discount, and profitability signals, but those signals are difficult to compare safely when raw rows are not validated or when joins multiply measures. This project cleans the source file, stores it in related MySQL tables, and generates repeatable business analysis.

## Technology Stack

Python, MySQL, SQL, Pandas, NumPy, Matplotlib, Seaborn, SQLAlchemy, MySQL Connector/Python, Jupyter, VS Code, Git.

## Dataset

Download the [Sample Superstore dataset from Kaggle](https://www.kaggle.com/datasets/vivek468/superstore-dataset-final). Kaggle may require a free account. Download the ZIP, extract the CSV, and place the CSV in `data/raw/`. The cleaning script inspects the actual headers and stops if required fields are missing.

The project does not include the dataset because the source file is externally licensed and is usually too large for a small source repository.

## Database Design

- `customers` stores the source customer ID, name, and segment.
- `products` stores the source product ID, name, category, and subcategory.
- `orders` stores one row per source order with dates, shipping, customer, and geography.
- `order_items` stores one row per source transaction line with sales, quantity, discount, and profit.

`customers` to `orders` and `orders` to `order_items` are one-to-many relationships. `products` to `order_items` is also one-to-many. The source `Row ID` is retained as `order_item_id`, preventing line-level records from being collapsed. Analysis joins aggregate at the correct grain before presenting totals.

## Project Structure

```text
retail-sales-analytics/
├── data/raw/                 # Put the downloaded CSV here
├── data/processed/           # Generated cleaned CSV
├── sql/                      # Schema and analysis queries
├── src/                      # Cleaning, loading, connection, reporting
├── notebooks/                # Exploratory notebook
├── outputs/plots/            # Generated PNG charts
├── outputs/reports/          # Generated Markdown report
├── outputs/csv/              # Generated query extracts
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Windows Setup

Open PowerShell in the project root:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt with `.venv\Scripts\activate.bat`, or run the project with `.venv\Scripts\python.exe` directly.

Install MySQL Community Server locally, start the MySQL service, and create a local user/database. In MySQL Workbench or the MySQL command-line client, run:

```sql
SOURCE D:/PY_SQL Project/retail-sales-analytics/sql/schema.sql;
```

Use forward slashes in the `SOURCE` path. Create `.env` by copying `.env.example`, then set the local MySQL username, password, host, port, and database. `.env` is ignored by Git.

## Run The Project In Stages

### 1. Inspect and clean data

Place the extracted CSV in `data/raw/`, then run from the project root:

```powershell
.\.venv\Scripts\python.exe src\data_cleaning.py
```

This writes `data/processed/superstore_cleaned.csv` and prints row counts, duplicate counts, invalid values, and an outlier review threshold. Exact duplicates and invalid required transactions are removed; valid high-value transactions are preserved.

### 2. Load MySQL

```powershell
.\.venv\Scripts\python.exe src\db_connection.py
.\.venv\Scripts\python.exe src\load_data.py
```

The loader truncates and reloads the four project tables in one transaction, so rerunning it does not duplicate records. Confirm the load with:

```sql
USE retail_analytics;
SELECT COUNT(*) FROM customers;
SELECT COUNT(*) FROM products;
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;
```

### 3. Run SQL analysis

Open `sql/basic_analysis.sql`, `sql/intermediate_analysis.sql`, or `sql/advanced_analysis.sql` in MySQL Workbench and execute the statements. The advanced file includes CTEs, `LAG`, `DENSE_RANK`, `HAVING`, a subquery, and an explicitly documented repeat-purchase definition: a customer with at least two distinct orders.

### 4. Generate charts and report

```powershell
.\.venv\Scripts\python.exe src\generate_report.py
```

The script executes the important SQL queries and creates ten PNG files in `outputs/plots/`, CSV extracts in `outputs/csv/`, and an actual-data Markdown report at `outputs/reports/business_report.md`. The discount chart describes association, not causation.

### 5. Run the notebook

```powershell
.\.venv\Scripts\python.exe -m jupyter notebook notebooks\retail_sales_analysis.ipynb
```

Run the cleaning stage first so the notebook can read the processed CSV. In VS Code, select the `.venv` interpreter and the Python 3 kernel.

## Troubleshooting

- **CSV not found:** confirm the file is in `data/raw/` and ends with `.csv`.
- **Missing expected columns:** use the named Sample Superstore CSV; the script intentionally stops rather than guessing.
- **Access denied or connection refused:** confirm MySQL is running, the port is correct, and the `.env` values match the local account.
- **Unknown database:** execute `schema.sql` once in MySQL before running Python, because the SQLAlchemy URL must connect to an existing database.
- **PowerShell execution policy:** use Command Prompt or the direct `.venv\Scripts\python.exe` path.
- **Notebook import/path issue:** launch Jupyter from the project root, or set the notebook working directory to the project root.

## Validation And Limitations

The cleaning stage validates required columns, parses dates, coerces numeric fields, checks duplicates and missing values, and reports possible outliers. The import is transactional and reloadable. The dataset is a sample, not a live retail feed; it does not prove causal relationships, and the geographic and customer coverage may not represent a real retailer. Future improvements could add automated tests, a data-quality summary table, incremental loading, and a scheduled local refresh.

## Portfolio Notes

This project demonstrates normalized relational design, foreign keys, safe aggregation grain, SQL joins, CTEs, window functions, Python/MySQL integration, data cleaning, exploratory analysis, and automated business reporting without web development, cloud services, external APIs, or machine learning.
