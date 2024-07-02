from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import notice_Base, notice_engine
from datetime import datetime

class Post(notice_Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content = Column(String(2000))
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    comments = relationship("Comment", back_populates="post")

class Comment(notice_Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    likes = Column(Integer, default=0)
    post = relationship("Post", back_populates="comments")

notice_Base.metadata.create_all(bind=notice_engine)
