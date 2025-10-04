"""
Train baseline SARIMAX forecasts for gym attendance (daily & weekly).

Inputs (from prepare_attendance.py):
  - phase5_data/outputs/attendance_forecasts_daily_input.csv
  - phase5_data/outputs/attendance_forecasts_weekly_input.csv

Outputs:
  - phase5_data/outputs/attendance_forecasts_daily.csv
  - phase5_data/outputs/attendance_forecasts_weekly.csv
  - phase5_data/models/attendance_sarimax_facility_<id>.joblib

Notes:
  - Simple per-facility univariate SARIMAX baseline
  - Train/test split with last 14 (daily) or last 8 (weekly) periods for evaluation
  - Metrics: RMSE, MAPE printed to console
"""

from __future__ import annotations

from pathlib import Path
from typing import Tuple, Dict

import warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_squared_error
import joblib


def resolve_paths() -> Dict[str, Path]:
    repo_root = Path(__file__).resolve().parents[2]
    phase5_dir = repo_root / "phase5_data"
    outputs_dir = phase5_dir / "outputs"
    models_dir = phase5_dir / "models"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)
    return {
        "in_daily": outputs_dir / "attendance_forecasts_daily_input.csv",
        "in_weekly": outputs_dir / "attendance_forecasts_weekly_input.csv",
        "out_daily": outputs_dir / "attendance_forecasts_daily.csv",
        "out_weekly": outputs_dir / "attendance_forecasts_weekly.csv",
        "models": models_dir,
    }


def train_sarimax(series: pd.Series, seasonal_period: int) -> SARIMAX:
    # Basic SARIMAX config; in practice tune via grid search
    # (p,d,q)=(1,1,1), (P,D,Q)m=(1,1,1, m)
    model = SARIMAX(series, order=(1, 1, 1), seasonal_order=(1, 1, 1, seasonal_period), enforce_stationarity=False, enforce_invertibility=False)
    return model


def rmse_mape(y_true: np.ndarray, y_pred: np.ndarray) -> Tuple[float, float]:
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    with np.errstate(divide='ignore', invalid='ignore'):
        mape = np.mean(np.abs((y_true - y_pred) / np.clip(np.abs(y_true), 1e-8, None))) * 100
    return float(rmse), float(mape)


def _seasonal_naive(ts: pd.Series, horizon: int, seasonal_period: int, freq: str) -> pd.Series:
    if len(ts) >= seasonal_period:
        last_season = ts[-seasonal_period:]
        reps = int(np.ceil(horizon / seasonal_period))
        forecast_vals = np.tile(last_season.values, reps)[:horizon]
        idx = pd.date_range(start=ts.index[-1] + pd.tseries.frequencies.to_offset(freq), periods=horizon, freq=freq)
        return pd.Series(forecast_vals, index=idx, name="forecast")
    else:
        last_val = float(ts.iloc[-1]) if len(ts) else 0.0
        idx = pd.date_range(start=ts.index[-1] + pd.tseries.frequencies.to_offset(freq) if len(ts) else None, periods=horizon, freq=freq)
        return pd.Series([last_val] * horizon, index=idx, name="forecast")


def forecast_per_facility(df: pd.DataFrame, freq: str, horizon: int, seasonal_period: int, models_dir: Path) -> pd.DataFrame:
    forecasts = []
    for facility_id, g in df.groupby("facility_id"):
        g = g.sort_values("date").copy()
        ts = g.set_index("date")["attendance"].asfreq(freq).fillna(0)

        # Guard for short series
        if len(ts) < max(10, seasonal_period + 3):
            fut = _seasonal_naive(ts, horizon, seasonal_period, freq)
            print(f"Facility {facility_id} [{freq}] -> short series (n={len(ts)}), using seasonal naive.")
        else:
            # Train/test split
            test_len = min(horizon, max(1, int(len(ts) * 0.2)))
            if test_len >= len(ts):
                test_len = max(1, len(ts) // 5)
            train, test = ts.iloc[:-test_len], ts.iloc[-test_len:]

            try:
                model = train_sarimax(train, seasonal_period)
                res = model.fit(disp=False)

                # In-sample test forecast
                pred = res.get_forecast(steps=test_len).predicted_mean
                r, m = rmse_mape(test.values, pred.values)
                print(f"Facility {facility_id} [{freq}] -> RMSE: {r:.2f}, MAPE: {m:.2f}% (n={test_len})")

                # Future forecast (same horizon)
                fut = res.get_forecast(steps=horizon).predicted_mean
                fut = fut.rename("forecast")

                # Persist model
                joblib.dump(res, models_dir / f"attendance_sarimax_facility_{facility_id}_{freq}.joblib")
            except Exception as ex:
                print(f"Facility {facility_id} [{freq}] -> SARIMAX failed ({ex}); using seasonal naive.")
                fut = _seasonal_naive(ts, horizon, seasonal_period, freq)
        fut_df = fut.reset_index().rename(columns={"index": "date"})
        fut_df["facility_id"] = facility_id
        forecasts.append(fut_df)

    if forecasts:
        return pd.concat(forecasts, ignore_index=True)
    return pd.DataFrame(columns=["date", "forecast", "facility_id"])


def main() -> None:
    paths = resolve_paths()

    # DAILY
    daily = pd.read_csv(paths["in_daily"])  # columns: date, facility_id, attendance, dow, week, month
    daily["date"] = pd.to_datetime(daily["date"])  # ensure datetime
    daily_fc = forecast_per_facility(daily, freq="D", horizon=14, seasonal_period=7, models_dir=paths["models"])  # 2-week horizon
    daily_fc.to_csv(paths["out_daily"], index=False)
    print(f"Wrote daily forecasts -> {paths['out_daily']} ({len(daily_fc)} rows)")

    # WEEKLY
    weekly = pd.read_csv(paths["in_weekly"])  # columns: date, facility_id, attendance, week, month
    weekly["date"] = pd.to_datetime(weekly["date"])  # ensure datetime
    weekly_fc = forecast_per_facility(weekly, freq="W-MON", horizon=8, seasonal_period=52, models_dir=paths["models"])  # 8-week horizon
    weekly_fc.to_csv(paths["out_weekly"], index=False)
    print(f"Wrote weekly forecasts -> {paths['out_weekly']} ({len(weekly_fc)} rows)")


if __name__ == "__main__":
    main()


