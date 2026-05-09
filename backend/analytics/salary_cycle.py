import pandas as pd
import numpy as np
from datetime import date


def detect_salary_day(df: pd.DataFrame) -> int:
    """Detect the day of month when salary typically arrives."""
    income = df[df["type"] == "credit"].copy()
    if income.empty:
        return 1  # fallback

    income["day"] = pd.to_datetime(income["date"]).dt.day
    day_totals = income.groupby("day")["amount"].sum()
    return int(day_totals.idxmax())


def flag_emotional_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Mark transactions as emotional if:
    - Occurred between 10pm–2am
    - Weekend AND amount > 2x daily average
    - Category is Food/Entertainment AND on historical spike day
    """
    df = df.copy()
    debits = df[df["type"] == "debit"]

    daily_avg = debits["amount"].mean() if not debits.empty else 0

    df["_dt"] = pd.to_datetime(df["date"])
    df["_hour"] = df["_dt"].dt.hour
    df["_dow"] = df["_dt"].dt.dayofweek  # 0=Mon, 5=Sat, 6=Sun

    late_night = df["_hour"].isin(range(22, 24)) | df["_hour"].isin(range(0, 3))
    weekend_splurge = df["_dow"].isin([5, 6]) & (df["amount"] > daily_avg * 2)
    food_ent_weekend = (
        df["category"].isin(["Food & Dining", "Entertainment"]) &
        df["_dow"].isin([5, 6])
    )

    df["is_emotional"] = (late_night | weekend_splurge | food_ent_weekend) & (df["type"] == "debit")

    df.drop(columns=["_dt", "_hour", "_dow"], inplace=True)
    return df


def emotional_spend_score(df: pd.DataFrame) -> float:
    """
    C5 DRS component. Returns 0–1.
    >33% emotional spend → 0, 0% → 1.
    """
    debits = df[df["type"] == "debit"]
    if debits.empty:
        return 1.0

    total = debits["amount"].sum()
    if total == 0:
        return 1.0

    emotional_col = "is_emotional" if "is_emotional" in debits.columns else None
    if not emotional_col:
        return 1.0

    emotional_total = debits[debits[emotional_col]]["amount"].sum()
    ratio = emotional_total / total
    score = max(0.0, 1.0 - ratio * 3)  # >33% → 0
    return round(score, 4)


def salary_gap_score(df: pd.DataFrame, monthly_income: float, salary_day: int) -> float:
    """
    C6 DRS component. Returns 0–1.
    Measures whether spending pace will outlast salary.
    """
    today = date.today()
    import calendar
    days_in_month = calendar.monthrange(today.year, today.month)[1]

    pct_month_elapsed = today.day / days_in_month

    month_start = today.replace(day=1)
    this_month = df[
        (df["type"] == "debit") &
        (pd.to_datetime(df["date"]).dt.date >= month_start)
    ]
    spent = this_month["amount"].sum()

    if monthly_income == 0:
        return 0.5

    pct_budget_used = spent / monthly_income
    gap_pressure = pct_budget_used - pct_month_elapsed
    score = max(0.0, 1.0 - max(0.0, gap_pressure) * 4)
    return round(score, 4)
