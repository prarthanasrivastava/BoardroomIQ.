from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


DATE_HINTS = ("date", "time", "created", "booked", "signup", "purchase")
REVENUE_HINTS = ("revenue", "amount", "paid", "price", "sales", "value")
SPEND_HINTS = ("spend", "cost", "budget", "ad_spend")
CONVERSION_HINTS = ("converted", "conversion", "won", "closed")
BOOKING_HINTS = ("book", "onboard", "appointment", "demo", "scheduled")
STATUS_HINTS = ("status", "stage", "state")
SOURCE_HINTS = ("source", "campaign", "channel", "medium")
LOCATION_HINTS = ("region", "city", "location", "zone")


@dataclass
class DatasetProfile:
    name: str
    rows: int
    columns: list[str]
    date_columns: list[str]
    numeric_columns: list[str]
    possible_revenue_columns: list[str]
    possible_spend_columns: list[str]
    possible_conversion_columns: list[str]
    possible_booking_columns: list[str]
    possible_status_columns: list[str]
    possible_source_columns: list[str]
    possible_location_columns: list[str]


def _matches(columns: list[str], hints: tuple[str, ...]) -> list[str]:
    matched = []
    for column in columns:
        normalized = column.lower().replace(" ", "_")
        if any(hint in normalized for hint in hints):
            matched.append(column)
    return matched


def profile_dataset(name: str, frame: pd.DataFrame) -> DatasetProfile:
    columns = [str(column) for column in frame.columns]
    numeric_columns = [str(column) for column in frame.select_dtypes(include="number").columns]
    non_numeric_columns = [column for column in columns if column not in numeric_columns]
    date_columns = []

    for column in columns:
        series = frame[column]
        if pd.api.types.is_datetime64_any_dtype(series):
            date_columns.append(column)
            continue
        if any(hint in column.lower() for hint in DATE_HINTS):
            parsed = pd.to_datetime(series, errors="coerce")
            if parsed.notna().mean() >= 0.5:
                date_columns.append(column)

    return DatasetProfile(
        name=name,
        rows=int(len(frame)),
        columns=columns,
        date_columns=date_columns,
        numeric_columns=numeric_columns,
        possible_revenue_columns=_matches(columns, REVENUE_HINTS),
        possible_spend_columns=_matches(columns, SPEND_HINTS),
        possible_conversion_columns=_matches(columns, CONVERSION_HINTS),
        possible_booking_columns=_matches(columns, BOOKING_HINTS),
        possible_status_columns=_matches(columns, STATUS_HINTS),
        possible_source_columns=_matches(non_numeric_columns, SOURCE_HINTS),
        possible_location_columns=_matches(columns, LOCATION_HINTS),
    )


def profile_datasets(data: dict[str, pd.DataFrame]) -> list[DatasetProfile]:
    return [profile_dataset(name, frame) for name, frame in data.items()]


def profile_to_dict(profile: DatasetProfile) -> dict[str, Any]:
    return {
        "name": profile.name,
        "rows": profile.rows,
        "columns": profile.columns,
        "date_columns": profile.date_columns,
        "numeric_columns": profile.numeric_columns,
        "possible_revenue_columns": profile.possible_revenue_columns,
        "possible_spend_columns": profile.possible_spend_columns,
        "possible_conversion_columns": profile.possible_conversion_columns,
        "possible_booking_columns": profile.possible_booking_columns,
        "possible_status_columns": profile.possible_status_columns,
        "possible_source_columns": profile.possible_source_columns,
        "possible_location_columns": profile.possible_location_columns,
    }
