import pandas as pd
from datetime import date


def compute_budget_usage(df: pd.DataFrame, budget_rules: list) -> list[dict]:
    """
    For each budget rule, compute how much has been spent this month
    and what % of the limit that represents.
    """
    today = date.today()
    month_start = today.replace(day=1)

    this_month = df[
        (df["type"] == "debit") &
        (pd.to_datetime(df["date"]).dt.date >= month_start)
    ]

    result = []
    for rule in budget_rules:
        spent = this_month[this_month["category"] == rule.category]["amount"].sum()
        usage_pct = round((spent / rule.monthly_limit) * 100, 1) if rule.monthly_limit > 0 else 0.0
        result.append({
            "category": rule.category,
            "limit": rule.monthly_limit,
            "spent": round(spent, 2),
            "usage_pct": usage_pct,
            "is_over": usage_pct > 100,
            "alert": usage_pct >= rule.alert_at_percent,
        })

    return sorted(result, key=lambda x: x["usage_pct"], reverse=True)


def budget_adherence_score(df: pd.DataFrame, budget_rules: list) -> float:
    """
    C1 component for DRS. Returns 0–1.
    Starts penalizing at 80% usage, hits 0 at 100%+.
    """
    if not budget_rules:
        return 0.7  # neutral if no rules set

    usage = compute_budget_usage(df, budget_rules)
    if not usage:
        return 0.7

    scores = []
    for u in usage:
        usage_ratio = u["spent"] / u["limit"] if u["limit"] > 0 else 0
        category_score = max(0.0, 1 - max(0.0, usage_ratio - 0.8) / 0.2)
        scores.append(category_score)

    return round(sum(scores) / len(scores), 4)
