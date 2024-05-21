from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime
from database import get_noticedb
from board import Post, Comment

class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    likes: int

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    post_id: int
    content: str

class CommentResponse(BaseModel):
    id: int
    post_id: int
    content: str
    created_at: datetime
    likes: int

    class Config:
        from_attributes = True

router = APIRouter()

@router.post("/posts/", response_model=PostResponse, tags=["board"])
def create_post(post: PostCreate, db: Session = Depends(get_noticedb)):
    db_post = Post(title=post.title, content=post.content)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/posts/", response_model=List[PostResponse], tags=["board"])
def read_posts(db: Session = Depends(get_noticedb)):
    return db.query(Post).all()

@router.post("/comments/", response_model=CommentResponse, tags=["board"])
def create_comment(comment: CommentCreate, db: Session = Depends(get_noticedb)):
    db_comment = Comment(content=comment.content, post_id=comment.post_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/comments/", response_model=List[CommentResponse], tags=["board"])
def read_comments(db: Session = Depends(get_noticedb)):
    return db.query(Comment).all()

@router.post("/posts/{post_id}/like", response_model=PostResponse, tags=["board"])
def like_post(post_id: int, db: Session = Depends(get_noticedb)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.likes += 1
    db.commit()
    db.refresh(db_post)
    return db_post

@router.post("/comments/{comment_id}/like", response_model=CommentResponse, tags=["board"])
def like_comment(comment_id: int, db: Session = Depends(get_noticedb)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    db_comment.likes += 1
    db.commit()
    db.refresh(db_comment)
    return db_comment
