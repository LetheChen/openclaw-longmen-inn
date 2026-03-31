"""
龙门客栈业务管理系统 - 数据库模型 (增强版)
===============================
作者: 厨子 (神厨小福贵)

数据模型定义，包含所有数据库表结构
支持项目阶段、任务依赖、Agent实时状态等
"""

from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Boolean, Float, JSON, Table
from sqlalchemy.orm import relationship

from app.db.base import Base


task_dependencies = Table(
    'task_dependencies',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True),
    Column('depends_on_task_id', Integer, ForeignKey('tasks.id'), primary_key=True)
)


class TaskStatus(str, PyEnum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, PyEnum):
    """任务优先级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class AgentStatus(str, PyEnum):
    """Agent状态"""
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ONLINE = "online"


class ProjectStatus(str, PyEnum):
    """项目状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectPhaseStatus(str, PyEnum):
    """项目阶段状态"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"


class AgentSessionStatus(str, PyEnum):
    """Agent会话状态 - 对接OpenClaw"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PROCESSING = "processing"
    WAITING = "waiting"


class ActivityType(str, PyEnum):
    """活动类型"""
    TASK_COMPLETED = "task_completed"           # 任务完成
    LOGIN = "login"                            # 登录
    LONGMENLING_ISSUED = "longmenling_issued"   # 龙门令发放


class Project(Base):
    """项目表"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    owner_agent_id = Column(String(50), ForeignKey("agents.agent_id"))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    progress = Column(Integer, default=0)
    extra_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    phases = relationship("ProjectPhase", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    owner = relationship("Agent", foreign_keys=[owner_agent_id])


class ProjectPhase(Base):
    """项目阶段表"""
    __tablename__ = "project_phases"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    status = Column(Enum(ProjectPhaseStatus), default=ProjectPhaseStatus.PLANNING)
    order = Column(Integer, default=0)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="phases")
    tasks = relationship("Task", back_populates="phase")


class Agent(Base):
    """Agent表"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    title = Column(String(50))
    motto = Column(Text)
    role_description = Column(Text)
    avatar_url = Column(String(255))
    status = Column(Enum(AgentStatus), default=AgentStatus.IDLE)
    session_status = Column(Enum(AgentSessionStatus), default=AgentSessionStatus.DISCONNECTED)
    longmenling = Column(Integer, default=0)
    level = Column(Integer, default=1)
    current_task_id = Column(Integer, ForeignKey("tasks.id"))
    last_heartbeat = Column(DateTime)
    openclaw_session_id = Column(String(100))
    workspace_path = Column(String(500))
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_agent_id", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.creator_agent_id", back_populates="creator")
    longmenling_logs = relationship("LongmenlingLog", back_populates="agent")
    current_task = relationship("Task", foreign_keys=[current_task_id])
    heartbeat_logs = relationship("AgentHeartbeat", back_populates="agent", cascade="all, delete-orphan")
    activities = relationship("AgentActivity", back_populates="agent", cascade="all, delete-orphan")


class AgentHeartbeat(Base):
    """Agent心跳记录表 - 对接OpenClaw"""
    __tablename__ = "agent_heartbeats"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), ForeignKey("agents.agent_id"), nullable=False)
    status = Column(Enum(AgentStatus), nullable=False)
    current_task_no = Column(String(50))
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    message = Column(Text)
    extra_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="heartbeat_logs")


class AgentActivity(Base):
    """Agent活动记录表"""
    __tablename__ = "agent_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), ForeignKey("agents.agent_id"), nullable=False, index=True)
    activity_type = Column(Enum(ActivityType), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    related_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    related_task_title = Column(String(200), nullable=True)
    extra_data = Column(JSON, default=dict)  # 存储额外信息，如龙门令数量等
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    agent = relationship("Agent")
    related_task = relationship("Task")


class Task(Base):
    """任务表"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    task_no = Column(String(50), unique=True, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    phase_id = Column(Integer, ForeignKey("project_phases.id"))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    creator_agent_id = Column(String(50), ForeignKey("agents.agent_id"))
    assignee_agent_id = Column(String(50), ForeignKey("agents.agent_id"))
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    progress = Column(Integer, default=0)
    deliverable_path = Column(String(500))
    parent_task_id = Column(Integer, ForeignKey("tasks.id"))
    blocked_reason = Column(Text)
    tags = Column(JSON)
    extra_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", back_populates="tasks")
    phase = relationship("ProjectPhase", back_populates="tasks")
    creator = relationship("Agent", foreign_keys=[creator_agent_id], back_populates="created_tasks")
    assignee = relationship("Agent", foreign_keys=[assignee_agent_id], back_populates="assigned_tasks")
    parent_task = relationship("Task", remote_side=[id], backref="sub_tasks")
    logs = relationship("TaskLog", back_populates="task", cascade="all, delete-orphan")
    dependencies = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.depends_on_task_id,
        backref="dependent_tasks"
    )


class LongmenlingLog(Base):
    """龙门令记录表"""
    __tablename__ = "longmenling_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(50), ForeignKey("agents.agent_id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    amount = Column(Integer, nullable=False)
    reason = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    agent = relationship("Agent", back_populates="longmenling_logs")
    task = relationship("Task")


class TaskLog(Base):
    """任务流转日志表"""
    __tablename__ = "task_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    from_status = Column(Enum(TaskStatus))
    to_status = Column(Enum(TaskStatus))
    operator_agent_id = Column(String(50), ForeignKey("agents.agent_id"))
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    task = relationship("Task", back_populates="logs")


class DataCollectionJob(Base):
    """数据采集任务表"""
    __tablename__ = "data_collection_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(50))
    source_path = Column(String(500))
    target_table = Column(String(50))
    schedule = Column(String(100))
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    status = Column(String(20), default="active")
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_level_by_longmenling(longmenling: int) -> int:
    """根据龙门令积分获取等级"""
    if longmenling >= 5000:
        return 6
    elif longmenling >= 2500:
        return 5
    elif longmenling >= 1000:
        return 4
    elif longmenling >= 500:
        return 3
    elif longmenling >= 100:
        return 2
    else:
        return 1


def get_level_name(level: int) -> str:
    """获取等级名称"""
    level_names = {
        1: "新手伙计",
        2: "熟练工",
        3: "老师傅",
        4: "大管家",
        5: "传奇掌柜",
        6: "龙门传说"
    }
    return level_names.get(level, "未知等级")
