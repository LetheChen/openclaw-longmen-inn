"""
龙门客栈业务管理系统 - OpenClaw API
===============================
作者: 厨子 (神厨小福贵)

OpenClaw Gateway集成API端点
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncio
import json

from app.services.openclaw_service import openclaw_service
from app.schemas.openclaw import (
    GatewayStatusResponse, AgentSessionResponse, AgentHeartbeatResponse,
    RouteConfigResponse, LiveStatusResponse, OpenClawConfigUpdate
)

router = APIRouter()


@router.get("/gateway/status", response_model=GatewayStatusResponse)
async def get_gateway_status():
    """
    获取Gateway状态
    
    返回Gateway的健康状态、版本、运行时间等信息
    """
    return await openclaw_service.check_gateway_health()


@router.get("/gateway/live-status", response_model=LiveStatusResponse)
async def get_live_status():
    """
    获取实时状态
    
    返回完整的实时状态数据，包括：
    - Gateway状态
    - Agent列表和状态
    - 会话列表
    - 路由配置
    - 统计数据
    """
    return await openclaw_service.get_live_status()


@router.get("/agents/{agent_id}/heartbeat", response_model=AgentHeartbeatResponse)
async def get_agent_heartbeat(agent_id: str):
    """
    获取Agent心跳状态
    
    返回指定Agent的心跳信息：
    - 最后心跳时间
    - 下次心跳时间
    - 心跳间隔
    - 活跃任务数
    """
    return await openclaw_service.get_agent_heartbeat(agent_id)


@router.get("/sessions", response_model=list[AgentSessionResponse])
async def get_sessions(
    agent_id: Optional[str] = Query(None, description="过滤指定Agent的会话")
):
    """
    获取会话列表
    
    返回所有或指定Agent的会话列表
    """
    return await openclaw_service.get_agent_sessions(agent_id)


@router.get("/routes", response_model=list[RouteConfigResponse])
async def get_routes():
    """
    获取路由配置
    
    返回所有消息路由配置
    """
    live_status = await openclaw_service.get_live_status()
    return live_status.routes


@router.get("/status")
async def get_openclaw_status():
    """
    获取OpenClaw整体状态
    
    通过CLI命令获取完整状态信息
    """
    return await openclaw_service.get_openclaw_status()


@router.post("/gateway/restart")
async def restart_gateway():
    """
    重启Gateway
    
    执行Gateway重启命令
    """
    result = await openclaw_service.execute_openclaw_command("gateway", ["restart"])
    
    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"重启Gateway失败: {result.get('error', '未知错误')}"
        )
    
    return {"message": "Gateway重启成功", "output": result.get("output")}


@router.post("/config", response_model=dict)
async def update_config(config: OpenClawConfigUpdate):
    """
    更新OpenClaw配置
    
    更新Gateway URL、WebSocket URL等配置
    """
    updated = {}
    
    if config.gateway_url:
        openclaw_service.gateway_url = config.gateway_url
        updated["gateway_url"] = config.gateway_url
    
    if config.ws_url:
        openclaw_service.ws_url = config.ws_url
        updated["ws_url"] = config.ws_url
    
    if config.api_key:
        openclaw_service.api_key = config.api_key
        updated["api_key"] = "***"
    
    return {
        "message": "配置更新成功",
        "updated": updated
    }


@router.get("/events/stream")
async def stream_events():
    """
    SSE事件流
    
    返回Server-Sent Events流，推送实时事件
    """
    async def event_generator():
        while True:
            try:
                live_status = await openclaw_service.get_live_status()
                
                event_data = {
                    "event": "status_update",
                    "data": {
                        "gateway_status": live_status.gateway.status.value,
                        "active_agents": len([a for a in live_status.agents if a.get("status") != "offline"]),
                        "active_sessions": len(live_status.sessions),
                        "timestamp": live_status.timestamp.isoformat()
                    }
                }
                
                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'event': 'error', 'data': str(e)}, ensure_ascii=False)}\n\n"
            
            await asyncio.sleep(5)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
