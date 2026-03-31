"""
龙门客栈业务管理系统 - Agent Schemas
===============================
作者: 厨子 (神厨小福贵)

Agent 相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.db.models import AgentStatus


# 基础 Agent 模型
class AgentBase(BaseModel):
    """Agent 基础模型"""
    agent_id: str = Field(..., description="Agent唯一标识", example="innkeeper")
    name: str = Field(..., description="显示名称", example="大掌柜")
    title: Optional[str] = Field(None, description="称号", example="诸葛掌柜")
    motto: Optional[str] = Field(None, description="信条", example="事无巨细，皆在我心")
    role_description: Optional[str] = Field(None, description="职责描述")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    status: AgentStatus = Field(default=AgentStatus.IDLE, description="当前状态")
    longmenling: int = Field(default=0, ge=0, description="龙门令积分")
    level: int = Field(default=1, ge=1, le=6, description="等级")


class AgentCreate(AgentBase):
    """创建 Agent 请求模型"""
    pass


class AgentUpdate(BaseModel):
    """更新 Agent 请求模型"""
    name: Optional[str] = Field(None, description="显示名称")
    title: Optional[str] = Field(None, description="称号")
    motto: Optional[str] = Field(None, description="信条")
    role_description: Optional[str] = Field(None, description="职责描述")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    status: Optional[AgentStatus] = Field(None, description="当前状态")
    longmenling: Optional[int] = Field(None, ge=0, description="龙门令积分")


class AgentStatusUpdate(BaseModel):
    """更新 Agent 状态请求模型"""
    status: AgentStatus = Field(..., description="新状态")
    reason: Optional[str] = Field(None, description="状态变更原因")


class AgentResponse(AgentBase):
    """Agent 响应模型"""
    created_at: datetime
    
    class Config:
        from_attributes = True


class TaskBrief(BaseModel):
    """任务简要信息"""
    id: int
    task_no: str
    title: str
    status: str
    priority: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LongmenlingLogBrief(BaseModel):
    """龙门令记录简要信息"""
    id: int
    amount: int
    reason: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentDetailResponse(AgentBase):
    """Agent 详情响应模型"""
    created_at: datetime
    task_statistics: Dict[str, int] = Field(default_factory=dict, description="任务统计")
    recent_tasks: List[TaskBrief] = Field(default_factory=list, description="最近任务")
    recent_longmenling_logs: List[LongmenlingLogBrief] = Field(default_factory=list, description="最近龙门令记录")
    
    class Config:
        from_attributes = True


# ============ Agent 活动记录 Schemas ============

class ActivityTypeEnum(str):
    """活动类型枚举"""
    TASK_COMPLETED = "task_completed"
    LOGIN = "login"
    LONGMENLING_ISSUED = "longmenling_issued"


class AgentActivityCreate(BaseModel):
    """创建活动记录请求"""
    agent_id: str = Field(..., description="Agent ID", example="chef")
    activity_type: str = Field(..., description="活动类型", example="task_completed")
    title: str = Field(..., description="活动标题", example="完成了任务 T-20250307-001")
    description: Optional[str] = Field(None, description="活动描述")
    related_task_id: Optional[int] = Field(None, description="关联任务ID")
    related_task_title: Optional[str] = Field(None, description="关联任务标题")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="额外元数据")


class AgentActivityResponse(BaseModel):
    """活动记录响应"""
    id: int
    agent_id: str
    agent_name: Optional[str] = None
    agent_avatar: Optional[str] = None
    activity_type: str
    title: str
    description: Optional[str] = None
    related_task_id: Optional[int] = None
    related_task_title: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentActivityQuery(BaseModel):
    """查询活动记录参数"""
    agent_id: Optional[str] = Field(None, description="过滤指定 Agent")
    activity_type: Optional[str] = Field(None, description="过滤活动类型")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    skip: int = Field(0, ge=0, description="跳过记录数")
    limit: int = Field(20, ge=1, le=100, description="返回记录数")


class AgentActivityListResponse(BaseModel):
    """活动记录列表响应"""
    total: int
    items: List[AgentActivityResponse]