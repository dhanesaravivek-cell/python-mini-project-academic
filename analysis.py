"""analysis.py - filtering and calculations (Pandas + NumPy)."""
import numpy as np
import pandas as pd

SEASON_ORDER = ["Winter", "Summer", "Monsoon", "Post-monsoon"]


def get_season(month):
    """Month number -> season name (Indian climate)."""
    if month in (12, 1, 2):
        return "Winter"
    if month in (3, 4, 5):
        return "Summer"
    if month in (6, 7, 8, 9):
        return "Monsoon"
    return "Post-monsoon"          


def filter_records(df, location="", start=None, end=None):
    """Keep only rows matching the location text and the date range."""
    if location.strip() != "":
        df = df[df["location"].str.contains(location.strip(), case=False)]
    if start is not None:
        df = df[df["date"] >= pd.Timestamp(start)]
    if end is not None:
        df = df[df["date"] <= pd.Timestamp(end)]
    return df


def total_and_average(df):
    """Return (total, average) rainfall using NumPy."""
    if df.empty:
        return 0.0, 0.0
    values = df["rainfall_mm"].to_numpy()
    return float(np.sum(values)), float(np.mean(values))


def monthly_totals(df):
    """Total rainfall for each month (index looks like '2026-07')."""
    months = df["date"].dt.strftime("%Y-%m")
    return df.groupby(months)["rainfall_mm"].sum()


def seasonal_totals(df):
    """Total and average rainfall for each season."""
    seasons = df["date"].dt.month.map(get_season)
    table = df.groupby(seasons)["rainfall_mm"].agg(["sum", "mean"])
    table.columns = ["total", "average"]
    return table.reindex(SEASON_ORDER).fillna(0)


def location_totals(df):
    """Total rainfall for each location."""
    return df.groupby("location")["rainfall_mm"].sum()


def compare_periods(df, start1, end1, start2, end2):
    """Compare two date ranges. Returns a dictionary of results."""
    total1, avg1 = total_and_average(filter_records(df, "", start1, end1))
    total2, avg2 = total_and_average(filter_records(df, "", start2, end2))
    difference = total2 - total1
    percent = None if total1 == 0 else difference / total1 * 100
    return {"total1": total1, "avg1": avg1, "total2": total2, "avg2": avg2,
            "difference": difference, "percent": percent}


def highest_lowest(df):
    """Return (highest row, lowest row), or (None, None) if there is no data."""
    if df.empty:
        return None, None
    return df.loc[df["rainfall_mm"].idxmax()], df.loc[df["rainfall_mm"].idxmin()]
