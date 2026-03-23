"""
龙门客栈业务管理系统 - Agent工作空间Schema
=====================================
作者: 老板娘 (凤老板)

Agent工作空间可视化数据模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AgentStatus(str, Enum):
    """Agent状态枚举"""
    IDLE = "idle"        # 空闲
    BUSY = "busy"        # 忙碌
    OFFLINE = "offline"  # 离线
    ERROR = "error"      # 异常


class AgentRole(BaseModel):
    """角色信息"""
    id: str = Field(..., description="角色ID，如 chef, main, innkeeper")
    name: str = Field(..., description="角色名称，如 厨子、老板娘")
    title: str = Field(..., description="称号，如 李师傅、凤老板")
    scene: str = Field(..., description="场所名称，如 后厨、内堂")
    description: str = Field(..., description="职责描述")
    avatar: Optional[str] = Field(None, description="形象图片URL")
    scene_image: Optional[str] = Field(None, description="场景背景图URL")
    motto: Optional[str] = Field(None, description="座右铭")
    level: int = Field(default=1, ge=1, le=10, description="等级")


class TaskInfo(BaseModel):
    """任务信息"""
    id: str = Field(..., description="任务ID")
    content: str = Field(..., description="任务内容")
    status: str = Field(..., description="任务状态：pending, in_progress, completed")
    priority: str = Field(default="medium", description="优先级：high, medium, low")
    assignee: Optional[str] = Field(None, description="负责人")
    project: Optional[str] = Field(None, description="所属项目")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    remarks: Optional[str] = Field(None, description="备注")


class ActivityRecord(BaseModel):
    """活动记录"""
    timestamp: datetime = Field(..., description="时间戳")
    action_type: str = Field(..., description="动作类型：message, tool_use, tool_result")
    action_detail: str = Field(..., description="动作详情")
    output_preview: Optional[str] = Field(None, description="输出预览（截断）")
    role: Optional[str] = Field(None, description="消息角色：user/assistant/system")
    tool_name: Optional[str] = Field(None, description="工具名称")
    is_error: Optional[bool] = Field(default=False, description="是否错误")


class WorkspaceFile(BaseModel):
    """工作空间文件"""
    path: str = Field(..., description="文件路径")
    type: str = Field(default="file", description="文件类型：file, directory")
    file_type: Optional[str] = Field(None, description="文件分类：code, doc, design, config")
    last_modified: Optional[datetime] = Field(None, description="最后修改时间")
    size: Optional[int] = Field(None, description="文件大小（字节）")


class AgentWorkspace(BaseModel):
    """Agent工作空间完整信息"""
    role: AgentRole = Field(..., description="角色信息")
    status: AgentStatus = Field(default=AgentStatus.OFFLINE, description="当前状态")
    current_tasks: List[TaskInfo] = Field(default_factory=list, description="进行中的任务")
    pending_tasks: List[TaskInfo] = Field(default_factory=list, description="待办任务")
    completed_tasks: List[TaskInfo] = Field(default_factory=list, description="已完成任务")
    recent_activities: List[ActivityRecord] = Field(default_factory=list, description="最近活动记录")
    workspace_files: List[WorkspaceFile] = Field(default_factory=list, description="工作空间文件")
    last_active: Optional[datetime] = Field(None, description="最后活跃时间")
    session_id: Optional[str] = Field(None, description="当前会话ID")
    session_start: Optional[datetime] = Field(None, description="会话开始时间")
    stats: Dict[str, Any] = Field(default_factory=dict, description="统计信息")


class AgentSummary(BaseModel):
    """Agent简要信息（列表用）"""
    agent_id: str = Field(..., description="Agent ID")
    name: str = Field(..., description="名称")
    title: Optional[str] = Field(None, description="称号")
    status: AgentStatus = Field(default=AgentStatus.OFFLINE, description="状态")
    scene: Optional[str] = Field(None, description="场所")
    level: int = Field(default=1, description="等级")
    longmenling: int = Field(default=0, description="龙门令数量")
    current_task: Optional[str] = Field(None, description="当前任务")
    last_active: Optional[datetime] = Field(None, description="最后活跃时间")


class AgentListResponse(BaseModel):
    """Agent列表响应"""
    total: int = Field(..., description="总数")
    agents: List[AgentSummary] = Field(..., description="Agent列表")
    statistics: Dict[str, int] = Field(default_factory=dict, description="统计信息")


class ActivityFilter(BaseModel):
    """活动记录过滤参数"""
    agent_id: str = Field(..., description="Agent ID")
    action_type: Optional[str] = Field(None, description="动作类型过滤")
    limit: int = Field(default=50, ge=1, le=200, description="返回数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")