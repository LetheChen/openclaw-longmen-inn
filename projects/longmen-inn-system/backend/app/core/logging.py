"""
龙门客栈业务管理系统 - 日志配置
===============================
作者: 厨子 (神厨小福贵)

日志系统配置和初始化
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO",
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    配置日志系统
    
    Args:
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: 日志格式字符串
        log_file: 日志文件路径 (None则只输出到控制台)
        max_bytes: 单个日志文件最大字节数
        backup_count: 保留的备份文件数量
    
    Returns:
        配置好的根日志记录器
    """
    # 创建根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有的处理器
    root_logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(log_format)
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 文件处理器 (如果指定了日志文件)
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 使用 RotatingFileHandler 自动轮转
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # 返回应用日志记录器
    logger = logging.getLogger(__name__)
    logger.info(f"日志系统初始化完成 - 级别: {log_level}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取命名日志记录器
    
    Args:
        name: 日志记录器名称 (通常使用 __name__)
    
    Returns:
        配置好的日志记录器
    """
    return logging.getLogger(name)


# 便捷方法
debug = logging.debug
info = logging.info
warning = logging.warning
error = logging.error
critical = logging.critical
exception = logging.exception


__all__ = [
    'setup_logging',
    'get_logger',
    'debug',
    'info',
    'warning',
    'error',
    'critical',
    'exception',
]