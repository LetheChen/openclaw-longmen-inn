"""
龙门客栈业务管理系统 - Agent工作空间API路由
=====================================
作者: 老板娘 (凤老板)

Agent工作空间可视化相关API端点
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
import os

from app.schemas.agent_workspace import (
    AgentWorkspace,
    AgentRole,
    AgentStatus,
    AgentSummary,
    AgentListResponse,
    TaskInfo,
    ActivityRecord,
    WorkspaceFile,
)
from app.services.session_parser import session_parser

router = APIRouter(prefix="/agent-workspace", tags=["Agent工作空间"])


# Agent角色配置（从ROSTER.md解析或硬编码）
AGENT_ROLES = {
    "main": AgentRole(
        id="main",
        name="老板娘",
        title="凤老板",
        scene="内堂雅间",
        description="总揽全局，查缺补漏。做调度，管应急，控全场。",
        avatar="/assets/agents/avatars/main.png",
        scene_image="/assets/agents/scenes/main-room.png",
        motto="客栈上下，事无巨细，皆在我心。诸位安心做事，后方有我。",
        level=5
    ),
    "innkeeper": AgentRole(
        id="innkeeper",
        name="大掌柜",
        title="掌柜",
        scene="客房柜台",
        description="洞察先机，定夺方向。出PRD，定技术栈。",
        avatar="/assets/agents/avatars/innkeeper.png",
        scene_image="/assets/agents/scenes/counter.png",
        motto="凡事预则立，不预则废。",
        level=5
    ),
    "waiter": AgentRole(
        id="waiter",
        name="店小二",
        title="阿贵",
        scene="大堂茶座",
        description="承上启下，跑腿催办。拆任务，跟进度，催流程。",
        avatar="/assets/agents/avatars/waiter.png",
        scene_image="/assets/agents/scenes/hall.png",
        motto="客官需要什么？",
        level=3
    ),
    "chef": AgentRole(
        id="chef",
        name="厨子",
        title="李师傅",
        scene="后厨灶台",
        description="灶上功夫，代码实现。接任务，写代码，解Bug。",
        avatar="/assets/agents/avatars/chef.png",
        scene_image="/assets/agents/scenes/kitchen.png",
        motto="代码如烹饪，火候是关键。",
        level=4
    ),
    "accountant": AgentRole(
        id="accountant",
        name="账房先生",
        title="钱先生",
        scene="账房",
        description="查验稽核，记账发赏。审代码，记工分，管交付。",
        avatar="/assets/agents/avatars/accountant.png",
        scene_image="/assets/agents/scenes/accounting.png",
        motto="一分一厘，皆要清楚。",
        level=4
    ),
    "painter": AgentRole(
        id="painter",
        name="画师",
        title="墨先生",
        scene="画室",
        description="UI/UX设计、视觉转化、体验塑造、规范制定。",
        avatar="/assets/agents/avatars/painter.png",
        scene_image="/assets/agents/scenes/studio.png",
        motto="美，是设计的灵魂。",
        level=3
    ),
    "storyteller": AgentRole(
        id="storyteller",
        name="说书先生",
        title="文先生",
        scene="书房茶座",
        description="妙笔生花，记录传承。写文档，编报告，润文案。",
        avatar="/assets/agents/avatars/storyteller.png",
        scene_image="/assets/agents/scenes/library.png",
        motto="文字，是思想的载体。",
        level=3
    ),
}


def get_ledger_path() -> str:
    """获取LEDGER.md路径"""
    return os.path.expanduser("~/.openclaw/workspace/.longmen_inn/LEDGER.md")


def parse_ledger_tasks() -> dict:
    """解析LEDGER.md获取任务信息"""
    ledger_path = get_ledger_path()
    tasks = {
        "pending": [],
        "in_progress": [],
        "completed": []
    }
    
    if not os.path.exists(ledger_path):
        return tasks
    
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 简单解析任务表
        lines = content.split("\n")
        in_task_table = False
        
        for line in lines:
            if "| 任务号 |" in line:
                in_task_table = True
                continue
            
            if in_task_table and line.startswith("|"):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 5:
                    task_id = parts[1]
                    content_str = parts[2]
                    status_str = parts[3]
                    
                    if task_id.startswith("T-"):
                        status = "completed"
                        if "进行中" in status_str or "🔄" in status_str:
                            status = "in_progress"
                        elif "待开始" in status_str or "⏳" in status_str:
                            status = "pending"
                        elif "部分完成" in status_str or "⚠️" in status_str:
                            status = "in_progress"
                        
                        task = {
                            "id": task_id,
                            "content": content_str,
                            "status": status,
                            "priority": "high" if "🔴" in status_str else ("medium" if "🟡" in status_str else "low")
                        }
                        
                        if status == "in_progress":
                            tasks["in_progress"].append(task)
                        elif status == "pending":
                            tasks["pending"].append(task)
                        else:
                            tasks["completed"].append(task)
            
            if in_task_table and not line.startswith("|"):
                break
                
    except Exception as e:
        print(f"解析LEDGER失败: {e}")
    
    return tasks


@router.get("/", response_model=AgentListResponse)
async def list_agents():
    """
    获取所有Agent列表
    
    返回所有Agent的简要信息和状态统计
    """
    agents = []
    statistics = {
        "total": 0,
        "online": 0,
        "busy": 0,
        "idle": 0,
        "offline": 0
    }
    
    for agent_id, role in AGENT_ROLES.items():
        # 获取状态
        status_str = session_parser.get_agent_status(agent_id)
        status_map = {
            "busy": AgentStatus.BUSY,
            "idle": AgentStatus.IDLE,
            "offline": AgentStatus.OFFLINE
        }
        status = status_map.get(status_str, AgentStatus.OFFLINE)
        
        # 更新统计
        statistics["total"] += 1
        if status == AgentStatus.BUSY:
            statistics["busy"] += 1
            statistics["online"] += 1
        elif status == AgentStatus.IDLE:
            statistics["idle"] += 1
            statistics["online"] += 1
        else:
            statistics["offline"] += 1
        
        # 获取当前任务（从LEDGER）
        tasks = parse_ledger_tasks()
        current_task = None
        if tasks["in_progress"]:
            # 找到该Agent负责的任务
            for task in tasks["in_progress"]:
                if agent_id in task.get("assignee", "").lower():
                    current_task = task.get("content", "")
                    break
        
        agents.append(AgentSummary(
            agent_id=agent_id,
            name=role.name,
            title=role.title,
            status=status,
            scene=role.scene,
            level=role.level,
            longmenling=0,# TODO: 从龙门令系统获取
            current_task=current_task,
            last_active=datetime.now()  # TODO: 从会话获取
        ))
    
    return AgentListResponse(
        total=len(agents),
        agents=agents,
        statistics=statistics
    )


@router.get("/{agent_id}", response_model=AgentWorkspace)
async def get_agent_workspace(agent_id: str):
    """
    获取指定Agent的工作空间详情
    
    Args:
        agent_id: Agent ID (如 chef, main, innkeeper)
        
    Returns:
        Agent的完整工作空间信息
    """
    if agent_id not in AGENT_ROLES:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' 不存在")
    
    role = AGENT_ROLES[agent_id]
    
    # 获取状态
    status_str = session_parser.get_agent_status(agent_id)
    status_map = {
        "busy": AgentStatus.BUSY,
        "idle": AgentStatus.IDLE,
        "offline": AgentStatus.OFFLINE
    }
    status = status_map.get(status_str, AgentStatus.OFFLINE)
    
    # 获取任务
    tasks = parse_ledger_tasks()
    current_tasks = []
    pending_tasks = []
    completed_tasks = []
    
    for task in tasks["in_progress"]:
        # 简单匹配：如果assignee包含agent_id
        if agent_id in ["main", "innkeeper"] or agent_id in task.get("content", "").lower():
            current_tasks.append(TaskInfo(**task))
    
    for task in tasks["pending"]:
        pending_tasks.append(TaskInfo(**task))
    
    for task in tasks["completed"][:10]:  # 只显示最近10个已完成
        completed_tasks.append(TaskInfo(**task))
    
    # 获取活动记录
    activities_data = session_parser.get_recent_activities(agent_id, limit=20)
    recent_activities = [ActivityRecord(**a) for a in activities_data if a.get("type") == "activity"]
    
    # 获取工作空间文件
    files_data = session_parser.scan_workspace(agent_id)
    workspace_files = [WorkspaceFile(**f) for f in files_data]
    
    # 获取最后活跃时间
    sessions = session_parser.get_session_files(agent_id)
    last_active = None
    session_id = None
    session_start = None
    
    if sessions:
        try:
            last_active = datetime.fromtimestamp(sessions[0].stat().st_mtime)
            session_id = sessions[0].stem
            # TODO: 解析会话开始时间
        except:
            pass
    
    # 统计信息
    stats = {
        "task_completed": len(tasks["completed"]),
        "task_in_progress": len(current_tasks),
        "task_pending": len(pending_tasks),
        "activity_count": len(activities_data),
        "file_count": len(workspace_files)
    }
    
    return AgentWorkspace(
        role=role,
        status=status,
        current_tasks=current_tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        recent_activities=recent_activities,
        workspace_files=workspace_files,
        last_active=last_active,
        session_id=session_id,
        session_start=session_start,
        stats=stats
    )


@router.get("/{agent_id}/activities", response_model=List[ActivityRecord])
async def get_agent_activities(
    agent_id: str,
    limit: int = Query(default=50, ge=1, le=200, description="返回数量限制"),
    action_type: Optional[str] = Query(default=None, description="动作类型过滤"),
    session_id: Optional[str] = Query(default=None, description="指定会话ID")
):
    """
    获取Agent活动记录
    
    Args:
        agent_id: Agent ID
        limit: 返回数量限制
        action_type: 动作类型过滤 (message, tool_use, tool_result)
        session_id: 指定会话ID
        
    Returns:
        活动记录列表
    """
    if agent_id not in AGENT_ROLES:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' 不存在")
    
    activities_data = session_parser.get_recent_activities(
        agent_id,
        limit=limit,
        action_type=action_type,
        session_id=session_id
    )
    
    return [ActivityRecord(**a) for a in activities_data if a.get("type") == "activity"]


@router.get("/{agent_id}/tasks")
async def get_agent_tasks(
    agent_id: str,
    status: Optional[str] = Query(default=None, description="任务状态过滤")
):
    """
    获取Agent任务列表
    
    Args:
        agent_id: Agent ID
        status: 任务状态过滤 (pending, in_progress, completed)
        
    Returns:
        任务列表
    """
    if agent_id not in AGENT_ROLES:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' 不存在")
    
    tasks = parse_ledger_tasks()
    
    result = []
    if status == "pending":
        result = tasks["pending"]
    elif status == "in_progress":
        result = tasks["in_progress"]
    elif status == "completed":
        result = tasks["completed"]
    else:
        # 返回所有
        result = tasks["pending"] + tasks["in_progress"] + tasks["completed"]
    
    return result


@router.get("/{agent_id}/files")
async def get_agent_files(agent_id: str):
    """
    获取Agent工作空间文件列表
    
    Args:
        agent_id: Agent ID
        
    Returns:
        文件列表
    """
    if agent_id not in AGENT_ROLES:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' 不存在")
    
    files_data = session_parser.scan_workspace(agent_id)
    return [WorkspaceFile(**f) for f in files_data]