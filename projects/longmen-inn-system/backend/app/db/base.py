"""
龙门客栈业务管理系统 - 数据库基础
===============================
作者: 厨子 (神厨小福贵)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明性基类
Base = declarative_base()


def get_db():
    """
    获取数据库会话
    用于 FastAPI 依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表结构
    """
    # 导入所有模型以确保它们被注册到Base.metadata
    # 业务模型
    from app.db.models import (
        Project, ProjectPhase, Agent, AgentHeartbeat,
        Task, LongmenlingLog, TaskLog, DataCollectionJob,
        task_dependencies
    )
    # 用户认证模型
    from app.models.user import User, RefreshToken, AuditLog
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
