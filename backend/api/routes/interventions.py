from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from services.intervention_service import InterventionService
from services.drs_service import DRSService
from ai.orchestrator import AIOrchestrator
from schemas.intervention import InterventionOut

router = APIRouter(prefix="/api/interventions", tags=["interventions"])

USER_ID = 1


@router.get("")
def list_interventions(db: Session = Depends(get_db)):
    svc = InterventionService(db)
    items = svc.get_active(USER_ID)
    return {"data": [InterventionOut.model_validate(i).model_dump() for i in items]}


@router.post("/generate")
async def generate_intervention(
    risk_type: str = "velocity_spike",
    db: Session = Depends(get_db),
):
    """Trigger AI to generate a new intervention for the given risk type."""
    intervention_svc = InterventionService(db)
    drs_svc = DRSService(db)

    drs = drs_svc.get_current(USER_ID)
    drs_score = drs["score"] if drs else 50

    context = intervention_svc.build_context(USER_ID, risk_type, risk_score=0.7)
    context["drs_score"] = drs_score

    orchestrator = AIOrchestrator()
    result = await orchestrator.generate_intervention(context)

    saved = intervention_svc.store(USER_ID, result)
    return {"data": InterventionOut.model_validate(saved).model_dump(), "message": "Intervention generated"}


@router.patch("/{intervention_id}/dismiss")
def dismiss_intervention(intervention_id: int, db: Session = Depends(get_db)):
    svc = InterventionService(db)
    obj = svc.dismiss(USER_ID, intervention_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Intervention not found")
    return {"data": {"id": intervention_id, "status": "dismissed"}}
