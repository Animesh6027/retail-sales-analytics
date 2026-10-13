"""Load the cleaned Superstore data into normalized MySQL tables."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_connection import get_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLEANED_PATH = PROJECT_ROOT / "data" / "processed" / "superstore_cleaned.csv"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "schema.sql"


def load_schema(connection) -> None:
    statements = [statement.strip() for statement in SCHEMA_PATH.read_text(encoding="utf-8").split(";")]
    for statement in statements:
        if statement and not statement.startswith("--") and not statement.upper().startswith("CREATE INDEX"):
            connection.execute(text(statement))


def load_tables() -> None:
    if not CLEANED_PATH.exists():
        raise FileNotFoundError("Run src/data_cleaning.py before loading data.")
    frame = pd.read_csv(CLEANED_PATH, parse_dates=["Order Date", "Ship Date"])
    engine = get_engine()
    try:
        with engine.begin() as connection:
            load_schema(connection)
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
            for table in ("order_items", "orders", "products", "customers"):
                connection.execute(text(f"TRUNCATE TABLE {table}"))
            connection.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

            customers = frame[["Customer ID", "Customer Name", "Segment"]].drop_duplicates("Customer ID")
            customers = customers.rename(columns={"Customer ID": "customer_id", "Customer Name": "customer_name", "Segment": "segment"})
            customers.to_sql("customers", connection, if_exists="append", index=False, method="multi")

            products = frame[["Product ID", "Product Name", "Category", "Sub-Category"]].drop_duplicates("Product ID")
            products = products.rename(columns={"Product ID": "product_id", "Product Name": "product_name", "Category": "category", "Sub-Category": "subcategory"})
            products.to_sql("products", connection, if_exists="append", index=False, method="multi")

            orders = frame[["Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID", "Country", "City", "State", "Postal Code", "Region"]].drop_duplicates("Order ID")
            orders = orders.rename(columns={"Order ID": "order_id", "Order Date": "order_date", "Ship Date": "ship_date", "Ship Mode": "ship_mode", "Customer ID": "customer_id", "Country": "country", "City": "city", "State": "state", "Postal Code": "postal_code", "Region": "region"})
            orders.to_sql("orders", connection, if_exists="append", index=False, method="multi")

            items = frame[["Row ID", "Order ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"]]
            items = items.rename(columns={"Row ID": "order_item_id", "Order ID": "order_id", "Product ID": "product_id", "Sales": "sales", "Quantity": "quantity", "Discount": "discount", "Profit": "profit"})
            items.to_sql("order_items", connection, if_exists="append", index=False, method="multi")
    finally:
        engine.dispose()
    print(f"Loaded {len(frame):,} line items into retail_analytics.")


if __name__ == "__main__":
    load_tables()
