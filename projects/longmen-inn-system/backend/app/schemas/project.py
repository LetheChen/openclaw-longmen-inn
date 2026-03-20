"""
龙门客栈业务管理系统 - Project Schemas
===============================
作者: 厨子 (神厨小福贵)

项目相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.db.models import ProjectStatus


# 基础 Project 模型
class ProjectBase(BaseModel):
    """项目基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="项目名称", example="龙门客栈官网")
    description: Optional[str] = Field(None, description="项目描述")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, description="项目状态")


class ProjectCreate(ProjectBase):
    """创建项目请求模型"""
    pass


class ProjectUpdate(BaseModel):
    """更新项目请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    status: Optional[ProjectStatus] = Field(None, description="项目状态")


class ProjectStatistics(BaseModel):
    """项目统计信息"""
    total_tasks: int = Field(0, description="总任务数")
    pending_tasks: int = Field(0, description="待处理任务数")
    in_progress_tasks: int = Field(0, description="进行中任务数")
    completed_tasks: int = Field(0, description="已完成任务数")


class TaskBrief(BaseModel):
    """任务简要信息"""
    id: int
    task_no: str
    title: str
    status: str
    priority: str
    assignee_agent_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectResponse(ProjectBase):
    """项目响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectBase):
    """项目详情响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    statistics: ProjectStatistics = Field(default_factory=ProjectStatistics)
    recent_tasks: List[TaskBrief] = Field(default_factory=list)
    
    class Config:
        from_attributes = True