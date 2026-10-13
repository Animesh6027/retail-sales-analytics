"""Inspect and clean the downloaded Sample Superstore CSV."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REQUIRED_COLUMNS = {
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode", "Customer ID",
    "Customer Name", "Segment", "Country", "City", "State", "Postal Code", "Region",
    "Product ID", "Category", "Sub-Category", "Product Name", "Sales", "Quantity",
    "Discount", "Profit",
}


def find_input_csv(input_path: Path | None = None) -> Path:
    if input_path:
        return input_path
    candidates = sorted(RAW_DIR.glob("*.csv"))
    if not candidates:
        raise FileNotFoundError(
            f"No CSV found in {RAW_DIR}. Download Sample Superstore and place its CSV there."
        )
    return candidates[0]


def clean_superstore(input_path: Path | None = None) -> tuple[pd.DataFrame, dict[str, object]]:
    source = find_input_csv(input_path)
    frame = pd.read_csv(source, encoding="latin1")
    frame.columns = frame.columns.astype(str).str.strip()
    missing_columns = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing_columns:
        raise ValueError(f"Dataset is missing expected columns: {missing_columns}")

    original_rows = len(frame)
    duplicate_rows = int(frame.duplicated().sum())
    frame = frame.drop_duplicates().copy()

    for column in ("Order Date", "Ship Date"):
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    numeric_columns = ["Row ID", "Postal Code", "Sales", "Quantity", "Discount", "Profit"]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    invalid_dates = int(frame[["Order Date", "Ship Date"]].isna().any(axis=1).sum())
    invalid_numbers = int(frame[["Sales", "Quantity", "Discount", "Profit"]].isna().any(axis=1).sum())
    invalid_business_rows = int(
        ((frame["Sales"] < 0) | (frame["Quantity"] <= 0) | (frame["Discount"] < 0)).sum()
    )

    # Required analytical fields cannot be loaded safely when null; keep valid transactions only.
    frame = frame.dropna(subset=["Order ID", "Order Date", "Customer ID", "Product ID", "Sales", "Quantity", "Discount", "Profit"])
    frame = frame[(frame["Quantity"] > 0) & (frame["Sales"] >= 0) & (frame["Discount"] >= 0)]
    frame["Postal Code"] = frame["Postal Code"].astype("Int64")
    frame["Row ID"] = frame["Row ID"].astype("int64")
    frame["Quantity"] = frame["Quantity"].astype("int64")
    frame["Discount"] = frame["Discount"].astype(float)
    frame["Sales"] = frame["Sales"].astype(float).round(2)
    frame["Profit"] = frame["Profit"].astype(float).round(2)
    frame = frame.sort_values(["Order Date", "Order ID", "Row ID"]).reset_index(drop=True)

    stats = {
        "source": str(source), "original_rows": original_rows, "duplicate_rows": duplicate_rows,
        "clean_rows": len(frame), "invalid_date_rows": invalid_dates,
        "invalid_numeric_rows": invalid_numbers, "invalid_business_rows": invalid_business_rows,
        "potential_outlier_sales_upper_quantile": float(frame["Sales"].quantile(0.99)),
    }
    return frame, stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Optional path to a Superstore CSV")
    args = parser.parse_args()
    cleaned, stats = clean_superstore(args.input)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    output_path = PROCESSED_DIR / "superstore_cleaned.csv"
    cleaned.to_csv(output_path, index=False, date_format="%Y-%m-%d")
    print(f"Cleaned data written to {output_path}")
    for key, value in stats.items():
        print(f"{key}: {value}")
    print("Outliers are reported, not automatically removed.")


if __name__ == "__main__":
    main()
