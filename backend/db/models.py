from datetime import datetime
from sqlalchemy import (
    Integer, String, Float, Boolean, Text, DateTime, Date,
    ForeignKey, Column
)
from sqlalchemy.orm import relationship
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String)
    monthly_income = Column(Float, default=0.0)
    salary_day = Column(Integer)  # day of month salary arrives, null for irregular
    archetype = Column(String)    # stress_spender, impulse_buyer, planner, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="user")
    drs_history = relationship("DRSHistory", back_populates="user")
    behavioral_profile = relationship("BehavioralProfile", back_populates="user", uselist=False)
    interventions = relationship("Intervention", back_populates="user")
    narratives = relationship("Narrative", back_populates="user")
    budget_rules = relationship("BudgetRule", back_populates="user")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)          # always positive; use type for direction
    type = Column(String, nullable=False)           # "debit" | "credit"
    category = Column(String, default="Uncategorized")
    is_recurring = Column(Boolean, default=False)
    recurring_group_id = Column(String)             # merchant name group key
    is_emotional = Column(Boolean, default=False)
    raw_description = Column(String)                # original before normalization
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")


class DRSHistory(Base):
    __tablename__ = "drs_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=False)
    c1_budget_adherence = Column(Float, default=0.0)
    c2_velocity_stability = Column(Float, default=0.0)
    c3_savings_rate = Column(Float, default=0.0)
    c4_recurring_coverage = Column(Float, default=0.0)
    c5_emotional_spend = Column(Float, default=0.0)
    c6_salary_gap = Column(Float, default=0.0)
    explanation = Column(Text)  # AI-generated explanation if score changed >5pts
    calculated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="drs_history")


class BehavioralProfile(Base):
    __tablename__ = "behavioral_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    archetype = Column(String)
    confidence = Column(Float, default=0.0)
    key_signals = Column(Text)  # JSON array stored as string
    last_updated = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="behavioral_profile")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    signal_type = Column(String, nullable=False)  # velocity_spike, salary_gap_risk, etc.
    risk_score = Column(Float, nullable=False)     # 0.0–1.0
    description = Column(Text)
    predicted_for_date = Column(Date)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    intervention = relationship("Intervention", back_populates="prediction", uselist=False)


class Intervention(Base):
    __tablename__ = "interventions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_id = Column(Integer, ForeignKey("predictions.id"))
    title = Column(String, nullable=False)
    action = Column(Text, nullable=False)
    reason = Column(Text, nullable=False)
    urgency = Column(String, default="medium")     # low | medium | high
    savings_potential = Column(Float, default=0.0)
    status = Column(String, default="active")      # active | dismissed | completed
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="interventions")
    prediction = relationship("Prediction", back_populates="intervention")


class Narrative(Base):
    __tablename__ = "narratives"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    week_start = Column(Date)
    narrative_text = Column(Text, nullable=False)
    key_insights = Column(Text)  # JSON array
    drs_at_generation = Column(Float)
    generated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="narratives")


class BudgetRule(Base):
    __tablename__ = "budget_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category = Column(String, nullable=False)
    monthly_limit = Column(Float, nullable=False)
    alert_at_percent = Column(Integer, default=80)

    user = relationship("User", back_populates="budget_rules")


class RecurringPattern(Base):
    __tablename__ = "recurring_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_name = Column(String, nullable=False)
    avg_amount = Column(Float)
    frequency = Column(String)     # weekly | biweekly | monthly
    next_expected = Column(Date)
    last_seen = Column(Date)
    updated_at = Column(DateTime, default=datetime.utcnow)
