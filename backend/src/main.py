from src.core.patch import apply_monkey_patches

# Apply patches early to ensure all downstream imports use patched versions
apply_monkey_patches()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from src.services.session_service import create_db_and_tables
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Value Analyst Backend")

# 挂载上传目录以提供文件服务
# 确保目录存在
os.makedirs("knowledge", exist_ok=True)
app.mount("/static", StaticFiles(directory="knowledge"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
