"""
龙门客栈业务管理系统 - 生产数据初始化
===============================
作者: 厨子 (神厨小福贵)

初始化龙门客栈多Agent开发过程中的实际生产数据
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db import models
from app.db.init_db import create_tables

logger = logging.getLogger(__name__)


def init_agents(db: Session):
    """初始化Agent数据"""
    agents_data = [
        {
            "agent_id": "innkeeper",
            "name": "老板娘",
            "title": "凤老板",
            "motto": "客官里边请，好酒好菜伺候着！",
            "role_description": "客栈总管，负责整体运营协调、客户接待、资源调配",
            "status": models.AgentStatus.IDLE,
            "longmenling": 3500,
            "level": 6
        },
        {
            "agent_id": "manager",
            "name": "大掌柜",
            "title": "诸葛掌柜",
            "motto": "事无巨细，皆在我心",
            "role_description": "项目管理专家，负责项目规划、进度跟踪、资源协调",
            "status": models.AgentStatus.IDLE,
            "longmenling": 2800,
            "level": 6
        },
        {
            "agent_id": "waiter",
            "name": "店小二",
            "title": "跑堂小二",
            "motto": "客官有什么吩咐？",
            "role_description": "服务支持，负责消息传递、任务分发、状态汇报",
            "status": models.AgentStatus.IDLE,
            "longmenling": 1200,
            "level": 4
        },
        {
            "agent_id": "chef",
            "name": "厨子",
            "title": "神厨小福贵",
            "motto": "代码如烹饪，火候要恰到好处",
            "role_description": "后端开发专家，负责API开发、数据库设计、系统架构",
            "status": models.AgentStatus.IDLE,
            "longmenling": 2100,
            "level": 5
        },
        {
            "agent_id": "accountant",
            "name": "账房先生",
            "title": "铁算盘老方",
            "motto": "一分一厘，清清楚楚",
            "role_description": "数据分析师，负责数据统计、报表生成、质量把控",
            "status": models.AgentStatus.IDLE,
            "longmenling": 1800,
            "level": 5
        },
        {
            "agent_id": "storyteller",
            "name": "说书先生",
            "title": "妙笔生花",
            "motto": "文字有灵，故事传情",
            "role_description": "文档专家，负责技术文档、API文档、用户手册编写",
            "status": models.AgentStatus.IDLE,
            "longmenling": 1500,
            "level": 5
        },
        {
            "agent_id": "painter",
            "name": "画师",
            "title": "墨染先生",
            "motto": "界面如画，用户体验为先",
            "role_description": "前端开发专家，负责UI设计、前端开发、用户交互",
            "status": models.AgentStatus.IDLE,
            "longmenling": 1600,
            "level": 5
        }
    ]
    
    for agent_data in agents_data:
        existing = db.query(models.Agent).filter(
            models.Agent.agent_id == agent_data["agent_id"]
        ).first()
        
        if not existing:
            agent = models.Agent(**agent_data)
            db.add(agent)
            logger.info(f"创建Agent: {agent_data['name']}")
    
    db.commit()
    return db.query(models.Agent).count()


def init_projects(db: Session):
    """初始化项目数据"""
    projects_data = [
        {
            "name": "龙门客栈多Agent协作系统",
            "description": "基于OpenClaw的多Agent协作管理平台，实现任务分发、进度跟踪、龙门令激励等功能",
            "status": models.ProjectStatus.ACTIVE
        },
        {
            "name": "龙门客栈前端看板",
            "description": "React + TypeScript + Ant Design实现的实时看板系统，包含任务看板、Agent管理、数据统计等功能",
            "status": models.ProjectStatus.ACTIVE
        },
        {
            "name": "龙门客栈后端API",
            "description": "FastAPI + SQLAlchemy实现的后端服务，提供RESTful API和WebSocket实时通信",
            "status": models.ProjectStatus.ACTIVE
        },
        {
            "name": "OpenClaw集成模块",
            "description": "与OpenClaw Gateway集成的服务模块，实现Agent心跳、会话管理、消息路由等功能",
            "status": models.ProjectStatus.ACTIVE
        }
    ]
    
    for project_data in projects_data:
        existing = db.query(models.Project).filter(
            models.Project.name == project_data["name"]
        ).first()
        
        if not existing:
            project = models.Project(**project_data)
            db.add(project)
            logger.info(f"创建项目: {project_data['name']}")
    
    db.commit()
    return db.query(models.Project).count()


def init_tasks(db: Session):
    """初始化任务数据"""
    tasks_data = [
        {
            "task_no": "LM-001",
            "title": "设计数据库模型",
            "description": "设计Agent、Task、Project、LongmenlingLog等核心数据模型",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.HIGH,
            "assignee_agent_id": "chef",
            "creator_agent_id": "manager",
            "estimated_hours": 8,
            "actual_hours": 6
        },
        {
            "task_no": "LM-002",
            "title": "实现Agent管理API",
            "description": "实现Agent的CRUD操作、状态管理、龙门令计算等API接口",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.HIGH,
            "assignee_agent_id": "chef",
            "creator_agent_id": "manager",
            "estimated_hours": 12,
            "actual_hours": 10
        },
        {
            "task_no": "LM-003",
            "title": "实现任务管理API",
            "description": "实现任务的创建、分配、状态流转、进度跟踪等功能",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.HIGH,
            "assignee_agent_id": "chef",
            "creator_agent_id": "manager",
            "estimated_hours": 16,
            "actual_hours": 14
        },
        {
            "task_no": "LM-004",
            "title": "实现WebSocket实时通信",
            "description": "实现WebSocket连接管理、消息广播、OpenClaw事件订阅等功能",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.HIGH,
            "assignee_agent_id": "chef",
            "creator_agent_id": "manager",
            "estimated_hours": 10,
            "actual_hours": 8
        },
        {
            "task_no": "LM-005",
            "title": "开发Dashboard看板页面",
            "description": "实现实时看板页面，包含统计卡片、任务看板、在线伙计展示等",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.HIGH,
            "assignee_agent_id": "painter",
            "creator_agent_id": "manager",
            "estimated_hours": 20,
            "actual_hours": 18
        },
        {
            "task_no": "LM-006",
            "title": "开发Agent管理页面",
            "description": "实现Agent列表、详情、状态管理、龙门令记录等功能页面",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.MEDIUM,
            "assignee_agent_id": "painter",
            "creator_agent_id": "manager",
            "estimated_hours": 16,
            "actual_hours": 12
        },
        {
            "task_no": "LM-007",
            "title": "开发OpenClaw服务管理页面",
            "description": "实现Gateway状态监控、会话管理、路由配置等功能页面",
            "status": models.TaskStatus.IN_PROGRESS,
            "priority": models.TaskPriority.HIGH,
            "assignee_agent_id": "painter",
            "creator_agent_id": "manager",
            "estimated_hours": 18
        },
        {
            "task_no": "LM-008",
            "title": "前后端接口联调",
            "description": "完成前后端API对接，实现真实数据展示和交互",
            "status": models.TaskStatus.IN_PROGRESS,
            "priority": models.TaskPriority.URGENT,
            "assignee_agent_id": "chef",
            "creator_agent_id": "manager",
            "estimated_hours": 12
        },
        {
            "task_no": "LM-009",
            "title": "编写API文档",
            "description": "编写完整的API文档，包含接口说明、请求示例、响应格式等",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.MEDIUM,
            "assignee_agent_id": "storyteller",
            "creator_agent_id": "manager",
            "estimated_hours": 8,
            "actual_hours": 6
        },
        {
            "task_no": "LM-010",
            "title": "编写系统架构文档",
            "description": "编写系统架构设计文档，包含技术选型、模块划分、数据流程等",
            "status": models.TaskStatus.COMPLETED,
            "priority": models.TaskPriority.MEDIUM,
            "assignee_agent_id": "storyteller",
            "creator_agent_id": "manager",
            "estimated_hours": 10,
            "actual_hours": 8
        },
        {
            "task_no": "LM-011",
            "title": "实现龙门令奖励机制",
            "description": "实现任务完成奖励、等级提升、排行榜等功能",
            "status": models.TaskStatus.REVIEWING,
            "priority": models.TaskPriority.MEDIUM,
            "assignee_agent_id": "accountant",
            "creator_agent_id": "manager",
            "estimated_hours": 8
        },
        {
            "task_no": "LM-012",
            "title": "实现数据统计报表",
            "description": "实现任务统计、Agent绩效、项目进度等数据报表",
            "status": models.TaskStatus.PENDING,
            "priority": models.TaskPriority.LOW,
            "assignee_agent_id": "accountant",
            "creator_agent_id": "manager",
            "estimated_hours": 12
        }
    ]
    
    project = db.query(models.Project).first()
    
    for task_data in tasks_data:
        existing = db.query(models.Task).filter(
            models.Task.task_no == task_data["task_no"]
        ).first()
        
        if not existing:
            task_dict = task_data.copy()
            if project:
                task_dict["project_id"] = project.id
            
            if task_data["status"] == models.TaskStatus.COMPLETED:
                task_dict["completed_at"] = datetime.utcnow() - timedelta(days=1)
            elif task_data["status"] == models.TaskStatus.IN_PROGRESS:
                task_dict["started_at"] = datetime.utcnow() - timedelta(hours=2)
            
            task = models.Task(**task_dict)
            db.add(task)
            logger.info(f"创建任务: {task_data['task_no']} - {task_data['title']}")
    
    db.commit()
    return db.query(models.Task).count()


def init_longmenling_logs(db: Session):
    """初始化龙门令记录"""
    logs_data = [
        {"agent_id": "chef", "amount": 200, "reason": "完成数据库模型设计"},
        {"agent_id": "chef", "amount": 300, "reason": "完成Agent管理API开发"},
        {"agent_id": "chef", "amount": 400, "reason": "完成任务管理API开发"},
        {"agent_id": "chef", "amount": 200, "reason": "完成WebSocket实现"},
        {"agent_id": "painter", "amount": 500, "reason": "完成Dashboard看板开发"},
        {"agent_id": "painter", "amount": 300, "reason": "完成Agent管理页面"},
        {"agent_id": "storyteller", "amount": 150, "reason": "完成API文档编写"},
        {"agent_id": "storyteller", "amount": 200, "reason": "完成架构文档编写"},
        {"agent_id": "accountant", "amount": 100, "reason": "数据统计功能开发中"},
    ]
    
    for log_data in logs_data:
        log = models.LongmenlingLog(**log_data)
        db.add(log)
    
    db.commit()
    return db.query(models.LongmenlingLog).count()


def init_production_data():
    """初始化所有生产数据"""
    logger.info("=" * 60)
    logger.info("开始初始化龙门客栈生产数据...")
    logger.info("=" * 60)
    
    create_tables()
    
    db = SessionLocal()
    
    try:
        agents_count = init_agents(db)
        logger.info(f"✅ Agent数据初始化完成，共 {agents_count} 条")
        
        projects_count = init_projects(db)
        logger.info(f"✅ 项目数据初始化完成，共 {projects_count} 条")
        
        tasks_count = init_tasks(db)
        logger.info(f"✅ 任务数据初始化完成，共 {tasks_count} 条")
        
        logs_count = init_longmenling_logs(db)
        logger.info(f"✅ 龙门令记录初始化完成，共 {logs_count} 条")
        
        logger.info("=" * 60)
        logger.info("🎉 生产数据初始化成功！")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 数据初始化失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    init_production_data()
