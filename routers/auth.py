import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "debtflow-secret-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# Single user credentials จาก .env
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

def create_token(data: dict) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode({**data, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = None) -> bool:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub") == "admin"
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalid หรือหมดอายุ")

@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    # ตรวจ username
    if req.username != ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Username หรือ password ไม่ถูกต้อง")
    # ตรวจ password
    if ADMIN_PASSWORD_HASH:
        if not pwd_context.verify(req.password, ADMIN_PASSWORD_HASH):
            raise HTTPException(status_code=401, detail="Username หรือ password ไม่ถูกต้อง")
    else:
        # fallback: plain password จาก env (สำหรับ dev)
        plain_pass = os.getenv("ADMIN_PASSWORD", "")
        if req.password != plain_pass:
            raise HTTPException(status_code=401, detail="Username หรือ password ไม่ถูกต้อง")

    token = create_token({"sub": "admin"})
    return TokenResponse(access_token=token)

@router.post("/logout")
def logout():
    # JWT stateless — client ลบ token เอง
    return {"message": "Logged out"}

# Helper สำหรับ router อื่น
def get_current_user(credentials: HTTPAuthorizationCredentials = None):
    if not credentials:
        raise HTTPException(status_code=401, detail="ไม่มี token")
    verify_token(credentials)
    return "admin"
