from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from jose import jwt, JWTError # type: ignore
from datetime import datetime, timedelta
from passlib.context import CryptContext # type: ignore
from ..database import SessionLocal
from ..models import User
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Request Models
# -----------------------------
class AuthRequest(BaseModel):
    username: str
    password: str


# -----------------------------
# Signup
# -----------------------------
@router.post("/signup")
def signup(user: AuthRequest, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # hashed_password = pwd_context.hash(user.password)
    safe_password = user.password[:72]
    hashed_password = pwd_context.hash(safe_password)

    new_user = User(
        username=user.username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}


# -----------------------------
# Login
# -----------------------------
@router.post("/login")
def login(user: AuthRequest, db: Session = Depends(get_db)):

    db_user = db.query(User).filter(User.username == user.username).first()

    if not db_user or not pwd_context.verify(user.password[:72], db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = jwt.encode(
        {
            "sub": db_user.username,
            "exp": datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": access_token}