from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime

from database import notice_Base, get_noticedb, notice_engine

class Notice(notice_Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    content = Column(String(1000))
    url = Column(String(500))
    category = Column(String(255))


notice_Base.metadata.create_all(bind=notice_engine)

class NoticeCreate(BaseModel):
    title: str
    content: str
    url: str 
    category: str


class NoticeUpdate(BaseModel):
    title: str 
    content: str 
    url: str 

class NoticeResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    url: str 
    category: str


    class Config:
        from_attributes = True
        
class NoticeInfo(BaseModel):
    id : int
    title: str
    content: str
    category: str
    url: str 
    created_at: datetime

def get_title(title: str, db: Session):
    return db.query(Notice).filter(Notice.title == title).first()
router = APIRouter()

@router.post("/notice/", response_model=NoticeResponse, tags=["notice"])
def create_notice(notice: NoticeCreate, db: Session = Depends(get_noticedb)):
    db_content = Notice(title=notice.title,content=notice.content,category=notice.category, url=notice.url)
    if notice.category != ("totalCouncil" or "departmentCouncil" or "departmentNotice" or "applyRecruit"):
        raise HTTPException(status_code=412 , detail= "유효하지않은 공지사항카테고리입니다.")
    existing_title = get_title(notice.title, db)
    if existing_title:
        raise HTTPException(status_code=409 , detail= "이미 존재하는 공지사항 제목입니다.")
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content



@router.get("/notice", response_model=List[NoticeResponse], tags=["notice"])
def read_notice(category: str, db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).filter(Notice.category == category).all()
    if db_notice is None:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없음")
    return db_notice



@router.get("/notice/{notice_id}", response_model=NoticeInfo, tags=["notice"])
def read_notice_info(notice_id: int, db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if db_notice is None:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없음")
    return db_notice

@router.patch("/notice/{notice_id}", response_model=NoticeResponse, tags=["notice"])
def update_notice(notice_id: int, notice_update: NoticeUpdate, db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).filter(Notice.id == notice_id).first()
    if db_notice is None:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없음")
    
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
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없음")
    db.delete(db_notice)
    db.commit()

@router.get("/notice_top5", response_model=List[NoticeResponse], tags=["notice"])
def read_notice(db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice).order_by(Notice.created_at.desc()).limit(5).all()
    if not db_notice:
        raise HTTPException(status_code=404, detail="공지사항을 찾을 수 없음")
    return db_notice