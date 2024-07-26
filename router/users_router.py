from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from data.models import User
from data.database import get_userdb
from data.schema import UserCreate,UserInfo,UserLogin,UserName,UserPwd,UserResponse
from crud import get_current_user,get_password_hash,get_user,get_user_nickname,get_userdb,verify_password,create_access_token,create_refresh_token,decode_jwt,ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_MINUTES
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
