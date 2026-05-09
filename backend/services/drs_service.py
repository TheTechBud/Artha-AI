from datetime import datetime
from sqlalchemy.orm import Session
from db import crud
from analytics.engine import AnalyticsEngine
from utils.constants import DRS_WEIGHTS, DRS_CHANGE_THRESHOLD
from utils.formatting import drs_label, drs_color
from observability.logger import get_logger
from ai.orchestrator import AIOrchestrator

logger = get_logger("services.drs")


class DRSService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsEngine(db)

    def calculate(self, user_id: int) -> dict:
        """Compute DRS, store to history, return full result."""
        components = self.analytics.get_drs_components(user_id)

        weighted_sum = sum(
            components[key] * DRS_WEIGHTS[key]
            for key in DRS_WEIGHTS
            if key in components
        )
        score = round(min(100.0, max(0.0, weighted_sum * 100)), 1)

        logger.info(f"DRS calculated for user {user_id}: {score}")

        # Check if we should generate an explanation
        prev = crud.get_latest_drs(self.db, user_id)
        explanation = None
        if prev and abs(score - prev.score) >= DRS_CHANGE_THRESHOLD:
            logger.info(f"DRS changed by {score - prev.score:.1f} — explanation eligible")

        saved = crud.save_drs(self.db, user_id, score, components, explanation)

        return {
            "score": score,
            "label": drs_label(score),
            "color": drs_color(score),
            "components": components,
            "explanation": explanation,
            "calculated_at": saved.calculated_at,
        }

    async def calculate_with_explanation(self, user_id: int) -> dict:
        """
        Compute DRS, store to history, and generate AI explanation only when
        score delta crosses the configured threshold.
        """
        components = self.analytics.get_drs_components(user_id)

        weighted_sum = sum(
            components[key] * DRS_WEIGHTS[key]
            for key in DRS_WEIGHTS
            if key in components
        )
        score = round(min(100.0, max(0.0, weighted_sum * 100)), 1)
        logger.info(f"DRS calculated for user {user_id}: {score}")

        prev = crud.get_latest_drs(self.db, user_id)
        explanation = None
        if prev and abs(score - prev.score) >= DRS_CHANGE_THRESHOLD:
            logger.info(f"DRS changed by {score - prev.score:.1f} — generating explanation")
            user = crud.get_user(self.db, user_id)
            orchestrator = AIOrchestrator()
            explanation = await orchestrator.explain_drs(
                name=user.name if user else "User",
                prev_score=prev.score,
                current_score=score,
                components=components,
            )

        saved = crud.save_drs(self.db, user_id, score, components, explanation)

        return {
            "score": score,
            "label": drs_label(score),
            "color": drs_color(score),
            "components": components,
            "explanation": explanation,
            "calculated_at": saved.calculated_at,
        }

    def get_current(self, user_id: int) -> dict | None:
        """Return latest stored DRS or recalculate if none exists."""
        row = crud.get_latest_drs(self.db, user_id)
        if not row:
            return self.calculate(user_id)

        return {
            "score": row.score,
            "label": drs_label(row.score),
            "color": drs_color(row.score),
            "components": {
                "budget_adherence": row.c1_budget_adherence,
                "velocity_stability": row.c2_velocity_stability,
                "savings_rate": row.c3_savings_rate,
                "recurring_coverage": row.c4_recurring_coverage,
                "emotional_spend": row.c5_emotional_spend,
                "salary_gap": row.c6_salary_gap,
            },
            "explanation": row.explanation,
            "calculated_at": row.calculated_at,
        }

    def get_history(self, user_id: int, days: int = 30) -> list[dict]:
        rows = crud.get_drs_history(self.db, user_id, days)
        return [
            {"score": r.score, "calculated_at": r.calculated_at}
            for r in reversed(rows)
        ]
