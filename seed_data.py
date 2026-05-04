"""
Seed data จริง ณ พ.ค. 2569 — FINAL VERSION
รัน: python seed_data.py
"""
from database import SessionLocal, engine
from models import Base, Debt, Account, Category, Transaction, ExternalAsset
from models import DebtType, AccountType, CategoryType, TransactionType, PaymentMethod
from datetime import date
import uuid

def gen_uuid():
    return str(uuid.uuid4())

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    db.query(Transaction).delete()
    db.query(Debt).delete()
    db.query(Account).delete()
    db.query(Category).delete()
    db.query(ExternalAsset).delete()
    db.commit()

    # ---- DEBTS ----
    debts = [
        Debt(id=gen_uuid(), name="KTB ธนวัฏ (OD)", bank="KTB",
             debt_type=DebtType.od, balance=216196.00, original_amount=400000,
             credit_limit=400000, interest_rate=18.0, due_day=15, priority=1,
             last_four="9429"),
        Debt(id=gen_uuid(), name="สินเชื่อบุคคล KTB", bank="KTB",
             debt_type=DebtType.personal, balance=440903.00, original_amount=800000,
             interest_rate=4.10, min_payment=5500, due_day=2, priority=2,
             last_four="7050", contract_end_date=date(2036, 2, 21)),
        Debt(id=gen_uuid(), name="สินเชื่อบ้าน KTB", bank="KTB",
             debt_type=DebtType.mortgage, balance=839764.00, original_amount=2300000,
             interest_rate=2.80, min_payment=13900, due_day=2, priority=3,
             last_four="0442", contract_end_date=date(2036, 3, 17)),
        Debt(id=gen_uuid(), name="KTC Visa Signature", bank="KTB",
             debt_type=DebtType.credit_card, balance=73740.00, credit_limit=80000,
             interest_rate=16.0, due_day=3, priority=4, last_four="6497"),
        Debt(id=gen_uuid(), name="Krungsri Platinum", bank="Krungsri",
             debt_type=DebtType.credit_card, balance=80922.00, credit_limit=97750,
             interest_rate=16.0, due_day=25, priority=5, last_four="0294"),
        Debt(id=gen_uuid(), name="Krungsri HomePro", bank="Krungsri",
             debt_type=DebtType.credit_card, balance=25702.00, credit_limit=97750,
             interest_rate=16.0, due_day=25, priority=6, last_four="1831"),
        Debt(id=gen_uuid(), name="UOB Privi Miles", bank="UOB",
             debt_type=DebtType.credit_card, balance=31405.00, credit_limit=39236,
             interest_rate=16.0, due_day=19, priority=7, last_four="3669"),
        Debt(id=gen_uuid(), name="First Choice HomePro", bank="Krungsri",
             debt_type=DebtType.credit_card, balance=0, credit_limit=0,
             interest_rate=0, due_day=5, priority=8, last_four="0483"),
    ]
    db.add_all(debts)

    # ---- ACCOUNTS ----
    accounts = [
        Account(id=gen_uuid(), name="KTB ออมทรัพย์", bank="KTB",
                account_type=AccountType.savings, last_four="9429",
                balance=284500, color="#1e40af", icon="🏦"),
        Account(id=gen_uuid(), name="SCB ออมทรัพย์", bank="SCB",
                account_type=AccountType.savings, last_four="0000",
                balance=156200, color="#166534", icon="🏦"),
        Account(id=gen_uuid(), name="กสิกร เดินสะพัด", bank="KBANK",
                account_type=AccountType.current, last_four="0000",
                balance=45800, color="#831843", icon="🏦"),
        Account(id=gen_uuid(), name="เงินสด", bank=None,
                account_type=AccountType.cash, balance=0,
                color="#404868", icon="💵"),
        # ลงทุน — กบข. ยอดจริง
        Account(id=gen_uuid(), name="กบข. (27%)", bank="กบข.",
                account_type=AccountType.invest, balance=1679583,
                color="#1e3a5f", icon="🏛️",
                note="ยอด ณ 28 เม.ย. 2569 / ผลตอบแทน 5.73%/ปี / นำส่ง ฿18,844/เดือน"),
        Account(id=gen_uuid(), name="KFGOLDRMF", bank="KAsset",
                account_type=AccountType.invest, balance=380000,
                color="#2d1b69", icon="🥇"),
        Account(id=gen_uuid(), name="Jitta Portfolio", bank="Jitta",
                account_type=AccountType.invest, balance=1020000,
                color="#064e3b", icon="📈"),
        # ประกัน AIA — มูลค่าเวนคืนจริง ชำระงวดสุดท้าย ธ.ค. 2569
        Account(id=gen_uuid(), name="AIA T175159831", bank="AIA",
                account_type=AccountType.insurance, balance=429329,
                color="#7c2d12", icon="🛡️",
                note="ทุน ฿625,000 ครบ 25 ธ.ค. 2580 — ชำระงวดสุดท้าย ธ.ค. 2569"),
        Account(id=gen_uuid(), name="AIA T161699509", bank="AIA",
                account_type=AccountType.insurance, balance=470394,
                color="#7c2d12", icon="🛡️",
                note="ทุน ฿675,000 ครบ 28 ธ.ค. 2579 — ชำระงวดสุดท้าย ธ.ค. 2569"),
    ]
    db.add_all(accounts)

    # ---- CATEGORIES ----
    income_cats = [
        Category(name="เงินเดือน", category_type=CategoryType.income, icon="💰", color="#34d399", is_default=True),
        Category(name="ประจำตำแหน่ง", category_type=CategoryType.income, icon="💰", color="#34d399", is_default=True),
        Category(name="ค่าเวร", category_type=CategoryType.income, icon="🏥", color="#34d399", is_default=True),
        Category(name="วิชาชีพสาขาขาดแคลน", category_type=CategoryType.income, icon="👨‍⚕️", color="#34d399", is_default=True),
        Category(name="พตส", category_type=CategoryType.income, icon="💊", color="#34d399", is_default=True),
        Category(name="P4P", category_type=CategoryType.income, icon="📊", color="#34d399", is_default=True),
        Category(name="รายได้คลินิก", category_type=CategoryType.income, icon="🏥", color="#34d399", is_default=True),
        Category(name="ค่าวิทยากร", category_type=CategoryType.income, icon="📖", color="#34d399"),
        Category(name="เงินปันผล", category_type=CategoryType.income, icon="📈", color="#34d399"),
        Category(name="รายได้อื่น", category_type=CategoryType.income, icon="💸", color="#34d399"),
    ]
    expense_cats = [
        Category(name="อาหาร", category_type=CategoryType.expense, icon="🍽️", color="#f87171", monthly_budget=8000, is_default=True),
        Category(name="น้ำมัน", category_type=CategoryType.expense, icon="⛽", color="#f87171", monthly_budget=3000),
        Category(name="บ้าน / ค่าน้ำค่าไฟ", category_type=CategoryType.expense, icon="🏠", color="#f87171", monthly_budget=3000),
        Category(name="บันเทิง", category_type=CategoryType.expense, icon="🎮", color="#f87171", monthly_budget=4000),
        Category(name="ค่าเล่าเรียนบุตร", category_type=CategoryType.expense, icon="🏫", color="#f87171", monthly_budget=29167, is_default=True),
        Category(name="สุขภาพ", category_type=CategoryType.expense, icon="💊", color="#f87171", monthly_budget=2000),
        Category(name="ประกัน AIA", category_type=CategoryType.expense, icon="🛡️", color="#f87171", monthly_budget=6250, is_default=True),
        Category(name="ประกัน Allianz SA", category_type=CategoryType.expense, icon="🛡️", color="#f87171", monthly_budget=13500, is_default=True),
        Category(name="ประกัน Allianz PAG", category_type=CategoryType.expense, icon="🛡️", color="#f87171", monthly_budget=1981, is_default=True),
        Category(name="Coway", category_type=CategoryType.expense, icon="💧", color="#f87171", monthly_budget=690, is_default=True),
        Category(name="ผ่อนสินค้า First Choice", category_type=CategoryType.expense, icon="🛒", color="#f87171", monthly_budget=15729, is_default=True),
        Category(name="หนี้สิน", category_type=CategoryType.expense, icon="⚡", color="#fb923c", is_default=True),
        Category(name="ค่าใช้จ่ายอื่น", category_type=CategoryType.expense, icon="📦", color="#f87171"),
    ]
    invest_cats = [
        Category(name="กบข.", category_type=CategoryType.invest, icon="🏛️", color="#60a5fa", is_default=True),
        Category(name="RMF", category_type=CategoryType.invest, icon="🥇", color="#60a5fa", is_default=True),
        Category(name="หุ้น", category_type=CategoryType.invest, icon="📈", color="#60a5fa"),
        Category(name="กองทุนอื่น", category_type=CategoryType.invest, icon="💼", color="#60a5fa"),
    ]
    db.add_all(income_cats + expense_cats + invest_cats)

    # ---- EXTERNAL ASSETS ----
    db.add_all([
        ExternalAsset(name="มูลค่าบ้าน (ประมาณการ)", value=3000000,
                      note="กรอก manual / อัปเดตตามราคาตลาด"),
    ])

    db.commit()
    db.close()

    # สรุป
    print("✅ Seed data FINAL completed!")
    print("")
    print("📊 Financial Summary:")
    print("   รายรับ/เดือน:")
    print("   - เงินเดือน + เบี้ยต่างๆ : ฿93,590")
    print("   - คลินิก                 : ฿24,000")
    print("   - รวม                    : ฿117,590")
    print("")
    print("   รายจ่ายประจำ/เดือน:")
    print("   - ผ่อนบ้าน + สินเชื่อ   : ฿19,400")
    print("   - Allianz SA+PAG         : ฿15,481")
    print("   - First Choice ผ่อน     : ฿15,729")
    print("   - ค่าเรียนบุตร (เฉลี่ย): ฿29,167")
    print("   - AIA (reserve)          : ฿6,250")
    print("   - Coway                  : ฿690")
    print("   - รวม                    : ฿86,717")
    print("")
    print("   💰 คงเหลือก่อนค่าใช้จ่ายทั่วไป: ฿30,873")
    print("")
    print("   🏦 กบข. จริง ณ 28 เม.ย. 2569: ฿1,679,583")
    print("   📈 Net Worth (Financial)      : ~฿2,757,000")
    print("")
    print("   ⚡ OD Priority #1: ฿216,196 / 18% → โปะก่อน")
    print("   🎉 AIA ปีนี้งวดสุดท้าย ธ.ค. 2569 → ประหยัด ฿6,250/เดือน")

if __name__ == "__main__":
    seed()
