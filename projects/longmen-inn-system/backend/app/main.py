"""
龙门客栈业务管理系统 - FastAPI 主入口
===============================
作者: 厨子 (神厨小福贵)
版本: v1.0.0
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.db.init_db import init_db
from app.websocket.handler import websocket_router, openclaw_event_loop
from app.services.openclaw_sync_service import openclaw_sync_service

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🏮 龙门客栈业务管理系统启动中...")
    
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, init_db)
    logger.info("✅ 数据库初始化完成")
    
    logger.info("🤖 加载 Agent 配置...")
    
    await openclaw_sync_service.sync_all_agents()
    logger.info("✅ OpenClaw Agent状态初始同步完成")
    
    openclaw_task = asyncio.create_task(openclaw_event_loop())
    sync_task = asyncio.create_task(openclaw_sync_service.start())
    logger.info("✅ OpenClaw事件循环已启动")
    logger.info("✅ OpenClaw状态同步服务已启动")
    
    logger.info("🎉 系统启动成功！")
    logger.info(f"📖 API 文档: http://{settings.HOST}:{settings.PORT}/docs")
    
    yield
    
    openclaw_task.cancel()
    openclaw_sync_service.stop()
    logger.info("🛑 系统正在关闭...")
    logger.info("👋 再见！")


app = FastAPI(
    title="龙门客栈业务管理系统",
    description="基于 OpenClaw 的多 Agent 协作管理平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {
        "message": "🏮 欢迎来到龙门客栈业务管理系统",
        "version": "1.0.0",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-03-14T12:00:00Z"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
