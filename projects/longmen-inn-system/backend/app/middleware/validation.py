"""
龙门客栈业务管理系统 - 输入验证中间件
===============================
作者: 厨子 (神厨小福贵)

防止SQL注入、XSS等攻击的输入验证中间件
"""

import re
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    输入验证中间件
    
    功能：
    1. 检测SQL注入模式
    2. 检测XSS攻击模式
    3. 验证Content-Type
    4. 限制请求体大小
    """
    
    # SQL注入危险模式
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b)",
        r"(\b(UNION|INTERSECT|EXCEPT)\b\s+\b(SELECT|ALL)\b)",
        r"(--\s*$|#\s*$)",
        r"(/\*.*\*/)",
        r"(;\s*$)",
        r"(\b(OR|AND)\b\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+)",
        r"(EXEC\s+|EXECUTE\s+)",
        r"(xp_cmdshell|sp_)",
    ]
    
    # XSS危险模式
    XSS_PATTERNS = [
        r"<\s*script[^>]*>",
        r"javascript\s*:",
        r"on\w+\s*=",
        r"<\s*iframe[^>]*>",
        r"<\s*object[^>]*>",
        r"<\s*embed[^>]*>",
        r"<\s*form[^>]*>",
        r"eval\s*\(",
        r"document\.(cookie|location|write)",
        r"window\.(location|open)",
    ]
    
    # 允许的最大请求体大小 (10MB)
    MAX_BODY_SIZE = 10 * 1024 * 1024
    
    # 需要跳过验证的路径
    SKIP_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health",
        "/favicon.ico",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过特定路径
        for skip_path in self.SKIP_PATHS:
            if request.url.path.startswith(skip_path):
                return await call_next(request)
        
        # 检查请求体大小
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                length = int(content_length)
                if length > self.MAX_BODY_SIZE:
                    logger.warning(f"请求体过大: {length} bytes (最大 {self.MAX_BODY_SIZE})")
                    return Response(
                        content='{"detail": "请求体过大"}',
                        status_code=413,
                        media_type="application/json"
                    )
            except ValueError:
                pass
        
        # 验证查询参数
        query_params = str(request.query_params)
        if self._detect_malicious(query_params, "Query参数"):
            logger.warning(f"检测到恶意查询参数: {request.url}")
            return Response(
                content='{"detail": "检测到非法输入"}',
                status_code=400,
                media_type="application/json"
            )
        
        # 验证路径参数
        path = request.url.path
        if self._detect_malicious(path, "路径"):
            logger.warning(f"检测到恶意路径: {path}")
            return Response(
                content='{"detail": "检测到非法输入"}',
                status_code=400,
                media_type="application/json"
            )
        
        # 对于JSON请求，验证请求体（只读取，不消费）
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    body = await request.body()
                    if body:
                        body_str = body.decode("utf-8", errors="ignore")
                        if self._detect_malicious(body_str, "请求体"):
                            logger.warning(f"检测到恶意请求体")
                            return Response(
                                content='{"detail": "检测到非法输入"}',
                                status_code=400,
                                media_type="application/json"
                            )
                except Exception as e:
                    logger.error(f"验证请求体时出错: {e}")
        
        return await call_next(request)
    
    def _detect_malicious(self, content: str, source: str) -> bool:
        """检测内容中是否存在恶意模式"""
        if not content:
            return False
        
        content_lower = content.lower()
        
        # 检测SQL注入
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                logger.debug(f"[{source}] 检测到SQL注入模式: {pattern}")
                return True
        
        # 检测XSS
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, content_lower, re.IGNORECASE):
                logger.debug(f"[{source}] 检测到XSS模式: {pattern}")
                return True
        
        return False


# 导出中间件实例
validation_middleware = ValidationMiddleware