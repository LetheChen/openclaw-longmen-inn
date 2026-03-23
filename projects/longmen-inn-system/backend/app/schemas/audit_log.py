"""
龙门客栈业务管理系统 - 审计日志 Schema
=====================================
作者: 厨子 (神厨小福贵)

用于审计日志API的数据模型定义
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class AuditLogEntry(BaseModel):
    """审计日志条目"""
    timestamp: str = Field(..., description="审计时间")
    type: str = Field(default="git_audit", description="类型")
    files_changed: List[str] = Field(default_factory=list, description="变更文件列表")
    lines_added: int = Field(default=0, description="新增行数")
    lines_deleted: int = Field(default=0, description="删除行数")
    tasks_found: List[str] = Field(default_factory=list, description="关联任务ID")
    summary: str = Field(..., description="摘要")
    status: str = Field(default="passed", description="状态")
    issues: List[str] = Field(default_factory=list, description="问题列表")


class AuditLogResponse(BaseModel):
    """审计日志响应"""
    total: int
    entries: List[AuditLogEntry]
    statistics: dict


class AuditFeedResponse(BaseModel):
    """版本动态Feed响应"""
    feed: List[dict]
