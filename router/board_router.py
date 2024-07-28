from fastapi import APIRouter, Depends, HTTPException, Security
from sqlalchemy.orm import Session
from typing import List
from data.database import get_communitydb,get_userdb
from data.models import Post, Comment
from .users_router import User
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from data.schema import PostCreate,PostResponse,PostUpdate,CommentCreate,CommentResponse,CommentUpdate
from .crud import decode_jwt
load_dotenv()

router = APIRouter()
security = HTTPBearer()


@router.post("/posts/", response_model=PostResponse, tags=["board"])
def create_post(post: PostCreate, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_communitydb), user_db: Session = Depends(get_userdb)):
    token = credentials.credentials
    payload = decode_jwt(token)
    user_id = payload.get("sub")
    user_info = user_db.query(User).filter(User.user_id == user_id).one_or_none()
    db_post = Post(title=post.title, content=post.content, user_name = user_info.nickname)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

@router.get("/posts/", response_model=List[PostResponse], tags=["board"])
def read_posts(db: Session = Depends(get_communitydb)):
    return db.query(Post).all()

@router.post("/comments/", response_model=CommentResponse, tags=["board"])
def create_comment(comment: CommentCreate, credentials: HTTPAuthorizationCredentials = Security(security),  db: Session = Depends(get_communitydb), user_db: Session = Depends(get_userdb)):
    token = credentials.credentials
    payload = decode_jwt(token)
    user_id = payload.get("sub")
    user_info = user_db.query(User).filter(User.user_id == user_id).one_or_none()
    db_comment = Comment(content=comment.content, post_id=comment.post_id, user_name = user_info.nickname)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.get("/comments/", response_model=List[CommentResponse], tags=["board"])
def read_comments(db: Session = Depends(get_communitydb)):
    return db.query(Comment).all()

@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse], tags=["board"])
def read_comments_by_post(post_id: int, db: Session = Depends(get_communitydb)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    comments = db.query(Comment).filter(Comment.post_id == post_id).all()
    return comments

@router.post("/posts/{post_id}/like", response_model=PostResponse, tags=["board"])
def like_post(post_id: int, db: Session = Depends(get_communitydb)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db_post.likes += 1
    db.commit()
    db.refresh(db_post)
    return db_post

@router.post("/comments/{comment_id}/like", response_model=CommentResponse, tags=["board"])
def like_comment(comment_id: int, db: Session = Depends(get_communitydb)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    db_comment.likes += 1
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.patch("/posts/{post_id}", response_model=PostResponse, tags=["board"])
def update_post(post_id: int, post: PostUpdate, db: Session = Depends(get_communitydb)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.title:
        db_post.title = post.title
    if post.content:
        db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete("/posts/{post_id}", tags=["board"])
def delete_post(post_id: int, db: Session = Depends(get_communitydb)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    db.delete(db_post)
    db.commit()
    return {"message": "Post deleted successfully"}

@router.patch("/comments/{comment_id}", response_model=CommentResponse, tags=["board"])
def update_comment(comment_id: int, comment: CommentUpdate, db: Session = Depends(get_communitydb)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.content:
        db_comment.content = comment.content
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/comments/{comment_id}", tags=["board"])
def delete_comment(comment_id: int, db: Session = Depends(get_communitydb)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(db_comment)
    db.commit()
    return {"message": "Comment deleted successfully"}

@router.post("/posts/{post_id}/unlike", response_model=PostResponse, tags=["board"])
def unlike_post(post_id: int, db: Session = Depends(get_communitydb)):
    db_post = db.query(Post).filter(Post.id == post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    if db_post.likes > 0:
        db_post.likes -= 1
    db.commit()
    db.refresh(db_post)
    return db_post

@router.post("/comments/{comment_id}/unlike", response_model=CommentResponse, tags=["board"])
def unlike_comment(comment_id: int, db: Session = Depends(get_communitydb)):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.likes > 0:
        db_comment.likes -= 1
    db.commit()
    db.refresh(db_comment)
    return db_comment
