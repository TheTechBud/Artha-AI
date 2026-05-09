from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    data: T
    meta: dict = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TransactionBase(BaseModel):
    date: datetime
    description: str
    amount: float = Field(gt=0)
    type: str  # "debit" | "credit"
    category: Optional[str] = "Uncategorized"
    is_recurring: bool = False
    is_emotional: bool = False


class TransactionOut(TransactionBase):
    id: int
    user_id: int
    recurring_group_id: Optional[str] = None

    model_config = {"from_attributes": True}


class TransactionListOut(BaseModel):
    transactions: list[TransactionOut]
    total: int
    page: int
    page_size: int
