"""
龙门客栈业务管理系统 - OpenClaw状态同步服务
===============================
作者: 厨子 (神厨小福贵)

自动同步OpenClaw Agent状态到数据库
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from app.db.session import SessionLocal
from app.db import models
from app.services.openclaw_service import openclaw_service

logger = logging.getLogger(__name__)


class OpenClawSyncService:
    """OpenClaw状态同步服务"""
    
    def __init__(self):
        self.running = False
        self.sync_interval = 30  # 30秒同步一次
        self.agents_dir = Path.home() / ".openclaw" / "agents"
        self._last_sync: Optional[datetime] = None
        self._sync_count = 0
    
    async def start(self):
        """启动同步服务"""
        if self.running:
            logger.warning("OpenClaw同步服务已在运行")
            return
        
        self.running = True
        logger.info("🔄 OpenClaw状态同步服务启动")
        
        await self._sync_loop()
    
    def stop(self):
        """停止同步服务"""
        self.running = False
        logger.info("🛑 OpenClaw状态同步服务停止")
    
    async def _sync_loop(self):
        """同步循环"""
        while self.running:
            try:
                await self.sync_all_agents()
                self._last_sync = datetime.now()
                self._sync_count += 1
            except Exception as e:
                logger.error(f"同步Agent状态失败: {e}")
            
            await asyncio.sleep(self.sync_interval)
    
    async def sync_all_agents(self) -> Dict[str, int]:
        """同步所有Agent状态"""
        db = SessionLocal()
        stats = {"total": 0, "updated": 0, "new": 0, "offline": 0}
        
        try:
            openclaw_agents = await self._get_openclaw_agents()
            stats["total"] = len(openclaw_agents)
            
            openclaw_agent_ids = set(openclaw_agents.keys())
            
            db_agents = db.query(models.Agent).all()
            db_agent_map = {a.agent_id: a for a in db_agents}
            
            for agent_id, agent_info in openclaw_agents.items():
                db_agent = db_agent_map.get(agent_id)
                
                if db_agent:
                    new_status = self._map_status(agent_info.get("status", "idle"))
                    
                    if db_agent.status != new_status:
                        old_status = db_agent.status
                        db_agent.status = new_status
                        db_agent.last_heartbeat = datetime.utcnow()
                        stats["updated"] += 1
                        logger.info(f"Agent {db_agent.name} 状态更新: {old_status.value} -> {new_status.value}")
                    else:
                        db_agent.last_heartbeat = datetime.utcnow()
                else:
                    new_agent = models.Agent(
                        agent_id=agent_id,
                        name=agent_info.get("name", agent_id),
                        status=self._map_status(agent_info.get("status", "idle")),
                        level=1,
                        longmenling=0,
                        last_heartbeat=datetime.utcnow()
                    )
                    db.add(new_agent)
                    stats["new"] += 1
                    logger.info(f"发现新Agent: {agent_id}")
            
            for db_agent in db_agents:
                if db_agent.agent_id not in openclaw_agent_ids:
                    if db_agent.status != models.AgentStatus.OFFLINE:
                        db_agent.status = models.AgentStatus.OFFLINE
                        stats["offline"] += 1
                        logger.info(f"Agent {db_agent.name} 已离线")
            
            db.commit()
            
            if stats["updated"] > 0 or stats["new"] > 0 or stats["offline"] > 0:
                logger.info(f"同步完成: 总计{stats['total']}个, 更新{stats['updated']}个, 新增{stats['new']}个, 离线{stats['offline']}个")
            
        except Exception as e:
            logger.error(f"同步Agent状态异常: {e}")
            db.rollback()
        finally:
            db.close()
        
        return stats
    
    async def _get_openclaw_agents(self) -> Dict[str, Any]:
        """获取OpenClaw中所有Agent信息
        
        状态判断规则：
        1. 检查sessions目录下最近活跃的jsonl文件
        2. 如果最后修改时间 < 180秒，则状态为busy（活跃）
        3. 如果最后修改时间 < 600秒，则状态为online（可能停滞）
        4. 否则状态为idle（空闲）
        """
        agents = {}
        now = datetime.now()
        active_threshold = 180
        stale_threshold = 600
        
        try:
            if not self.agents_dir.exists():
                logger.debug(f"OpenClaw agents目录不存在: {self.agents_dir}")
                return agents
            
            for agent_path in self.agents_dir.iterdir():
                if not agent_path.is_dir():
                    continue
                
                agent_id = agent_path.name
                config_file = agent_path / "config.json"
                
                agent_info = {
                    "agent_id": agent_id,
                    "name": agent_id,
                    "status": "idle",
                    "last_activity": None
                }
                
                if config_file.exists():
                    try:
                        with open(config_file, "r", encoding="utf-8") as f:
                            config = json.load(f)
                            agent_info["name"] = config.get("name", agent_id)
                    except Exception as e:
                        logger.debug(f"读取Agent配置失败 {agent_id}: {e}")
                
                sessions_dir = agent_path / "sessions"
                if sessions_dir.exists():
                    jsonl_files = [
                        f for f in sessions_dir.glob("*.jsonl")
                        if "deleted" not in f.name and "reset" not in f.name
                    ]
                    
                    if jsonl_files:
                        latest_file = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                        mtime = datetime.fromtimestamp(latest_file.stat().st_mtime)
                        agent_info["last_activity"] = mtime.isoformat()
                        
                        age_seconds = (now - mtime).total_seconds()
                        
                        if age_seconds < active_threshold:
                            agent_info["status"] = "busy"
                        elif age_seconds < stale_threshold:
                            agent_info["status"] = "online"
                        else:
                            agent_info["status"] = "idle"
                
                agents[agent_id] = agent_info
                
        except Exception as e:
            logger.error(f"获取OpenClaw Agent列表失败: {e}")
        
        return agents
    
    def _map_status(self, status: str) -> models.AgentStatus:
        """映射状态字符串到数据库枚举"""
        status_map = {
            "idle": models.AgentStatus.IDLE,
            "online": models.AgentStatus.ONLINE,
            "busy": models.AgentStatus.BUSY,
            "offline": models.AgentStatus.OFFLINE,
        }
        return status_map.get(status.lower(), models.AgentStatus.IDLE)
    
    async def sync_single_agent(self, agent_id: str) -> bool:
        """同步单个Agent状态"""
        db = SessionLocal()
        try:
            agent_info = await self._get_single_agent_info(agent_id)
            
            if not agent_info:
                return False
            
            db_agent = db.query(models.Agent).filter(
                models.Agent.agent_id == agent_id
            ).first()
            
            if db_agent:
                new_status = self._map_status(agent_info.get("status", "idle"))
                db_agent.status = new_status
                db_agent.last_heartbeat = datetime.utcnow()
                db.commit()
                logger.info(f"Agent {db_agent.name} 状态同步: {new_status.value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"同步Agent {agent_id} 失败: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    async def _get_single_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """获取单个Agent信息"""
        agents = await self._get_openclaw_agents()
        return agents.get(agent_id)
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步服务状态"""
        return {
            "running": self.running,
            "sync_interval": self.sync_interval,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "sync_count": self._sync_count,
        }


openclaw_sync_service = OpenClawSyncService()
