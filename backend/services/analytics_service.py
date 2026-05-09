from sqlalchemy.orm import Session
from analytics.engine import AnalyticsEngine
from analytics.risk_signals import score_all_signals
from db import crud
from observability.logger import get_logger

logger = get_logger("services.analytics")


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
        self.engine = AnalyticsEngine(db)

    def get_summary(self, user_id: int) -> dict:
        return self.engine.get_summary(user_id)

    def get_velocity(self, user_id: int) -> list[dict]:
        return self.engine.get_velocity(user_id)

    def get_recurring(self, user_id: int) -> list[dict]:
        return self.engine.get_recurring(user_id)

    def get_risk_signals(self, user_id: int) -> dict:
        data = self.engine.get_risk_data(user_id)
        scores = score_all_signals(data)
        logger.info(f"Risk signals for user {user_id}: aggregate={scores.get('aggregate', 0):.3f}")
        return scores

    def get_predictions_calendar(self, user_id: int) -> list[dict]:
        """
        Return a month-view calendar with risk-flagged dates.
        Combines recurring bill dates (amber) + high-risk dates (red).
        """
        from datetime import date, timedelta
        import calendar as cal_module

        today = date.today()
        days_in_month = cal_module.monthrange(today.year, today.month)[1]
        recurring = self.engine.get_recurring(user_id)
        signals = score_all_signals(self.engine.get_risk_data(user_id))

        calendar_days = []
        for day in range(1, days_in_month + 1):
            d = today.replace(day=day)
            day_type = "normal"

            # Check if any recurring bill is due on this day
            for r in recurring:
                ne = r.get("next_expected")
                if ne:
                    try:
                        from datetime import datetime
                        nd = datetime.strptime(ne, "%Y-%m-%d").date()
                        if nd == d:
                            day_type = "amber"  # recurring due
                    except (ValueError, TypeError):
                        pass

            # Flag high-risk dates (elevated spending probability)
            if signals.get("aggregate", 0) > 0.6 and d >= today:
                if d.weekday() in [4, 5]:  # Fri-Sat
                    day_type = "red"  # predicted overspend

            calendar_days.append({
                "date": d.isoformat(),
                "day": day,
                "type": day_type,
                "is_today": d == today,
                "is_past": d < today,
            })

        return calendar_days
