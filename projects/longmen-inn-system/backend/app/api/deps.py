"""
龙门客栈业务管理系统 - API依赖
===============================
作者: 厨子 (神厨小福贵)

FastAPI 依赖注入定义
"""

from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.user import User


# HTTP Bearer认证方案（可选，用于API调用）
security = HTTPBearer(auto_error=False)


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


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    获取当前用户（可选认证）
    
    从Cookie或Authorization头获取token并验证。
    如果未认证则返回None，不抛出异常。
    """
    from app.core.security import verify_token
    
    token = None
    
    # 1. 从HttpOnly Cookie获取token
    token = request.cookies.get("access_token")
    
    # 2. 从Authorization头获取（API调用场景）
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        return None
    
    # 验证token
    payload = verify_token(token, "access")
    if not payload:
        return None
    
    # 获取用户ID
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return None
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    
    return user


async def get_current_user_required(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前用户（必须认证）
    
    如果未认证则抛出401异常
    """
    from app.core.security import verify_token
    
    token = None
    
    # 1. 从HttpOnly Cookie获取token
    token = request.cookies.get("access_token")
    
    # 2. 从Authorization头获取（API调用场景）
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证token
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 获取用户ID
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的用户ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用",
        )
    
    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user_required)
) -> User:
    """获取管理员用户（必须管理员权限）"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user


# 导出常用依赖
__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_required",
    "get_admin_user",
]