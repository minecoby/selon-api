from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from data.database import community_Base, notice_Base, user_Base, alarm_Base, community_engine, notice_engine, user_engine, alarm_engine
from datetime import datetime
import pytz

def get_korean_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime('%Y/%m/%d - %H시 %M분')

class Notice(notice_Base):
    __tablename__ = "notification"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), unique=True)
    created_at = Column(String(30), default=get_korean_time)
    content = Column(String(1000))
    url = Column(String(500))
    category = Column(String(255), index=True)
    deadline = Column(String(40))

class User(user_Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    realname = Column(String(30), nullable=False)
    nickname = Column(String(30), unique=True, nullable=False)
    grade = Column(Integer)

class Contact(user_Base):
    __tablename__ = "contact"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), unique=True, index=True)
    device_token = Column(String(500))
    content = Column(String(300))
    answer = Column(String(300))

class Post(community_Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String(30),index=True)
    title = Column(String(255), index=True)
    content = Column(String(2000))
    created_at = Column(String(30), default=get_korean_time)
    likes = Column(Integer, default=0)
    comments = relationship("Comment", back_populates="post")

class Comment(community_Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_name = Column(String(30),index=True)
    content = Column(String(1000))
    created_at = Column(String(30), default=get_korean_time)
    likes = Column(Integer, default=0)
    post = relationship("Post", back_populates="comments")

class Alarm(alarm_Base):
    __tablename__ = "alarm"
    id = Column(Integer, primary_key=True, index=True)
    device_token = Column(String(500))
    check_totalcouncil = Column(Boolean)
    check_departcouncil = Column(Boolean)
    check_depart = Column(Boolean)
    check_apply = Column(Boolean)


community_Base.metadata.create_all(bind=community_engine)
notice_Base.metadata.create_all(bind=notice_engine)
user_Base.metadata.create_all(bind=user_engine)
alarm_Base.metadata.create_all(bind=alarm_engine)
