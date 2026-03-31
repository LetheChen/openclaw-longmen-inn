"""
龙门客栈业务管理系统 - 数据库初始化
===============================
作者: 厨子 (神厨小福贵)

数据库初始化和迁移管理
"""

import logging
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine
from app.db import models

logger = logging.getLogger(__name__)


def create_tables():
    """
    创建所有数据表
    基于 SQLAlchemy 模型定义
    """
    try:
        logger.info("开始创建数据库表...")
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建完成！")
        return True
    except Exception as e:
        logger.error(f"创建数据库表失败: {str(e)}")
        return False


def drop_tables():
    """
    删除所有数据表
    ⚠️ 危险操作，请谨慎使用
    """
    try:
        logger.warning("开始删除数据库表...")
        Base.metadata.drop_all(bind=engine)
        logger.warning("数据库表已删除！")
        return True
    except Exception as e:
        logger.error(f"删除数据库表失败: {str(e)}")
        return False


def init_db(skip_import: bool = False):
    """
    初始化数据库
    创建所有必要的表，可选是否导入生产数据
    
    注意：LEDGER.md 同步到 DB 的功能已禁用。
    如需从 DB 生成 LEDGER.md，请使用：
        python -m app.cli ledger generate
        POST /files/ledger/generate
    """
    logger.info("=" * 50)
    logger.info("开始初始化数据库...")
    logger.info("=" * 50)
    
    success = create_tables()
    
    if success:
        if not skip_import:
            logger.info("生产数据导入已禁用（LEDGER.md 不再作为数据源）")
            logger.info("如需从 DB 导出 LEDGER.md，请运行：python -m app.cli ledger generate")
        
        logger.info("=" * 50)
        logger.info("数据库初始化成功！")
        logger.info("=" * 50)
    else:
        logger.error("=" * 50)
        logger.error("数据库初始化失败！")
        logger.error("=" * 50)
    
    return success


def check_db_connection():
    """
    检查数据库连接是否正常
    
    Returns:
        bool: 连接是否正常
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("数据库连接正常")
        return True
    except Exception as e:
        logger.error(f"数据库连接失败: {str(e)}")
        return False


if __name__ == "__main__":
    # 直接运行此文件时初始化数据库
    import sys
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        confirm = input("⚠️ 确定要删除所有数据表吗？(yes/no): ")
        if confirm.lower() == "yes":
            drop_tables()
        else:
            print("已取消删除操作")
    else:
        init_db()