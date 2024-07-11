from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from passlib.context import CryptContext
from typing import Optional

from database import user_Base, get_userdb, user_engine

class User(user_Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    nickname = Column(String(255), unique=True, index=True, nullable=True)
    realname = Column(String(255), unique=True, index=True, nullable=True)
    grade = Column(Integer, nullable=True)

user_Base.metadata.create_all(bind=user_engine)

class UserCreate(BaseModel):
    user_id: str
    realname: str
    nickname: str
    password: str
    grade: int

class UserLogin(BaseModel):
    user_id: str
    password: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    grade: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    user_id: str
    realname: str
    nickname: Optional[str] = None
    grade: Optional[int] = None

    class Config:
        from_attributes = True

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@router.post("/users/signup", response_model=UserResponse, tags=["user"])
def create_user(user: UserCreate, db: Session = Depends(get_userdb)):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        user_id=user.user_id,
        realname = user.realname,
        nickname = user.nickname,
        hashed_password=hashed_password,
        grade = user.grade
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="user_id already registered")
    return db_user

@router.post("/users/login", response_model=UserResponse, tags=["user"])
def login_user(user: UserLogin, db: Session = Depends(get_userdb)):
    db_user = db.query(User).filter(User.user_id == user.user_id).first()
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid user_id or password")
    return db_user

@router.patch("/users/{user_id}", response_model=UserResponse, tags=["user"])
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_userdb)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.nickname is not None:
        db_user.nickname = user_update.nickname
    if user_update.grade is not None:
        db_user.grade = user_update.grade

    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserResponse, tags=["user"])
def read_user(user_id: int, db: Session = Depends(get_userdb)):
    db_user = db.query(User).filter(User.user_id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
