from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from services.narrative_service import NarrativeService
from services.drs_service import DRSService
from ai.orchestrator import AIOrchestrator
from schemas.intervention import NarrativeOut

router = APIRouter(prefix="/api/narrative", tags=["narrative"])

USER_ID = 1


@router.get("/latest")
def get_latest_narrative(db: Session = Depends(get_db)):
    svc = NarrativeService(db)
    obj = svc.get_latest(USER_ID)
    if not obj:
        return {"data": None}
    return {"data": NarrativeOut.model_validate(obj).model_dump()}


@router.post("/generate")
async def generate_narrative(db: Session = Depends(get_db)):
    """Trigger AI to generate a new weekly narrative."""
    narrative_svc = NarrativeService(db)
    drs_svc = DRSService(db)

    drs = drs_svc.get_current(USER_ID)
    drs_score = drs["score"] if drs else 50

    context = narrative_svc.build_context(USER_ID, drs_score)

    orchestrator = AIOrchestrator()
    text = await orchestrator.generate_narrative(context)

    saved = narrative_svc.store(USER_ID, text, drs_score)
    return {"data": NarrativeOut.model_validate(saved).model_dump(), "message": "Narrative generated"}
