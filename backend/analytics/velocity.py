import pandas as pd
import numpy as np
from datetime import timedelta


def compute_velocity(df: pd.DataFrame, window_days: int = 7) -> pd.Series:
    """
    Rolling window spend sum (debits only), indexed by date.
    Returns a Series aligned to the input DataFrame.
    """
    debits = df[df["type"] == "debit"].copy()
    if debits.empty:
        return pd.Series(dtype=float)

    debits = debits.sort_values("date").set_index("date")
    rolling = (
        debits["amount"]
        .rolling(f"{window_days}D", min_periods=1)
        .sum()
        .reset_index()
    )
    rolling.columns = ["date", "rolling_spend"]
    return rolling


def detect_velocity_spike(df: pd.DataFrame, multiplier: float = 1.8) -> float:
    """
    Returns a 0–1 risk score based on how much the current window
    exceeds the historical median. 0 = no spike, 1 = extreme spike.
    """
    velocity_df = compute_velocity(df)
    if velocity_df.empty or len(velocity_df) < 2:
        return 0.0

    current = velocity_df["rolling_spend"].iloc[-1]
    historical_median = velocity_df["rolling_spend"].median()

    if historical_median == 0:
        return 0.0

    ratio = current / historical_median
    # normalize: ratio >= multiplier → 1.0, ratio <= 1.0 → 0.0
    score = max(0.0, min(1.0, (ratio - 1.0) / (multiplier - 1.0)))
    return round(score, 3)


def velocity_to_chart_data(df: pd.DataFrame) -> list[dict]:
    """Return velocity data shaped for the frontend chart."""
    velocity_df = compute_velocity(df)
    return [
        {"date": row["date"].strftime("%Y-%m-%d"), "rolling_spend": round(row["rolling_spend"], 2)}
        for _, row in velocity_df.iterrows()
    ]
