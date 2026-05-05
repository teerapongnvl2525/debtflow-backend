from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import auth, transactions, debts, summary
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DebtFlow API",
    description="Personal Finance & Debt Reduction",
    version="1.0.0"
)

# CORS — อนุญาตทุก origin (แก้ทีหลังเมื่อ stable)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(debts.router)
app.include_router(summary.router)

@app.get("/")
def root():
    return {"app": "DebtFlow API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}
