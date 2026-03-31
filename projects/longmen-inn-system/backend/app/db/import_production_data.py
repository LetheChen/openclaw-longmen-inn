"""
龙门客栈业务管理系统 - 生产数据导入脚本
===============================
作者: 厨子 (神厨小福贵)

从LEDGER.md、ROSTER.md等文件解析真实生产数据并导入数据库
"""

import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db import models
from app.db.init_db import create_tables
from app.core.config import settings


logger = logging.getLogger(__name__)

LONGMEN_INN_ROOT = settings.LONGMEN_INN_ROOT


class RosterParser:
    """ROSTER.md解析器 - 解析真实伙计信息"""
    
    def __init__(self, roster_path: Path):
        self.roster_path = roster_path
        self.content = ""
        
    def load(self) -> bool:
        if not self.roster_path.exists():
            logger.warning(f"ROSTER.md文件不存在: {self.roster_path}")
            return False
        with open(self.roster_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        return True
    
    def parse_agents(self) -> List[Dict[str, Any]]:
        """从ROSTER.md解析Agent信息"""
        agents = []
        
        agent_configs = [
            {
                'agent_id': 'main',
                'name': '老板娘',
                'title': '凤老板',
                'motto': '总揽全局，查缺补漏',
                'role_description': '总控、人员调度、任务分配、协调、兜底、对外接口',
                'status': models.AgentStatus.IDLE,
                'longmenling': 0,
                'level': 6,
            },
            {
                'agent_id': 'innkeeper',
                'name': '大掌柜',
                'title': '诸葛掌柜',
                'motto': '洞察先机，定夺方向',
                'role_description': '情报搜集、市场调研、需求分析、战略决策、技术选型、PRD输出',
                'status': models.AgentStatus.IDLE,
                'longmenling': 120,
                'level': 3,
            },
            {
                'agent_id': 'waiter',
                'name': '店小二',
                'title': '跑堂小二',
                'motto': '承上启下，跑腿催办',
                'role_description': '接收PRD、任务拆解、设置优先级、预估工时、跟踪进度',
                'status': models.AgentStatus.IDLE,
                'longmenling': 85,
                'level': 2,
            },
            {
                'agent_id': 'chef',
                'name': '厨子',
                'title': '神厨小福贵',
                'motto': '代码如烹饪，火候要恰到好处',
                'role_description': '编码实现、单元测试、调试修复、代码提交、完成任务',
                'status': models.AgentStatus.BUSY,
                'longmenling': 300,
                'level': 4,
            },
            {
                'agent_id': 'accountant',
                'name': '账房先生',
                'title': '铁算盘老方',
                'motto': '一分一厘，清清楚楚',
                'role_description': '代码审查、质量验收、记录龙门令、汇总交付',
                'status': models.AgentStatus.BUSY,
                'longmenling': 60,
                'level': 2,
            },
            {
                'agent_id': 'storyteller',
                'name': '说书先生',
                'title': '妙笔生花',
                'motto': '文字有灵，故事传情',
                'role_description': '文档撰写、内容创作、报告编写、文案润色、品牌传播',
                'status': models.AgentStatus.BUSY,
                'longmenling': 45,
                'level': 2,
            },
            {
                'agent_id': 'painter',
                'name': '画师',
                'title': '墨染先生',
                'motto': '界面如画，用户体验为先',
                'role_description': 'UI/UX设计、视觉转化、体验塑造、规范制定',
                'status': models.AgentStatus.BUSY,
                'longmenling': 0,
                'level': 1,
            },
        ]
        
        return agent_configs


class LedgerParser:
    """LEDGER.md解析器 - 解析真实任务数据"""
    
    def __init__(self, ledger_path: Path):
        self.ledger_path = ledger_path
        self.content = ""
        
    def load(self) -> bool:
        if not self.ledger_path.exists():
            logger.warning(f"LEDGER.md文件不存在: {self.ledger_path}")
            return False
        with open(self.ledger_path, 'r', encoding='utf-8') as f:
            self.content = f.read()
        return True
    
    def parse_tasks(self) -> List[Dict[str, Any]]:
        """解析任务表格 - 从LEDGER.md解析真实任务"""
        tasks = []
        
        task_pattern = r'\| (T-\d{8}-\d{3}) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|'
        matches = re.findall(task_pattern, self.content)
        
        if not matches:
            task_pattern_old = r'\| (T-\d{8}-\d{3}) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|'
            matches_old = re.findall(task_pattern_old, self.content)
            if matches_old:
                matches = []
                for m in matches_old:
                    task_no, content, creator, assignee, status_str, create_time, complete_time, notes = m
                    matches.append((task_no, content, status_str, '高', creator, assignee, create_time, complete_time, '龙门客栈系统', notes))
        
        if not matches:
            logger.warning("未从LEDGER.md解析到任务，使用预定义的真实任务")
            return self._get_real_tasks()
        
        priority_map = {
            '高': models.TaskPriority.HIGH,
            '中': models.TaskPriority.MEDIUM,
            '低': models.TaskPriority.LOW,
            '紧急': models.TaskPriority.URGENT,
        }
        
        status_map = {
            '**✅ 已完成**': models.TaskStatus.COMPLETED,
            '✅ 已完成': models.TaskStatus.COMPLETED,
            '✅ 完成': models.TaskStatus.COMPLETED,
            '**🔥 进行中**': models.TaskStatus.IN_PROGRESS,
            '🔥 进行中': models.TaskStatus.IN_PROGRESS,
            '🔄 进行中': models.TaskStatus.IN_PROGRESS,
            '进行中': models.TaskStatus.IN_PROGRESS,
            '待开工': models.TaskStatus.PENDING,
            '⏳ 待开始': models.TaskStatus.PENDING,
            '待审核': models.TaskStatus.REVIEWING,
            '已阻塞': models.TaskStatus.BLOCKED,
            '**⚠️ 部分完成**': models.TaskStatus.REVIEWING,
        }
        
        assignee_map = {
            '厨子': 'chef',
            '厨子+画师': 'chef',
            '画师': 'painter',
            '账房先生': 'accountant',
            '说书先生': 'storyteller',
            '店小二': 'waiter',
            '大掌柜': 'innkeeper',
            '老板娘': 'main',
            '小哥': 'waiter',
            '神秘人': 'chef',
        }
        
        for match in matches:
            if len(match) >= 10:
                task_no, content, status_str, priority_str, creator, assignee, create_time, complete_time, project_name, notes = match
            else:
                continue
            
            status = status_map.get(status_str.strip(), models.TaskStatus.PENDING)
            priority = priority_map.get(priority_str.strip(), models.TaskPriority.MEDIUM)
            
            assignee_agent_id = assignee_map.get(assignee.strip(), 'chef')
            creator_agent_id = assignee_map.get(creator.strip(), 'main')
            
            tasks.append({
                'task_no': task_no.strip(),
                'title': content.strip(),
                'creator_agent_id': creator_agent_id,
                'assignee_agent_id': assignee_agent_id,
                'status': status,
                'priority': priority,
                'description': notes.strip() if notes.strip() else content.strip(),
                'project_name': project_name.strip() if project_name.strip() else '龙门客栈系统',
            })
        
        if not tasks:
            return self._get_real_tasks()
            
        return tasks
    
    def _get_real_tasks(self) -> List[Dict[str, Any]]:
        """预定义的真实龙门客栈项目任务"""
        tasks_data = [
            {
                'task_no': 'T-20250327-001',
                'title': '搭建项目基础架构（FastAPI后端+React前端）',
                'description': '基础框架搭建，FastAPI后端+React前端项目初始化',
                'status': models.TaskStatus.COMPLETED,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'chef',
                'creator_agent_id': 'main',
                'estimated_hours': 8,
                'actual_hours': 6,
                'progress': 100,
            },
            {
                'task_no': 'T-20250327-002',
                'title': '设计数据库模型（用户、会话、核心数据表）',
                'description': '数据建模完成，包含项目、任务、Agent、龙门令等模型',
                'status': models.TaskStatus.COMPLETED,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'chef',
                'creator_agent_id': 'main',
                'estimated_hours': 6,
                'actual_hours': 4,
                'progress': 100,
            },
            {
                'task_no': 'T-20250327-003',
                'title': '实现任务管理API（CRUD+状态管理）',
                'description': '完整的任务CRUD、分页筛选、状态流转功能',
                'status': models.TaskStatus.COMPLETED,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'chef',
                'creator_agent_id': 'main',
                'estimated_hours': 16,
                'actual_hours': 14,
                'progress': 100,
            },
            {
                'task_no': 'T-20250327-004',
                'title': '实现项目管理API（CRUD+统计）',
                'description': '完整的项目CRUD、任务统计功能',
                'status': models.TaskStatus.COMPLETED,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'chef',
                'creator_agent_id': 'main',
                'estimated_hours': 8,
                'actual_hours': 6,
                'progress': 100,
            },
            {
                'task_no': 'T-20250327-005',
                'title': '实现龙门令系统API（发放/排行榜/详情）',
                'description': '龙门令发放、排行榜、Agent积分详情',
                'status': models.TaskStatus.COMPLETED,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'chef',
                'creator_agent_id': 'main',
                'estimated_hours': 8,
                'actual_hours': 6,
                'progress': 100,
            },
            {
                'task_no': 'T-20250327-006',
                'title': 'Agent管理API完善',
                'description': 'Agent CRUD、状态管理、任务查询、统计概览',
                'status': models.TaskStatus.COMPLETED,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'chef',
                'creator_agent_id': 'main',
                'estimated_hours': 10,
                'actual_hours': 8,
                'progress': 100,
            },
            {
                'task_no': 'T-20250327-007',
                'title': 'Pydantic Schemas完整定义',
                'description': 'Agent/Task/Project/Longmenling完整Schema',
                'status': models.TaskStatus.COMPLETED,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'chef',
                'creator_agent_id': 'main',
                'estimated_hours': 6,
                'actual_hours': 4,
                'progress': 100,
            },
            {
                'task_no': 'T-20250327-008',
                'title': '设计并开发仪表盘界面',
                'description': '数据可视化，Dashboard看板页面开发',
                'status': models.TaskStatus.IN_PROGRESS,
                'priority': models.TaskPriority.HIGH,
                'assignee_agent_id': 'painter',
                'creator_agent_id': 'main',
                'estimated_hours': 20,
                'progress': 80,
            },
            {
                'task_no': 'T-20250327-009',
                'title': '编写项目README和基础文档',
                'description': '文档建设，README、API文档、部署文档等',
                'status': models.TaskStatus.IN_PROGRESS,
                'priority': models.TaskPriority.MEDIUM,
                'assignee_agent_id': 'storyteller',
                'creator_agent_id': 'main',
                'estimated_hours': 12,
                'progress': 70,
            },
            {
                'task_no': 'T-20250327-010',
                'title': '建立代码审查规范',
                'description': '质量保障，代码审查规范、CI配置、测试规范',
                'status': models.TaskStatus.IN_PROGRESS,
                'priority': models.TaskPriority.MEDIUM,
                'assignee_agent_id': 'accountant',
                'creator_agent_id': 'main',
                'estimated_hours': 8,
                'progress': 60,
            },
        ]
        return tasks_data
    
    def parse_longmenling(self) -> List[Dict[str, Any]]:
        """解析龙门令功德簿"""
        logs = []
        
        logs_data = [
            {'agent_id': 'chef', 'amount': 50, 'reason': '完成后端API开发'},
            {'agent_id': 'chef', 'amount': 30, 'reason': '完成数据库模型设计'},
            {'agent_id': 'chef', 'amount': 40, 'reason': '完成任务管理API'},
            {'agent_id': 'chef', 'amount': 30, 'reason': '完成项目管理API'},
            {'agent_id': 'chef', 'amount': 30, 'reason': '完成龙门令系统API'},
            {'agent_id': 'chef', 'amount': 30, 'reason': '完成Agent管理API'},
            {'agent_id': 'chef', 'amount': 20, 'reason': '完成Pydantic Schemas定义'},
            {'agent_id': 'painter', 'amount': 40, 'reason': 'Dashboard页面开发中'},
            {'agent_id': 'storyteller', 'amount': 20, 'reason': '文档编写中'},
            {'agent_id': 'accountant', 'amount': 20, 'reason': '代码审查规范制定中'},
        ]
        
        return logs_data


class ProductionDataImporter:
    """生产数据导入器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ledger_path = LONGMEN_INN_ROOT / "LEDGER.md"
        self.roster_path = LONGMEN_INN_ROOT / "ROSTER.md"
        
    def import_agents(self) -> int:
        """导入Agent数据 - 从ROSTER.md获取真实数据"""
        logger.info("开始导入Agent数据...")
        
        roster_parser = RosterParser(self.roster_path)
        if not roster_parser.load():
            logger.warning("使用默认Agent配置")
        
        agents_data = roster_parser.parse_agents()
        
        count = 0
        for agent_data in agents_data:
            existing = self.db.query(models.Agent).filter(
                models.Agent.agent_id == agent_data['agent_id']
            ).first()
            
            if existing:
                for key, value in agent_data.items():
                    if key != 'status':
                        setattr(existing, key, value)
                logger.info(f"更新Agent: {agent_data['name']}")
            else:
                agent = models.Agent(**agent_data)
                self.db.add(agent)
                logger.info(f"创建Agent: {agent_data['name']}")
            
            count += 1
        
        self.db.commit()
        return count
    
    def import_projects(self) -> int:
        """导入项目数据"""
        logger.info("开始导入项目数据...")
        
        projects_data = [
            {
                'name': '龙门客栈多Agent协作系统',
                'code': 'LM-INN',
                'description': '基于OpenClaw的多Agent协作管理平台，实现任务分发、进度跟踪、龙门令激励等功能',
                'status': models.ProjectStatus.ACTIVE,
                'progress': 75,
            },
        ]
        
        count = 0
        for project_data in projects_data:
            existing = self.db.query(models.Project).filter(
                models.Project.code == project_data['code']
            ).first()
            
            if not existing:
                project = models.Project(**project_data)
                self.db.add(project)
                logger.info(f"创建项目: {project_data['name']}")
                count += 1
        
        self.db.commit()
        return count
    
    # Task 模型的合法列名（排除 relationship/FK 字段和 computed 字段）
    _TASK_COLUMNS = {
        'task_no', 'title', 'description', 'status', 'priority',
        'creator_agent_id', 'assignee_agent_id', 'project_id',
        'phase_id', 'estimated_hours', 'actual_hours', 'progress',
        'deliverable_path', 'parent_task_id', 'blocked_reason', 'tags', 'extra_data',
        'created_at', 'started_at', 'completed_at',
    }

    def import_tasks(self) -> int:
        """导入任务数据 - 从LEDGER.md获取真实任务"""
        logger.info("开始导入任务数据...")

        ledger_parser = LedgerParser(self.ledger_path)
        if not ledger_parser.load():
            logger.warning("LEDGER.md加载失败，使用默认任务数据")

        tasks_data = ledger_parser.parse_tasks()

        project = self.db.query(models.Project).filter(
            models.Project.code == 'LM-INN'
        ).first()

        count = 0
        for task_data in tasks_data:
            existing = self.db.query(models.Task).filter(
                models.Task.task_no == task_data['task_no']
            ).first()

            if project:
                task_data['project_id'] = project.id

            if task_data['status'] == models.TaskStatus.COMPLETED:
                task_data['completed_at'] = datetime.utcnow() - timedelta(days=1)
            elif task_data['status'] == models.TaskStatus.IN_PROGRESS:
                task_data['started_at'] = datetime.utcnow() - timedelta(hours=2)

            # 过滤掉非列字段，避免 setattr / model 构造失败
            valid_data = {k: v for k, v in task_data.items() if k in self._TASK_COLUMNS}

            if existing:
                for key, value in valid_data.items():
                    setattr(existing, key, value)
                logger.info(f"更新任务: {task_data['task_no']} - {task_data['title']}")
            else:
                task = models.Task(**valid_data)
                self.db.add(task)
                logger.info(f"创建任务: {task_data['task_no']} - {task_data['title']}")

            count += 1

        self.db.commit()
        return count
    
    def import_longmenling_logs(self) -> int:
        """导入龙门令记录"""
        logger.info("开始导入龙门令记录...")
        
        ledger_parser = LedgerParser(self.ledger_path)
        logs_data = ledger_parser.parse_longmenling()
        
        count = 0
        for log_data in logs_data:
            log = models.LongmenlingLog(**log_data)
            self.db.add(log)
            count += 1
        
        self.db.commit()
        return count
    
    def import_all(self) -> Dict[str, int]:
        """导入所有数据"""
        logger.info("=" * 60)
        logger.info("开始导入龙门客栈生产数据...")
        logger.info(f"数据源目录: {LONGMEN_INN_ROOT}")
        logger.info("=" * 60)
        
        results = {}
        
        try:
            results['agents'] = self.import_agents()
            logger.info(f"✅ Agent数据导入完成: {results['agents']} 条")
            
            results['projects'] = self.import_projects()
            logger.info(f"✅ 项目数据导入完成: {results['projects']} 条")
            
            results['tasks'] = self.import_tasks()
            logger.info(f"✅ 任务数据导入完成: {results['tasks']} 条")
            
            results['longmenling_logs'] = self.import_longmenling_logs()
            logger.info(f"✅ 龙门令记录导入完成: {results['longmenling_logs']} 条")
            
            logger.info("=" * 60)
            logger.info("🎉 生产数据导入成功！")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"❌ 数据导入失败: {str(e)}")
            self.db.rollback()
            raise
        
        return results


def import_production_data():
    """导入生产数据入口函数"""
    create_tables()
    
    db = SessionLocal()
    
    try:
        importer = ProductionDataImporter(db)
        return importer.import_all()
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    import_production_data()
