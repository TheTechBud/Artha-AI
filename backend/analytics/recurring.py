import pandas as pd
from datetime import timedelta, date


def classify_frequency(avg_gap_days: float) -> str:
    if avg_gap_days <= 9:
        return "weekly"
    if avg_gap_days <= 18:
        return "biweekly"
    return "monthly"


def detect_recurring(df: pd.DataFrame) -> list[dict]:
    """
    Identify transactions that recur with a consistent interval.
    Returns a list of recurring pattern dicts.
    """
    debits = df[df["type"] == "debit"].copy()
    if debits.empty:
        return []

    debits["description_upper"] = debits["description"].str.upper().str.strip()
    groups = debits.groupby("description_upper")

    recurring = []
    for desc, group in groups:
        if len(group) < 2:
            continue

        group = group.sort_values("date")
        gaps = group["date"].diff().dt.days.dropna()

        if gaps.empty:
            continue

        avg_gap = gaps.mean()
        std_gap = gaps.std() if len(gaps) > 1 else 0

        # Consistent interval: std < 5 days OR coefficient of variation < 0.25
        is_consistent = std_gap < 5 or (avg_gap > 0 and std_gap / avg_gap < 0.25)

        if is_consistent and 5 <= avg_gap <= 35:
            last_date = group["date"].max()
            next_date = last_date + timedelta(days=avg_gap)

            recurring.append({
                "name": desc,
                "avg_amount": round(group["amount"].mean(), 2),
                "frequency": classify_frequency(avg_gap),
                "next_expected": next_date.strftime("%Y-%m-%d") if hasattr(next_date, "strftime") else str(next_date),
                "last_seen": last_date.strftime("%Y-%m-%d") if hasattr(last_date, "strftime") else str(last_date),
                "occurrence_count": len(group),
            })

    return sorted(recurring, key=lambda x: x["avg_amount"], reverse=True)


def tag_recurring_in_df(df: pd.DataFrame) -> pd.DataFrame:
    """Add is_recurring and recurring_group_id columns to transaction DataFrame."""
    df = df.copy()
    df["is_recurring"] = False
    df["recurring_group_id"] = None

    patterns = detect_recurring(df)
    recurring_names = {p["name"] for p in patterns}

    mask = df["description"].str.upper().str.strip().isin(recurring_names)
    df.loc[mask, "is_recurring"] = True
    df.loc[mask, "recurring_group_id"] = df.loc[mask, "description"].str.upper().str.strip()

    return df
