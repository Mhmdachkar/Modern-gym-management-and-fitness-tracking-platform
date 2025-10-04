"""
Prepare attendance time series datasets from phase4 gym usage logs.

Inputs:
  - phase4_data/data/gym_usage_data.csv

Outputs (created if missing):
  - phase5_data/outputs/attendance_forecasts_daily_input.csv
  - phase5_data/outputs/attendance_forecasts_weekly_input.csv

Notes:
  - Aggregates by date (and by facility_id) counts of check-ins
  - Adds calendar features useful for forecasting (dow, week, month)
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path


def resolve_paths() -> dict[str, Path]:
    repo_root = Path(__file__).resolve().parents[2]
    phase4_dir = repo_root / "phase4_data"
    phase5_dir = repo_root / "phase5_data"
    data_in = phase4_dir / "data" / "gym_usage_data.csv"
    out_dir = phase5_dir / "outputs"
    out_dir.mkdir(parents=True, exist_ok=True)
    return {
        "input": data_in,
        "out_daily": out_dir / "attendance_forecasts_daily_input.csv",
        "out_weekly": out_dir / "attendance_forecasts_weekly_input.csv",
    }


def load_usage(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    # Expected columns include: check_in_time, facility_id
    # Parse datetimes; tolerate missing seconds
    df["check_in_time"] = pd.to_datetime(df["check_in_time"], errors="coerce")
    # Drop rows with invalid timestamps
    df = df.dropna(subset=["check_in_time"]).copy()
    # Normalize date
    df["date"] = df["check_in_time"].dt.date
    # Ensure facility_id exists; if not, create a single facility
    if "facility_id" not in df.columns:
        df["facility_id"] = 0
    return df


def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    daily = (
        df.groupby(["date", "facility_id"])  # type: ignore[arg-type]
        .size()
        .reset_index(name="attendance")
        .sort_values(["facility_id", "date"])  # type: ignore[list-item]
    )
    daily["date"] = pd.to_datetime(daily["date"])  # back to Timestamp
    # Calendar features
    daily["dow"] = daily["date"].dt.dayofweek
    daily["week"] = daily["date"].dt.isocalendar().week.astype(int)
    daily["month"] = daily["date"].dt.month
    return daily


def aggregate_weekly(daily: pd.DataFrame) -> pd.DataFrame:
    weekly = (
        daily.assign(week_start=daily["date"] - pd.to_timedelta(daily["date"].dt.dayofweek, unit="D"))
        .groupby(["week_start", "facility_id"], as_index=False)["attendance"]
        .sum()
        .rename(columns={"week_start": "date"})
        .sort_values(["facility_id", "date"])
    )
    weekly["week"] = weekly["date"].dt.isocalendar().week.astype(int)
    weekly["month"] = weekly["date"].dt.month
    return weekly


def main() -> None:
    paths = resolve_paths()
    df = load_usage(paths["input"])
    daily = aggregate_daily(df)
    weekly = aggregate_weekly(daily)
    # Save
    daily.to_csv(paths["out_daily"], index=False)
    weekly.to_csv(paths["out_weekly"], index=False)
    print(f"Wrote: {paths['out_daily']} ({len(daily)} rows)")
    print(f"Wrote: {paths['out_weekly']} ({len(weekly)} rows)")


if __name__ == "__main__":
    main()


