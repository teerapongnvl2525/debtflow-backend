from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal
import calendar

from database import get_db
from models import Transaction, TransactionType, PaymentMethod
from routers.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])
security = HTTPBearer()

# ---- SCHEMAS ----
class TransactionCreate(BaseModel):
    transaction_type: TransactionType
    amount: Decimal
    transaction_date: date
    payment_method: Optional[PaymentMethod] = PaymentMethod.transfer
    note: Optional[str] = None
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    debt_id: Optional[str] = None
    to_account_id: Optional[str] = None
    is_recurring: bool = False
    recurring_day: Optional[int] = None
    recurring_end_date: Optional[date] = None

class TransactionUpdate(BaseModel):
    transaction_type: Optional[TransactionType] = None
    amount: Optional[Decimal] = None
    transaction_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    note: Optional[str] = None
    category_id: Optional[str] = None
    account_id: Optional[str] = None
    debt_id: Optional[str] = None

class TransactionOut(BaseModel):
    id: str
    transaction_type: str
    amount: float
    transaction_date: date
    payment_method: Optional[str]
    note: Optional[str]
    category_id: Optional[str]
    account_id: Optional[str]
    debt_id: Optional[str]
    is_recurring: bool

    class Config:
        from_attributes = True

# ---- ROUTES ----
@router.get("", response_model=List[TransactionOut])
def get_transactions(
    month: Optional[str] = Query(None, description="YYYY-MM"),
    type: Optional[TransactionType] = None,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    q = db.query(Transaction)
    if month:
        year, m = month.split("-")
        q = q.filter(
            extract("year", Transaction.transaction_date) == int(year),
            extract("month", Transaction.transaction_date) == int(m)
        )
    if type:
        q = q.filter(Transaction.transaction_type == type)
    return q.order_by(Transaction.transaction_date.desc()).all()

@router.get("/summary")
def get_summary(
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    year, m = month.split("-")

    def total(tx_type):
        result = db.query(func.sum(Transaction.amount)).filter(
            Transaction.transaction_type == tx_type,
            extract("year", Transaction.transaction_date) == int(year),
            extract("month", Transaction.transaction_date) == int(m)
        ).scalar()
        return float(result or 0)

    income = total(TransactionType.income)
    expense = total(TransactionType.expense)
    debt_payment = total(TransactionType.debt)
    invest = total(TransactionType.invest)
    remaining = income - expense - debt_payment - invest

    return {
        "month": month,
        "income": income,
        "expense": expense,
        "debt_payment": debt_payment,
        "invest": invest,
        "remaining": remaining,
        "cashflow_alert": remaining < 0
    }

@router.post("", response_model=TransactionOut)
def create_transaction(
    data: TransactionCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    tx = Transaction(**data.model_dump())
    db.add(tx)

    # ถ้าโปะหนี้ → อัปเดต balance ใน Debts
    if data.transaction_type == TransactionType.debt and data.debt_id:
        from models import Debt
        debt = db.query(Debt).filter(Debt.id == data.debt_id).first()
        if debt:
            debt.balance = max(0, float(debt.balance) - float(data.amount))

    db.commit()
    db.refresh(tx)
    return tx

@router.put("/{tx_id}", response_model=TransactionOut)
def update_transaction(
    tx_id: str,
    data: TransactionUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="ไม่พบรายการ")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(tx, k, v)
    db.commit()
    db.refresh(tx)
    return tx

@router.delete("/{tx_id}")
def delete_transaction(
    tx_id: str,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    tx = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not tx:
        raise HTTPException(status_code=404, detail="ไม่พบรายการ")
    db.delete(tx)
    db.commit()
    return {"message": "ลบแล้ว"}
