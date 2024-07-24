from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import community_Base,community_engine
from datetime import datetime
import pytz

def get_korean_time():
    seoul_tz = pytz.timezone('Asia/Seoul')
    return datetime.now(seoul_tz).strftime('%Y/%m/%d - %H시 %M분')


class Post(community_Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content = Column(String(2000))
    created_at = Column(String(30), default=get_korean_time)
    likes = Column(Integer, default=0)
    comments = relationship("Comment", back_populates="post")

class Comment(community_Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(String(1000))
    created_at = Column(String(30), default=get_korean_time)
    likes = Column(Integer, default=0)
    post = relationship("Post", back_populates="comments")

community_Base.metadata.create_all(bind=community_engine)
