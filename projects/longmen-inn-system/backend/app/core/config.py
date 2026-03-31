"""
龙门客栈业务管理系统 - 核心配置
===============================
作者: 厨子 (神厨小福贵)

安全警告：
- 生产环境必须设置 SECRET_KEY 环境变量
- 开发环境会使用固定的开发密钥，仅用于本地开发
- 绝不要将真实密钥提交到版本控制系统
"""

import os
import secrets
import warnings
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


# 开发环境使用的默认密钥（仅限本地开发！）
_DEV_SECRET_KEY = "dev-secret-key-DO-NOT-USE-IN-PRODUCTION"


class Settings(BaseSettings):
    """
    应用配置类
    
    所有敏感配置都从环境变量读取。
    开发环境会自动生成测试密钥。
    生产环境必须设置真实的安全密钥。
    """
    # 应用信息
    APP_NAME: str = "龙门客栈业务管理系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于 OpenClaw 的多 Agent 协作管理平台"
    
    # 运行环境
    ENVIRONMENT: str = "development"  # development | staging | production
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # 龙门客栈根目录
    LONGMEN_INN_ROOT: Path = Path(__file__).parent.parent.parent.parent.parent.parent
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./longmen_inn.db"
    DATABASE_ECHO: bool = False  # 是否打印 SQL 语句
    
    # Redis 配置
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT 配置 - 从环境变量读取，生产环境必须设置
    SECRET_KEY: Optional[str] = None  # 不再有硬编码默认值
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    # CORS 配置 - 从环境变量读取
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v, values):
        """解析 CORS 配置并验证生产环境安全性"""
        environment = values.get("ENVIRONMENT", "development")
        
        if isinstance(v, str) and not v.startswith("["):
            origins = [origin.strip() for origin in v.split(",")]
        elif isinstance(v, (list, str)):
            origins = v if isinstance(v, list) else [v]
        else:
            raise ValueError(v)
        
        # 生产环境安全检查：禁止使用 localhost
        if environment == "production":
            localhost_patterns = ["localhost", "127.0.0.1", "0.0.0.0"]
            for origin in origins:
                if any(pattern in origin for pattern in localhost_patterns):
                    raise ValueError(
                        f"[SECURITY ERROR] Production CORS_ORIGINS cannot contain localhost: {origin}\n"
                        "Please set explicit production domains in CORS_ORIGINS environment variable."
                    )
            # 生产环境必须设置至少一个明确的源
            if not origins:
                raise ValueError(
                    "[SECURITY ERROR] Production environment requires explicit CORS_ORIGINS!\n"
                    "Set CORS_ORIGINS environment variable with your production domain(s)."
                )
        
        return origins
    
    @validator("SECRET_KEY", pre=True)
    def validate_secret_key(cls, v, values):
        """
        验证 SECRET_KEY：
        - 开发环境：如果没有设置，使用固定的开发密钥并发出警告
        - 生产环境：必须设置，否则抛出异常；且不能是默认开发密钥
        """
        environment = values.get("ENVIRONMENT", "development")
        
        # 如果环境变量已设置，直接使用
        if v:
            # 生产环境检测：如果是设置了环境变量但仍使用默认开发密钥，报错
            if environment == "production" and v == _DEV_SECRET_KEY:
                raise ValueError(
                    "[SECURITY ERROR] Production environment detected but SECRET_KEY "
                    "is still the default development key! Please set a real SECRET_KEY.\n"
                    "Generate a secure key: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
                )
            return v
        
        # 未设置环境变量
        # 开发环境：允许使用默认开发密钥
        if environment == "development":
            warnings.warn(
                "[WARNING] Using default development SECRET_KEY. "
                "Please set SECRET_KEY environment variable.\n"
                "Dev key is for local testing only - NEVER use in production!",
                UserWarning
            )
            return _DEV_SECRET_KEY
        
        # 预发布环境：允许使用默认密钥但发出警告
        if environment == "staging":
            warnings.warn(
                "[WARNING] Staging environment without SECRET_KEY! "
                "Recommend setting a dedicated test key.",
                UserWarning
            )
            return _DEV_SECRET_KEY
        
        # 生产环境：必须设置，未设置则拒绝启动
        raise ValueError(
            "[SECURITY ERROR] Production environment requires SECRET_KEY environment variable!\n"
            "Generate a secure key: python -c \"import secrets; print(secrets.token_urlsafe(32))\"\n"
            "See .env.example for configuration."
        )
    
    # OpenClaw 集成配置
    OPENCLAW_GATEWAY_URL: str = "http://127.0.0.1:18789"
    OPENCLAW_API_KEY: Optional[str] = None
    OPENCLAW_WS_URL: str = "ws://127.0.0.1:18789"
    OPENCLAW_CLI_PATH: str = "openclaw"
    
    # 任务配置
    TASK_NUMBER_PREFIX: str = "DEV-"
    DEFAULT_TASK_PRIORITY: str = "medium"
    AUTO_ASSIGN_ENABLED: bool = True
    
    # 龙门令配置
    LONGMENLING_BASE_REWARD: int = 10  # 基础奖励
    LONGMENLING_LEVEL_RANGES: dict = {
        1: (0, 99, "新手伙计"),
        2: (100, 499, "熟练工"),
        3: (500, 999, "老师傅"),
        4: (1000, 2499, "大管家"),
        5: (2500, 4999, "传奇掌柜"),
        6: (5000, float('inf'), "龙门传说")
    }
    
    # 客栈情报配置
    AI_DAILY_REPORTS_PATH: Optional[str] = None  # AI日报存储路径，默认: LONGMEN_INN_ROOT/ai-daily-reports
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @property
    def is_production(self) -> bool:
        """是否为生产环境"""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """是否为开发环境"""
        return self.ENVIRONMENT == "development"
    
    class Config:
        """Pydantic 配置"""
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# 创建设置实例
settings = Settings()


def get_settings() -> Settings:
    """
    获取设置实例
    用于 FastAPI 依赖注入
    """
    return settings
