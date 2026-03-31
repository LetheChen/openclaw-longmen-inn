"""
龙门客栈业务管理系统 - WebSocket处理器
===============================
作者: 厨子 (神厨小福贵)

WebSocket路由和消息处理，支持OpenClaw事件订阅
"""

import json
import logging
import asyncio
from typing import Optional, Set
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, WebSocketException

from .manager import manager
from app.services.openclaw_service import openclaw_service
from app.core.security import verify_token

logger = logging.getLogger(__name__)

websocket_router = APIRouter()

openclaw_subscribers: Set[WebSocket] = set()


async def verify_websocket_token(token: Optional[str]) -> Optional[dict]:
    """
    验证WebSocket连接令牌
    
    Returns:
        解码后的payload，验证失败返回None
    """
    if not token:
        return None
    return verify_token(token, "access")


@websocket_router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: Optional[str] = Query(None),
    groups: Optional[str] = Query(None)
):
    # 验证token（可选，但推荐开启）
    if token:
        payload = await verify_websocket_token(token)
        if not payload:
            await websocket.close(code=4001, reason="Invalid or expired token")
            logger.warning(f"WebSocket connection rejected: invalid token for client {client_id}")
            return
        logger.info(f"WebSocket authenticated: client_id={client_id}, user_id={payload.get('sub')}")
    
    group_list = groups.split(",") if groups else []
    
    await manager.connect(websocket, client_id=client_id, groups=group_list)
    
    try:
        await manager.send_personal_message({
            "type": "connection_established",
            "data": {
                "client_id": client_id,
                "groups": group_list,
                "message": "欢迎连接到龙门客栈业务管理系统！",
                "timestamp": datetime.now().isoformat()
            }
        }, websocket)
        
        while True:
            try:
                data = await websocket.receive_text()
                
                try:
                    message = json.loads(data)
                except json.JSONDecodeError:
                    await manager.send_personal_message({
                        "type": "error",
                        "data": {"message": "消息格式错误，请发送JSON格式数据"}
                    }, websocket)
                    continue
                
                await handle_message(message, websocket, client_id)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket连接断开 | Client: {client_id}")
                break
            except Exception as e:
                logger.error(f"处理WebSocket消息时出错: {str(e)}")
                try:
                    await manager.send_personal_message({
                        "type": "error",
                        "data": {"message": f"处理消息时出错: {str(e)}"}
                    }, websocket)
                except:
                    pass
    
    finally:
        manager.disconnect(websocket)
        openclaw_subscribers.discard(websocket)
        logger.info(f"WebSocket连接已清理 | Client: {client_id}")


async def handle_message(message: dict, websocket: WebSocket, client_id: str):
    msg_type = message.get("type")
    data = message.get("data", {})
    
    logger.debug(f"收到消息 | Type: {msg_type} | Client: {client_id}")
    
    if msg_type == "ping":
        await manager.send_personal_message({
            "type": "pong",
            "data": {"timestamp": data.get("timestamp")}
        }, websocket)
    
    elif msg_type == "subscribe":
        channel = data.get("channel")
        
        if channel == "openclaw":
            openclaw_subscribers.add(websocket)
            await manager.send_personal_message({
                "type": "subscribed",
                "data": {"channel": channel, "message": "已订阅OpenClaw实时事件"}
            }, websocket)
            
            live_status = await openclaw_service.get_live_status()
            await manager.send_personal_message({
                "type": "openclaw_status",
                "data": {
                    "gateway": live_status.gateway.model_dump(),
                    "agents": live_status.agents,
                    "sessions": [s.model_dump() for s in live_status.sessions],
                    "timestamp": live_status.timestamp.isoformat()
                }
            }, websocket)
        else:
            await manager.send_personal_message({
                "type": "subscribed",
                "data": {"channel": channel}
            }, websocket)
    
    elif msg_type == "unsubscribe":
        channel = data.get("channel")
        
        if channel == "openclaw":
            openclaw_subscribers.discard(websocket)
        
        await manager.send_personal_message({
            "type": "unsubscribed",
            "data": {"channel": channel}
        }, websocket)
    
    elif msg_type == "agent_status":
        await manager.broadcast({
            "type": "agent_status_update",
            "data": data
        })
    
    elif msg_type == "task_status":
        await manager.broadcast({
            "type": "task_status_update",
            "data": data
        })
    
    elif msg_type == "get_live_status":
        live_status = await openclaw_service.get_live_status()
        await manager.send_personal_message({
            "type": "live_status",
            "data": {
                "gateway": live_status.gateway.model_dump(),
                "agents": live_status.agents,
                "sessions": [s.model_dump() for s in live_status.sessions],
                "routes": [r.model_dump() for r in live_status.routes],
                "statistics": live_status.statistics,
                "timestamp": live_status.timestamp.isoformat()
            }
        }, websocket)
    
    else:
        await manager.send_personal_message({
            "type": "error",
            "data": {"message": f"未知的消息类型: {msg_type}"}
        }, websocket)


async def broadcast_openclaw_event(event_type: str, data: dict):
    """广播OpenClaw事件给所有订阅者"""
    if not openclaw_subscribers:
        return
    
    message = {
        "type": event_type,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    disconnected = []
    for websocket in openclaw_subscribers:
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"广播OpenClaw事件失败: {str(e)}")
            disconnected.append(websocket)
    
    for ws in disconnected:
        openclaw_subscribers.discard(ws)


async def openclaw_event_loop():
    """OpenClaw事件循环，定期推送状态更新"""
    while True:
        try:
            if openclaw_subscribers:
                live_status = await openclaw_service.get_live_status()
                
                await broadcast_openclaw_event("openclaw_heartbeat", {
                    "gateway_status": live_status.gateway.status.value,
                    "connected_agents": len(live_status.agents),
                    "active_sessions": len(live_status.sessions),
                    "timestamp": live_status.timestamp.isoformat()
                })
            
        except Exception as e:
            logger.error(f"OpenClaw事件循环错误: {str(e)}")
        
        await asyncio.sleep(10)
