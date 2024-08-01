from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from data.database import get_noticedb, get_alarmdb
from data.models import Notice, Alarm
from data.schema import NoticeUpdate, NoticeCreate, NoticeInfo, NoticeResponse
from .crud import get_title
import firebase_admin
from firebase_admin import credentials, messaging
from dotenv import load_dotenv
import os

file = os.environ.get("FILE_JSON")
cred = credentials.Certificate(file)
firebase_admin.initialize_app(cred)
router = APIRouter()

@router.post("/notice/", response_model=NoticeResponse, tags=["notice"])
def create_notice(notice: NoticeCreate, db: Session = Depends(get_noticedb), token_db: Session = Depends(get_alarmdb)):
    db_content = Notice(title=notice.title,content=notice.content,category=notice.category, url=notice.url, deadline=notice.deadline)
    if notice.category != "totalCouncil" and notice.category != "departmentNotice" and notice.category != "departmentCouncil" and notice.category !="applyRecruit":
        raise HTTPException(status_code=412 , detail= "유효하지않은 공지사항카테고리입니다.")
    existing_title = get_title(notice.title, db)
    if existing_title:
        raise HTTPException(status_code=409 , detail= "이미 존재하는 공지사항 제목입니다.")
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    try:
        category_filters = {
            "totalCouncil": Alarm.check_totalcouncil,
            "departmentNotice": Alarm.check_depart,
            "departmentCouncil": Alarm.check_departcouncil,
            "applyRecruit": Alarm.check_apply
        }
        category_name = {
            "totalCouncil": "총학생회공지",
            "departmentNotice": "학과공지",
            "departmentCouncil": "과학생회공지",
            "applyRecruit": "신청/모집"
        }
        filter_condition = category_filters[notice.category]
        device_tokens = token_db.query(Alarm.device_token).filter(filter_condition == True).all()
        device_tokens = [token[0] for token in device_tokens]
        if not device_tokens:
            raise HTTPException(status_code=400, detail="No device tokens found")
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=f'[{category_name[notice.category]}] {notice.title}',
                body=notice.content,
            ),
            android=messaging.AndroidConfig(
                notification=messaging.AndroidNotification(
                    channel_id='high_importance_channel', 
                ),
            ),
            tokens=device_tokens,
        )
        response = messaging.send_multicast(message)
        if response.failure_count > 0:
            responses = response.responses
            invalid_tokens = []
            for idx, resp in enumerate(responses):
                if not resp.success:
                    error = resp.exception
                    # if error.code in ['invalid-registration-token', 'registration-token-not-registered']:
                    invalid_tokens.append(device_tokens[idx])
            print(invalid_tokens)
            
            if invalid_tokens:
                token_db.query(Alarm).filter(Alarm.device_token.in_(invalid_tokens)).delete(synchronize_session=False)
                token_db.commit()
        return db_content
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



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