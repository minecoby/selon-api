
import hmac
import hashlib
import subprocess
from fastapi import HTTPException
from dotenv import load_dotenv
import os
load_dotenv()
token = os.environ.get("GITHUB_TOKEN")
SECRET_TOKEN = token.encode('utf-8')

async def handle_github_webhook(request):
    signature = request.headers.get('X-Hub-Signature-256')
    body = await request.body()
    expected_signature = 'sha256=' + hmac.new(SECRET_TOKEN, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected_signature, signature):
        raise HTTPException(status_code=400, detail="서명 검증 실패")

    subprocess.run(['C:\\Program Files\\Git\\bin\\git.exe', 'pull'], check=True)

    return {"message": "성공적으로 업데이트됨"}