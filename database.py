from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
load_dotenv()
DB_PASSWORD = os.environ.get("DB_PASSWORD")
USER_DB_NAME = os.environ.get("USER_DB_NAME")
NOTICE_DB_NAME = os.environ.get("NOTICE_DB_NAME")
SQLALCHEMY_DATABASE_URL_USER = f"mysql+mysqlconnector://root:{DB_PASSWORD}@localhost:3306/{USER_DB_NAME}"
SQLALCHEMY_DATABASE_URL_NOTICE = f"mysql+mysqlconnector://root:{DB_PASSWORD}@localhost:3306/{NOTICE_DB_NAME}?charset=utf8mb4"

user_engine = create_engine(SQLALCHEMY_DATABASE_URL_USER)
notice_engine = create_engine(SQLALCHEMY_DATABASE_URL_NOTICE)

user_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=user_engine)
notice_SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=notice_engine)

user_Base = declarative_base()
notice_Base = declarative_base()

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
