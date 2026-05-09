from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class DRSComponents(BaseModel):
    budget_adherence: float
    velocity_stability: float
    savings_rate: float
    recurring_coverage: float
    emotional_spend: float
    salary_gap: float


class DRSResult(BaseModel):
    score: float
    label: str
    color: str
    components: DRSComponents
    explanation: Optional[str] = None
    calculated_at: datetime


class DRSHistoryPoint(BaseModel):
    score: float
    calculated_at: datetime

    model_config = {"from_attributes": True}
