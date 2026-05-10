import calendar

import pandas as pd
import numpy as np
from datetime import date, datetime
from sqlalchemy.orm import Session

from db import crud
from db.models import User, Transaction
from utils.constants import (
    CATEGORY_RULES,
    DRS_SAVINGS_MARGIN_TARGET,
    DRS_SAVINGS_INVEST_BLEND,
    DRS_SAVINGS_INVEST_SCALE,
    DRS_SAVINGS_INVEST_CEILING,
    DRS_VELOCITY_CV_SCALE,
    DRS_VELOCITY_CV_CAP,
)
from analytics.reference_period import reference_month_start, filter_df_to_calendar_month
from analytics.velocity import compute_velocity, velocity_to_chart_data, detect_velocity_spike
from analytics.recurring import detect_recurring, tag_recurring_in_df
from analytics.salary_cycle import flag_emotional_transactions, emotional_spend_score, salary_gap_score
from analytics.budget_tracker import compute_budget_usage, budget_adherence_score


class AnalyticsEngine:
    def __init__(self, db: Session):
        self.db = db

    def load_transactions_df(self, user_id: int, days: int = 90) -> pd.DataFrame:
        """Load user transactions as a pandas DataFrame."""
        txns = self.db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).all()

        if not txns:
            return pd.DataFrame(columns=["id", "date", "description", "amount", "type", "category", "is_emotional", "is_recurring"])

        records = [{
            "id": t.id,
            "date": pd.to_datetime(t.date),
            "description": t.description,
            "amount": t.amount,
            "type": t.type,
            "category": t.category or "Uncategorized",
            "is_emotional": t.is_emotional or False,
            "is_recurring": t.is_recurring or False,
        } for t in txns]

        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        return df

    def categorize_transaction(self, description: str) -> str:
        """Rule-based categorization. Returns category name."""
        desc_upper = description.upper().strip()
        for category, keywords in CATEGORY_RULES.items():
            if any(kw in desc_upper for kw in keywords):
                return category
        return "Uncategorized"

    def categorize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply categorization to all rows."""
        df = df.copy()
        df["category"] = df["description"].apply(self.categorize_transaction)
        return df

    def get_summary(self, user_id: int) -> dict:
        """Full analytics summary for the dashboard."""
        df = self.load_transactions_df(user_id)

        if df.empty:
            return self._empty_summary()

        df = flag_emotional_transactions(df)

        # Current month
        today = date.today()
        month_start = today.replace(day=1)
        this_month = df[pd.to_datetime(df["date"]).dt.date >= month_start]

        debits = df[df["type"] == "debit"]
        credits = df[df["type"] == "credit"]
        total_spend = debits["amount"].sum()
        total_income = credits["amount"].sum()

        # Category breakdown
        cat_spend = debits.groupby("category")["amount"].agg(["sum", "count"]).reset_index()
        cat_spend.columns = ["category", "total", "count"]
        cat_spend["pct_of_total"] = (cat_spend["total"] / total_spend * 100).round(1) if total_spend > 0 else 0
        cat_spend = cat_spend.sort_values("total", ascending=False)

        # Velocity
        velocity_data = velocity_to_chart_data(df)

        # Recurring
        recurring = detect_recurring(df)

        # Emotional spend
        emotional_total = debits[debits["is_emotional"]]["amount"].sum() if "is_emotional" in debits.columns else 0

        top_category = cat_spend.iloc[0]["category"] if not cat_spend.empty else "N/A"

        return {
            "total_spend": round(total_spend, 2),
            "total_income": round(total_income, 2),
            "net": round(total_income - total_spend, 2),
            "by_category": cat_spend.to_dict("records"),
            "velocity_data": velocity_data,
            "recurring": recurring,
            "emotional_spend_total": round(emotional_total, 2),
            "top_category": top_category,
            "month": today.strftime("%B %Y"),
        }

    def get_velocity(self, user_id: int) -> list[dict]:
        df = self.load_transactions_df(user_id)
        return velocity_to_chart_data(df)

    def get_recurring(self, user_id: int) -> list[dict]:
        df = self.load_transactions_df(user_id)
        return detect_recurring(df)

    def get_risk_data(self, user_id: int) -> dict:
        """Prepare the data dict used by risk_signals.score_all_signals."""
        user = crud.get_user(self.db, user_id)
        df = self.load_transactions_df(user_id)
        df = flag_emotional_transactions(df)
        budget_rules = crud.get_budget_rules(self.db, user_id)
        recurring = detect_recurring(df)
        return {
            "user": user,
            "df": df,
            "budget_rules": budget_rules,
            "recurring": recurring,
        }

    def get_drs_components(self, user_id: int) -> dict:
        """Compute raw 0–1 scores for all 6 DRS components."""
        user = crud.get_user(self.db, user_id)
        df = self.load_transactions_df(user_id)
        df = flag_emotional_transactions(df)
        budget_rules = crud.get_budget_rules(self.db, user_id)

        monthly_income = user.monthly_income if user else 0
        salary_day = user.salary_day if user and user.salary_day else 1
        today = date.today()
        month_ref = reference_month_start(df, today)

        # C1
        c1 = budget_adherence_score(df, budget_rules, month_ref)

        # C2 — velocity stability (normalized spend lumpiness)
        velocity = compute_velocity(df)
        if not velocity.empty and len(velocity) > 1:
            mean_v = velocity["rolling_spend"].mean()
            std_v = velocity["rolling_spend"].std()
            cv = std_v / mean_v if mean_v > 0 else 1.0
            cv_adj = min(float(cv), DRS_VELOCITY_CV_CAP)
            c2 = round(max(0.0, 1.0 - min(1.0, cv_adj * DRS_VELOCITY_CV_SCALE)), 4)
        else:
            c2 = 0.5

        # C3 — savings margin + Savings-category consistency (multi-month aware)
        periods = sorted(pd.to_datetime(df["date"]).dt.to_period("M").unique())
        debits_all = df[df["type"] == "debit"]
        if not len(periods):
            c3 = 0.5
        else:
            margins = []
            for p in periods:
                sub = df[pd.to_datetime(df["date"]).dt.to_period("M") == p]
                deb_m = sub[sub["type"] == "debit"]["amount"].sum()
                if monthly_income > 0:
                    m = (monthly_income - deb_m) / monthly_income
                    margins.append(max(0.0, min(1.0, m)))
            avg_margin = float(np.mean(margins)) if margins else 0.0
            c3_core = min(1.0, max(0.0, avg_margin / DRS_SAVINGS_MARGIN_TARGET))

            n_months = len(periods)
            denom_inc = monthly_income * n_months if monthly_income > 0 else 0.0
            savings_debits = debits_all[debits_all["category"] == "Savings"]["amount"].sum()
            invest_share = savings_debits / max(denom_inc, 1.0)
            invest_component = min(
                DRS_SAVINGS_INVEST_CEILING,
                invest_share * DRS_SAVINGS_INVEST_SCALE,
            )

            c3 = (
                c3_core * (1.0 - DRS_SAVINGS_INVEST_BLEND)
                + invest_component * DRS_SAVINGS_INVEST_BLEND
            )
            c3 = round(min(1.0, max(0.0, c3)), 4)
            # Compress very high savings/investment scores so planners land ~65–80 DRS, not mid‑80s
            if c3 > 0.68:
                c3 = round(0.52 + (c3 - 0.68) * 0.35, 4)

        # C4 — recurring coverage (headroom vs obligations due soon)
        recurring = detect_recurring(df)
        days_left = calendar.monthrange(today.year, today.month)[1] - today.day
        upcoming_total = 0.0
        for r in recurring:
            ne = r.get("next_expected")
            if ne:
                try:
                    next_date = datetime.strptime(ne, "%Y-%m-%d").date()
                    if 0 <= (next_date - today).days <= days_left:
                        upcoming_total += r["avg_amount"]
                except (ValueError, TypeError):
                    pass

        month_df = filter_df_to_calendar_month(df, month_ref)
        debits_m = month_df[month_df["type"] == "debit"]
        spent_this_cycle = debits_m[~debits_m["category"].isin(["Savings"])]["amount"].sum()
        available_cash = monthly_income - spent_this_cycle
        c4 = min(1.0, available_cash / upcoming_total) if upcoming_total > 0 else 1.0
        c4 = round(max(0.0, c4), 4)

        # C5 — emotional spend
        c5 = emotional_spend_score(df)

        # C6 — salary gap
        c6 = salary_gap_score(df, monthly_income, salary_day, month_ref, today)

        return {
            "budget_adherence": c1,
            "velocity_stability": c2,
            "savings_rate": c3,
            "recurring_coverage": c4,
            "emotional_spend": c5,
            "salary_gap": c6,
        }

    def _empty_summary(self) -> dict:
        return {
            "total_spend": 0,
            "total_income": 0,
            "net": 0,
            "by_category": [],
            "velocity_data": [],
            "recurring": [],
            "emotional_spend_total": 0,
            "top_category": "N/A",
            "month": date.today().strftime("%B %Y"),
        }
