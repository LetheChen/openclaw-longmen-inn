"""
龙门客栈业务管理系统 - API依赖
===============================
作者: 厨子 (神厨小福贵)

FastAPI 依赖注入定义
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话
    
    用于 FastAPI 依赖注入，确保每个请求都有独立的数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 可以在这里添加更多的依赖，比如:
# - 当前用户认证
# - 权限检查
# - 日志记录器等