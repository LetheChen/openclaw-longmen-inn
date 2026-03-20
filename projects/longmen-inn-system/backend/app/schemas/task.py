"""
龙门客栈业务管理系统 - Task Schemas
===============================
作者: 厨子 (神厨小福贵)

任务相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.db.models import TaskStatus, TaskPriority


# 基础 Task 模型
class TaskBase(BaseModel):
    """任务基础模型"""
    task_no: str = Field(..., description="任务编号", example="DEV-001")
    title: str = Field(..., description="任务标题", example="实现用户登录功能")
    description: Optional[str] = Field(None, description="任务描述")
    project_id: Optional[int] = Field(None, description="所属项目ID")
    creator_agent_id: str = Field(..., description="创建者Agent ID")
    assignee_agent_id: Optional[str] = Field(None, description="被分配者Agent ID")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="任务状态")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="任务优先级")
    estimated_hours: Optional[int] = Field(None, ge=0, description="预计工时")
    actual_hours: Optional[int] = Field(None, ge=0, description="实际工时")
    deliverable_path: Optional[str] = Field(None, description="产出物路径")
    parent_task_id: Optional[int] = Field(None, description="父任务ID")


class TaskCreate(TaskBase):
    """创建任务请求模型"""
    pass


class TaskUpdate(BaseModel):
    """更新任务请求模型"""
    title: Optional[str] = Field(None, description="任务标题")
    description: Optional[str] = Field(None, description="任务描述")
    project_id: Optional[int] = Field(None, description="所属项目ID")
    assignee_agent_id: Optional[str] = Field(None, description="被分配者Agent ID")
    status: Optional[TaskStatus] = Field(None, description="任务状态")
    priority: Optional[TaskPriority] = Field(None, description="任务优先级")
    estimated_hours: Optional[int] = Field(None, ge=0, description="预计工时")
    actual_hours: Optional[int] = Field(None, ge=0, description="实际工时")
    deliverable_path: Optional[str] = Field(None, description="产出物路径")
    parent_task_id: Optional[int] = Field(None, description="父任务ID")


class TaskStatusUpdate(BaseModel):
    """更新任务状态请求模型"""
    status: TaskStatus = Field(..., description="新状态")
    comment: Optional[str] = Field(None, description="状态变更备注")


class TaskListParams(BaseModel):
    """任务列表查询参数"""
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(20, ge=1, le=100, description="返回记录数")
    project_id: Optional[int] = Field(None, description="项目ID筛选")
    assignee_agent_id: Optional[str] = Field(None, description="被分配者Agent ID筛选")
    creator_agent_id: Optional[str] = Field(None, description="创建者Agent ID筛选")
    status: Optional[TaskStatus] = Field(None, description="状态筛选")
    priority: Optional[TaskPriority] = Field(None, description="优先级筛选")


class ProjectBrief(BaseModel):
    """项目简要信息"""
    id: int
    name: str
    status: str
    
    class Config:
        from_attributes = True


class AgentBrief(BaseModel):
    """Agent简要信息"""
    agent_id: str
    name: str
    avatar_url: Optional[str]
    
    class Config:
        from_attributes = True


class TaskLogResponse(BaseModel):
    """任务日志响应模型"""
    id: int
    from_status: Optional[str]
    to_status: str
    operator_agent_id: Optional[str]
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """任务响应模型"""
    id: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class TaskDetailResponse(TaskBase):
    """任务详情响应模型"""
    id: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    project: Optional[ProjectBrief] = None
    creator: Optional[AgentBrief] = None
    assignee: Optional[AgentBrief] = None
    parent_task: Optional[TaskResponse] = None
    sub_tasks: List[TaskResponse] = []
    logs: List[TaskLogResponse] = []
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    items: List[TaskResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """任务列表响应模型"""
    items: List[TaskResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        from_attributes = True