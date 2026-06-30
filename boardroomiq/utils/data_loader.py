from __future__ import annotations

from pathlib import Path

import pandas as pd


SAMPLE_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "sample"


def read_sample_data() -> dict[str, pd.DataFrame]:
    return {
        "sales": pd.read_csv(SAMPLE_DATA_DIR / "sales.csv", parse_dates=["date"]),
        "customers": pd.read_csv(
            SAMPLE_DATA_DIR / "customers.csv",
            parse_dates=["signup_date", "last_purchase_date"],
        ),
        "inventory": pd.read_csv(SAMPLE_DATA_DIR / "inventory.csv", parse_dates=["date"]),
        "marketing": pd.read_csv(SAMPLE_DATA_DIR / "marketing.csv", parse_dates=["date"]),
    }


def normalize_uploads(uploaded_files: dict[str, object]) -> dict[str, pd.DataFrame]:
    frames = {}
    date_columns = {
        "sales": ["date"],
        "customers": ["signup_date", "last_purchase_date"],
        "inventory": ["date"],
        "marketing": ["date"],
    }

    for name, file in uploaded_files.items():
        if file is None:
            continue

        frame = pd.read_csv(file)
        for column in date_columns.get(name, []):
            if column in frame.columns:
                frame[column] = pd.to_datetime(frame[column], errors="coerce")
        frames[name] = frame

    return frames
