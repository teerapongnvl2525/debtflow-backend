from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import Account, Debt, ExternalAsset, AccountType
from routers.auth import get_current_user

router = APIRouter(prefix="/summary", tags=["summary"])
security = HTTPBearer()

@router.get("/net-worth")
def get_net_worth(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    get_current_user(credentials)

    # สินทรัพย์ทางการเงิน (ไม่รวมหนี้)
    financial_types = [AccountType.savings, AccountType.current, AccountType.cash,
                       AccountType.invest, AccountType.insurance]
    accounts = db.query(Account).filter(
        Account.account_type.in_(financial_types),
        Account.is_active == True
    ).all()

    assets_by_type = {
        "cash_savings": 0.0,
        "invest": 0.0,
        "insurance_cv": 0.0,
    }
    for a in accounts:
        bal = float(a.balance or 0)
        if a.account_type in [AccountType.savings, AccountType.current, AccountType.cash]:
            assets_by_type["cash_savings"] += bal
        elif a.account_type == AccountType.invest:
            assets_by_type["invest"] += bal
        elif a.account_type == AccountType.insurance:
            assets_by_type["insurance_cv"] += bal

    total_assets = sum(assets_by_type.values())

    # หนี้รวม
    debts = db.query(Debt).filter(Debt.is_active == True).all()
    total_debt = sum(float(d.balance or 0) for d in debts)

    # สินทรัพย์นอกระบบ
    external = db.query(ExternalAsset).all()
    external_assets = [{"name": e.name, "value": float(e.value)} for e in external]
    total_external = sum(e["value"] for e in external_assets)

    financial_net_worth = total_assets - total_debt

    return {
        "financial_net_worth": round(financial_net_worth, 2),
        "total_financial_assets": round(total_assets, 2),
        "breakdown": {
            "cash_and_savings": assets_by_type["cash_savings"],
            "investments": assets_by_type["invest"],
            "insurance_cash_value": assets_by_type["insurance_cv"],
        },
        "total_debt": round(total_debt, 2),
        "external_assets": external_assets,
        "total_external": total_external,
        "total_net_worth_incl_property": round(financial_net_worth + total_external, 2),
        "note": "Financial Net Worth ไม่รวมมูลค่าบ้าน — ดูใน external_assets"
    }

@router.get("/cashflow-alert")
def cashflow_alert(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """แจ้งเตือนถ้า recurring expense > รายรับ"""
    get_current_user(credentials)
    # คำนวณจาก recurring transactions
    from models import Transaction
    from sqlalchemy import and_
    recurring = db.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.is_recurring == True,
        Transaction.transaction_type.in_(["expense", "debt"])
    ).scalar()

    total_recurring = float(recurring or 86716)  # fallback seed value
    est_income = 85200  # รายรับประมาณการ

    return {
        "estimated_income": est_income,
        "total_recurring_expense": total_recurring,
        "cashflow": est_income - total_recurring,
        "is_negative": total_recurring > est_income,
        "alert_message": "⚠ รายจ่ายประจำสูงกว่ารายรับ — ควรทบทวนค่าใช้จ่าย" if total_recurring > est_income else "✓ Cash flow ปกติ",
        "aia_ends": "ธ.ค. 2569 — ประหยัดได้ ฿6,250/เดือน หลังจากนั้น"
    }
