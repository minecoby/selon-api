from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import datetime

from database import notice_Base, get_noticedb, notice_engine

class Notice(notice_Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, index=True)
    created_at = Column(String(255),index=True)
    content = Column(String(1000))

notice_Base.metadata.create_all(bind=notice_engine)

class NoticeCreate(BaseModel):
    title: str
    content: str

class NoticeUpdate(BaseModel):
    title: str = None
    content: str = None

class NoticeResponse(BaseModel):
    id: int
    title: str
    created_at: str

    class Config:
        from_attributes = True
        
class NoticeInfo(BaseModel):
    id : int
    title: str
    content: str
    created_at: str

router = APIRouter()

@router.post("/notice/", response_model=NoticeResponse, tags=["notice"])
def create_notice(notice: NoticeCreate, db: Session = Depends(get_noticedb)):
    db_content = Notice(title=notice.title,created_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') ,content=notice.content)
    db_content = Notice(title=notice.title, content=notice.content)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@router.get("/notice/", response_model=List[NoticeResponse], tags=["notice"])
def read_notice(db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).all()
    if db_notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    return db_notice

@router.get("/notice/{notice_id}", response_model=NoticeInfo, tags=["notice"])
def read_notice_info(notice_id: int, db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if db_notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    return db_notice

@router.patch("/notice/{notice_id}", response_model=NoticeResponse, tags=["notice"])
def update_notice(notice_id: int, notice_update: NoticeUpdate, db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if db_notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    
    if notice_update.title is not None:
        db_notice.title = notice_update.title
    if notice_update.content is not None:
        db_notice.content = notice_update.content

    db.commit()
    db.refresh(db_notice)
    return db_notice

@router.delete("/notice/{notice_id}", tags=['notice'])
def delete_notice(notice_id: int, db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if db_notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    db.delete(db_notice)
    db.commit()
