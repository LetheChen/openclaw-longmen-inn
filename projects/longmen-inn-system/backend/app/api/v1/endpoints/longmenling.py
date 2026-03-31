"""
龙门客栈业务管理系统 - 龙门令系统API
===============================
作者: 厨子 (神厨小福贵)

龙门令（积分）的发放、查询、排行榜等功能
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.api.deps import get_db, get_current_user_required
from app.db import models
from app.models.user import User
from app.schemas import longmenling as longmenling_schema

router = APIRouter()


def _get_level_requirement(level: int) -> int:
    """获取升级到指定等级所需的积分"""
    requirements = {
        1: 0,
        2: 100,
        3: 500,
        4: 1000,
        5: 2500,
        6: 5000
    }
    return requirements.get(level, 5000)


@router.post("/", response_model=longmenling_schema.LongmenlingResponse, status_code=status.HTTP_201_CREATED)
async def create_longmenling(
    longmenling_in: longmenling_schema.LongmenlingCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    发放龙门令
    
    给指定Agent发放（或扣除）龙门令积分，自动更新Agent等级
    """
    # 检查Agent是否存在
    agent = db.query(models.Agent).filter(models.Agent.agent_id == longmenling_in.agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{longmenling_in.agent_id}' 不存在"
        )
    
    # 检查关联任务是否存在
    if longmenling_in.task_id:
        task = db.query(models.Task).filter(models.Task.id == longmenling_in.task_id).first()
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"任务 ID {longmenling_in.task_id} 不存在"
            )
    
    # 创建龙门令记录
    longmenling_log = models.LongmenlingLog(**longmenling_in.dict())
    db.add(longmenling_log)
    
    # 更新Agent的龙门令积分
    agent.longmenling += longmenling_in.amount
    
    # 自动更新Agent等级
    new_level = models.get_level_by_longmenling(agent.longmenling)
    if new_level != agent.level:
        agent.level = new_level
    
    db.commit()
    db.refresh(longmenling_log)
    
    return longmenling_log


@router.get("/ranking", response_model=longmenling_schema.LongmenlingRanking)
async def get_longmenling_ranking(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    top_n: int = Query(10, ge=1, le=100, description="返回前几名"),
    agent_id: Optional[str] = Query(None, description="查询指定Agent的排名")
):
    """
    获取龙门令排行榜
    
    返回龙门令积分排名，可选查询特定Agent的排名位置
    """
    # 获取所有Agent按龙门令积分排序
    all_agents = db.query(models.Agent).order_by(desc(models.Agent.longmenling)).all()
    
    # 构建排行榜项
    ranking_items = []
    my_rank = None
    
    for rank, agent in enumerate(all_agents, start=1):
        item = longmenling_schema.LongmenlingRankingItem(
            rank=rank,
            agent_id=agent.agent_id,
            name=agent.name,
            title=agent.title,
            avatar_url=agent.avatar_url,
            level=agent.level,
            longmenling=agent.longmenling
        )
        
        if rank <= top_n:
            ranking_items.append(item)
        
        # 记录查询Agent的排名
        if agent_id and agent.agent_id == agent_id:
            my_rank = item
    
    return longmenling_schema.LongmenlingRanking(
        total_count=len(all_agents),
        top_agents=ranking_items,
        my_rank=my_rank,
        generated_at=datetime.utcnow()
    )


@router.get("/{agent_id}", response_model=longmenling_schema.AgentLongmenlingDetail)
async def get_agent_longmenling_detail(
    agent_id: str,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    history_limit: int = Query(20, ge=1, le=100, description="历史记录数量")
):
    """
    获取Agent龙门令详情
    
    包含当前积分、等级、历史记录、排名等信息
    """
    # 检查Agent是否存在
    agent = db.query(models.Agent).filter(models.Agent.agent_id == agent_id).first()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent '{agent_id}' 不存在"
        )
    
    # 计算等级信息
    current_level = agent.level
    next_level = min(current_level + 1, 6)
    next_level_required = _get_level_requirement(next_level)
    points_to_next = max(0, next_level_required - agent.longmenling)
    
    # 获取历史记录统计
    total_earned = db.query(func.sum(models.LongmenlingLog.amount)).filter(
        models.LongmenlingLog.agent_id == agent_id,
        models.LongmenlingLog.amount > 0
    ).scalar() or 0
    
    total_spent = db.query(func.sum(models.LongmenlingLog.amount)).filter(
        models.LongmenlingLog.agent_id == agent_id,
        models.LongmenlingLog.amount < 0
    ).scalar() or 0
    total_spent = abs(total_spent)
    
    # 获取最近历史记录
    recent_history = db.query(models.LongmenlingLog).filter(
        models.LongmenlingLog.agent_id == agent_id
    ).order_by(models.LongmenlingLog.created_at.desc()).limit(history_limit).all()
    
    # 获取排名
    rank = db.query(func.count(models.Agent.id)).filter(
        models.Agent.longmenling > agent.longmenling
    ).scalar() + 1
    
    return longmenling_schema.AgentLongmenlingDetail(
        agent_id=agent.agent_id,
        name=agent.name,
        title=agent.title,
        avatar_url=agent.avatar_url,
        level=current_level,
        longmenling=agent.longmenling,
        next_level_required=next_level_required,
        points_to_next_level=points_to_next,
        total_earned=int(total_earned),
        total_spent=int(total_spent),
        recent_history=[
            longmenling_schema.LongmenlingHistoryItem(
                id=log.id,
                amount=log.amount,
                reason=log.reason,
                description=log.description,
                task_id=log.task_id,
                created_at=log.created_at
            ) for log in recent_history
        ],
        rank_in_all=rank,
        generated_at=datetime.utcnow()
    )