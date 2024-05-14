# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL_USER = "mysql+mysqlconnector://root:iRqLKIqRI4IHvKx@localhost:3306/user_database"
SQLALCHEMY_DATABASE_URL_NOTICE = "mysql+mysqlconnector://root:iRqLKIqRI4IHvKx@localhost:3306/notice_database"

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
