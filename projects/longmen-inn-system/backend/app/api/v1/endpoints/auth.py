"""
龙门客栈业务管理系统 - 认证API端点
===============================
作者: 厨子 (神厨小福贵)

用户登录、注册、令牌管理等认证相关API
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.base import SessionLocal
from app.models.user import User, UserRole, RefreshToken, AuditLog
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
    revoke_refresh_token,
    revoke_all_user_tokens,
    validate_refresh_token,
    generate_csrf_token,
    validate_csrf_token,
)
from app.core.config import settings
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserDetail,
    UserListResponse,
    LoginRequest,
    LoginResponse,
    TokenRefreshResponse,
    LogoutResponse,
    ChangePasswordRequest,
)
from app.deps import get_db, get_current_user, get_current_user_required, get_admin_user

logger = logging.getLogger(__name__)

router = APIRouter(tags=["认证"])
security = HTTPBearer(auto_error=False)


# Cookie配置
ACCESS_TOKEN_COOKIE_NAME = "access_token"
REFRESH_TOKEN_COOKIE_NAME = "refresh_token"
CSRF_TOKEN_COOKIE_NAME = "csrf_token"

# Cookie过期时间
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小时
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30天


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
    csrf_token: str
):
    """
    设置认证Cookie（HttpOnly）
    
    Args:
        response: FastAPI响应对象
        access_token: JWT访问令牌
        refresh_token: 刷新令牌
        csrf_token: CSRF令牌
    """
    # 设置安全属性：生产环境强制 HttpOnly, Secure, SameSite
    is_production = settings.is_production
    
    # Access Token Cookie
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,  # 防止XSS攻击
        secure=is_production,  # 生产环境强制HTTPS
        samesite="strict",  # 防止CSRF
        path="/"
    )
    
    # Refresh Token Cookie
    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=is_production,
        samesite="strict",
        path="/api/v1/auth"  # 只在认证端点发送
    )
    
    # CSRF Token Cookie（非HttpOnly，前端可读）
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE_NAME,
        value=csrf_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=False,  # 前端需要读取
        secure=is_production,
        samesite="strict",
        path="/"
    )


def clear_auth_cookies(response: Response):
    """清除认证Cookie"""
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME, path="/")
    response.delete_cookie(key=REFRESH_TOKEN_COOKIE_NAME, path="/api/v1/auth")
    response.delete_cookie(key=CSRF_TOKEN_COOKIE_NAME, path="/")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    创建新用户账户。仅开发环境或管理员可调用。
    """
    # 检查用户名是否存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建用户
    hashed_password = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=UserRole.WORKER.value,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=user.id,
        username=user.username,
        action="register",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"用户注册成功: {user.username} (ID: {user.id})")
    
    return UserResponse.model_validate(user)


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    验证用户名/邮箱和密码，返回用户信息和Cookie中的令牌。
    """
    # 查找用户（支持用户名或邮箱登录）
    user = db.query(User).filter(
        (User.username == credentials.username) | 
        (User.email == credentials.username)
    ).first()
    
    if not user:
        # 记录失败的登录尝试
        _log_failed_login(db, credentials.username, request, "用户不存在")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 检查账户是否锁定
    if user.locked_until and user.locked_until > datetime.now(timezone.utc):
        _log_failed_login(db, user.username, request, "账户已锁定")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"账户已锁定，请{user.locked_until.strftime('%Y-%m-%d %H:%M')}后再试"
        )
    
    # 检查账户是否激活
    if not user.is_active:
        _log_failed_login(db, user.username, request, "账户未激活")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用，请联系管理员"
        )
    
    # 验证密码
    if not verify_password(credentials.password, user.hashed_password):
        # 增加失败尝试次数
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        
        # 超过5次锁定账户30分钟
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=30)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="登录失败次数过多，账户已锁定30分钟"
            )
        
        db.commit()
        _log_failed_login(db, user.username, request, "密码错误")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    # 登录成功，重置失败计数
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = request.client.host if request.client else None
    
    # 生成令牌
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role
    }
    
    # 根据remember_me设置过期时间
    if credentials.remember_me:
        access_token = create_access_token(
            token_data,
            timedelta(days=7)  # 记住我：7天
        )
    else:
        access_token = create_access_token(token_data)
    
    refresh_token = create_refresh_token(
        user.id,
        db,
        device_info=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None
    )
    
    csrf_token = generate_csrf_token()
    
    # 设置Cookie
    set_auth_cookies(response, access_token, refresh_token, csrf_token)
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=user.id,
        username=user.username,
        action="login",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"用户登录成功: {user.username} (ID: {user.id})")
    
    return LoginResponse(
        user=UserResponse.model_validate(user),
        message="登录成功"
    )


@router.post("/refresh", response_model=TokenRefreshResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌
    
    使用HttpOnly Cookie中的refresh_token获取新的access_token
    """
    # 从Cookie获取refresh_token
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未找到刷新令牌"
        )
    
    # 验证refresh_token
    refresh_token_obj = validate_refresh_token(refresh_token_value, db)
    
    if not refresh_token_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的刷新令牌"
        )
    
    # 获取用户
    user = db.query(User).filter(User.id == refresh_token_obj.user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已禁用"
        )
    
    # 生成新的access_token
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role
    }
    access_token = create_access_token(token_data)
    
    # 生成新的CSRF token
    csrf_token = generate_csrf_token()
    
    # 更新Cookie
    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.is_production,
        samesite="strict",
        path="/"
    )
    
    response.set_cookie(
        key=CSRF_TOKEN_COOKIE_NAME,
        value=csrf_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=False,
        secure=settings.is_production,
        samesite="strict",
        path="/"
    )
    
    logger.info(f"令牌刷新成功: 用户 {user.username}")
    
    return TokenRefreshResponse(message="令牌刷新成功")


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    用户登出
    
    撤销refresh_token并清除所有认证Cookie
    """
    # 从Cookie获取refresh_token并撤销
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    
    if refresh_token_value:
        revoke_refresh_token(refresh_token_value, db)
    
    # 清除所有Cookie
    clear_auth_cookies(response)
    
    # 记录审计日志（如果用户已登录）
    user = await get_current_user(request, db=db)
    if user:
        audit_log = AuditLog(
            user_id=user.id,
            username=user.username,
            action="logout",
            resource_type="user",
            resource_id=user.id,
            ip_address=request.client.host if request.client else None,
            status="success"
        )
        db.add(audit_log)
        db.commit()
        logger.info(f"用户登出: {user.username}")
    
    return LogoutResponse(message="登出成功")


@router.post("/logout-all", response_model=LogoutResponse)
async def logout_all_devices(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    登出所有设备
    
    撤销用户所有refresh_token，强制所有设备重新登录
    """
    # 撤销所有令牌
    count = revoke_all_user_tokens(current_user.id, db)
    
    # 清除Cookie
    clear_auth_cookies(response)
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="logout_all_devices",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        details=f"撤销了{count}个令牌",
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"用户登出所有设备: {current_user.username}, 撤销{count}个令牌")
    
    return LogoutResponse(message=f"已登出所有设备，撤销{count}个会话")


@router.get("/me", response_model=UserDetail)
async def get_current_user_info(
    current_user: User = Depends(get_current_user_required)
):
    """获取当前用户信息"""
    return UserDetail.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    更新当前用户信息
    
    支持修改昵称、邮箱、密码
    """
    # 修改密码需要验证当前密码
    if user_data.new_password:
        if not user_data.current_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="修改密码需要提供当前密码"
            )
        
        if not verify_password(user_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前密码错误"
            )
        
        current_user.hashed_password = hash_password(user_data.new_password)
        current_user.password_changed_at = datetime.now(timezone.utc)
    
    # 更新其他字段
    if user_data.full_name:
        current_user.full_name = user_data.full_name
    
    if user_data.email and user_data.email != current_user.email:
        # 检查邮箱是否已存在
        if db.query(User).filter(User.email == user_data.email, User.id != current_user.id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
        current_user.email = user_data.email
    
    db.commit()
    db.refresh(current_user)
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="update_profile",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    return UserResponse.model_validate(current_user)


@router.post("/change-password", response_model=dict)
async def change_password(
    password_data: ChangePasswordRequest,
    request: Request,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证当前密码
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码错误"
        )
    
    # 更新密码
    current_user.hashed_password = hash_password(password_data.new_password)
    current_user.password_changed_at = datetime.now(timezone.utc)
    
    # 撤销所有refresh_token（强制其他设备重新登录）
    revoke_all_user_tokens(current_user.id, db)
    
    db.commit()
    
    # 记录审计日志
    audit_log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="change_password",
        resource_type="user",
        resource_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        status="success"
    )
    db.add(audit_log)
    db.commit()
    
    logger.info(f"用户修改密码: {current_user.username}")
    
    return {"message": "密码修改成功，请在其他设备重新登录"}


@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    """
    获取CSRF令牌
    
    返回Cookie中存储的CSRF令牌，前端需要在POST/PUT/DELETE请求中
    通过X-CSRF-Token头发送此令牌
    """
    csrf_token = request.cookies.get(CSRF_TOKEN_COOKIE_NAME)
    
    if not csrf_token:
        # 如果没有CSRF令牌，生成一个新的
        csrf_token = generate_csrf_token()
    
    return {"csrf_token": csrf_token}


@router.post("/verify-csrf")
async def verify_csrf(
    request: Request,
):
    """
    验证CSRF令牌
    
    开发环境测试用，验证X-CSRF-Token头是否正确
    """
    # 从请求头获取CSRF令牌
    header_token = request.headers.get("X-CSRF-Token")
    
    if not header_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少X-CSRF-Token头"
        )
    
    if not validate_csrf_token(request, header_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF令牌验证失败"
        )
    
    return {"message": "CSRF令牌验证成功"}


def _log_failed_login(db: Session, username: str, request: Request, reason: str):
    """记录失败的登录尝试"""
    audit_log = AuditLog(
        username=username,
        action="login_failed",
        resource_type="user",
        details=reason,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        status="failed"
    )
    db.add(audit_log)
    db.commit()