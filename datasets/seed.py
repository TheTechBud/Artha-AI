"""
Seed script — loads demo data into the SQLite database.

Usage:
    cd backend
    python ../datasets/seed.py --persona riya
    python ../datasets/seed.py --reset       # wipe and re-seed
"""

import sys
import os
import argparse
import json

# Allow importing from backend/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "backend", ".env"))

from db.database import SessionLocal, init_db, engine
from db.models import Base, User, BudgetRule, DRSHistory, BehavioralProfile
from services.transaction_service import TransactionService
from services.drs_service import DRSService
from utils.constants import DEFAULT_BUDGET_RULES
from observability.logger import get_logger

logger = get_logger("seed")

PERSONAS = {
    "riya": {
        "id": 1,
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
    }
}


def reset_db():
    logger.info("Dropping all tables…")
    Base.metadata.drop_all(bind=engine)
    logger.info("Recreating tables…")
    init_db()


def seed_persona(name: str):
    persona = PERSONAS.get(name)
    if not persona:
        print(f"Unknown persona: {name}. Available: {list(PERSONAS.keys())}")
        sys.exit(1)

    db = SessionLocal()
    try:
        # Create / update user
        user = db.query(User).filter(User.id == persona["id"]).first()
        if user:
            logger.info(f"User {persona['name']} already exists — updating")
            user.name = persona["name"]
            user.monthly_income = persona["monthly_income"]
            user.salary_day = persona["salary_day"]
            user.archetype = persona["archetype"]
        else:
            user = User(
                id=persona["id"],
                name=persona["name"],
                email=persona["email"],
                monthly_income=persona["monthly_income"],
                salary_day=persona["salary_day"],
                archetype=persona["archetype"],
            )
            db.add(user)

        db.commit()
        logger.info(f"User saved: {user.name} (id={user.id})")

        # Budget rules
        for category, limit in persona["budget_rules"].items():
            existing = db.query(BudgetRule).filter_by(user_id=user.id, category=category).first()
            if existing:
                existing.monthly_limit = limit
            else:
                db.add(BudgetRule(user_id=user.id, category=category, monthly_limit=limit))
        db.commit()
        logger.info("Budget rules seeded")

        # Transactions
        csv_path = persona["csv"]
        if not os.path.exists(csv_path):
            logger.warning(f"CSV not found: {csv_path} — skipping transactions")
        else:
            with open(csv_path, "rb") as f:
                csv_bytes = f.read()
            svc = TransactionService(db)
            result = svc.process_csv(user.id, csv_bytes)
            logger.info(f"Transactions imported: {result['inserted']} rows")

        # Calculate initial DRS
        drs_svc = DRSService(db)
        drs = drs_svc.calculate(user.id)
        logger.info(f"Initial DRS calculated: {drs['score']} ({drs['label']})")

        # Pre-set behavioral profile
        profile = db.query(BehavioralProfile).filter_by(user_id=user.id).first()
        if not profile:
            profile = BehavioralProfile(
                user_id=user.id,
                archetype=persona["archetype"],
                confidence=0.87,
                key_signals=json.dumps([
                    "High Zomato/Swiggy spend on weekends",
                    "Late-night orders (11pm–1am) on Fridays",
                    "Food & Dining exceeds budget by month week 3",
                ]),
            )
            db.add(profile)
            db.commit()

        print(f"\n✅ Demo data seeded successfully!")
        print(f"   User:  {user.name}")
        print(f"   DRS:   {drs['score']} — {drs['label']}")
        print(f"\n   Run the backend: uvicorn main:app --reload")
        print(f"   API docs:        http://localhost:8000/docs\n")

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Seed Artha AI demo data")
    parser.add_argument("--persona", default="riya", choices=list(PERSONAS.keys()))
    parser.add_argument("--reset", action="store_true", help="Drop and recreate DB first")
    args = parser.parse_args()

    init_db()

    if args.reset:
        reset_db()

    seed_persona(args.persona)


if __name__ == "__main__":
    main()
