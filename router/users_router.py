from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from data.models import User, Contact
from data.database import get_userdb
from typing import List
from data.schema import UserCreate,UserInfo,UserLogin,UserName,UserPwd,UserResponse, ContactInfo, SendContact, UpdateAnswer
from .crud import get_current_user,get_password_hash,get_user,get_user_nickname,get_userdb,verify_password,create_access_token,create_refresh_token,decode_jwt,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_MINUTES
from firebase_admin import messaging

router = APIRouter()
security = HTTPBearer()


@router.post("/users/", response_model=UserResponse, tags=["user"])
def create_user(user: UserCreate, db: Session = Depends(get_userdb)):
    existing_user = get_user(user.user_id, db)
    if existing_user:
        raise HTTPException(status_code=409, detail="해당 아이디는 이미 존재합니다")
    existing_user_name = get_user_nickname(user.nickname, db)
    if existing_user_name:
        raise HTTPException(status_code=409, detail="해당 닉네임은 이미 존재합니다")

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
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": db_user.user_id}, expires_delta=refresh_token_expires
    )
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/users/info",response_model=UserInfo, tags=["user"])
def user_info(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_userdb)):
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        user_id = payload.get("sub")
        user_info = db.query(User).filter(User.user_id == user_id).one_or_none()
        return UserInfo(realname=user_info.realname, nickname=user_info.nickname)
    except HTTPException as e:
        return {"status": "invalid", "detail": e.detail}

@router.patch("/users/changepwd",tags=["user"])
def change_password(user: UserPwd,credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_userdb)):
    token = credentials.credentials
    payload = decode_jwt(token)
    user_id = payload.get("sub")
    user_info = db.query(User).filter(User.user_id == user_id).one_or_none()
    if not verify_password(user.password, user_info.hashed_password):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 올바르지 않습니다.")
    user_info.hashed_password = get_password_hash(user.new_password)
    db.commit()
    db.refresh(user_info)
    return HTTPException(status_code=200, detail="정상적으로 비밀번호가 변경되었습니다.")

@router.patch("/users/changenickname",tags=["user"])
def change_nickname(user: UserName,credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_userdb)):
    token = credentials.credentials
    payload = decode_jwt(token)
    user_id = payload.get("sub")
    existing_user_name = get_user_nickname(user.nickname, db)
    if existing_user_name:
        raise HTTPException(status_code=409, detail="해당 닉네임은 이미 존재합니다")
    user_info = db.query(User).filter(User.user_id == user_id).one_or_none()
    user_info.nickname = user.nickname
    db.commit()
    db.refresh(user_info)
    return HTTPException(status_code=200, detail="정상적으로 닉네임이 변경되었습니다.")

@router.get("/check_token", tags=["user"])
def check_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        return {"status": "valid", "user_id": payload.get("sub")}
    except HTTPException as e:
        return {"status": "invalid", "detail": e.detail}

@router.post("/refresh_token", tags=["user"])
def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        user_id: str = payload.get("sub")
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": user_id}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
@router.post("/send_contact", tags=["user"])
def send_contact(contact: SendContact, credentials: HTTPAuthorizationCredentials = Security(security), db : Session = Depends(get_userdb)):
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        user_id: str = payload.get("sub")
        db_info = Contact(user_id=user_id, content = contact.content, answer = contact.answer, device_token = contact.device_token)
        db.add(db_info)
        db.commit()
        db.refresh(db_info)
        return HTTPException(status_code=200, detail="정상적으로 문의사항이 전송되었습니다.")

    except HTTPException as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/mycontact", response_model=List[ContactInfo], tags=["user"])
def read_contact(credentials: HTTPAuthorizationCredentials = Security(security), db : Session = Depends(get_userdb)):
    token = credentials.credentials
    try:
        payload = decode_jwt(token)
        user_id: str = payload.get("sub")
        db_info = db.query(Contact).filter(Contact.user_id == user_id).all()
        return db_info
    except HTTPException as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token") 

@router.patch("/update_answer/{contact_id}", tags=["user"])
def update_answer(contact_id: int, update_data: UpdateAnswer, db: Session = Depends(get_userdb)):
    contact_entry = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact_entry:
        raise HTTPException(status_code=404, detail="문의사항을 찾을 수 없습니다.")

    contact_entry.answer = update_data.answer
    db.commit()
    db.refresh(contact_entry)

    message = messaging.Message(
    notification=messaging.Notification(
        title='[문의하기] 답변이 등록되었습니다',
        body='문의하신 내용에 대한 답변이 등록되었습니다. 확인부탁드립니다.'
    ),
    token=contact_entry.device_token,  # 개별 사용자 디바이스 토큰
    android=messaging.AndroidConfig(
        notification=messaging.AndroidNotification(
            channel_id='high_importance_channel'
        )
    )
)

    # 메시지 전송 시도 및 로깅
    try:
        response = messaging.send(message)
        print("Successfully sent message:", response)
    except Exception as e:
        print("Failed to send message:", e)

    return HTTPException(status_code=200, detail="답변이 정상적으로 변경되었습니다.")

   