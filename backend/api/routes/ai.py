from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from analytics.engine import AnalyticsEngine
from services.analytics_service import AnalyticsService
from ai.orchestrator import AIOrchestrator
from schemas.intervention import ArchetypeOut, RiskSignalOut

router = APIRouter(prefix="/api/ai", tags=["ai"])

USER_ID = 1


@router.get("/archetype")
async def get_archetype(db: Session = Depends(get_db)):
    """Return stored archetype or classify on the fly."""
    user = crud.get_user(db, USER_ID)

    # Use stored archetype if available
    if user and user.archetype:
        profile = db.query(__import__("db.models", fromlist=["BehavioralProfile"]).BehavioralProfile).filter_by(user_id=USER_ID).first()
        if profile:
            import json
            signals = json.loads(profile.key_signals) if profile.key_signals else []
            return {"data": {
                "archetype": profile.archetype,
                "confidence": profile.confidence,
                "key_signals": signals,
            }}

    # Otherwise generate fresh
    engine = AnalyticsEngine(db)
    summary = engine.get_summary(USER_ID)

    debits_total = summary["total_spend"] or 1
    food_spend = next((c["total"] for c in summary["by_category"] if c["category"] == "Food & Dining"), 0)

    context = {
        "name": user.name if user else "User",
        "monthly_income": user.monthly_income if user else 0,
        "top_categories": ", ".join(c["category"] for c in summary["by_category"][:3]),
        "emotional_ratio": round(summary["emotional_spend_total"] / debits_total * 100, 1),
        "weekend_ratio": "1.8x weekday average",
        "cv": "0.42",
        "food_pct": round(food_spend / debits_total * 100, 1),
        "velocity_spike": "Yes" if summary["total_spend"] > 50000 else "No",
        "net_savings": f"₹{summary['net']:,.0f}",
    }

    orchestrator = AIOrchestrator()
    result = await orchestrator.classify_archetype(context)

    # Store result
    from db.models import BehavioralProfile
    import json
    profile = BehavioralProfile(
        user_id=USER_ID,
        archetype=result.get("archetype"),
        confidence=result.get("confidence", 0.5),
        key_signals=json.dumps(result.get("key_signals", [])),
    )
    db.add(profile)
    if user:
        user.archetype = result.get("archetype")
    db.commit()

    return {"data": result}


@router.get("/risks")
def get_risks(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    signals = svc.get_risk_signals(USER_ID)

    risk_list = []
    for name, val in signals.items():
        if name == "aggregate" or not isinstance(val, dict):
            continue
        risk_list.append({
            "signal_type": name,
            "risk_score": val["raw"],
            "description": _signal_description(name, val["raw"]),
            "predicted_for_date": None,
        })

    return {
        "data": {
            "signals": risk_list,
            "aggregate": signals.get("aggregate", 0),
        }
    }


@router.get("/predictions/calendar")
def get_predictions_calendar(db: Session = Depends(get_db)):
    svc = AnalyticsService(db)
    return {"data": svc.get_predictions_calendar(USER_ID)}


def _signal_description(name: str, score: float) -> str:
    descs = {
        "velocity_spike": f"Spending velocity is {score*100:.0f}% elevated above normal",
        "salary_gap_risk": f"Risk of running short before next salary: {score*100:.0f}%",
        "budget_overflow": f"Category budgets overflowing: severity {score*100:.0f}%",
        "emotional_spend": f"Emotional spending pattern detected: {score*100:.0f}% intensity",
        "recurring_miss": f"Upcoming recurring bills may strain balance: {score*100:.0f}% risk",
    }
    return descs.get(name, name)
