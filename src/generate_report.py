"""Run SQL-backed analyses, save ten charts, CSV extracts, and a Markdown report."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import text

from db_connection import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PLOTS_DIR = PROJECT_ROOT / "outputs" / "plots"
CSV_DIR = PROJECT_ROOT / "outputs" / "csv"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports"

QUERIES = {
    "monthly": """SELECT DATE_FORMAT(o.order_date, '%Y-%m-01') AS month, SUM(i.sales) AS revenue, SUM(i.profit) AS profit
        FROM orders o JOIN order_items i ON i.order_id = o.order_id GROUP BY month ORDER BY month""",
    "category": """SELECT p.category, SUM(i.sales) AS revenue, SUM(i.profit) AS profit
        FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.category ORDER BY revenue DESC""",
    "subcategory": """SELECT p.subcategory, SUM(i.sales) AS revenue, SUM(i.profit) AS profit
        FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.subcategory ORDER BY profit DESC""",
    "top_products": """SELECT p.product_name, SUM(i.sales) AS revenue
        FROM products p JOIN order_items i ON i.product_id = p.product_id GROUP BY p.product_id, p.product_name ORDER BY revenue DESC LIMIT 10""",
    "top_customers": """SELECT c.customer_name, SUM(i.sales) AS spending
        FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN order_items i ON i.order_id = o.order_id
        GROUP BY c.customer_id, c.customer_name ORDER BY spending DESC LIMIT 10""",
    "region": """SELECT o.region, SUM(i.sales) AS revenue FROM orders o JOIN order_items i ON i.order_id = o.order_id
        GROUP BY o.region ORDER BY revenue DESC""",
    "discount_profit": """SELECT discount, SUM(profit) AS profit, SUM(sales) AS revenue
        FROM order_items GROUP BY discount ORDER BY discount""",
    "quantity": """SELECT quantity, COUNT(*) AS line_count FROM order_items GROUP BY quantity ORDER BY quantity""",
    "summary": """SELECT ROUND(SUM(i.sales), 2) AS revenue, ROUND(SUM(i.profit), 2) AS profit,
        COUNT(DISTINCT o.order_id) AS order_count, SUM(i.quantity) AS units_sold
        FROM orders o JOIN order_items i ON i.order_id = o.order_id""",
}


def load_results() -> dict[str, pd.DataFrame]:
    engine = get_engine()
    try:
        with engine.connect() as connection:
            return {name: pd.read_sql(text(query), connection) for name, query in QUERIES.items()}
    finally:
        engine.dispose()


def save_chart(name: str) -> None:
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / f"{name}.png", dpi=150, bbox_inches="tight")
    plt.close()


def generate_charts(results: dict[str, pd.DataFrame]) -> None:
    sns.set_theme(style="whitegrid", palette="colorblind")
    monthly = results["monthly"].copy()
    monthly["month"] = pd.to_datetime(monthly["month"])
    for column, title, ylabel, filename in [
        ("revenue", "Monthly Revenue Trend", "Revenue", "monthly_sales_trend"),
        ("profit", "Monthly Profit Trend", "Profit", "monthly_profit_trend"),
    ]:
        fig, axis = plt.subplots(figsize=(10, 5))
        sns.lineplot(data=monthly, x="month", y=column, marker="o", ax=axis, label=column.title())
        axis.set(title=title, xlabel="Month", ylabel=ylabel)
        axis.tick_params(axis="x", rotation=45)
        save_chart(filename)

    chart_specs = [
        ("category", "category", "revenue", "Revenue by Product Category", "Category", "Revenue", "category_revenue"),
        ("top_products", "product_name", "revenue", "Top 10 Products by Revenue", "Product", "Revenue", "top_10_products"),
        ("top_customers", "customer_name", "spending", "Top 10 Customers by Spending", "Customer", "Spending", "top_10_customers"),
        ("region", "region", "revenue", "Sales by Region", "Region", "Revenue", "sales_by_region"),
        ("subcategory", "subcategory", "profit", "Profitability by Subcategory", "Subcategory", "Profit", "subcategory_profitability"),
    ]
    for key, x, y, title, xlabel, ylabel, filename in chart_specs:
        data = results[key].sort_values(y, ascending=False)
        fig, axis = plt.subplots(figsize=(10, 5))
        sns.barplot(data=data, x=y, y=x, ax=axis)
        axis.set(title=title, xlabel=ylabel, ylabel=xlabel)
        save_chart(filename)

    discount = results["discount_profit"]
    fig, axis = plt.subplots(figsize=(8, 5))
    sns.scatterplot(data=discount, x="discount", y="profit", size="revenue", sizes=(30, 300), legend=False, ax=axis)
    axis.set(title="Discount versus Profit", xlabel="Discount rate", ylabel="Total profit")
    save_chart("discount_vs_profit")

    category = results["category"]
    fig, axis = plt.subplots(figsize=(9, 5))
    category.set_index("category")[["revenue", "profit"]].plot(kind="bar", ax=axis)
    axis.set(title="Revenue and Profit by Category", xlabel="Category", ylabel="Amount")
    axis.legend(title="Measure")
    save_chart("revenue_profit_comparison")

    quantity = results["quantity"]
    fig, axis = plt.subplots(figsize=(8, 5))
    sns.barplot(data=quantity, x="quantity", y="line_count", ax=axis)
    axis.set(title="Order Quantity Distribution", xlabel="Quantity per line item", ylabel="Line-item count")
    save_chart("order_quantity_distribution")


def write_outputs(results: dict[str, pd.DataFrame]) -> None:
    for directory in (PLOTS_DIR, CSV_DIR, REPORT_DIR):
        directory.mkdir(parents=True, exist_ok=True)
    for name, frame in results.items():
        frame.to_csv(CSV_DIR / f"{name}.csv", index=False)
    summary = results["summary"].iloc[0]
    category = results["category"].iloc[0]
    region = results["region"].iloc[0]
    report = f"""# Retail Sales Analytics Report

Generated from the local MySQL database by `src/generate_report.py`.

## Executive Summary

| Metric | Value |
|---|---:|
| Revenue | ${summary['revenue']:,.2f} |
| Profit | ${summary['profit']:,.2f} |
| Orders | {int(summary['order_count']):,} |
| Units sold | {int(summary['units_sold']):,} |

## Observations

- The highest-revenue category in this run was **{category['category']}** (${category['revenue']:,.2f}).
- The highest-revenue region in this run was **{region['region']}** (${region['revenue']:,.2f}).
- The discount chart shows association between discount levels and aggregate profit; it does not establish causation.
- The complete result tables are available as CSV files in `outputs/csv/`, and charts are in `outputs/plots/`.
"""
    (REPORT_DIR / "business_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    results = load_results()
    write_outputs(results)
    generate_charts(results)
    print(f"Generated {len(results)} CSV files, 10 charts, and outputs/reports/business_report.md")


if __name__ == "__main__":
    main()
