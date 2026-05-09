import io
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from analytics.engine import AnalyticsEngine
from analytics.recurring import tag_recurring_in_df
from analytics.salary_cycle import flag_emotional_transactions
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
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=True)
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
