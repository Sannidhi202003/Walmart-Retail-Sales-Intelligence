"""
retail_sales_engine.py
======================
Walmart Retail Sales Intelligence — Data Processing & Analysis
Refactored pipeline: loads JSON data, cleans it, engineers features,
and outputs summary statistics for dashboard consumption.
"""

import json
import os
import numpy as np
import pandas as pd
from datetime import datetime


# ── CONFIG ──────────────────────────────────────────────────────
DATA_FILE      = os.path.join(os.path.dirname(__file__), "../data/walmart_transactions.json")
OUTPUT_DIR     = os.path.join(os.path.dirname(__file__), "../models")
DATE_FORMAT    = "%d/%m/%y"
SHIFT_MORNING  = range(0, 12)
SHIFT_AFTERNOON= range(12, 18)


# ── DATA LOADER ─────────────────────────────────────────────────
def load_transaction_data(filepath: str) -> pd.DataFrame:
    """Read JSON transaction records into a DataFrame."""
    with open(filepath, "r") as fh:
        records = json.load(fh)
    df = pd.DataFrame(records)
    print(f"[Loader] Loaded {len(df):,} transactions | Columns: {list(df.columns)}")
    return df


# ── DATA CLEANER ────────────────────────────────────────────────
def clean_transaction_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardises the raw transaction dataframe.
    Steps:
      - Drop exact duplicate rows
      - Parse date strings into datetime objects
      - Ensure numeric columns are float
      - Standardise column names to snake_case
    """
    df = df.copy()

    # Standardise column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Remove duplicates
    before = len(df)
    df.drop_duplicates(inplace=True)
    print(f"[Cleaner] Removed {before - len(df)} duplicate rows")

    # Parse dates
    df["parsed_date"] = pd.to_datetime(df["date"], format=DATE_FORMAT, errors="coerce")
    df["year"]        = df["parsed_date"].dt.year
    df["month"]       = df["parsed_date"].dt.month
    df["month_name"]  = df["parsed_date"].dt.strftime("%b")
    df["day_of_week"] = df["parsed_date"].dt.strftime("%A")

    # Parse hour from time string
    df["hour"] = df["time"].str.split(":").str[0].astype(int)

    # Assign day shift
    df["shift"] = df["hour"].apply(assign_shift)

    # Ensure numeric types
    for col in ["unit_price", "quantity", "rating", "profit_margin", "total"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Compute estimated profit
    df["estimated_profit"] = df["total"] * df["profit_margin"]

    print(f"[Cleaner] Final dataset: {df.shape[0]:,} rows × {df.shape[1]} columns")
    return df


def assign_shift(hour: int) -> str:
    """Classify transaction hour into Morning / Afternoon / Evening."""
    if hour in SHIFT_MORNING:
        return "Morning"
    elif hour in SHIFT_AFTERNOON:
        return "Afternoon"
    return "Evening"


# ── ANALYSIS FUNCTIONS ──────────────────────────────────────────
def revenue_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Total revenue, transaction count, and avg ticket per product category."""
    return (
        df.groupby("category")
        .agg(
            total_revenue    = ("total", "sum"),
            num_transactions = ("invoice_id", "count"),
            avg_ticket       = ("total", "mean"),
            total_units      = ("quantity", "sum"),
        )
        .round(2)
        .sort_values("total_revenue", ascending=False)
        .reset_index()
    )


def revenue_by_branch(df: pd.DataFrame) -> pd.DataFrame:
    """Sales and profit summary grouped by store branch."""
    return (
        df.groupby("branch")
        .agg(
            total_revenue    = ("total", "sum"),
            total_profit     = ("estimated_profit", "sum"),
            num_transactions = ("invoice_id", "count"),
            avg_rating       = ("rating", "mean"),
        )
        .round(2)
        .sort_values("total_revenue", ascending=False)
        .reset_index()
    )


def payment_method_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Breakdown of transactions and revenue by payment type."""
    return (
        df.groupby("payment_method")
        .agg(
            transaction_count = ("invoice_id", "count"),
            total_items_sold  = ("quantity", "sum"),
            total_revenue     = ("total", "sum"),
        )
        .round(2)
        .sort_values("total_revenue", ascending=False)
        .reset_index()
    )


def daily_sales_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Daily aggregated revenue for time-series plotting."""
    trend = (
        df.groupby("parsed_date")
        .agg(daily_revenue = ("total", "sum"), transactions = ("invoice_id", "count"))
        .reset_index()
        .sort_values("parsed_date")
    )
    trend["rolling_7d"] = trend["daily_revenue"].rolling(7).mean()
    return trend


def hourly_traffic(df: pd.DataFrame) -> pd.DataFrame:
    """Transaction volume and revenue by hour of day."""
    return (
        df.groupby("hour")
        .agg(transaction_count = ("invoice_id", "count"), hourly_revenue = ("total", "sum"))
        .round(2)
        .reset_index()
        .sort_values("hour")
    )


def city_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Average and total transaction value by city."""
    return (
        df.groupby("city")
        .agg(
            avg_transaction  = ("total", "mean"),
            total_revenue    = ("total", "sum"),
            num_transactions = ("invoice_id", "count"),
        )
        .round(2)
        .sort_values("avg_transaction", ascending=False)
        .reset_index()
    )


def shift_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Transaction and revenue distribution across Morning/Afternoon/Evening."""
    return (
        df.groupby(["branch", "shift"])
        .agg(transaction_count = ("invoice_id", "count"), shift_revenue = ("total", "sum"))
        .round(2)
        .reset_index()
    )


def yoy_revenue_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-year revenue change per branch (2022 vs 2023)."""
    yearly = (
        df[df["year"].isin([2022, 2023])]
        .groupby(["branch", "year"])["total"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    if 2022 in yearly.columns and 2023 in yearly.columns:
        yearly.columns = ["branch", "revenue_2022", "revenue_2023"]
        yearly["pct_change"] = (
            (yearly["revenue_2023"] - yearly["revenue_2022"]) / yearly["revenue_2022"] * 100
        ).round(2)
    return yearly


# ── SUMMARY REPORT ──────────────────────────────────────────────
def print_executive_summary(df: pd.DataFrame) -> None:
    """Print top-level KPIs to console."""
    print("\n" + "═" * 55)
    print("   WALMART SALES — EXECUTIVE SUMMARY")
    print("═" * 55)
    print(f"  Total Revenue        : ${df['total'].sum():>14,.2f}")
    print(f"  Total Profit Est.    : ${df['estimated_profit'].sum():>14,.2f}")
    print(f"  Total Transactions   : {len(df):>15,}")
    print(f"  Unique Branches      : {df['branch'].nunique():>15,}")
    print(f"  Unique Cities        : {df['city'].nunique():>15,}")
    print(f"  Avg Transaction Value: ${df['total'].mean():>14,.2f}")
    print(f"  Avg Customer Rating  : {df['rating'].mean():>14.2f} / 10")
    print(f"  Date Range           : {df['parsed_date'].min().date()} → {df['parsed_date'].max().date()}")
    top_cat  = df.groupby("category")["total"].sum().idxmax()
    top_city = df.groupby("city")["total"].sum().idxmax()
    print(f"  Top Category         : {top_cat}")
    print(f"  Top City             : {top_city}")
    print("═" * 55 + "\n")


# ── MAIN ────────────────────────────────────────────────────────
if __name__ == "__main__":
    raw_df    = load_transaction_data(DATA_FILE)
    clean_df  = clean_transaction_data(raw_df)

    print_executive_summary(clean_df)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Export summaries as CSV
    summaries = {
        "category_revenue"  : revenue_by_category(clean_df),
        "branch_revenue"    : revenue_by_branch(clean_df),
        "payment_summary"   : payment_method_summary(clean_df),
        "daily_trend"       : daily_sales_trend(clean_df),
        "hourly_traffic"    : hourly_traffic(clean_df),
        "city_performance"  : city_performance(clean_df),
        "shift_analysis"    : shift_analysis(clean_df),
        "yoy_comparison"    : yoy_revenue_comparison(clean_df),
    }

    for name, frame in summaries.items():
        out_path = os.path.join(OUTPUT_DIR, f"{name}.csv")
        frame.to_csv(out_path, index=False)
        print(f"[Output] Saved → {out_path}")

    print("\n✅ Analysis complete. All summaries saved to /models/")
