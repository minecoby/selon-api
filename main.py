# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from users import router as users_router
from notices import router as notices_router
from github_pull import handle_github_webhook

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

#===================================================================================================

# GitHub 자동 pull 함수 코드작성하실때 주석처리하시고 하세요
@app.post("/webhook/")
async def github_webhook(request: Request):
    return await handle_github_webhook(request)

@app.get("/")
async def root():
    return {"message": "반가워요 여러분"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)