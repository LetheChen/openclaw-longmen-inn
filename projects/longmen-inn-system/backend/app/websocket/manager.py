"""
龙门客栈业务管理系统 - WebSocket连接管理
===============================
作者: 厨子 (神厨小福贵)

管理WebSocket连接和消息广播
"""

import json
import logging
from typing import Dict, List, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    WebSocket连接管理器
    
    管理所有活动的WebSocket连接，支持：
    - 连接注册和注销
    - 个人消息发送
    - 广播消息
    - 分组消息（Agent组、项目组等）
    """
    
    def __init__(self):
        # 所有活跃连接 {websocket: {"client_id": str, "groups": List[str]}}
        self.active_connections: Dict[WebSocket, dict] = {}
        
        # 按client_id索引的连接
        self.client_connections: Dict[str, WebSocket] = {}
        
        logger.info("WebSocket连接管理器初始化完成")
    
    async def connect(
        self, 
        websocket: WebSocket, 
        client_id: Optional[str] = None,
        groups: Optional[List[str]] = None
    ):
        """
        接受新的WebSocket连接
        
        Args:
            websocket: WebSocket连接对象
            client_id: 客户端唯一标识（可选）
            groups: 客户端所属组列表（可选）
        """
        await websocket.accept()
        
        connection_info = {
            "client_id": client_id,
            "groups": groups or []
        }
        
        self.active_connections[websocket] = connection_info
        
        if client_id:
            self.client_connections[client_id] = websocket
        
        logger.info(f"WebSocket连接已建立 | Client: {client_id} | 总连接数: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        断开WebSocket连接
        
        Args:
            websocket: 要断开的WebSocket连接
        """
        connection_info = self.active_connections.pop(websocket, {})
        client_id = connection_info.get("client_id")
        
        if client_id and client_id in self.client_connections:
            del self.client_connections[client_id]
        
        logger.info(f"WebSocket连接已断开 | Client: {client_id} | 剩余连接数: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        向指定连接发送个人消息
        
        Args:
            message: 要发送的消息字典
            websocket: 目标WebSocket连接
        """
        try:
            await websocket.send_json(message)
            logger.debug(f"个人消息已发送 | Message: {message.get('type', 'unknown')}")
        except Exception as e:
            logger.error(f"发送个人消息失败: {str(e)}")
    
    async def send_to_client(self, message: dict, client_id: str):
        """
        通过client_id向指定客户端发送消息
        
        Args:
            message: 要发送的消息字典
            client_id: 目标客户端ID
        """
        websocket = self.client_connections.get(client_id)
        if websocket:
            await self.send_personal_message(message, websocket)
        else:
            logger.warning(f"客户端未连接 | Client: {client_id}")
    
    async def broadcast(self, message: dict):
        """
        广播消息给所有连接的客户端
        
        Args:
            message: 要广播的消息字典
        """
        disconnected = []
        
        for websocket in self.active_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败: {str(e)}")
                disconnected.append(websocket)
        
        # 清理断开的连接
        for websocket in disconnected:
            self.disconnect(websocket)
        
        logger.info(f"广播消息已发送 | 目标数: {len(self.active_connections)} | Type: {message.get('type', 'unknown')}")
    
    async def broadcast_to_group(self, message: dict, group: str):
        """
        向指定组的所有成员广播消息
        
        Args:
            message: 要广播的消息字典
            group: 目标组名
        """
        count = 0
        
        for websocket, connection_info in self.active_connections.items():
            groups = connection_info.get("groups", [])
            if group in groups:
                try:
                    await websocket.send_json(message)
                    count += 1
                except Exception as e:
                    logger.error(f"组播消息失败: {str(e)}")
        
        logger.info(f"组播消息已发送 | Group: {group} | 目标数: {count}")


# 创建全局连接管理器实例
manager = ConnectionManager()