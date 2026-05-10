"""Pick which calendar month to use for month-scoped DRS signals."""

from datetime import date

import pandas as pd


def filter_df_to_calendar_month(df: pd.DataFrame, month_start: date) -> pd.DataFrame:
    """Keep rows whose transaction date falls in the given calendar month."""
    if df.empty:
        return df
    dtm = pd.to_datetime(df["date"])
    mask = (dtm.dt.year == month_start.year) & (dtm.dt.month == month_start.month)
    return df[mask]


def reference_month_start(df: pd.DataFrame, today: date) -> date:
    """
    Prefer the current calendar month when it contains debits.

    When the dataset ends before the current calendar month (typical seeded CSV behind the
    system clock), anchor to the latest month present in the file so metrics stay populated.

    If the clock month has debits (live uploads), use that month.
    """
    debits = df[df["type"] == "debit"]
    if debits.empty:
        return today.replace(day=1)

    latest_day = pd.to_datetime(debits["date"]).max().date()
    cur_start = today.replace(day=1)

    if latest_day < cur_start:
        return latest_day.replace(day=1)

    cur_debits = filter_df_to_calendar_month(debits, cur_start)
    if len(cur_debits) > 0:
        return cur_start

    return latest_day.replace(day=1)
