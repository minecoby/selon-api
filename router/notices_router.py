from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from data.database import notice_Base, get_noticedb, notice_engine
from data.models import Notice
from data.schema import NoticeUpdate, NoticeCreate, NoticeInfo, NoticeResponse
from crud import get_title

router = APIRouter()

@router.post("/notice/", response_model=NoticeResponse, tags=["notice"])
def create_notice(notice: NoticeCreate, db: Session = Depends(get_noticedb)):
    db_content = Notice(title=notice.title,content=notice.content,category=notice.category, url=notice.url, deadline=notice.deadline)
    if notice.category != "totalCouncil" and notice.category != "departmentNotice" and notice.category != "departmentCouncil" and notice.category !="applyRecruit":
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