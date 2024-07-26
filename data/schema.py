from pydantic import BaseModel
from typing import Optional
#공지사항
class NoticeCreate(BaseModel):
    title: str
    content: str
    url: str 
    category: str
    deadline: str


class NoticeUpdate(BaseModel):
    title: str 
    content: str 
    url: str 

class NoticeResponse(BaseModel):
    id: int
    title: str
    created_at: str
    url: str 
    category: str
    deadline: str

    class Config:
        from_attributes = True
        
class NoticeInfo(BaseModel):
    id : int
    title: str
    content: str
    category: str
    url: str 
    created_at: str
    deadline: str


#유저정보
class UserCreate(BaseModel):
    user_id: str
    password: str
    realname: str
    nickname: str
    grade: int

class UserLogin(BaseModel):
    user_id: str
    password: str

class UserPwd(BaseModel):
    password: str
    new_password: str

class UserName(BaseModel):
    nickname: str
class UserResponse(BaseModel):
    id: int
    user_id: str

    class Config:
        from_attributes = True
class UserInfo(BaseModel):
    realname: str
    nickname: str

#커뮤니티
class PostCreate(BaseModel):
    title: str
    content: str

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_name: str
    created_at: str
    likes: int

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    post_id: int
    content: str

class CommentUpdate(BaseModel):
    content: Optional[str] = None

class CommentResponse(BaseModel):
    id: int
    post_id: int
    content: str
    user_name: str
    created_at: str
    likes: int

    class Config:
        from_attributes = True