from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from services.drs_service import DRSService

router = APIRouter(prefix="/api/drs", tags=["drs"])

USER_ID = 1


@router.get("/current")
def get_current_drs(db: Session = Depends(get_db)):
    svc = DRSService(db)
    result = svc.get_current(USER_ID)
    return {"data": result}


@router.get("/history")
def get_drs_history(days: int = 30, db: Session = Depends(get_db)):
    svc = DRSService(db)
    return {"data": svc.get_history(USER_ID, days)}


@router.post("/recalculate")
async def recalculate_drs(db: Session = Depends(get_db)):
    svc = DRSService(db)
    result = await svc.calculate_with_explanation(USER_ID)
    return {"data": result, "message": "DRS recalculated"}
