"""
龙门客栈业务管理系统 - Longmenling Schemas
===============================
作者: 厨子 (神厨小福贵)

龙门令相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# 基础龙门令模型
class LongmenlingBase(BaseModel):
    """龙门令基础模型"""
    agent_id: str = Field(..., description="Agent ID", example="innkeeper")
    task_id: Optional[int] = Field(None, description="关联任务ID")
    amount: int = Field(..., description="变动数量(正数获得/负数扣除)", example=100)
    reason: Optional[str] = Field(None, description="变动原因", example="完成重要任务")
    description: Optional[str] = Field(None, description="详细描述")


class LongmenlingCreate(LongmenlingBase):
    """发放龙门令请求模型"""
    pass


class LongmenlingResponse(LongmenlingBase):
    """龙门令记录响应模型"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class LongmenlingRankingItem(BaseModel):
    """排行榜单项"""
    rank: int = Field(..., description="排名")
    agent_id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent名称")
    title: Optional[str] = Field(None, description="称号")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    level: int = Field(..., description="等级")
    longmenling: int = Field(..., description="龙门令积分")


class LongmenlingRanking(BaseModel):
    """龙门令排行榜响应模型"""
    total_count: int = Field(..., description="总Agent数")
    top_agents: List[LongmenlingRankingItem] = Field(default_factory=list, description="前几名")
    my_rank: Optional[LongmenlingRankingItem] = Field(None, description="查询者自己的排名")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")


class LongmenlingHistoryItem(BaseModel):
    """龙门令历史记录单项"""
    id: int
    amount: int = Field(..., description="变动数量")
    reason: Optional[str] = Field(None, description="变动原因")
    description: Optional[str] = Field(None, description="详细描述")
    task_id: Optional[int] = Field(None, description="关联任务ID")
    created_at: datetime
    
    class Config:
        from_attributes = True


class AgentLongmenlingDetail(BaseModel):
    """Agent龙门令详情响应模型"""
    agent_id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="Agent名称")
    title: Optional[str] = Field(None, description="称号")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    level: int = Field(..., description="当前等级")
    longmenling: int = Field(..., description="当前龙门令积分")
    next_level_required: int = Field(..., description="下一级所需积分")
    points_to_next_level: int = Field(..., description="距离下一级还需积分")
    total_earned: int = Field(..., description="历史总获得")
    total_spent: int = Field(..., description="历史总消耗")
    recent_history: List[LongmenlingHistoryItem] = Field(default_factory=list, description="最近记录")
    rank_in_all: Optional[int] = Field(None, description="总排名")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="生成时间")