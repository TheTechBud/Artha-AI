from sqlalchemy.orm import Session
from analytics.engine import AnalyticsEngine
from analytics.risk_signals import score_all_signals
from db import crud
from observability.logger import get_logger

logger = get_logger("services.intervention")


class InterventionService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsEngine(db)

    def get_active(self, user_id: int) -> list:
        return crud.get_interventions(self.db, user_id, status="active")

    def dismiss(self, user_id: int, intervention_id: int):
        return crud.dismiss_intervention(self.db, intervention_id)

    def build_context(self, user_id: int, risk_type: str, risk_score: float) -> dict:
        """Assemble context dict for the AI orchestrator."""
        user = crud.get_user(self.db, user_id)
        summary = self.analytics.get_summary(user_id)

        top_categories = ", ".join(
            f"{c['category']} (₹{c['total']:,.0f})"
            for c in summary["by_category"][:3]
        )

        risk_descriptions = {
            "velocity_spike": "Spending velocity has spiked significantly above historical average",
            "salary_gap_risk": "At current pace, money may run out before next salary date",
            "budget_overflow": "Multiple spending categories are exceeding monthly limits",
            "emotional_spend": "High proportion of spending is occurring in emotional contexts",
            "recurring_miss": "Upcoming recurring bills may exceed available funds",
        }

        return {
            "name": user.name if user else "User",
            "archetype": user.archetype if user else "unknown",
            "risk_type": risk_type,
            "risk_score": round(risk_score, 2),
            "drs_score": "—",  # will be filled by route handler
            "context": risk_descriptions.get(risk_type, risk_type),
            "top_categories": top_categories,
            "recent_pattern": f"Emotional spend: ₹{summary['emotional_spend_total']:,.0f}, "
                              f"Top category: {summary['top_category']}",
        }

    def store(self, user_id: int, data: dict, prediction_id=None):
        return crud.create_intervention(self.db, user_id, data, prediction_id)
