"""
Seed script — loads demo data into the SQLite database.

Single demo user (id=1). Switching --persona replaces that slot so only one
behavioral scenario is active at a time.

Usage:
    cd backend
    python ../datasets/seed.py --persona riya
    python ../datasets/seed.py --persona arjun
    python ../datasets/seed.py --reset --persona arjun   # wipe DB then seed
"""

import sys
import os
import argparse
import json

# Allow importing from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from sqlalchemy.orm import Session

from db.database import SessionLocal, init_db, engine
from db.models import (
    Base,
    User,
    BudgetRule,
    DRSHistory,
    BehavioralProfile,
    Transaction,
    Intervention,
    Narrative,
    Prediction,
    RecurringPattern,
)
from services.transaction_service import TransactionService
from services.drs_service import DRSService
from observability.logger import get_logger

logger = get_logger("seed")

# Matches backend single-user demo (api routes USER_ID = 1).
DEMO_USER_ID = 1

PERSONAS = {
    "riya": {
        "name": "Riya Sharma",
        "email": "riya@demo.com",
        "monthly_income": 85000.0,
        "salary_day": 1,
        "archetype": "stress_spender",
        "csv": os.path.join(os.path.dirname(__file__), "transactions", "riya_transactions.csv"),
        "budget_rules": {
            "Food & Dining": 12000,
            "Transport": 4000,
            "Entertainment": 3000,
            "Shopping": 8000,
            "Groceries": 6000,
            "Health": 3000,
            "Rent/EMI": 23000,
        },
        "key_signals": [
            "High Zomato/Swiggy spend on weekends",
            "Late-night orders (11pm–1am) on Fridays",
            "Food & Dining exceeds budget by month week 3",
        ],
    },
    "arjun": {
        "name": "Arjun Mehta",
        "email": "arjun@demo.com",
        "monthly_income": 120000.0,
        "salary_day": 1,
        "archetype": "planner",
        "csv": os.path.join(os.path.dirname(__file__), "transactions", "arjun_transactions.csv"),
        "budget_rules": {
            "Food & Dining": 7000,
            "Transport": 4500,
            "Entertainment": 2800,
            "Shopping": 5500,
            "Groceries": 9000,
            "Health": 3500,
            "Rent/EMI": 28000,
        },
        "key_signals": [
            "Salary-day SIP and mutual fund transfers before discretionary spend",
            "Groceries skew to DMART/BigBasket vs food delivery",
            "Food & Dining consistently under cap vs income",
        ],
    },
}


def reset_db():
    logger.info("Dropping all tables…")
    Base.metadata.drop_all(bind=engine)
    logger.info("Recreating tables…")
    init_db()


def clear_demo_user_data(db: Session, user_id: int) -> None:
    """Remove all rows for the demo user so another persona can load without stacking data."""
    db.query(Intervention).filter(Intervention.user_id == user_id).delete()
    db.query(Prediction).filter(Prediction.user_id == user_id).delete()
    db.query(Narrative).filter(Narrative.user_id == user_id).delete()
    db.query(DRSHistory).filter(DRSHistory.user_id == user_id).delete()
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(BehavioralProfile).filter(BehavioralProfile.user_id == user_id).delete()
    db.query(BudgetRule).filter(BudgetRule.user_id == user_id).delete()
    db.query(RecurringPattern).filter(RecurringPattern.user_id == user_id).delete()
    db.commit()
    logger.info(f"Cleared existing demo data for user_id={user_id}")


def seed_persona(name: str):
    persona = PERSONAS.get(name)
    if not persona:
        print(f"Unknown persona: {name}. Available: {list(PERSONAS.keys())}")
        sys.exit(1)

    db = SessionLocal()
    try:
        clear_demo_user_data(db, DEMO_USER_ID)

        user = db.query(User).filter(User.id == DEMO_USER_ID).first()
        if user:
            logger.info(f"Updating demo user row — {persona['name']}")
            user.name = persona["name"]
            user.email = persona["email"]
            user.monthly_income = persona["monthly_income"]
            user.salary_day = persona["salary_day"]
            user.archetype = persona["archetype"]
        else:
            user = User(
                id=DEMO_USER_ID,
                name=persona["name"],
                email=persona["email"],
                monthly_income=persona["monthly_income"],
                salary_day=persona["salary_day"],
                archetype=persona["archetype"],
            )
            db.add(user)

        db.commit()
        logger.info(f"User saved: {user.name} (id={user.id})")

        for category, limit in persona["budget_rules"].items():
            db.add(BudgetRule(user_id=user.id, category=category, monthly_limit=limit))
        db.commit()
        logger.info("Budget rules seeded")

        csv_path = persona["csv"]
        if not os.path.exists(csv_path):
            logger.warning(f"CSV not found: {csv_path} — skipping transactions")
        else:
            with open(csv_path, "rb") as f:
                csv_bytes = f.read()
            svc = TransactionService(db)
            result = svc.process_csv(user.id, csv_bytes)
            logger.info(f"Transactions imported: {result['inserted']} rows")

        drs_svc = DRSService(db)
        drs = drs_svc.calculate(user.id)
        logger.info(f"Initial DRS calculated: {drs['score']} ({drs['label']})")

        profile = BehavioralProfile(
            user_id=user.id,
            archetype=persona["archetype"],
            confidence=0.87,
            key_signals=json.dumps(persona["key_signals"]),
        )
        db.add(profile)
        db.commit()

        print(f"\n✅ Demo data seeded successfully!")
        print(f"   Persona: {name}")
        print(f"   User:    {user.name}")
        print(f"   DRS:     {drs['score']} — {drs['label']}")
        print(f"\n   Run the backend: uvicorn main:app --reload")
        print(f"   API docs:        http://localhost:8000/docs\n")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Seed Artha AI demo data")
    parser.add_argument(
        "--persona",
        default="riya",
        choices=sorted(PERSONAS.keys()),
        help="Demo behavioral dataset (loads into user id=%s)" % DEMO_USER_ID,
    )
    parser.add_argument("--reset", action="store_true", help="Drop and recreate DB first")
    args = parser.parse_args()

    init_db()

    if args.reset:
        reset_db()

    seed_persona(args.persona)


if __name__ == "__main__":
    main()
