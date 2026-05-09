from pydantic import BaseModel
from typing import Optional


class CategorySpend(BaseModel):
    category: str
    total: float
    count: int
    pct_of_total: float


class VelocityPoint(BaseModel):
    date: str
    rolling_spend: float


class RecurringItem(BaseModel):
    name: str
    avg_amount: float
    frequency: str  # weekly | biweekly | monthly
    next_expected: Optional[str] = None


class AnalyticsSummary(BaseModel):
    total_spend: float
    total_income: float
    net: float
    by_category: list[CategorySpend]
    velocity_data: list[VelocityPoint]
    recurring: list[RecurringItem]
    emotional_spend_total: float
    top_category: str
    month: str
