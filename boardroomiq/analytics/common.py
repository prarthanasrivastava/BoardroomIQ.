from __future__ import annotations

import pandas as pd


def split_half_by_date(frame: pd.DataFrame, date_column: str = "date") -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = frame.dropna(subset=[date_column]).sort_values(date_column)
    if clean.empty:
        return clean, clean

    midpoint = clean[date_column].min() + (clean[date_column].max() - clean[date_column].min()) / 2
    previous = clean[clean[date_column] <= midpoint]
    current = clean[clean[date_column] > midpoint]
    return previous, current


def pct_change(previous: float, current: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / abs(previous)) * 100


def safe_divide(numerator: float, denominator: float) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator
