import pandas as pd
import numpy as np
from datetime import date, datetime
from utils.constants import RISK_SIGNAL_WEIGHTS
from analytics.velocity import detect_velocity_spike
from utils.date_utils import pct_month_elapsed, days_in_month


def detect_salary_gap(data: dict) -> float:
    """
    Risk that user will run out of money before next salary.
    Returns 0–1 score.
    """
    user = data.get("user")
    df = data.get("df")
    if user is None or df is None or df.empty:
        return 0.0

    today = date.today()
    monthly_income = user.monthly_income or 0
    if monthly_income == 0:
        return 0.0

    month_start = today.replace(day=1)
    this_month = df[
        (df["type"] == "debit") &
        (pd.to_datetime(df["date"]).dt.date >= month_start)
    ]
    spent = this_month["amount"].sum()
    pct_elapsed = pct_month_elapsed(today)
    pct_used = spent / monthly_income

    gap_pressure = pct_used - pct_elapsed
    score = max(0.0, min(1.0, gap_pressure * 2))
    return round(score, 3)


def detect_budget_overflow(data: dict) -> float:
    """
    How many budget categories are over their limits.
    Returns average overflow ratio (0–1).
    """
    budget_rules = data.get("budget_rules", [])
    df = data.get("df")
    if not budget_rules or df is None or df.empty:
        return 0.0

    today = date.today()
    month_start = today.replace(day=1)
    this_month = df[
        (df["type"] == "debit") &
        (pd.to_datetime(df["date"]).dt.date >= month_start)
    ]

    overflow_scores = []
    for rule in budget_rules:
        cat_spend = this_month[this_month["category"] == rule.category]["amount"].sum()
        ratio = cat_spend / rule.monthly_limit if rule.monthly_limit > 0 else 0
        # Score is how far over the limit (0 if under, up to 1 if 2x over)
        overflow = max(0.0, min(1.0, (ratio - 1.0)))
        overflow_scores.append(overflow)

    return round(np.mean(overflow_scores) if overflow_scores else 0.0, 3)


def detect_emotional_pattern(data: dict) -> float:
    """
    What fraction of spending is emotionally-flagged?
    Returns 0–1 where 1 = all spending is emotional.
    """
    df = data.get("df")
    if df is None or df.empty:
        return 0.0

    debits = df[df["type"] == "debit"]
    if debits.empty:
        return 0.0

    emotional_total = debits[debits.get("is_emotional", pd.Series([False] * len(debits)))]["amount"].sum()
    total = debits["amount"].sum()
    ratio = emotional_total / total if total > 0 else 0.0
    return round(min(1.0, ratio * 2), 3)  # amplify: 50%+ emotional → score 1.0


def detect_missed_recurring(data: dict) -> float:
    """
    Are there recurring bills due soon that the user may not have budget for?
    Returns 0–1.
    """
    recurring = data.get("recurring", [])
    user = data.get("user")
    df = data.get("df")

    if not recurring or user is None or df is None:
        return 0.0

    today = date.today()
    days_left_in_month = days_in_month(today) - today.day
    monthly_income = user.monthly_income or 1

    upcoming_total = 0.0
    for r in recurring:
        next_exp = r.get("next_expected")
        if next_exp:
            try:
                next_date = datetime.strptime(next_exp, "%Y-%m-%d").date()
                if 0 <= (next_date - today).days <= days_left_in_month:
                    upcoming_total += r["avg_amount"]
            except (ValueError, TypeError):
                pass

    month_start = today.replace(day=1)
    spent = df[
        (df["type"] == "debit") & (pd.to_datetime(df["date"]).dt.date >= month_start)
    ]["amount"].sum()

    available = monthly_income - spent
    if upcoming_total == 0:
        return 0.0

    shortfall_ratio = max(0.0, (upcoming_total - available) / upcoming_total)
    return round(min(1.0, shortfall_ratio), 3)


def score_all_signals(data: dict) -> dict:
    """
    Run all risk signals and return weighted scores + aggregate.
    data: {user, df (DataFrame), budget_rules, recurring}
    """
    signal_fns = {
        "velocity_spike":  lambda d: detect_velocity_spike(d["df"]) if d.get("df") is not None else 0.0,
        "salary_gap_risk": detect_salary_gap,
        "budget_overflow": detect_budget_overflow,
        "emotional_spend": detect_emotional_pattern,
        "recurring_miss":  detect_missed_recurring,
    }

    scores = {}
    for name, fn in signal_fns.items():
        try:
            raw = fn(data)
        except Exception:
            raw = 0.0
        weight = RISK_SIGNAL_WEIGHTS.get(name, 0.0)
        scores[name] = {"raw": raw, "weighted": round(raw * weight, 4)}

    scores["aggregate"] = round(sum(s["weighted"] for s in scores.values() if isinstance(s, dict)), 4)
    return scores
