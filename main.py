from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import subprocess
import hmac
import hashlib

app = FastAPI() #fast api 어플리케이션 생성? 

origins = [
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],   
    allow_headers=["*"],	
)
#=========================================================================================================================================================


SECRET_TOKEN = b"74D55CAF58DFEF548645C15FA8EA4"

@app.post("/webhook/")
async def github_webhook(request: Request):
    # GitHub에서 보낸 서명 검증
    signature = request.headers.get('X-Hub-Signature-256')
    body = await request.body()
    expected_signature = 'sha256=' + hmac.new(SECRET_TOKEN, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        return {"error": "서명 검증 실패"}

    # git pull 실행
    subprocess.run(['git', 'pull'], check=True)

    # 필요한 추가 작업 실행
    # 예: subprocess.run(['./restart_server.sh'], check=True)

    return {"message": "성공적으로 업데이트됨"}



#=========================================================================================================================================================
@app.get("/") #데코레이터
async def root():
    return {"message" : "반가워요 여러분"}


logging.basicConfig(level =logging.INFO)
logger = logging.getLogger(__name__)


items = {"1": {"name" : "pen"}, "2":{"name":"pencil"}}

@app.get("/items")
async def read_items(): 
    logger.info("Fetching all items addd")
    return items


@app.post("/items/{item_id}")  #
async def create_item(item_id : str, name: str = Form(...)):
    items[item_id] = {"name": name}
    logger.info(f"item created: {item_id} - {name}")
    return items[item_id]


@app.put("/items/{item_id}")
async def update_item(item_id: str, name :str = Form(...)):
    items[item_id] = {"name" : name}
    logger.info(f"item updated: {item_id} - {name}")
    return items[item_id]

@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    if item_id in items:
        del items[item_id]
        logger.info(f"item deleted: {item_id}")
        return {"message:" "Item deleted"}
    else:
        logger.info(f"item not found: {item_id}")
        return {"message": "item not found"}

@app.patch("/items/{item_id}")
async def patch_item(item_id: str, name: str =Form(...)):
    if item_id in items:
        items[item_id]["name"] = name
        logger.info(f"Item patched: {item_id} - {name}")
        return items[item_id]
    else:
        logger.info(f"Item not found {item_id}")
        return {"message": "Item not found"}
    

#=========================================================================================================================================================



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port = 8000, reload= True)