from sqlalchemy.orm import Session
from database import user_engine, notice_engine
from users import User
from notices import Notice
from board import Post, Comment

def view_db():
    user_session = Session(bind=user_engine)
    users = user_session.query(User).all()
    
    notice_session = Session(bind=notice_engine)
    notices = notice_session.query(Notice).all()
    posts = notice_session.query(Post).all()
    comments = notice_session.query(Comment).all()

    print("Users:")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}, Nickname: {user.nickname}, Grade: {user.grade}")
    
    print("\nNotices:")
    for notice in notices:
        print(f"ID: {notice.id}, Title: {notice.title}, Content: {notice.content}")
    
    print("\nPosts:")
    for post in posts:
        print(f"ID: {post.id}, Title: {post.title}, Content: {post.content}, Likes: {post.likes}, Created At: {post.created_at}")
    
    print("\nComments:")
    for comment in comments:
        print(f"ID: {comment.id}, Post ID: {comment.post_id}, Content: {comment.content}, Likes: {comment.likes}, Created At: {comment.created_at}")

    user_session.close()
    notice_session.close()

if __name__ == "__main__":
    view_db()
