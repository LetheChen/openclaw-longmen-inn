"""
龙门客栈业务管理系统 - 任务管理API
===============================
作者: 厨子 (神厨小福贵)

提供任务的CRUD操作、状态管理等功能
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.api.deps import get_db, get_current_user, get_current_user_required
from app.db import models
from app.models.user import User
from app.schemas import task as task_schema

router = APIRouter()


@router.get("/")
async def get_tasks(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    project_id: Optional[int] = Query(None, description="项目ID筛选"),
    assignee_agent_id: Optional[str] = Query(None, description="被分配者Agent ID筛选"),
    creator_agent_id: Optional[str] = Query(None, description="创建者Agent ID筛选"),
    status: Optional[models.TaskStatus] = Query(None, description="状态筛选"),
    priority: Optional[models.TaskPriority] = Query(None, description="优先级筛选")
):
    """
    获取任务列表
    
    支持分页、多条件筛选
    """
    query = db.query(models.Task).options(
        joinedload(models.Task.creator),
        joinedload(models.Task.assignee),
        joinedload(models.Task.project)
    )
    
    if project_id:
        query = query.filter(models.Task.project_id == project_id)
    if assignee_agent_id:
        query = query.filter(models.Task.assignee_agent_id == assignee_agent_id)
    if creator_agent_id:
        query = query.filter(models.Task.creator_agent_id == creator_agent_id)
    if status:
        query = query.filter(models.Task.status == status)
    if priority:
        query = query.filter(models.Task.priority == priority)
    
    total = query.count()
    
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    
    task_list = []
    for task in tasks:
        task_dict = {
            "id": task.id,
            "task_no": task.task_no,
            "title": task.title,
            "description": task.description,
            "status": task.status.value if task.status else "pending",
            "priority": task.priority.value if task.priority else "medium",
            "project_id": task.project_id,
            "project_name": task.project.name if task.project else None,
            "creator_agent_id": task.creator_agent_id,
            "creator_name": task.creator.name if task.creator else None,
            "assignee_agent_id": task.assignee_agent_id,
            "assignee_name": task.assignee.name if task.assignee else None,
            "estimated_hours": task.estimated_hours,
            "actual_hours": task.actual_hours,
            "progress": task.progress or 0,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        }
        task_list.append(task_dict)
    
    return {
        "data": task_list,
        "total": total,
        "page": (skip // limit) + 1,
        "pageSize": limit
    }


@router.get("/statistics")
async def get_task_statistics(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """获取任务统计信息"""
    total = db.query(func.count(models.Task.id)).scalar() or 0
    pending = db.query(func.count(models.Task.id)).filter(
        models.Task.status == models.TaskStatus.PENDING
    ).scalar() or 0
    in_progress = db.query(func.count(models.Task.id)).filter(
        models.Task.status == models.TaskStatus.IN_PROGRESS
    ).scalar() or 0
    reviewing = db.query(func.count(models.Task.id)).filter(
        models.Task.status == models.TaskStatus.REVIEWING
    ).scalar() or 0
    completed = db.query(func.count(models.Task.id)).filter(
        models.Task.status == models.TaskStatus.COMPLETED
    ).scalar() or 0
    blocked = db.query(func.count(models.Task.id)).filter(
        models.Task.status == models.TaskStatus.BLOCKED
    ).scalar() or 0
    
    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "review": reviewing,
        "completed": completed,
        "blocked": blocked,
    }


@router.get("/kanban")
async def get_kanban_data(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """获取看板数据"""
    def get_tasks_by_status(status):
        return db.query(models.Task).filter(
            models.Task.status == status
        ).order_by(models.Task.created_at.desc()).all()
    
    return {
        "pending": get_tasks_by_status(models.TaskStatus.PENDING),
        "inProgress": get_tasks_by_status(models.TaskStatus.IN_PROGRESS),
        "review": get_tasks_by_status(models.TaskStatus.REVIEWING),
        "completed": get_tasks_by_status(models.TaskStatus.COMPLETED),
    }


@router.get("/my")
async def get_my_tasks(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[models.TaskStatus] = Query(None)
):
    """获取当前用户的任务（按创建者Agent过滤）"""
    # 获取用户关联的Agent ID（通过 username 匹配 agent_id）
    user_agent = db.query(models.Agent).filter(models.Agent.agent_id == current_user.username).first()
    
    query = db.query(models.Task)
    
    # 按创建者Agent过滤（返回用户作为创建者的任务）
    if user_agent:
        query = query.filter(models.Task.creator_agent_id == user_agent.agent_id)
    
    if status:
        query = query.filter(models.Task.status == status)
    
    total = query.count()
    tasks = query.order_by(models.Task.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "data": tasks,
        "total": total,
        "page": (skip // limit) + 1,
        "pageSize": limit,
    }


@router.get("/{task_id}", response_model=task_schema.TaskDetailResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    获取任务详情
    
    包含完整信息：关联项目、创建者、被分配者、父任务、子任务、操作日志等
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )
    
    return task


@router.post("/", response_model=task_schema.TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: task_schema.TaskCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    创建任务
    
    自动生成任务编号，创建初始任务日志
    """
    # 检查任务编号是否已存在
    existing = db.query(models.Task).filter(models.Task.task_no == task_in.task_no).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务编号 '{task_in.task_no}' 已存在"
        )
    
    # 检查项目是否存在
    if task_in.project_id:
        project = db.query(models.Project).filter(models.Project.id == task_in.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目 ID {task_in.project_id} 不存在"
            )
    
    # 检查创建者Agent是否存在
    creator = db.query(models.Agent).filter(models.Agent.agent_id == task_in.creator_agent_id).first()
    if not creator:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"创建者 Agent '{task_in.creator_agent_id}' 不存在"
        )
    
    # 检查被分配者Agent是否存在
    if task_in.assignee_agent_id:
        assignee = db.query(models.Agent).filter(models.Agent.agent_id == task_in.assignee_agent_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"被分配者 Agent '{task_in.assignee_agent_id}' 不存在"
            )
    
    # 检查父任务是否存在
    if task_in.parent_task_id:
        parent = db.query(models.Task).filter(models.Task.id == task_in.parent_task_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"父任务 ID {task_in.parent_task_id} 不存在"
            )
    
    # 创建任务
    task = models.Task(**task_in.dict())
    db.add(task)
    db.commit()
    db.refresh(task)
    
    # 创建初始任务日志
    task_log = models.TaskLog(
        task_id=task.id,
        from_status=None,
        to_status=task.status,
        operator_agent_id=task.creator_agent_id,
        comment="创建任务"
    )
    db.add(task_log)
    db.commit()
    
    return task


@router.put("/{task_id}", response_model=task_schema.TaskResponse)
async def update_task(
    task_id: int,
    task_in: task_schema.TaskUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    更新任务
    
    支持部分字段更新，自动记录变更日志
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )
    
    # 检查项目是否存在
    if task_in.project_id:
        project = db.query(models.Project).filter(models.Project.id == task_in.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目 ID {task_in.project_id} 不存在"
            )
    
    # 检查被分配者Agent是否存在
    if task_in.assignee_agent_id:
        assignee = db.query(models.Agent).filter(models.Agent.agent_id == task_in.assignee_agent_id).first()
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"被分配者 Agent '{task_in.assignee_agent_id}' 不存在"
            )
    
    # 检查父任务是否存在（且不能是自身）
    if task_in.parent_task_id:
        if task_in.parent_task_id == task_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="父任务不能是自身"
            )
        parent = db.query(models.Task).filter(models.Task.id == task_in.parent_task_id).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"父任务 ID {task_in.parent_task_id} 不存在"
            )
    
    # 更新字段
    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    删除任务
    
    注意：删除前请确保该任务没有子任务
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )
    
    # 检查是否有子任务
    sub_tasks = db.query(models.Task).filter(models.Task.parent_task_id == task_id).count()
    if sub_tasks > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该任务还有 {sub_tasks} 个子任务，请先删除或转移"
        )
    
    db.delete(task)
    db.commit()


@router.patch("/{task_id}/status", response_model=task_schema.TaskResponse)
async def update_task_status(
    task_id: int,
    status_update: task_schema.TaskStatusUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    更新任务状态
    
    自动记录状态变更日志，更新相关时间字段
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"任务 ID {task_id} 不存在"
        )
    
    old_status = task.status
    new_status = status_update.status
    
    # 检查状态是否变化
    if old_status == new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"任务已经是 '{new_status.value}' 状态"
        )
    
    # 更新任务状态
    task.status = new_status
    
    # 根据状态更新相关时间字段
    now = datetime.utcnow()
    if new_status == models.TaskStatus.IN_PROGRESS and not task.started_at:
        task.started_at = now
    elif new_status == models.TaskStatus.COMPLETED:
        task.completed_at = now
        # 计算实际工时（如果有开始时间）
        if task.started_at:
            # 计算从开始到完成的小时数
            delta = task.completed_at - task.started_at
            task.actual_hours = int(delta.total_seconds() / 3600)
    
    db.commit()
    db.refresh(task)
    
    # 获取当前用户关联的Agent ID
    operator_agent_id = current_user.username  # 使用用户名作为agent_id
    # 如果有对应的Agent记录，使用其agent_id
    user_agent = db.query(models.Agent).filter(models.Agent.agent_id == current_user.username).first()
    if user_agent:
        operator_agent_id = user_agent.agent_id
    
    # 创建任务日志
    task_log = models.TaskLog(
        task_id=task.id,
        from_status=old_status,
        to_status=new_status,
        operator_agent_id=operator_agent_id,
        comment=status_update.comment or f"状态变更: {old_status.value} -> {new_status.value}"
    )
    db.add(task_log)
    db.commit()
    
    return task
