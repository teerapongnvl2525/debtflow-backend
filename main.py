from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import auth, transactions, debts, summary
import os

# สร้าง tables อัตโนมัติ
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DebtFlow API",
    description="Personal Finance & Debt Reduction — นพ.ป่อง",
    version="1.0.0"
)

# CORS — อนุญาต frontend
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://debtflow-frontend.vercel.app,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(debts.router)
app.include_router(summary.router)

@app.get("/")
def root():
    return {
        "app": "DebtFlow API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
def health():
    return {"status": "ok"}
