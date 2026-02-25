from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api.agents import router as agents_router
from api.conversations import router as conversations_router
from api.llm import router as llm_router

app = FastAPI(title="MetisAI", version="0.1.0")

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(agents_router)
app.include_router(conversations_router)
app.include_router(llm_router)

@app.get("/")
async def root():
    return {"message": "MetisAI Backend"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
