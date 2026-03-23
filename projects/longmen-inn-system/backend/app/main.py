"""
龙门客栈业务管理系统 - FastAPI 主入口
===============================
作者: 厨子 (神厨小福贵)
版本: v1.0.0
"""

import asyncio
import uvicorn
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.db.init_db import init_db
from app.websocket.handler import websocket_router, openclaw_event_loop
from app.services.openclaw_sync_service import openclaw_sync_service
from app.middleware.validation import ValidationMiddleware
from app.middleware.error_handler import ErrorHandlerMiddleware
from app.routers import audit_log

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
    
    # openclaw_task.cancel()
    # openclaw_sync_service.stop()
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

# 简单的内存速率限制器
class RateLimiter:
    """基于内存的简单速率限制器"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self._requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        """检查是否允许请求，返回 (是否允许, 剩余次数)"""
        now = time.time()
        minute_ago = now - 60
        
        # 清理过期请求
        self._requests[client_id] = [
            t for t in self._requests[client_id] if t > minute_ago
        ]
        
        # 检查限制
        if len(self._requests[client_id]) >= self.requests_per_minute:
            return False, 0
        
        # 记录请求
        self._requests[client_id].append(now)
        remaining = self.requests_per_minute - len(self._requests[client_id])
        return True, remaining


# 全局速率限制器（每分钟1000次请求，方便开发测试）
rate_limiter = RateLimiter(requests_per_minute=1000)


# 速率限制中间件
class RateLimitMiddleware:
    """速率限制中间件"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request = Request(scope, receive)
        
        # 获取客户端标识（IP 或用户ID）
        client_id = request.client.host if request.client else "unknown"
        if hasattr(request.state, "user") and request.state.user:
            client_id = f"user_{request.state.user.id}"
        
        # 跳过特定路径
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        if any(request.url.path.startswith(p) for p in skip_paths):
            await self.app(scope, receive, send)
            return
        
        # 检查速率限制
        allowed, remaining = rate_limiter.is_allowed(client_id)
        
        if not allowed:
            response = JSONResponse(
                status_code=429,
                content={
                    "detail": "请求过于频繁，请稍后重试",
                    "type": "rate_limit_exceeded",
                    "retry_after": 60
                }
            )
            await response(scope, receive, send)
            return
        
        await self.app(scope, receive, send)

# 安全中间件（暂时全部禁用，待修复）
# app.add_middleware(ErrorHandlerMiddleware)
# app.add_middleware(ValidationMiddleware)
# app.add_middleware(RateLimitMiddleware)

# CORS配置（严格模式）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    max_age=600,  # 预检请求缓存10分钟
)

app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router)
app.include_router(audit_log.router, prefix="/api/v1", tags=["Audit Log"])


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
