from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
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


SECRET_TOKEN = "74D55CAF58DFEF548645C15FA8EA4"

@app.post("/webhook/")
async def github_webhook(request: Request):
    webhook_data = await request.json()
    # 여기서 webhook_data를 사용하여 특정 조건이 충족되었는지 확인하거나 로깅할 수 있습니다.
    # 예: 특정 브랜치에 대한 push 이벤트인지 확인

    # 여기서는 예제를 단순화하기 위해 모든 push에서 코드를 pull하도록 설정합니다.
    # 보안상의 이유로, 실제 환경에서는 요청이 실제 GitHub으로부터 왔는지 등을 검증해야 합니다.

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
    logger.info("Fetching all items adddd")
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