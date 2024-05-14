from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from notices import router as notices_router

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

@app.get("/")
async def root():
    return {"message": "반가워요 여러분"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
