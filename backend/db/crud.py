from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.models import (
    User, Transaction, DRSHistory, BehavioralProfile,
    Prediction, Intervention, Narrative, BudgetRule
)


# ── Users ──────────────────────────────────────────────────────────────────────

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_or_create_demo_user(db: Session) -> User:
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        user = User(
            id=1,
            name="Riya Sharma",
            email="riya@demo.com",
            monthly_income=85000.0,
            salary_day=1,
            archetype="stress_spender",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


# ── Transactions ──────────────────────────────────────────────────────────────

def get_transactions(
    db: Session,
    user_id: int,
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
) -> list[Transaction]:
    q = db.query(Transaction).filter(Transaction.user_id == user_id)
    if category:
        q = q.filter(Transaction.category == category)
    return q.order_by(desc(Transaction.date)).offset(offset).limit(limit).all()


def count_transactions(db: Session, user_id: int) -> int:
    return db.query(Transaction).filter(Transaction.user_id == user_id).count()


def bulk_insert_transactions(db: Session, txns: list[dict]) -> int:
    objs = [Transaction(**t) for t in txns]
    db.add_all(objs)
    db.commit()
    return len(objs)


# ── DRS ───────────────────────────────────────────────────────────────────────

def save_drs(db: Session, user_id: int, score: float, components: dict, explanation: Optional[str] = None) -> DRSHistory:
    row = DRSHistory(
        user_id=user_id,
        score=score,
        c1_budget_adherence=components.get("budget_adherence", 0),
        c2_velocity_stability=components.get("velocity_stability", 0),
        c3_savings_rate=components.get("savings_rate", 0),
        c4_recurring_coverage=components.get("recurring_coverage", 0),
        c5_emotional_spend=components.get("emotional_spend", 0),
        c6_salary_gap=components.get("salary_gap", 0),
        explanation=explanation,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_latest_drs(db: Session, user_id: int) -> Optional[DRSHistory]:
    return (
        db.query(DRSHistory)
        .filter(DRSHistory.user_id == user_id)
        .order_by(desc(DRSHistory.calculated_at))
        .first()
    )


def get_drs_history(db: Session, user_id: int, days: int = 30) -> list[DRSHistory]:
    return (
        db.query(DRSHistory)
        .filter(DRSHistory.user_id == user_id)
        .order_by(desc(DRSHistory.calculated_at))
        .limit(days)
        .all()
    )


# ── Interventions ─────────────────────────────────────────────────────────────

def get_interventions(db: Session, user_id: int, status: str = "active") -> list[Intervention]:
    return (
        db.query(Intervention)
        .filter(Intervention.user_id == user_id, Intervention.status == status)
        .order_by(desc(Intervention.generated_at))
        .all()
    )


def create_intervention(db: Session, user_id: int, data: dict, prediction_id: Optional[int] = None) -> Intervention:
    obj = Intervention(
        user_id=user_id,
        prediction_id=prediction_id,
        title=data["title"],
        action=data["action"],
        reason=data["reason"],
        urgency=data.get("urgency", "medium"),
        savings_potential=data.get("savings_potential", 0.0),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def dismiss_intervention(db: Session, intervention_id: int) -> Optional[Intervention]:
    obj = db.query(Intervention).filter(Intervention.id == intervention_id).first()
    if obj:
        obj.status = "dismissed"
        db.commit()
        db.refresh(obj)
    return obj


# ── Narratives ────────────────────────────────────────────────────────────────

def get_latest_narrative(db: Session, user_id: int) -> Optional[Narrative]:
    return (
        db.query(Narrative)
        .filter(Narrative.user_id == user_id)
        .order_by(desc(Narrative.generated_at))
        .first()
    )


def create_narrative(db: Session, user_id: int, text: str, insights: str, drs_score: float) -> Narrative:
    from datetime import date as dt_date
    today = dt_date.today()
    # week_start = Monday of current week
    week_start = today  # simplified
    obj = Narrative(
        user_id=user_id,
        week_start=week_start,
        narrative_text=text,
        key_insights=insights,
        drs_at_generation=drs_score,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# ── Budget Rules ──────────────────────────────────────────────────────────────

def get_budget_rules(db: Session, user_id: int) -> list[BudgetRule]:
    return db.query(BudgetRule).filter(BudgetRule.user_id == user_id).all()


def upsert_budget_rule(db: Session, user_id: int, category: str, monthly_limit: float) -> BudgetRule:
    rule = (
        db.query(BudgetRule)
        .filter(BudgetRule.user_id == user_id, BudgetRule.category == category)
        .first()
    )
    if rule:
        rule.monthly_limit = monthly_limit
    else:
        rule = BudgetRule(user_id=user_id, category=category, monthly_limit=monthly_limit)
        db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


# ── Predictions ───────────────────────────────────────────────────────────────

def create_prediction(db: Session, user_id: int, signal_type: str, risk_score: float, description: str) -> Prediction:
    obj = Prediction(
        user_id=user_id,
        signal_type=signal_type,
        risk_score=risk_score,
        description=description,
        predicted_for_date=datetime.utcnow().date(),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_active_predictions(db: Session, user_id: int) -> list[Prediction]:
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id, Prediction.is_resolved == False)  # noqa: E712
        .order_by(desc(Prediction.created_at))
        .all()
    )
