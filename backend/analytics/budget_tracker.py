import pandas as pd
from datetime import date

from analytics.reference_period import filter_df_to_calendar_month


def compute_budget_usage(df: pd.DataFrame, budget_rules: list, month_start: date) -> list[dict]:
    """
    For each budget rule, compute how much has been spent in the given calendar month
    and what % of the limit that represents.
    """
    month_df = filter_df_to_calendar_month(df, month_start)
    this_month = month_df[month_df["type"] == "debit"]

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


def budget_adherence_score(df: pd.DataFrame, budget_rules: list, month_start: date) -> float:
    """
    C1 component for DRS. Returns 0–1.
    Starts penalizing at 80% usage, hits 0 at 100%+.
    """
    if not budget_rules:
        return 0.7  # neutral if no rules set

    usage = compute_budget_usage(df, budget_rules, month_start)
    if not usage:
        return 0.7

    scores = []
    for u in usage:
        usage_ratio = u["spent"] / u["limit"] if u["limit"] > 0 else 0
        # Penalize above ~68% of limit for clearer stress-spender vs planner spread
        category_score = max(0.0, 1 - max(0.0, usage_ratio - 0.68) / 0.32)
        scores.append(category_score)

    return round(sum(scores) / len(scores), 4)
