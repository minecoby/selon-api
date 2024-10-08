from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from router.users_router import router as users_router
from router.notices_router import router as notices_router
from router.board_router import router as board_router
from router.alarm_router import router as alarm_router
from github_pull import handle_github_webhook
from data.database import user_Base, user_engine

import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate('data/selon-2ac18-8f9bf90cb657.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
else:
    default_app = firebase_admin.get_app()
app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(notices_router)
app.include_router(board_router)
app.include_router(alarm_router)

@app.post("/webhook/")
async def github_webhook(request: Request):
    return await handle_github_webhook(request)

@app.get("/")
async def root():
    return {"message": "반가워요 여러분"}

if __name__ == "__main__":
    import uvicorn

    user_Base.metadata.create_all(bind=user_engine)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
