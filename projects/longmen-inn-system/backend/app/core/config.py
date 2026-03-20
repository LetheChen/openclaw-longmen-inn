"""
龙门客栈业务管理系统 - 核心配置
===============================
作者: 厨子 (神厨小福贵)
"""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """
    应用配置类
    """
    # 应用信息
    APP_NAME: str = "龙门客栈业务管理系统"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "基于 OpenClaw 的多 Agent 协作管理平台"
    
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
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 小时
    
    # CORS 配置
    CORS_ORIGINS: List[str] = ["*"]
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """解析 CORS 配置"""
        if isinstance(v, str) and not v.startswith("["):
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
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
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
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
