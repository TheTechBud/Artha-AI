import json
from sqlalchemy.orm import Session
from analytics.engine import AnalyticsEngine
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
            "risk_flags": "Velocity spike detected" if summary["total_spend"] > 30000 else "No critical flags",
            "week_over_week": "Data available for trend analysis",
        }

    def store(self, user_id: int, text: str, drs_score: float) -> object:
        insights = json.dumps(["Spending patterns analyzed", "DRS calculated", "AI narrative generated"])
        return crud.create_narrative(self.db, user_id, text, insights, drs_score)
