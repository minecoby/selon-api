from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List

from database import user_Base, get_userdb, user_engine

class User(user_Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(255), unique=True, index=True)
    grade = Column(Integer)

user_Base.metadata.create_all(bind=user_engine)

class UserCreate(BaseModel):
    nickname: str
    grade: int

class UserUpdate(BaseModel):
    nickname: str = None
    grade: int = None

class UserResponse(BaseModel):
    id: int
    nickname: str
    grade: int

    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/users/", response_model=UserResponse, tags=["user"])
def create_user(user: UserCreate, db: Session = Depends(get_userdb)):
    db_user = User(nickname=user.nickname, grade=user.grade)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="이미 존재하는 닉네임입니다.")
    return db_user

@router.get("/users/{user_id}", response_model=UserResponse, tags=["user"])
def read_user(user_id: int, db: Session = Depends(get_userdb)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
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
