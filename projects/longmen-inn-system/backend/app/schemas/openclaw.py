"""
龙门客栈业务管理系统 - OpenClaw Schemas
===============================
作者: 厨子 (神厨小福贵)

OpenClaw Gateway 集成相关的 Pydantic 模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GatewayStatus(str, Enum):
    """Gateway状态"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class SessionStatus(str, Enum):
    """会话状态"""
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"


class GatewayStatusResponse(BaseModel):
    """Gateway状态响应"""
    status: GatewayStatus = Field(..., description="Gateway状态")
    version: Optional[str] = Field(None, description="版本号")
    uptime: Optional[str] = Field(None, description="运行时间")
    last_checked: datetime = Field(default_factory=datetime.now, description="最后检查时间")
    connected_agents: int = Field(default=0, description="连接的Agent数量")
    active_sessions: int = Field(default=0, description="活跃会话数")
    message_queue_size: int = Field(default=0, description="消息队列大小")


class AgentSessionResponse(BaseModel):
    """Agent会话响应"""
    id: str = Field(..., description="会话ID")
    agent_id: str = Field(..., description="Agent ID")
    agent_name: str = Field(..., description="Agent名称")
    status: SessionStatus = Field(..., description="会话状态")
    channel: Optional[str] = Field(None, description="消息渠道")
    last_activity: Optional[datetime] = Field(None, description="最后活动时间")
    message_count: int = Field(default=0, description="消息数量")
    created_at: Optional[datetime] = Field(None, description="创建时间")


class AgentHeartbeatResponse(BaseModel):
    """Agent心跳响应"""
    agent_id: str = Field(..., description="Agent ID")
    status: str = Field(..., description="状态")
    last_heartbeat: Optional[datetime] = Field(None, description="最后心跳时间")
    next_heartbeat: Optional[datetime] = Field(None, description="下次心跳时间")
    heartbeat_interval: int = Field(default=1800, description="心跳间隔(秒)")
    active_tasks: int = Field(default=0, description="活跃任务数")
    memory_usage: Optional[float] = Field(None, description="内存使用率")
    cpu_usage: Optional[float] = Field(None, description="CPU使用率")


class RouteConfigResponse(BaseModel):
    """路由配置响应"""
    id: str = Field(..., description="路由ID")
    name: str = Field(..., description="路由名称")
    source: str = Field(..., description="源渠道")
    target: str = Field(..., description="目标Agent")
    enabled: bool = Field(default=True, description="是否启用")
    priority: int = Field(default=1, description="优先级")
    message_count: int = Field(default=0, description="消息数量")


class LiveStatusResponse(BaseModel):
    """实时状态响应"""
    gateway: GatewayStatusResponse = Field(..., description="Gateway状态")
    agents: List[Dict[str, Any]] = Field(default_factory=list, description="Agent列表")
    sessions: List[AgentSessionResponse] = Field(default_factory=list, description="会话列表")
    routes: List[RouteConfigResponse] = Field(default_factory=list, description="路由配置")
    statistics: Dict[str, Any] = Field(default_factory=dict, description="统计数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class WebSocketMessage(BaseModel):
    """WebSocket消息"""
    type: str = Field(..., description="消息类型: req/res/event")
    id: Optional[str] = Field(None, description="消息ID")
    method: Optional[str] = Field(None, description="方法名(请求)")
    params: Optional[Dict[str, Any]] = Field(None, description="参数")
    event: Optional[str] = Field(None, description="事件名")
    payload: Optional[Dict[str, Any]] = Field(None, description="负载")
    ok: Optional[bool] = Field(None, description="是否成功(响应)")
    error: Optional[str] = Field(None, description="错误信息")


class OpenClawConfigUpdate(BaseModel):
    """OpenClaw配置更新请求"""
    gateway_url: Optional[str] = Field(None, description="Gateway URL")
    ws_url: Optional[str] = Field(None, description="WebSocket URL")
    api_key: Optional[str] = Field(None, description="API Key")
    heartbeat_interval: Optional[int] = Field(None, description="心跳间隔(秒)")
    # 客栈情报开关
    ai_news_enabled: Optional[bool] = Field(None, description="AI日报开关")
    news_enabled: Optional[bool] = Field(None, description="时事要闻开关")
    red_news_enabled: Optional[bool] = Field(None, description="红色印记开关")


class OpenClawConfigResponse(BaseModel):
    """OpenClaw配置响应（用于GET /openclaw/config）"""
    gateway_url: str
    ws_url: str
    api_key: Optional[str] = None
    heartbeat_interval: int = 1800
    ai_news_enabled: bool = True
    news_enabled: bool = True
    red_news_enabled: bool = True
