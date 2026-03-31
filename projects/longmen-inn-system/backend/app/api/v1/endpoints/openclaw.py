"""
龙门客栈业务管理系统 - OpenClaw API
===============================
作者: 厨子 (神厨小福贵)

OpenClaw Gateway集成API端点
"""

from pathlib import Path
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncio
import json
import base64
import hashlib

from app.services.openclaw_service import openclaw_service
from app.schemas.openclaw import (
    GatewayStatusResponse, AgentSessionResponse, AgentHeartbeatResponse,
    RouteConfigResponse, LiveStatusResponse, OpenClawConfigUpdate, OpenClawConfigResponse
)
from app.core.config import settings

router = APIRouter()

# 配置文件路径
CONFIG_FILE = settings.LONGMEN_INN_ROOT / "openclaw_config.json"


def _derive_key(secret: str) -> bytes:
    """从 SECRET_KEY 派生加密密钥"""
    return hashlib.sha256(secret.encode()).digest()


def _encrypt_value(value: str) -> str:
    """简单XOR加密（防止明文泄露，不使用外部库）"""
    key = _derive_key(settings.SECRET_KEY or "default-key")
    encrypted = bytes(a ^ b for a, b in zip(value.encode(), key * (len(value) // len(key) + 1)))
    return base64.b64encode(encrypted).decode()


def _decrypt_value(encrypted: str) -> str:
    """解密"""
    try:
        key = _derive_key(settings.SECRET_KEY or "default-key")
        decoded = base64.b64decode(encrypted.encode())
        return bytes(a ^ b for a, b in zip(decoded, key * (len(decoded) // len(key) + 1))).decode()
    except Exception:
        return ""


def _load_config() -> dict:
    """从JSON文件加载配置（API Key已加密存储）"""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            # 解密敏感字段
            result = dict(raw)
            if result.get("api_key"):
                result["api_key"] = _decrypt_value(result["api_key"])
            return result
        except Exception:
            pass
    return {}


def _save_config(config: dict):
    """
    保存配置到JSON文件（敏感字段加密存储）
    
    警告：此文件仍可被有服务器访问权限的人解密。
    生产环境应使用专业密钥管理服务（如 AWS Secrets Manager）。
    """
    to_save = dict(config)
    # 加密敏感字段
    if to_save.get("api_key"):
        to_save["api_key"] = _encrypt_value(to_save["api_key"])
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)


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


@router.get("/config", response_model=OpenClawConfigResponse)
async def get_config():
    """
    获取OpenClaw配置
    
    返回当前生效的配置（内存 + 持久化配置）
    """
    saved = _load_config()
    return OpenClawConfigResponse(
        gateway_url=openclaw_service.gateway_url,
        ws_url=openclaw_service.ws_url,
        api_key=openclaw_service.api_key or saved.get("api_key"),
        heartbeat_interval=saved.get("heartbeat_interval", 1800),
        ai_news_enabled=saved.get("ai_news_enabled", True),
        news_enabled=saved.get("news_enabled", True),
        red_news_enabled=saved.get("red_news_enabled", True),
    )


@router.post("/config", response_model=dict)
async def update_config(config: OpenClawConfigUpdate):
    """
    更新OpenClaw配置
    
    更新Gateway URL、WebSocket URL、情报开关等配置
    """
    updated = {}
    saved = _load_config()

    if config.gateway_url is not None:
        openclaw_service.gateway_url = config.gateway_url
        saved["gateway_url"] = config.gateway_url
        updated["gateway_url"] = config.gateway_url

    if config.ws_url is not None:
        openclaw_service.ws_url = config.ws_url
        saved["ws_url"] = config.ws_url
        updated["ws_url"] = config.ws_url

    if config.api_key is not None:
        openclaw_service.api_key = config.api_key
        saved["api_key"] = config.api_key
        updated["api_key"] = "***"

    if config.heartbeat_interval is not None:
        saved["heartbeat_interval"] = config.heartbeat_interval
        updated["heartbeat_interval"] = config.heartbeat_interval

    # 客栈情报开关（F09）
    if config.ai_news_enabled is not None:
        saved["ai_news_enabled"] = config.ai_news_enabled
        updated["ai_news_enabled"] = config.ai_news_enabled

    if config.news_enabled is not None:
        saved["news_enabled"] = config.news_enabled
        updated["news_enabled"] = config.news_enabled

    if config.red_news_enabled is not None:
        saved["red_news_enabled"] = config.red_news_enabled
        updated["red_news_enabled"] = config.red_news_enabled

    _save_config(saved)

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
