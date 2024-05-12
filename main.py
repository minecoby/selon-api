from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
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


SECRET_TOKEN = "74D55CAF58DFEF548645C15FA8EA4"


@app.post("/webhook/")
async def github_webhook(request: Request):
    # GitHub에서 보낸 서명을 헤더에서 추출
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        raise HTTPException(status_code=400, detail="X-Hub-Signature-256 header missing")

    # 요청 본문을 받아옴
    body = await request.body()

    # HMAC을 사용해 서명 검증
    expected_signature = hmac.new(bytes(SECRET_TOKEN, 'utf-8'), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(f"sha256={expected_signature}", signature):
        raise HTTPException(status_code=400, detail="Invalid signature")

    # 서명이 유효하면 처리 로직 실행 (예: git pull 명령 실행)
    # 처리 로직을 여기에 구현
    
    return {"message": "Webhook received successfully"}

#=========================================================================================================================================================
@app.get("/") #데코레이터
async def root():
    return {"message" : "반가워요 여러분"}


logging.basicConfig(level =logging.INFO)
logger = logging.getLogger(__name__)


items = {"1": {"name" : "pen"}, "2":{"name":"pencil"}}

@app.get("/items")
async def read_items(): 
    logger.info("Fetching all items ddddda")
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