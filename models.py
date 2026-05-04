from sqlalchemy import Column, String, Numeric, Integer, Boolean, Date, DateTime, Enum, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from database import Base

def gen_uuid():
    return str(uuid.uuid4())

# ---- ENUMS ----
class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"
    debt = "debt"
    invest = "invest"
    transfer = "transfer"

class PaymentMethod(str, enum.Enum):
    cash = "cash"
    transfer = "transfer"
    debit = "debit"
    credit = "credit"

class AccountType(str, enum.Enum):
    savings = "savings"
    current = "current"
    credit_card = "credit_card"
    invest = "invest"
    cash = "cash"
    loan = "loan"
    insurance = "insurance"

class DebtType(str, enum.Enum):
    od = "od"
    personal = "personal"
    mortgage = "mortgage"
    credit_card = "credit_card"

class CategoryType(str, enum.Enum):
    income = "income"
    expense = "expense"
    invest = "invest"

# ---- MODELS ----
class Debt(Base):
    __tablename__ = "debts"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    bank = Column(String(50))
    debt_type = Column(Enum(DebtType), nullable=False)
    balance = Column(Numeric(12, 2), nullable=False)
    original_amount = Column(Numeric(12, 2))
    credit_limit = Column(Numeric(12, 2))          # สำหรับ OD/บัตรเครดิต
    interest_rate = Column(Numeric(5, 2))           # % ต่อปี
    min_payment = Column(Numeric(10, 2))
    due_day = Column(Integer)                       # วันที่ครบชำระ (1-31)
    priority = Column(Integer, default=1)           # Avalanche order
    last_four = Column(String(4))                   # เลขท้าย
    contract_end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    transactions = relationship("Transaction", back_populates="debt")

class Account(Base):
    __tablename__ = "accounts"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    bank = Column(String(50))
    account_type = Column(Enum(AccountType), nullable=False)
    last_four = Column(String(4))
    balance = Column(Numeric(12, 2), default=0)
    color = Column(String(7), default="#60a5fa")
    icon = Column(String(10), default="🏦")
    is_active = Column(Boolean, default=True)
    note = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    transactions = relationship("Transaction", back_populates="account")

class Category(Base):
    __tablename__ = "categories"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    category_type = Column(Enum(CategoryType), nullable=False)
    icon = Column(String(10), default="📁")
    color = Column(String(7), default="#60a5fa")
    monthly_budget = Column(Numeric(10, 2))
    is_default = Column(Boolean, default=False)     # ลบไม่ได้
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    transactions = relationship("Transaction", back_populates="category")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, default=gen_uuid)
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_date = Column(Date, nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.transfer)
    note = Column(Text)
    is_recurring = Column(Boolean, default=False)
    recurring_day = Column(Integer)                 # วันที่ตัดเงินในเดือน
    recurring_end_date = Column(Date)               # AIA จบ ธ.ค. 2569
    # Foreign keys
    category_id = Column(String, ForeignKey("categories.id"))
    account_id = Column(String, ForeignKey("accounts.id"))
    debt_id = Column(String, ForeignKey("debts.id"))
    to_account_id = Column(String, ForeignKey("accounts.id"))  # สำหรับ transfer
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    # Relationships
    category = relationship("Category", back_populates="transactions")
    account = relationship("Account", foreign_keys=[account_id], back_populates="transactions")
    debt = relationship("Debt", back_populates="transactions")

class ExternalAsset(Base):
    """สินทรัพย์นอกระบบ เช่น มูลค่าบ้าน"""
    __tablename__ = "external_assets"
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String(100), nullable=False)
    value = Column(Numeric(12, 2), nullable=False)
    note = Column(Text)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
