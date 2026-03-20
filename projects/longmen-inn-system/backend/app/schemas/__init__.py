"""
龙门客栈业务管理系统 - Pydantic Schemas
===============================
作者: 厨子 (神厨小福贵)

Pydantic 模型定义，用于请求和响应验证
"""

from .agent import AgentCreate, AgentUpdate, AgentResponse, AgentDetailResponse, AgentStatusUpdate
from .task import TaskCreate, TaskUpdate, TaskResponse, TaskDetailResponse, TaskStatusUpdate, TaskListParams, TaskListResponse
from .project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse
from .longmenling import LongmenlingCreate, LongmenlingResponse, LongmenlingRanking, AgentLongmenlingDetail

__all__ = [
    # Agent Schemas
    "AgentCreate",
    "AgentUpdate", 
    "AgentResponse",
    "AgentDetailResponse",
    "AgentStatusUpdate",
    # Task Schemas
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskDetailResponse",
    "TaskStatusUpdate",
    "TaskListParams",
    # Project Schemas
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectDetailResponse",
    # Longmenling Schemas
    "LongmenlingCreate",
    "LongmenlingResponse",
    "LongmenlingRanking",
    "AgentLongmenlingDetail",
]