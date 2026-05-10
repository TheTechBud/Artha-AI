import calendar

import pandas as pd
from datetime import date

from analytics.reference_period import filter_df_to_calendar_month
from utils.constants import DRS_EMOTIONAL_RATIO_MULT, DRS_SALARY_GAP_PRESSURE_MULT


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

    # Exclude lumpy committed flows from the baseline — rent/SIP-sized amounts inflate "average debit"
    # and hide stress-spend patterns (food delivery, entertainment spikes).
    disc_mask = ~debits["category"].isin({"Rent/EMI", "Savings"})
    disc = debits[disc_mask] if disc_mask.any() else debits
    daily_avg = float(disc["amount"].mean()) if not disc.empty else 0.0
    if daily_avg <= 0:
        daily_avg = float(debits["amount"].mean()) if not debits.empty else 0.0

    df["_dt"] = pd.to_datetime(df["date"])
    df["_hour"] = df["_dt"].dt.hour
    df["_dow"] = df["_dt"].dt.dayofweek  # 0=Mon, 5=Sat, 6=Sun

    desc_upper = df["description"].astype(str).str.upper()

    # Date-only CSV timestamps parse as midnight — exclude 00:00–03:00 from late-night so we
    # don't mark every row as emotional; keep true late-night as 22:00–23:59 only.
    late_night = df["_hour"].isin(range(22, 24))
    # Large weekend debits only count when discretionary — avoids tagging grocery stock-ups / rent as emotional
    _splurge_eligible = ~df["category"].isin(
        {"Rent/EMI", "Utilities", "Savings", "Groceries", "Health"}
    )
    weekend_splurge = (
        df["_dow"].isin([5, 6]) & (df["amount"] > daily_avg * 2) & _splurge_eligible
    )
    # Weekend food/entertainment only when elevated vs typical discretionary spend
    food_ent_weekend = (
        df["category"].isin(["Food & Dining", "Entertainment"]) &
        df["_dow"].isin([5, 6]) &
        (df["amount"] > daily_avg * 1.35)
    )
    # Food delivery apps — stress-spend proxy (demo CSVs are date-only; weekday orders matter too)
    delivery_app = desc_upper.str.contains(r"ZOMATO|SWIGGY|DOMINOS", regex=True, na=False)

    df["is_emotional"] = (
        late_night | weekend_splurge | food_ent_weekend | delivery_app
    ) & (df["type"] == "debit")

    df.drop(columns=["_dt", "_hour", "_dow"], inplace=True)
    return df


def emotional_spend_score(df: pd.DataFrame) -> float:
    """
    C5 DRS component. Returns 0–1.
    Higher share of emotional-tagged debits → lower score (calibrated for persona spread).
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
    score = max(0.0, 1.0 - min(1.0, ratio * DRS_EMOTIONAL_RATIO_MULT))
    return round(score, 4)


def salary_gap_score(
    df: pd.DataFrame,
    monthly_income: float,
    _salary_day: int,
    month_start: date,
    today: date,
) -> float:
    """
    C6 DRS component. Returns 0–1.
    Measures whether spending pace vs salary is sustainable through the month.
    Uses the same reference calendar month as budget adherence (often latest month in CSV).
    """
    month_slice = filter_df_to_calendar_month(df, month_start)
    debits_m = month_slice[month_slice["type"] == "debit"]
    # SIP/investment debits are intentional outflows — don't treat like runway erosion vs salary
    runway = debits_m[~debits_m["category"].isin(["Savings"])]
    spent = runway["amount"].sum()

    if monthly_income == 0:
        return 0.5

    pct_budget_used = spent / monthly_income

    ref_key = (month_start.year, month_start.month)
    now_key = (today.year, today.month)
    dim = calendar.monthrange(today.year, today.month)[1]
    if ref_key < now_key:
        pct_month_elapsed = 1.0
    elif ref_key == now_key:
        pct_month_elapsed = today.day / dim
    else:
        pct_month_elapsed = 1.0

    gap_pressure = pct_budget_used - pct_month_elapsed
    score = max(0.0, 1.0 - max(0.0, gap_pressure) * DRS_SALARY_GAP_PRESSURE_MULT)
    return round(score, 4)
