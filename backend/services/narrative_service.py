import json
from sqlalchemy.orm import Session
from analytics.engine import AnalyticsEngine
from services.analytics_service import AnalyticsService
from db import crud
from utils.formatting import drs_label
from observability.logger import get_logger

logger = get_logger("services.narrative")


class NarrativeService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsEngine(db)

    def get_latest(self, user_id: int):
        return crud.get_latest_narrative(self.db, user_id)

    def build_context(self, user_id: int, drs_score: float) -> dict:
        user = crud.get_user(self.db, user_id)
        summary = self.analytics.get_summary(user_id)

        total = summary["total_spend"] or 1
        emotional_pct = round(summary["emotional_spend_total"] / total * 100, 1) if total > 0 else 0

        top_categories = ", ".join(
            f"{c['category']} (₹{c['total']:,.0f}, {c['pct_of_total']}%)"
            for c in summary["by_category"][:4]
        )

        recurring_due = ", ".join(
            r["name"] for r in summary["recurring"][:3]
        ) or "None detected"

        risk_flags = self._risk_flags_summary(user_id)

        return {
            "name": user.name if user else "User",
            "archetype": (user.archetype or "unknown") if user else "unknown",
            "drs_score": drs_score,
            "drs_label": drs_label(drs_score),
            "total_spend": f"{summary['total_spend']:,.0f}",
            "top_categories": top_categories,
            "emotional_spend": f"{summary['emotional_spend_total']:,.0f}",
            "emotional_pct": emotional_pct,
            "recurring_due": recurring_due,
            "risk_flags": risk_flags,
            "week_over_week": "Data available for trend analysis",
        }

    def _risk_flags_summary(self, user_id: int) -> str:
        svc = AnalyticsService(self.db)
        blob = svc.get_risk_signals(user_id)
        agg = blob.get("aggregate", 0.0)
        lines = []
        for name, val in blob.items():
            if name == "aggregate" or not isinstance(val, dict):
                continue
            raw = val.get("raw", 0.0)
            if raw >= 0.35:
                lines.append(f"{name.replace('_', ' ')} ({raw:.0%})")
        if lines:
            return f"Aggregate risk index {agg:.0%}; elevated: " + "; ".join(lines[:4])
        return f"Aggregate risk index {agg:.0%}; no single signal dominating"

    def store(self, user_id: int, text: str, drs_score: float) -> object:
        insights = json.dumps(["Spending patterns analyzed", "DRS calculated", "AI narrative generated"])
        return crud.create_narrative(self.db, user_id, text, insights, drs_score)
