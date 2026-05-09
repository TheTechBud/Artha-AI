from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class InterventionOut(BaseModel):
    id: int
    title: str
    action: str
    reason: str
    urgency: str
    savings_potential: float
    status: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class NarrativeOut(BaseModel):
    id: int
    narrative_text: str
    key_insights: Optional[str] = None
    drs_at_generation: Optional[float] = None
    generated_at: datetime

    model_config = {"from_attributes": True}


class ArchetypeOut(BaseModel):
    archetype: str
    confidence: float
    key_signals: list[str]


class RiskSignalOut(BaseModel):
    signal_type: str
    risk_score: float
    description: str
    predicted_for_date: Optional[str] = None
