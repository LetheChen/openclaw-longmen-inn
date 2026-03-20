"""
龙门客栈业务管理系统 - OpenClaw服务
===============================
作者: 厨子 (神厨小福贵)

与OpenClaw Gateway通信的服务层
支持Agent心跳、会话管理、实时状态监控
"""

import asyncio
import json
import subprocess
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pathlib import Path
import aiohttp
import websockets

from app.core.config import settings
from app.schemas.openclaw import (
    GatewayStatus, GatewayStatusResponse, AgentSessionResponse,
    AgentHeartbeatResponse, RouteConfigResponse, LiveStatusResponse,
    SessionStatus
)
from app.db.session import SessionLocal
from app.db import models
from app.services.data_collection_service import OpenClawHeartbeatHandler


class OpenClawService:
    """OpenClaw Gateway服务"""

    def __init__(self):
        self.gateway_url = settings.OPENCLAW_GATEWAY_URL
        self.ws_url = settings.OPENCLAW_WS_URL
        self.api_key = settings.OPENCLAW_API_KEY
        self._ws_connection = None
        self._session_cache: Dict[str, Any] = {}
        self._last_status_check: Optional[datetime] = None
        self._heartbeat_callbacks: List[callable] = []

    def register_heartbeat_callback(self, callback: callable):
        """注册心跳回调函数"""
        self._heartbeat_callbacks.append(callback)

    async def _notify_heartbeat(self, agent_id: str, status: str, **kwargs):
        """通知心跳回调"""
        db = SessionLocal()
        try:
            handler = OpenClawHeartbeatHandler(db)
            handler.handle_heartbeat(agent_id, status, **kwargs)
            
            for callback in self._heartbeat_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(agent_id, status, **kwargs)
                    else:
                        callback(agent_id, status, **kwargs)
                except Exception as e:
                    pass
        finally:
            db.close()

    async def check_gateway_health(self) -> GatewayStatusResponse:
        """检查Gateway健康状态"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.gateway_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return GatewayStatusResponse(
                            status=GatewayStatus.ONLINE,
                            version=data.get("version", "unknown"),
                            uptime=data.get("uptime", "unknown"),
                            last_checked=datetime.now(),
                            connected_agents=data.get("connected_agents", 0),
                            active_sessions=data.get("active_sessions", 0),
                            message_queue_size=data.get("message_queue_size", 0)
                        )
                    else:
                        return GatewayStatusResponse(
                            status=GatewayStatus.DEGRADED,
                            last_checked=datetime.now()
                        )
        except Exception as e:
            return GatewayStatusResponse(
                status=GatewayStatus.OFFLINE,
                last_checked=datetime.now()
            )

    async def get_agent_heartbeat(self, agent_id: str) -> AgentHeartbeatResponse:
        """获取Agent心跳状态"""
        try:
            agent_dir = Path.home() / ".openclaw" / "agents" / agent_id
            heartbeat_file = agent_dir / "heartbeat.json"
            
            if heartbeat_file.exists():
                with open(heartbeat_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return AgentHeartbeatResponse(
                        agent_id=agent_id,
                        status=data.get("status", "unknown"),
                        last_heartbeat=datetime.fromisoformat(data["last_heartbeat"]) if data.get("last_heartbeat") else None,
                        next_heartbeat=datetime.fromisoformat(data["next_heartbeat"]) if data.get("next_heartbeat") else None,
                        heartbeat_interval=data.get("heartbeat_interval", 1800),
                        active_tasks=data.get("active_tasks", 0),
                        memory_usage=data.get("memory_usage"),
                        cpu_usage=data.get("cpu_usage")
                    )
        except Exception:
            pass
        
        return AgentHeartbeatResponse(
            agent_id=agent_id,
            status="unknown",
            heartbeat_interval=1800
        )

    async def get_agent_sessions(self, agent_id: Optional[str] = None) -> List[AgentSessionResponse]:
        """获取Agent会话列表"""
        sessions = []
        
        try:
            agents_dir = Path.home() / ".openclaw" / "agents"
            
            for agent_path in agents_dir.iterdir():
                if agent_path.is_dir():
                    current_agent_id = agent_path.name
                    
                    if agent_id and current_agent_id != agent_id:
                        continue
                    
                    sessions_dir = agent_path / "sessions"
                    if sessions_dir.exists():
                        for session_file in sessions_dir.glob("*.jsonl"):
                            try:
                                with open(session_file, "r", encoding="utf-8") as f:
                                    first_line = f.readline()
                                    if first_line:
                                        header = json.loads(first_line)
                                        session_id = header.get("id", session_file.stem)
                                        
                                        message_count = sum(1 for _ in f)
                                        
                                        sessions.append(AgentSessionResponse(
                                            id=session_id,
                                            agent_id=current_agent_id,
                                            agent_name=self._get_agent_name(current_agent_id),
                                            status=SessionStatus.ACTIVE,
                                            channel=None,
                                            last_activity=datetime.fromtimestamp(
                                                session_file.stat().st_mtime
                                            ),
                                            message_count=message_count
                                        ))
                            except Exception:
                                continue
        except Exception:
            pass
        
        return sessions

    def _get_agent_name(self, agent_id: str) -> str:
        """获取Agent显示名称"""
        agent_names = {
            "main": "老板娘",
            "innkeeper": "老板娘",
            "manager": "大掌柜",
            "waiter": "店小二",
            "chef": "厨子",
            "accountant": "账房先生",
            "storyteller": "说书先生",
            "painter": "画师"
        }
        return agent_names.get(agent_id, agent_id)

    async def get_live_status(self) -> LiveStatusResponse:
        """获取实时状态"""
        gateway_status = await self.check_gateway_health()
        sessions = await self.get_agent_sessions()
        
        agents = await self._get_agents_status()
        routes = await self._get_routes()
        statistics = await self._get_statistics()
        
        return LiveStatusResponse(
            gateway=gateway_status,
            agents=agents,
            sessions=sessions,
            routes=routes,
            statistics=statistics,
            timestamp=datetime.now()
        )

    async def _get_agents_status(self) -> List[Dict[str, Any]]:
        """获取所有Agent状态"""
        agents = []
        
        try:
            agents_dir = Path.home() / ".openclaw" / "agents"
            
            for agent_path in agents_dir.iterdir():
                if agent_path.is_dir():
                    agent_id = agent_path.name
                    config_file = agent_path / "config.json"
                    
                    agent_info = {
                        "agent_id": agent_id,
                        "name": self._get_agent_name(agent_id),
                        "status": "idle",
                        "last_activity": None
                    }
                    
                    if config_file.exists():
                        try:
                            with open(config_file, "r", encoding="utf-8") as f:
                                config = json.load(f)
                                agent_info.update({
                                    "name": config.get("name", agent_info["name"]),
                                    "status": config.get("status", "idle")
                                })
                        except Exception:
                            pass
                    
                    agents.append(agent_info)
        except Exception:
            pass
        
        return agents

    async def _get_routes(self) -> List[RouteConfigResponse]:
        """获取路由配置"""
        routes = []
        
        try:
            config_file = Path.home() / ".openclaw" / "openclaw.json"
            
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    
                    bindings = config.get("bindings", [])
                    for idx, binding in enumerate(bindings):
                        match = binding.get("match", {})
                        routes.append(RouteConfigResponse(
                            id=f"route-{idx + 1}",
                            name=f"{match.get('channel', 'unknown')}路由",
                            source=match.get("channel", "unknown"),
                            target=binding.get("agentId", "unknown"),
                            enabled=True,
                            priority=idx + 1,
                            message_count=0
                        ))
        except Exception:
            pass
        
        return routes

    async def _get_statistics(self) -> Dict[str, Any]:
        """获取统计数据"""
        return {
            "total_agents": len(await self._get_agents_status()),
            "active_sessions": len(await self.get_agent_sessions()),
            "messages_today": 0,
            "tasks_completed": 0
        }

    async def execute_openclaw_command(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """执行OpenClaw CLI命令"""
        try:
            cmd = ["openclaw", command]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout"
            }
        except FileNotFoundError:
            return {
                "success": False,
                "error": "OpenClaw CLI not found"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def get_openclaw_status(self) -> Dict[str, Any]:
        """获取OpenClaw整体状态"""
        result = await self.execute_openclaw_command("status", ["--json"])
        
        if result["success"]:
            try:
                return json.loads(result["output"])
            except json.JSONDecodeError:
                pass
        
        return {
            "status": "unknown",
            "version": "unknown",
            "gateway": "offline"
        }

    async def subscribe_to_events(self):
        """订阅OpenClaw事件流"""
        logger.info(f"连接OpenClaw WebSocket: {self.ws_url}")
        
        try:
            async with websockets.connect(self.ws_url) as ws:
                logger.info("OpenClaw WebSocket连接成功")
                
                subscribe_msg = {
                    "type": "subscribe",
                    "events": ["agent_heartbeat", "session_update", "task_update"]
                }
                await ws.send(json.dumps(subscribe_msg))
                
                while True:
                    try:
                        message = await ws.recv()
                        data = json.loads(message)
                        
                        event_type = data.get("type")
                        
                        if event_type == "agent_heartbeat":
                            await self._handle_heartbeat_event(data)
                        elif event_type == "session_update":
                            await self._handle_session_event(data)
                        elif event_type == "task_update":
                            await self._handle_task_event(data)
                            
                    except websockets.exceptions.ConnectionClosed:
                        logger.warning("OpenClaw WebSocket连接断开，尝试重连...")
                        await asyncio.sleep(5)
                        break
                    except json.JSONDecodeError:
                        logger.warning("无效的JSON消息")
                    except Exception as e:
                        logger.error(f"处理消息错误: {e}")
                        
        except Exception as e:
            logger.error(f"WebSocket连接失败: {e}")
            await asyncio.sleep(10)

    async def _handle_heartbeat_event(self, data: Dict[str, Any]):
        """处理心跳事件"""
        agent_id = data.get("agent_id")
        status = data.get("status", "idle")
        
        if agent_id:
            await self._notify_heartbeat(
                agent_id,
                status,
                task_no=data.get("task_no"),
                message=data.get("message"),
                extra_data=data.get("metadata")
            )

    async def _handle_session_event(self, data: Dict[str, Any]):
        """处理会话事件"""
        logger.info(f"会话事件: {data}")

    async def _handle_task_event(self, data: Dict[str, Any]):
        """处理任务事件"""
        logger.info(f"任务事件: {data}")

    async def get_online_agents_from_db(self) -> List[Dict[str, Any]]:
        """从数据库获取在线Agent列表"""
        db = SessionLocal()
        try:
            threshold = datetime.utcnow() - timedelta(minutes=5)
            
            agents = db.query(models.Agent).filter(
                models.Agent.last_heartbeat >= threshold
            ).all()
            
            return [
                {
                    "agent_id": a.agent_id,
                    "name": a.name,
                    "title": a.title,
                    "status": a.status.value,
                    "longmenling": a.longmenling,
                    "level": a.level,
                    "current_task": a.current_task.task_no if a.current_task else None,
                    "last_heartbeat": a.last_heartbeat.isoformat() if a.last_heartbeat else None,
                }
                for a in agents
            ]
        finally:
            db.close()


import logging
logger = logging.getLogger(__name__)

openclaw_service = OpenClawService()
