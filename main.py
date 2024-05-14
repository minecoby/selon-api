from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from github_pull import handle_github_webhook
from typing import List

app = FastAPI() # FastAPI 애플리케이션 생성

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],   
    allow_headers=["*"],	
)

#=========================================================================================================================================================
SQLALCHEMY_DATABASE_URL_USER = "mysql+mysqlconnector://root:iRqLKIqRI4IHvKx@127.0.0.1:3306/user_database"
SQLALCHEMY_DATABASE_URL_NOTICE = "mysql+mysqlconnector://root:iRqLKIqRI4IHvKx@127.0.0.1:3306/notice_database"
user_engine = create_engine(SQLALCHEMY_DATABASE_URL_USER)
notice_engine = create_engine(SQLALCHEMY_DATABASE_URL_NOTICE)
user_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
notice_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=notice_engine)

user_Base = declarative_base()
notice_Base = declarative_base()


class User(user_Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(255), unique=True, index=True)
    grade = Column(Integer)

user_Base.metadata.create_all(bind=user_engine)

def get_userdb():
    db = user_SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_noticedb():
    db = notice_SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/users/", response_model=UserResponse, tags=["user"])
def create_user(user: UserCreate, db: Session = Depends(get_userdb)):
    db_user = User(nickname=user.nickname, grade=user.grade)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse, tags=["user"])
def read_user(user_id: int, db: Session = Depends(get_userdb)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.patch("/users/{user_id}", response_model=UserResponse, tags=["user"])
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
#=====================================================================================================================
class Notice(notice_Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True, index=True)
    content = Column(String(1000))

class NoticeTitleResponse(BaseModel):
    title: str

notice_Base.metadata.create_all(bind=notice_engine)

class NoticeCreate(BaseModel):
    title: str
    content: str

class NoticeUpdate(BaseModel):
    title: str
    content: str

class NoticeResponse(BaseModel):
    id: int
    title: str
    content: str

    class Config:
        from_attributes = True

@app.post("/notice/", response_model=NoticeResponse, tags=["notice"])
def create_notice(notice: NoticeCreate, db: Session = Depends(get_noticedb)):
    db_content = Notice(title=notice.title, content=notice.content)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    return db_content

@app.get("/notice/{notice_id}", response_model=List[NoticeTitleResponse], tags=["notice"])
def read_notice(db: Session = Depends(get_noticedb)):
    db_notice = db.query(Notice.title).all()
    titles = [NoticeTitleResponse(title = title[0]) for title in db_notice]
    if titles is None:
        raise HTTPException(status_code=404, detail="Notice not found")
    return titles

@app.patch("/notice/{notice_id}", response_model=NoticeResponse, tags=["notice"])
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

#===================================================================================================

# GitHub 자동 pull 함수 코드작성하실때 주석처리하시고 하세요
@app.post("/webhook/")
async def github_webhook(request: Request):
    return await handle_github_webhook(request)

@app.get("/") # 데코레이터
async def root():
    return {"message": "반가워요 여러분"}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

items = {"1": {"name": "pen"}, "2": {"name": "pencil"}}

@app.get("/items")
async def read_items(): 
    logger.info("Fetching all items")
    return items

@app.post("/items/{item_id}") 
async def create_item(item_id: str, name: str = Form(...)):
    items[item_id] = {"name": name}
    logger.info(f"item created: {item_id} - {name}")
    return items[item_id]

@app.put("/items/{item_id}")
async def update_item(item_id: str, name: str = Form(...)):
    items[item_id] = {"name": name}
    logger.info(f"item updated: {item_id} - {name}")
    return items[item_id]

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    if item_id in items:
        del items[item_id]
        logger.info(f"item deleted: {item_id}")
        return {"message": "Item deleted"}
    else:
        logger.info(f"item not found: {item_id}")
        return {"message": "Item not found"}

@app.patch("/items/{item_id}")
async def patch_item(item_id: str, name: str = Form(...)):
    if item_id in items:
        items[item_id]["name"] = name
        logger.info(f"Item patched: {item_id} - {name}")
        return items[item_id]
    else:
        logger.info(f"Item not found {item_id}")
        return {"message": "Item not found"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
