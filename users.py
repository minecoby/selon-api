from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
from database import user_Base, get_userdb, user_engine

class User(user_Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    realname = Column(String(30), nullable=False)
    nickname = Column(String(30), unique=True, nullable=False)
    grade = Column(Integer)

user_Base.metadata.create_all(bind=user_engine)

class UserCreate(BaseModel):
    user_id: str
    password: str
    realname: str
    nickname: str
    grade: int

class UserLogin(BaseModel):
    user_id: str
    password: str


class UserResponse(BaseModel):
    id: int
    user_id: str

    class Config:
        from_attributes = True

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_user(user_id: str, db: Session):
    return db.query(User).filter(User.user_id == user_id).first()

@router.post("/users/", response_model=UserResponse, tags=["user"])
def create_user(user: UserCreate, db: Session = Depends(get_userdb)):
    existing_user = get_user(user.user_id, db)
    if existing_user:
        raise HTTPException(status_code=409, detail="해당 아이디는 이미 존재합니다")

    hashed_password = get_password_hash(user.password)
    db_user = User(user_id=user.user_id, hashed_password=hashed_password, realname=user.realname, nickname=user.nickname, grade=user.grade)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user

@router.post("/users/login", tags=["user"])
def login_user(user: UserLogin, db: Session = Depends(get_userdb)):
    db_user = db.query(User).filter(User.user_id == user.user_id).first()
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="로그인 정보 불일치.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.user_id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}