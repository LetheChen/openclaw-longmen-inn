"""
龙门客栈业务管理系统 - Agent管理API
===============================
作者: 厨子 (神厨小福贵)

提供Agent的CRUD操作、状态管理、配置更新等功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db import models
from app.schemas import agent as agent_schema

router = APIRouter()


@router.get("/", response_model=List[agent_schema.AgentResponse])
async def get_agents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    level: Optional[int] = Query(None, ge=1, le=6, description="按等级筛选")
):
    """
    获取Agent列表
    
    支持分页、状态筛选、等级筛选
    """
    query = db.query(models.Agent)
    
    # 应用筛选条件
    if status:
        query = query.filter(models.Agent.status == status)
    if level:
        query = query.filter(models.Agent.level == level)
    
    # 分页
    agents = query.offset(skip).limit(limit).all()
    
    return agents


@router.get("/statistics")
async def get_agent_statistics(db: Session = Depends(get_db)):
    """获取 Agent 汇总统计信息"""
    total = db.query(models.Agent).count()
    offline = db.query(models.Agent).filter(models.Agent.status == models.AgentStatus.OFFLINE).count()
    busy = db.query(models.Agent).filter(models.Agent.status == models.AgentStatus.BUSY).count()
    idle = db.query(models.Agent).filter(models.Agent.status == models.AgentStatus.IDLE).count()
    online = total - offline  # 由于没有 ONLINE 状态，在线数等于非离线数量
    return {
        "total": total,
        "online": online,
        "offline": offline,
        "busy": busy,
        "idle": idle,
    }


@router.get("/online", response_model=List[agent_schema.AgentResponse])
async def get_online_agents(db: Session = Depends(get_db)):
    """获取在线（非离线）Agent 列表"""
    agents = db.query(models.Agent).filter(models.Agent.status != models.AgentStatus.OFFLINE).all()
    return agents


@router.get("/activities")
async def get_agent_activities(
    db: Session = Depends(get_db),
    agent_id: Optional[str] = Query(None, description="过滤指定 Agent 的活动"),
    type: Optional[str] = Query(None, description="过滤类型（保留）"),
    limit: int = Query(20, ge=1, le=100, description="返回条数")
):
    """获取 Agent 活动日志（简化实现）"""
    from app.db import models as _models
    from sqlalchemy import desc
    logs = db.query(_models.TaskLog).order_by(desc(_models.TaskLog.created_at)).limit(limit).all()

    activities = []
    for log in logs:
        task = getattr(log, "task", None)
        agent = None
        if getattr(log, "operator_agent_id", None):
            agent = db.query(_models.Agent).filter(_models.Agent.agent_id == log.operator_agent_id).first()
        activities.append({
            "id": log.id,
            "agentId": log.operator_agent_id,
            "agentName": agent.name if agent else None,
            "agentAvatar": agent.avatar_url if agent else None,
            "type": getattr(log.to_status, "value", str(log.to_status)) if getattr(log, "to_status", None) is not None else "task_updated",
            "content": log.comment or (f"{getattr(task, 'title', '')}" if task else ""),
            "relatedTaskId": getattr(log, "task_id", None),
            "relatedTaskTitle": getattr(task, "title", None) if task else None,
            "metadata": {},
            "createdAt": log.created_at.isoformat() if log.created_at else None,
        })
    return activities


@router.get("/me", response_model=agent_schema.AgentResponse)
async def get_my_agent(db: Session = Depends(get_db)):
    """获取当前（示意）Agent 信息，未集成认证时返回第一个 Agent 作为占位"""
    agent = db.query(models.Agent).first()
    if not agent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="没有找到 Agent")
    return agent


@router.get("/{agent_id}", response_model=agent_schema.AgentDetailResponse)
async def get_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """
    获取Agent详情
    
    包含基本信息、统计数据、最近任务等
    """
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' 不存在"
        )
    
    # 获取统计数据
    from sqlalchemy import func
    
    # 任务统计
    task_stats = db.query(
        models.Task.status,
        func.count(models.Task.id).label('count')
    ).filter(
        models.Task.assignee_agent_id == agent_id
    ).group_by(models.Task.status).all()
    
    # 最近任务
    recent_tasks = db.query(models.Task).filter(
        models.Task.assignee_agent_id == agent_id
    ).order_by(models.Task.created_at.desc()).limit(5).all()
    
    # 龙门令记录
    recent_longmenling = db.query(models.LongmenlingLog).filter(
        models.LongmenlingLog.agent_id == agent_id
    ).order_by(models.LongmenlingLog.created_at.desc()).limit(10).all()
    
    # 构建响应
    result = {
        **agent.__dict__,
        "task_statistics": {stat.status: stat.count for stat in task_stats},
        "recent_tasks": recent_tasks,
        "recent_longmenling_logs": recent_longmenling
    }
    
    return result


@router.post("/", response_model=agent_schema.AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_in: agent_schema.AgentCreate,
    db: Session = Depends(get_db)
):
    """
    创建新Agent
    """
    # 检查 agent_id 是否已存在
    existing = db.query(models.Agent).filter(
        models.Agent.agent_id == agent_in.agent_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent ID '{agent_in.agent_id}' 已存在"
        )
    
    # 创建新Agent
    agent = models.Agent(**agent_in.dict())
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return agent


@router.put("/{agent_id}", response_model=agent_schema.AgentResponse)
async def update_agent(
    agent_id: str,
    agent_in: agent_schema.AgentUpdate,
    db: Session = Depends(get_db)
):
    """
    更新Agent信息
    """
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' 不存在"
        )
    
    # 更新字段
    update_data = agent_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)
    
    # 自动更新等级
    if 'longmenling' in update_data:
        agent.level = models.get_level_by_longmenling(agent.longmenling)
    
    db.commit()
    db.refresh(agent)
    
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: Session = Depends(get_db)
):
    """
    删除Agent
    
    注意：删除前请确保该Agent没有未完成的任务
    """
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' 不存在"
        )
    
    # 检查是否有未完成的任务
    active_tasks = db.query(models.Task).filter(
        models.Task.assignee_agent_id == agent_id,
        models.Task.status.in_(["pending", "in_progress", "reviewing"])
    ).count()
    
    if active_tasks > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent '{agent_id}' 还有 {active_tasks} 个未完成的任务，请先处理或转移"
        )
    
    db.delete(agent)
    db.commit()


@router.post("/{agent_id}/status", response_model=agent_schema.AgentResponse)
async def update_agent_status(
    agent_id: str,
    status_update: agent_schema.AgentStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    更新Agent状态
    
    用于手动设置Agent状态（空闲/忙碌/离线）
    """
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' 不存在"
        )
    
    # 检查状态转换是否合法
    if status_update.status == models.AgentStatus.BUSY and agent.status == models.AgentStatus.BUSY:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent '{agent_id}' 已经是忙碌状态"
        )
    
    # 如果要设置为忙碌，检查是否有足够的理由
    if status_update.status == models.AgentStatus.BUSY:
        # 这里可以添加更多的业务逻辑检查
        pass
    
    # 如果要设置为离线，检查是否有未完成的任务
    if status_update.status == models.AgentStatus.OFFLINE:
        active_tasks = db.query(models.Task).filter(
            models.Task.assignee_agent_id == agent_id,
            models.Task.status.in_(["in_progress", "reviewing"])
        ).count()
        
        if active_tasks > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent '{agent_id}' 还有 {active_tasks} 个进行中的任务，无法设置为离线"
            )
    
    agent.status = status_update.status
    db.commit()
    db.refresh(agent)
    
    return agent


@router.get("/{agent_id}/tasks", response_model=list)
async def get_agent_tasks(
    agent_id: str,
    db: Session = Depends(get_db),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    """
    获取Agent的任务列表
    """
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' 不存在"
        )
    
    query = db.query(models.Task).filter(models.Task.assignee_agent_id == agent_id)
    
    if status:
        query = query.filter(models.Task.status == status)
    
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    
    return tasks


@router.get("/stats/overview", response_model=dict)
async def get_agents_overview(
    db: Session = Depends(get_db)
):
    """
    获取Agent总体统计
    
    返回所有Agent的汇总统计数据
    """
    from sqlalchemy import func
    
    # 总Agent数
    total_agents = db.query(models.Agent).count()
    
    # 各状态Agent数
    status_counts = db.query(
        models.Agent.status,
        func.count(models.Agent.id).label('count')
    ).group_by(models.Agent.status).all()
    
    # 各等级Agent数
    level_counts = db.query(
        models.Agent.level,
        func.count(models.Agent.id).label('count')
    ).group_by(models.Agent.level).all()
    
    # 总龙门令
    total_longmenling = db.query(func.sum(models.Agent.longmenling)).scalar() or 0
    
    # 平均龙门令
    avg_longmenling = db.query(func.avg(models.Agent.longmenling)).scalar() or 0
    
    return {
        "total_agents": total_agents,
        "status_distribution": {stat.status: stat.count for stat in status_counts},
        "level_distribution": {lvl.level: lvl.count for lvl in level_counts},
        "total_longmenling": int(total_longmenling),
        "average_longmenling": round(float(avg_longmenling), 2),
        "top_agents": db.query(models.Agent).order_by(
            models.Agent.longmenling.desc()
        ).limit(5).all()
    }
