"""
龙门客栈业务管理系统 - 数据自动采集服务
===============================
作者: 厨子 (神厨小福贵)

定时从LEDGER.md、ROSTER.md等文件同步数据到数据库
支持OpenClaw心跳事件监听
"""

import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db import models
from app.db.import_production_data import ProductionDataImporter, LONGMEN_INN_ROOT

logger = logging.getLogger(__name__)


class DataCollectionService:
    """数据自动采集服务"""
    
    def __init__(self):
        self.running = False
        self.interval_seconds = 300  # 5分钟同步一次
        self.ledger_path = LONGMEN_INN_ROOT / "LEDGER.md"
        self.roster_path = LONGMEN_INN_ROOT / "ROSTER.md"
        self.last_sync_time: Optional[datetime] = None
        self.file_mtimes: Dict[str, float] = {}
        
    def _get_file_mtime(self, path: Path) -> Optional[float]:
        """获取文件修改时间"""
        if path.exists():
            return path.stat().st_mtime
        return None
    
    def _check_file_changed(self, path: Path) -> bool:
        """检查文件是否变更"""
        current_mtime = self._get_file_mtime(path)
        if current_mtime is None:
            return False
        
        last_mtime = self.file_mtimes.get(str(path))
        if last_mtime is None:
            self.file_mtimes[str(path)] = current_mtime
            return True
        
        if current_mtime > last_mtime:
            self.file_mtimes[str(path)] = current_mtime
            return True
        
        return False
    
    def sync_agent_status(self, db: Session) -> int:
        """同步Agent状态"""
        logger.info("同步Agent状态...")
        
        if not self._check_file_changed(self.ledger_path):
            logger.debug("LEDGER.md未变更，跳过同步")
            return 0
        
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            status_pattern = r'\| `(\w+)` \| (.+?) \| (.+?) \| (.+?) \|'
            matches = re.findall(status_pattern, content)
            
            updated = 0
            for match in matches:
                agent_id, status_str, current_task, today_goal = match
                
                status_map = {
                    '✅ 空闲': models.AgentStatus.IDLE,
                    '🔥 **进行中**': models.AgentStatus.BUSY,
                    '🔥 进行中': models.AgentStatus.BUSY,
                    '离线': models.AgentStatus.OFFLINE,
                }
                
                status = status_map.get(status_str.strip(), models.AgentStatus.IDLE)
                
                agent = db.query(models.Agent).filter(
                    models.Agent.agent_id == agent_id.strip()
                ).first()
                
                if agent and agent.status != status:
                    agent.status = status
                    agent.last_heartbeat = datetime.utcnow()
                    updated += 1
                    logger.info(f"更新Agent状态: {agent.name} -> {status.value}")
            
            db.commit()
            return updated
            
        except Exception as e:
            logger.error(f"同步Agent状态失败: {e}")
            db.rollback()
            return 0
    
    def sync_task_status(self, db: Session) -> int:
        """同步任务状态"""
        logger.info("同步任务状态...")
        
        if not self._check_file_changed(self.ledger_path):
            return 0
        
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            task_pattern = r'\| (T-\d{8}-\d{3}) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|'
            matches = re.findall(task_pattern, content)
            
            status_map = {
                '✅ 已完成': models.TaskStatus.COMPLETED,
                '🔥 进行中': models.TaskStatus.IN_PROGRESS,
                '待开工': models.TaskStatus.PENDING,
                '待审核': models.TaskStatus.REVIEWING,
                '已阻塞': models.TaskStatus.BLOCKED,
            }
            
            updated = 0
            for match in matches:
                task_no, content_str, creator, assignee, status_str = match
                
                status = status_map.get(status_str.strip())
                if not status:
                    continue
                
                task = db.query(models.Task).filter(
                    models.Task.task_no == task_no.strip()
                ).first()
                
                if task and task.status != status:
                    old_status = task.status
                    task.status = status
                    
                    if status == models.TaskStatus.COMPLETED:
                        task.completed_at = datetime.utcnow()
                        task.progress = 100
                    elif status == models.TaskStatus.IN_PROGRESS:
                        if not task.started_at:
                            task.started_at = datetime.utcnow()
                    
                    task_log = models.TaskLog(
                        task_id=task.id,
                        from_status=old_status,
                        to_status=status,
                        operator_agent_id='system',
                        comment='自动同步自LEDGER.md'
                    )
                    db.add(task_log)
                    
                    updated += 1
                    logger.info(f"更新任务状态: {task_no} -> {status.value}")
            
            db.commit()
            return updated
            
        except Exception as e:
            logger.error(f"同步任务状态失败: {e}")
            db.rollback()
            return 0
    
    def sync_longmenling(self, db: Session) -> int:
        """同步龙门令积分"""
        logger.info("同步龙门令积分...")
        
        if not self._check_file_changed(self.ledger_path):
            return 0
        
        try:
            with open(self.ledger_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            lml_pattern = r'\| (\w+) \| (\d+) \| (.+?) \|'
            matches = re.findall(lml_pattern, content)
            
            name_to_id = {
                '大掌柜': 'innkeeper',
                '店小二': 'waiter',
                '厨子': 'chef',
                '账房先生': 'accountant',
                '说书先生': 'storyteller',
                '画师': 'painter',
                '老板娘': 'main',
            }
            
            updated = 0
            for match in matches:
                name, amount, notes = match
                
                agent_id = name_to_id.get(name.strip())
                if not agent_id:
                    continue
                
                agent = db.query(models.Agent).filter(
                    models.Agent.agent_id == agent_id
                ).first()
                
                if agent:
                    new_amount = int(amount.strip())
                    if agent.longmenling != new_amount:
                        diff = new_amount - agent.longmenling
                        agent.longmenling = new_amount
                        agent.level = models.get_level_by_longmenling(new_amount)
                        
                        log = models.LongmenlingLog(
                            agent_id=agent_id,
                            amount=diff,
                            reason=f"同步自LEDGER.md: {notes.strip()}"
                        )
                        db.add(log)
                        
                        updated += 1
                        logger.info(f"更新龙门令: {agent.name} -> {new_amount}")
            
            db.commit()
            return updated
            
        except Exception as e:
            logger.error(f"同步龙门令失败: {e}")
            db.rollback()
            return 0
    
    def run_sync_cycle(self) -> Dict[str, int]:
        """执行一次同步周期"""
        logger.info("=" * 40)
        logger.info("开始数据同步周期...")
        logger.info("=" * 40)
        
        db = SessionLocal()
        results = {}
        
        try:
            results['agents'] = self.sync_agent_status(db)
            results['tasks'] = self.sync_task_status(db)
            results['longmenling'] = self.sync_longmenling(db)
            
            self.last_sync_time = datetime.utcnow()
            
            total = sum(results.values())
            logger.info(f"同步完成，共更新 {total} 条记录")
            
        finally:
            db.close()
        
        return results
    
    async def start(self):
        """启动自动采集服务"""
        logger.info("🚀 数据自动采集服务启动")
        logger.info(f"同步间隔: {self.interval_seconds}秒")
        logger.info(f"数据源目录: {LONGMEN_INN_ROOT}")
        
        self.running = True
        
        while self.running:
            try:
                self.run_sync_cycle()
            except Exception as e:
                logger.error(f"同步周期执行失败: {e}")
            
            await asyncio.sleep(self.interval_seconds)
    
    def stop(self):
        """停止自动采集服务"""
        logger.info("🛑 数据自动采集服务停止")
        self.running = False


class OpenClawHeartbeatHandler:
    """OpenClaw心跳处理器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def handle_heartbeat(self, agent_id: str, status: str, task_no: Optional[str] = None, **kwargs):
        """处理Agent心跳"""
        agent = self.db.query(models.Agent).filter(
            models.Agent.agent_id == agent_id
        ).first()
        
        if not agent:
            logger.warning(f"未找到Agent: {agent_id}")
            return
        
        status_map = {
            'idle': models.AgentStatus.IDLE,
            'busy': models.AgentStatus.BUSY,
            'online': models.AgentStatus.ONLINE,
            'offline': models.AgentStatus.OFFLINE,
        }
        
        new_status = status_map.get(status, models.AgentStatus.IDLE)
        
        if agent.status != new_status:
            agent.status = new_status
            logger.info(f"Agent {agent.name} 状态变更: {status}")
        
        agent.last_heartbeat = datetime.utcnow()
        
        heartbeat_log = models.AgentHeartbeat(
            agent_id=agent_id,
            status=new_status,
            current_task_no=task_no,
            message=kwargs.get('message'),
            extra_data=kwargs.get('metadata'),
        )
        self.db.add(heartbeat_log)
        
        if task_no:
            task = self.db.query(models.Task).filter(
                models.Task.task_no == task_no
            ).first()
            if task:
                agent.current_task_id = task.id
        
        self.db.commit()
        logger.debug(f"记录心跳: {agent_id} - {status}")
    
    def get_online_agents(self) -> List[Dict[str, Any]]:
        """获取在线Agent列表"""
        threshold = datetime.utcnow() - timedelta(minutes=5)
        
        agents = self.db.query(models.Agent).filter(
            models.Agent.last_heartbeat >= threshold
        ).all()
        
        return [
            {
                'agent_id': a.agent_id,
                'name': a.name,
                'status': a.status.value,
                'current_task': a.current_task.task_no if a.current_task else None,
                'last_heartbeat': a.last_heartbeat.isoformat() if a.last_heartbeat else None,
            }
            for a in agents
        ]


data_collection_service = DataCollectionService()


def start_data_collection():
    """启动数据采集服务"""
    import threading
    
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(data_collection_service.start())
    
    thread = threading.Thread(target=run_in_thread, daemon=True)
    thread.start()
    logger.info("数据采集服务线程已启动")
    return thread


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    service = DataCollectionService()
    service.run_sync_cycle()
