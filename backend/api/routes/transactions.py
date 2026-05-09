from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from db import crud
from services.transaction_service import TransactionService
from schemas.transaction import TransactionOut, TransactionListOut

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

USER_ID = 1  # Single-user demo


@router.post("/upload")
async def upload_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a CSV file and process all transactions."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    svc = TransactionService(db)
    try:
        result = svc.process_csv(USER_ID, contents)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    return {"data": result, "message": f"Successfully imported {result['inserted']} transactions"}


@router.get("", response_model=dict)
def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    category: str | None = Query(None),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * page_size
    txns = crud.get_transactions(db, USER_ID, limit=page_size, offset=offset, category=category)
    total = crud.count_transactions(db, USER_ID)

    return {
        "data": {
            "transactions": [TransactionOut.model_validate(t).model_dump() for t in txns],
            "total": total,
            "page": page,
            "page_size": page_size,
        }
    }


@router.get("/{txn_id}", response_model=dict)
def get_transaction(txn_id: int, db: Session = Depends(get_db)):
    from db.models import Transaction
    txn = db.query(Transaction).filter(Transaction.id == txn_id, Transaction.user_id == USER_ID).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"data": TransactionOut.model_validate(txn).model_dump()}
