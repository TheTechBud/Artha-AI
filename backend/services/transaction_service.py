import io
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from analytics.engine import AnalyticsEngine
from analytics.recurring import tag_recurring_in_df
from analytics.salary_cycle import flag_emotional_transactions
from services.analytics_service import AnalyticsService
from services.drs_service import DRSService
from services.intervention_service import InterventionService
from ai.orchestrator import AIOrchestrator
from db.models import BehavioralProfile
from utils.constants import ALERT_THRESHOLD
from db import crud
from observability.logger import get_logger

logger = get_logger("services.transaction")


class TransactionService:
    def __init__(self, db: Session):
        self.db = db
        self.analytics = AnalyticsEngine(db)

    def process_csv(self, user_id: int, csv_bytes: bytes) -> dict:
        """
        Full upload pipeline:
        1. Parse CSV
        2. Clean and normalize
        3. Categorize
        4. Detect recurring
        5. Flag emotional
        6. Bulk insert
        """
        df = self._parse_csv(csv_bytes)
        df = self._clean(df)
        df = self.analytics.categorize_dataframe(df)
        df = tag_recurring_in_df(df)
        df = flag_emotional_transactions(df)

        rows = []
        for _, row in df.iterrows():
            rows.append({
                "user_id": user_id,
                "date": row["date"],
                "description": row["description"],
                "amount": float(row["amount"]),
                "type": row["type"],
                "category": row.get("category", "Uncategorized"),
                "is_recurring": bool(row.get("is_recurring", False)),
                "recurring_group_id": row.get("recurring_group_id"),
                "is_emotional": bool(row.get("is_emotional", False)),
                "raw_description": row["description"],
            })

        count = crud.bulk_insert_transactions(self.db, rows)
        logger.info(f"Inserted {count} transactions for user {user_id}")
        return {"inserted": count, "rows_processed": len(df)}

    async def run_post_upload_pipeline(self, user_id: int) -> dict:
        """
        Hackathon-safe post-upload orchestration in-process:
        - recalculate DRS (+ conditional explanation)
        - refresh archetype/profile
        - recompute risk signals
        - generate intervention only if risk threshold is crossed
        """
        drs_service = DRSService(self.db)
        drs_result = await drs_service.calculate_with_explanation(user_id)

        user = crud.get_user(self.db, user_id)
        summary = self.analytics.get_summary(user_id)
        debits_total = summary["total_spend"] or 1
        food_spend = next(
            (c["total"] for c in summary["by_category"] if c["category"] == "Food & Dining"),
            0,
        )
        archetype_context = {
            "name": user.name if user else "User",
            "monthly_income": user.monthly_income if user else 0,
            "top_categories": ", ".join(c["category"] for c in summary["by_category"][:3]),
            "emotional_ratio": round(summary["emotional_spend_total"] / debits_total * 100, 1),
            "weekend_ratio": "1.8x weekday average",
            "cv": "0.42",
            "food_pct": round(food_spend / debits_total * 100, 1),
            "velocity_spike": "Yes" if summary["total_spend"] > 50000 else "No",
            "net_savings": f"₹{summary['net']:,.0f}",
        }

        orchestrator = AIOrchestrator()
        archetype_result = await orchestrator.classify_archetype(archetype_context)

        profile = self.db.query(BehavioralProfile).filter_by(user_id=user_id).first()
        import json
        if profile:
            profile.archetype = archetype_result.get("archetype")
            profile.confidence = archetype_result.get("confidence", 0.5)
            profile.key_signals = json.dumps(archetype_result.get("key_signals", []))
        else:
            profile = BehavioralProfile(
                user_id=user_id,
                archetype=archetype_result.get("archetype"),
                confidence=archetype_result.get("confidence", 0.5),
                key_signals=json.dumps(archetype_result.get("key_signals", [])),
            )
            self.db.add(profile)

        if user:
            user.archetype = archetype_result.get("archetype")
        self.db.commit()

        analytics_service = AnalyticsService(self.db)
        risk_signals = analytics_service.get_risk_signals(user_id)
        aggregate_risk = risk_signals.get("aggregate", 0.0)

        intervention_payload = None
        if aggregate_risk >= ALERT_THRESHOLD:
            top_signal = None
            top_signal_score = 0.0
            for signal_name, signal_data in risk_signals.items():
                if signal_name == "aggregate" or not isinstance(signal_data, dict):
                    continue
                raw = signal_data.get("raw", 0.0)
                if raw > top_signal_score:
                    top_signal = signal_name
                    top_signal_score = raw

            if top_signal:
                intervention_service = InterventionService(self.db)
                context = intervention_service.build_context(
                    user_id=user_id,
                    risk_type=top_signal,
                    risk_score=top_signal_score,
                )
                context["drs_score"] = drs_result["score"]
                generated = await orchestrator.generate_intervention(context)
                saved = intervention_service.store(user_id, generated)
                intervention_payload = {"id": saved.id, "urgency": saved.urgency}

        return {
            "drs_score": drs_result["score"],
            "archetype": archetype_result.get("archetype"),
            "risk_aggregate": aggregate_risk,
            "intervention_generated": intervention_payload,
        }

    def _parse_csv(self, csv_bytes: bytes) -> pd.DataFrame:
        try:
            df = pd.read_csv(io.BytesIO(csv_bytes))
        except Exception as e:
            raise ValueError(f"Could not parse CSV: {e}")

        # Normalize column names
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

        required = {"date", "description", "amount"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"CSV missing columns: {missing}")

        return df

    def _clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.dropna(subset=["date", "amount"])
        # Seed CSVs use ISO dates (YYYY-MM-DD); dayfirst=True mis-parses them into wrong months.
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["amount"] = pd.to_numeric(df["amount"].astype(str).str.replace(",", ""), errors="coerce").abs()
        df = df.dropna(subset=["amount"])
        df = df[df["amount"] > 0]

        # Ensure type column exists
        if "type" not in df.columns:
            df["type"] = "debit"
        df["type"] = df["type"].str.strip().str.lower()
        df["type"] = df["type"].where(df["type"].isin(["debit", "credit"]), "debit")

        df["description"] = df["description"].fillna("Unknown").str.strip()
        return df.reset_index(drop=True)
