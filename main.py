from fastapi import FastAPI, Form, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from github_pull import handle_github_webhook

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
SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://<username>:<password>@<host>/<database_name>"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True, index=True)
    grade = Column(Integer)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
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
        orm_mode = True

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(nickname=user.nickname, grade=user.grade)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
