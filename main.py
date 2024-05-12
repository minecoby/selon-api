from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import hmac
import hashlib
import subprocess
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


WEBHOOK_SECRET = "74D55CAF58DFEF548645C15FA8EA4"



def verify_signature(x_hub_signature, data):
    """
    GitHub에서 전송된 X-Hub-Signature 헤더와 요청 데이터를 사용하여 HMAC SHA1 서명을 검증합니다.
    """
    github_signature = hmac.new(bytes(WEBHOOK_SECRET, 'utf-8'), msg=data, digestmod=hashlib.sha1).hexdigest()
    return hmac.compare_digest(f'sha1={github_signature}', x_hub_signature)

@app.post("/webhook/")
async def github_webhook(request: Request, x_hub_signature):
    body = await request.body()

    # 시그니처 검증
    if x_hub_signature is None or not verify_signature(x_hub_signature, body):
        raise HTTPException(status_code=400, detail="Invalid signature")

    webhook_data = await request.json()
    # 여기서 webhook_data를 사용하여 특정 이벤트(예: push 이벤트)에 대한 처리를 할 수 있습니다.

    # push 이벤트가 감지되면 로컬에서 git pull 실행
    subprocess.run(["git", "pull"], cwd="/path/to/your/local/repo")
    return {"message": "Successfully pulled."}

#=========================================================================================================================================================
@app.get("/") #데코레이터
async def root():
    return {"message" : "반가워요 여러분"}


logging.basicConfig(level =logging.INFO)
logger = logging.getLogger(__name__)


items = {"1": {"name" : "pen"}, "2":{"name":"pencil"}}

@app.get("/items")
async def read_items(): 
    logger.info("Fetching all items ddsafsdd")
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