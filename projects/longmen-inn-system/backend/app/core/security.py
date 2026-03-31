"""
龙门客栈业务管理系统 - JWT认证工具
===============================
作者: 厨子 (神厨小福贵)

JWT token 生成、验证、刷新等安全功能
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Set
import secrets
import logging

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import SessionLocal
from app.models.user import User, RefreshToken

logger = logging.getLogger(__name__)

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer认证方案（可选，用于API调用）
security = HTTPBearer(auto_error=False)

# =============================================================================
# Access Token 黑名单（登出后撤销）
# 注意：这是进程内内存存储，仅适用于单实例部署。
# 多实例或需要持久化时，应使用 Redis 实现。
# =============================================================================
_revoked_access_token_jtis: Set[str] = set()


def hash_password(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码的数据（通常是用户ID和角色）
        expires_delta: 过期时间增量
    
    Returns:
        JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # 生成唯一令牌ID，用于撤销
    jti = secrets.token_urlsafe(16)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
        "jti": jti,  # 令牌唯一ID，用于黑名单追踪
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def revoke_access_token_jti(jti: str) -> None:
    """
    将 access_token 的 jti 加入黑名单（登出时调用）
    
    Args:
        jti: 令牌唯一ID
    """
    _revoked_access_token_jtis.add(jti)
    logger.info(f"Access token revoked: jti={jti[:8]}...")


def create_refresh_token(
    user_id: int,
    db: Session,
    device_info: Optional[str] = None,
    ip_address: Optional[str] = None
) -> str:
    """
    创建刷新令牌并存储到数据库
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        device_info: 设备信息
        ip_address: IP地址
    
    Returns:
        刷新令牌字符串
    """
    # 生成随机令牌
    token = secrets.token_urlsafe(32)
    
    # 设置过期时间（30天）
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    
    # 存储到数据库
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at,
        device_info=device_info,
        ip_address=ip_address
    )
    db.add(refresh_token)
    db.commit()
    
    return token


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    验证JWT令牌
    
    Args:
        token: JWT令牌字符串
        token_type: 令牌类型（access 或 refresh）
    
    Returns:
        解码后的payload，验证失败返回None
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # 检查令牌类型
        if payload.get("type") != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        # 检查 access_token 是否已被撤销（黑名单）
        if token_type == "access":
            jti = payload.get("jti")
            if jti and jti in _revoked_access_token_jtis:
                logger.warning(f"Attempted use of revoked access token: jti={jti[:8] if jti else 'None'}...")
                return None
        
        return payload
        
    except JWTError as e:
        logger.warning(f"JWT verification failed: {str(e)}")
        return None


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """解码访问令牌（兼容旧方法名）"""
    return verify_token(token, "access")


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = None  # 调用者需传入正确的 db Session（通过 Depends(get_db)）
) -> Optional[User]:
    """
    获取当前用户（从Cookie或Authorization头）
    
    优先从Cookie中获取token，其次从Authorization头获取。
    用于可选认证的场景。
    
    注意：db 参数必须由调用者通过 Depends(get_db) 传入，
    不要自行实例化 SessionLocal()！
    """
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
    db: Session = None  # 调用者需传入正确的 db Session（通过 Depends(get_db)）
) -> User:
    """
    获取当前用户（必须认证）
    
    抛出401异常如果没有认证。
    
    注意：db 参数必须由调用者通过 Depends(get_db) 传入，
    不要自行实例化 SessionLocal()！
    """
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


def revoke_refresh_token(token: str, db: Session) -> bool:
    """
    撤销刷新令牌
    
    Args:
        token: 刷新令牌
        db: 数据库会话
    
    Returns:
        是否成功撤销
    """
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token
    ).first()
    
    if refresh_token:
        refresh_token.revoked = True
        db.commit()
        return True
    
    return False


def revoke_all_user_tokens(user_id: int, db: Session) -> int:
    """
    撤销用户所有刷新令牌（登出所有设备）
    
    Args:
        user_id: 用户ID
        db: 数据库会话
    
    Returns:
        撤销的令牌数量
    """
    count = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked == False
    ).update({"revoked": True})
    
    db.commit()
    return count


def validate_refresh_token(token: str, db: Session) -> Optional[RefreshToken]:
    """
    验证刷新令牌
    
    Args:
        token: 刷新令牌
        db: 数据库会话
    
    Returns:
        RefreshToken对象，无效返回None
    """
    refresh_token = db.query(RefreshToken).filter(
        RefreshToken.token == token,
        RefreshToken.revoked == False
    ).first()
    
    if not refresh_token:
        return None
    
    # 检查是否过期
    if refresh_token.expires_at < datetime.now(timezone.utc):
        refresh_token.revoked = True
        db.commit()
        return None
    
    return refresh_token


# CSRF保护
def generate_csrf_token() -> str:
    """生成CSRF令牌"""
    return secrets.token_urlsafe(32)


def validate_csrf_token(
    request: Request,
    csrf_token: str
) -> bool:
    """
    验证CSRF令牌
    
    从Cookie中读取CSRF token并与请求头中的token对比
    """
    cookie_token = request.cookies.get("csrf_token")
    
    if not cookie_token or not csrf_token:
        return False
    
    return secrets.compare_digest(cookie_token, csrf_token)