"""
龙门客栈业务管理系统 - 用户认证Schema
===============================
作者: 厨子 (神厨小福贵)

用户登录、注册、令牌等数据模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import re


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: str = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")
    
    @validator('email')
    def validate_email(cls, v):
        """邮箱格式验证（宽松）"""
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('邮箱格式不正确')
        return v


class UserCreate(UserBase):
    """用户创建请求"""
    password: str = Field(..., min_length=8, max_length=128, description="密码")
    
    @validator('password')
    def validate_password(cls, v):
        """密码强度验证"""
        if len(v) < 8:
            raise ValueError('密码长度至少8位')
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码需要包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码需要包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码需要包含数字')
        return v
    
    @validator('username')
    def validate_username(cls, v):
        """用户名验证"""
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含字母、数字和下划线')
        return v


class UserUpdate(BaseModel):
    """用户更新请求"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = None
    current_password: Optional[str] = Field(None, min_length=8)
    new_password: Optional[str] = Field(None, min_length=8, max_length=128)
    
    @validator('email')
    def validate_email(cls, v):
        """邮箱格式验证（宽松）"""
        if v and not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('邮箱格式不正确')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v, values):
        """新密码验证"""
        if v and not values.get('current_password'):
            raise ValueError('修改密码需要提供当前密码')
        if v:
            if not re.search(r'[A-Z]', v):
                raise ValueError('密码需要包含大写字母')
            if not re.search(r'[a-z]', v):
                raise ValueError('密码需要包含小写字母')
            if not re.search(r'\d', v):
                raise ValueError('密码需要包含数字')
        return v


class UserResponse(UserBase):
    """用户响应"""
    id: int
    role: str
    is_active: bool
    agent_id: Optional[str] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserDetail(UserResponse):
    """用户详情（包含更多信息）"""
    failed_login_attempts: int = 0
    password_changed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")
    remember_me: bool = Field(False, description="记住我（延长token有效期）")


class LoginResponse(BaseModel):
    """登录响应"""
    user: UserResponse
    message: str = "登录成功"
    
    # 注意：access_token 通过 HttpOnly Cookie 返回
    # refresh_token 也通过 HttpOnly Cookie 返回
    # CSRF token 通过 Cookie 返回，前端需要从响应头获取


class TokenRefreshRequest(BaseModel):
    """令牌刷新请求（通过refresh_token cookie）"""
    pass  # refresh_token 通过 HttpOnly Cookie 传递


class TokenRefreshResponse(BaseModel):
    """令牌刷新响应"""
    message: str = "令牌刷新成功"


class LogoutResponse(BaseModel):
    """登出响应"""
    message: str = "登出成功"


class PasswordResetRequest(BaseModel):
    """密码重置请求"""
    email: str = Field(..., description="邮箱地址")
    
    @validator('email')
    def validate_email(cls, v):
        """邮箱格式验证（宽松）"""
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError('邮箱格式不正确')
        return v


class PasswordResetConfirm(BaseModel):
    """密码重置确认"""
    token: str = Field(..., description="重置令牌")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    current_password: str = Field(..., description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码")
    
    @validator('new_password')
    def validate_new_password(cls, v):
        """密码强度验证"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('密码需要包含大写字母')
        if not re.search(r'[a-z]', v):
            raise ValueError('密码需要包含小写字母')
        if not re.search(r'\d', v):
            raise ValueError('密码需要包含数字')
        return v


class UserListResponse(BaseModel):
    """用户列表响应"""
    data: List[UserResponse]
    total: int
    page: int
    page_size: int


class AuditLogResponse(BaseModel):
    """审计日志响应"""
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[int]
    details: Optional[str]
    ip_address: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """审计日志列表响应"""
    data: List[AuditLogResponse]
    total: int
    page: int
    page_size: int