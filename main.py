from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import uvicorn
import hmac
import hashlib
import asyncio
import aiofiles
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


SECRET_KEY = "74D55CAF58DFEF548645C15FA8EA4"


@app.post("/webhook")
async def github_webhook(request: Request):
    signature_header = request.headers.get('X-Hub-Signature-256')
    if not signature_header:
        raise HTTPException(status_code=400, detail="Signature header missing")

    body = await request.body()

    hmac_gen = hmac.new(SECRET_KEY.encode(), body, hashlib.sha256)
    expected_signature = "sha256=" + hmac_gen.hexdigest()

    if not hmac.compare_digest(expected_signature, signature_header):
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        repo_path = 'C:/Users/admin/Documents/GitHub/selon-api'
        await git_pull(repo_path)
    except Exception as e:
        return {"message": "pull 되지않음", "details": str(e)}
    
    return {"message": "정상적으로 pull 되었음"}

async def git_pull(repo_path: str):
    process = await asyncio.create_subprocess_exec(
        'git',
        '-C',
        repo_path,
        'pull',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(f"Git pull failed: {stderr.decode().strip()}")

#=========================================================================================================================================================
@app.get("/") #데코레이터
async def root():
    return {"message" : "반가워요 여러분"}


logging.basicConfig(level =logging.INFO)
logger = logging.getLogger(__name__)


items = {"1": {"name" : "pen"}, "2":{"name":"pencil"}}

@app.get("/items")
async def read_items(): 
    logger.info("Fetching all items ddadddd")
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