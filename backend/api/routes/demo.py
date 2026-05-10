from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db.database import get_db
from db import crud

router = APIRouter(prefix="/api/demo", tags=["demo"])

USER_ID = 1


@router.get("/user")
def get_demo_user(db: Session = Depends(get_db)):
    """Single demo user profile (id=1) — reflects whichever persona was last seeded."""
    user = crud.get_user(db, USER_ID)
    if not user:
        raise HTTPException(status_code=404, detail="Demo user not found")
    return {
        "data": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "archetype": user.archetype,
            "monthly_income": user.monthly_income,
            "salary_day": user.salary_day,
        }
    }
