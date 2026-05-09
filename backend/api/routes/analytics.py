from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

USER_ID = 1


@router.get("/summary")
def get_summary(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return {"data": svc.get_summary(USER_ID)}


@router.get("/velocity")
def get_velocity(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return {"data": svc.get_velocity(USER_ID)}


@router.get("/recurring")
def get_recurring(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return {"data": svc.get_recurring(USER_ID)}
