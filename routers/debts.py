from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
import math

from database import get_db
from models import Debt, DebtType
from routers.auth import get_current_user

router = APIRouter(prefix="/debts", tags=["debts"])
security = HTTPBearer()

class DebtCreate(BaseModel):
    name: str
    bank: Optional[str] = None
    debt_type: DebtType
    balance: Decimal
    original_amount: Optional[Decimal] = None
    credit_limit: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    min_payment: Optional[Decimal] = None
    due_day: Optional[int] = None
    priority: int = 1
    last_four: Optional[str] = None

class DebtUpdate(BaseModel):
    name: Optional[str] = None
    balance: Optional[Decimal] = None
    interest_rate: Optional[Decimal] = None
    min_payment: Optional[Decimal] = None
    due_day: Optional[int] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class DebtOut(BaseModel):
    id: str
    name: str
    bank: Optional[str]
    debt_type: str
    balance: float
    original_amount: Optional[float]
    credit_limit: Optional[float]
    interest_rate: Optional[float]
    min_payment: Optional[float]
    due_day: Optional[int]
    priority: int
    last_four: Optional[str]
    is_active: bool
    # computed
    monthly_interest: Optional[float] = None
    payoff_pct: Optional[float] = None

    class Config:
        from_attributes = True

def calc_monthly_interest(balance: float, rate: float) -> float:
    return round(balance * (rate / 100 / 12), 2)

def calc_payoff_months(balance: float, rate: float, min_pay: float, extra: float = 0) -> int | str:
    r = rate / 100 / 12
    pay = min_pay + extra
    if pay <= 0 or balance <= 0:
        return 0
    if r == 0:
        return math.ceil(balance / pay)
    if pay <= balance * r:
        return "∞"
    months = -math.log(1 - (balance * r) / pay) / math.log(1 + r)
    return math.ceil(months)

@router.get("", response_model=List[DebtOut])
def get_debts(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    debts = db.query(Debt).filter(Debt.is_active == True).order_by(Debt.priority).all()
    result = []
    for d in debts:
        out = DebtOut.model_validate(d)
        if d.interest_rate and d.balance:
            out.monthly_interest = calc_monthly_interest(float(d.balance), float(d.interest_rate))
        if d.original_amount and d.balance:
            paid = float(d.original_amount) - float(d.balance)
            out.payoff_pct = round(paid / float(d.original_amount) * 100, 1)
        result.append(out)
    return result

@router.get("/summary")
def get_debt_summary(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    debts = db.query(Debt).filter(Debt.is_active == True).all()
    total_balance = sum(float(d.balance) for d in debts)
    total_interest = sum(
        calc_monthly_interest(float(d.balance), float(d.interest_rate))
        for d in debts if d.interest_rate
    )
    total_min = sum(float(d.min_payment or 0) for d in debts)
    # upcoming due this month
    upcoming = [
        {"name": d.name, "due_day": d.due_day, "min_payment": float(d.min_payment or 0)}
        for d in sorted(debts, key=lambda x: x.due_day or 99)
        if d.due_day
    ]
    return {
        "total_balance": total_balance,
        "total_monthly_interest": round(total_interest, 2),
        "total_min_payment": total_min,
        "upcoming_payments": upcoming,
        "debt_count": len(debts)
    }

@router.get("/payoff-calc")
def payoff_calculator(
    extra_payment: float = Query(0, description="โปะเพิ่ม/เดือน"),
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Avalanche Method: คำนวณลำดับโปะหนี้ที่ดอกสูงก่อน"""
    get_current_user(credentials)
    debts = db.query(Debt).filter(
        Debt.is_active == True,
        Debt.debt_type != DebtType.credit_card
    ).order_by(Debt.interest_rate.desc()).all()

    results = []
    remaining_extra = extra_payment

    for d in debts:
        if not d.balance or not d.interest_rate:
            continue
        bal = float(d.balance)
        rate = float(d.interest_rate)
        min_pay = float(d.min_payment or 0)
        extra = remaining_extra  # ใช้เงินโปะกับหนี้ดอกแพงก่อน

        months_min = calc_payoff_months(bal, rate, min_pay, 0)
        months_extra = calc_payoff_months(bal, rate, min_pay, extra)
        monthly_interest = calc_monthly_interest(bal, rate)

        results.append({
            "debt_name": d.name,
            "balance": bal,
            "interest_rate": rate,
            "min_payment": min_pay,
            "extra_payment": extra,
            "months_min_only": months_min,
            "months_with_extra": months_extra,
            "monthly_interest": monthly_interest,
            "interest_saved_est": round(monthly_interest * (
                (int(months_min) if months_min != "∞" else 0) -
                (int(months_extra) if months_extra != "∞" else 0)
            ), 0)
        })
        # ถ้าหนี้นี้หมดก็ย้าย extra ไปหนี้ถัดไป (snowball)
        if months_extra != "∞" and months_extra < 12:
            remaining_extra += min_pay

    return {
        "method": "Avalanche (ดอกสูงก่อน)",
        "extra_payment_per_month": extra_payment,
        "debts": results,
        "recommendation": results[0]["debt_name"] if results else None
    }

@router.post("", response_model=DebtOut)
def create_debt(
    data: DebtCreate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    debt = Debt(**data.model_dump())
    db.add(debt)
    db.commit()
    db.refresh(debt)
    return debt

@router.put("/{debt_id}", response_model=DebtOut)
def update_debt(
    debt_id: str,
    data: DebtUpdate,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)
    debt = db.query(Debt).filter(Debt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="ไม่พบรายการหนี้")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(debt, k, v)
    db.commit()
    db.refresh(debt)
    return debt
