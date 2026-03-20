"""
龙门客栈业务管理系统 - 数据库会话管理
===============================
作者: 厨子 (神厨小福贵)

数据库会话创建和管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings


# 同步数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 同步会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    获取数据库会话（同步）
    用于 FastAPI 依赖注入
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session():
    """
    获取数据库会话（同步）
    用于非 FastAPI 场景（如后台任务）
    """
    return SessionLocal()


# 异步数据库支持（如果 DATABASE_URL 是异步的）
# 注意：SQLite 需要 aiosqlite 驱动
if settings.DATABASE_URL.startswith("sqlite"):
    ASYNC_DATABASE_URL = settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://")
else:
    ASYNC_DATABASE_URL = settings.DATABASE_URL

# 异步数据库引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(async_engine, autocommit=False, autoflush=False)


async def get_async_db():
    """
    获取异步数据库会话
    用于 FastAPI 异步依赖注入
    """
    async with AsyncSessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()


async def get_async_db_session():
    """
    获取异步数据库会话
    用于非 FastAPI 异步场景
    """
    return AsyncSessionLocal()