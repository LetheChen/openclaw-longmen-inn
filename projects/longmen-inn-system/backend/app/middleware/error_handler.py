"""
龙门客栈业务管理系统 - 错误处理中间件
===============================
作者: 厨子 (神厨小福贵)

错误信息脱敏处理中间件
"""

import logging
import traceback
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    全局错误处理中间件
    
    功能：
    1. 捕获所有未处理异常
    2. 记录详细错误日志
    3. 返回脱敏后的错误响应
    4. 区分开发/生产环境响应
    """
    
    # 敏感信息关键字（不暴露给用户）
    SENSITIVE_KEYWORDS = [
        "password",
        "secret",
        "key",
        "token",
        "credential",
        "database",
        "connection",
        "stack",
        "traceback",
        "file",
        "line",
        "internal",
    ]
    
    # 需要跳过处理的路径（FastAPI内置文档）
    SKIP_PATHS = [
        "/docs",
        "/redoc",
        "/openapi.json",
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 跳过文档路径
        for skip_path in self.SKIP_PATHS:
            if request.url.path.startswith(skip_path):
                return await call_next(request)
        
        try:
            return await call_next(request)
        
        except RequestValidationError as exc:
            # 请求验证错误（用户输入问题）
            errors = []
            for error in exc.errors():
                # 脱敏错误信息
                error_msg = self._sanitize_message(str(error.get("msg", "")))
                errors.append({
                    "field": ".".join(str(loc) for loc in error.get("loc", [])),
                    "message": error_msg,
                    "type": error.get("type", "validation_error")
                })
            
            logger.warning(f"请求验证错误: {errors}")
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "请求参数验证失败",
                    "errors": errors,
                    "type": "validation_error"
                }
            )
        
        except StarletteHTTPException as exc:
            # HTTP异常（已知的错误）
            message = self._sanitize_message(str(exc.detail))
            
            logger.warning(f"HTTP异常 [{exc.status_code}]: {message}")
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "detail": message,
                    "type": "http_error"
                }
            )
        
        except Exception as exc:
            # 未处理的异常（需要记录详细日志）
            error_id = id(exc)  # 简单的错误ID
            
            # 记录详细错误日志（仅服务器端）
            logger.error(
                f"未处理异常 [{error_id}]: {type(exc).__name__}: {exc}\n"
                f"路径: {request.method} {request.url.path}\n"
                f"追踪:\n{traceback.format_exc()}"
            )
            
            # 返回脱敏后的错误响应
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "服务器内部错误，请稍后重试",
                    "error_id": str(error_id),
                    "type": "internal_error"
                }
            )
    
    def _sanitize_message(self, message: str) -> str:
        """脱敏错误消息，移除敏感信息"""
        import re
        
        sanitized = message
        
        # 移除文件路径
        sanitized = re.sub(r'[A-Za-z]:\\[^\s]+', '[path]', sanitized)
        sanitized = re.sub(r'/[^\s]+\.(py|js|ts|json)', '[path]', sanitized)
        
        # 移除敏感关键字相关内容
        for keyword in self.SENSITIVE_KEYWORDS:
            # 匹配 keyword=值 或 keyword: 值 的模式
            pattern = rf'{keyword}\s*[=:]\s*\S+'
            sanitized = re.sub(pattern, f'{keyword}=[hidden]', sanitized, flags=re.IGNORECASE)
        
        # 移除IP地址
        sanitized = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[ip]', sanitized)
        
        # 移除SQL语句片段
        sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER']
        for kw in sql_keywords:
            sanitized = re.sub(rf'\b{kw}\b', '[sql]', sanitized, flags=re.IGNORECASE)
        
        return sanitized


# 导出中间件实例
error_handler_middleware = ErrorHandlerMiddleware