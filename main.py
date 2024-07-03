from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from notices import router as notices_router
from board_router import router as board_router
from github_pull import handle_github_webhook
from database import user_Base, user_engine

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
