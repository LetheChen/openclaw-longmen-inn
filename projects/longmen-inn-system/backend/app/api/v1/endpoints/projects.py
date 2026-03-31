"""
龙门客栈业务管理系统 - 项目管理API
===============================
作者: 厨子 (神厨小福贵)

提供项目的CRUD操作、统计等功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user_required
from app.db import models
from app.models.user import User
from app.schemas import project as project_schema

router = APIRouter()


@router.get("/")
async def get_projects(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
    status: Optional[models.ProjectStatus] = Query(None, description="按状态筛选")
):
    """
    获取项目列表
    
    支持分页、状态筛选
    """
    query = db.query(models.Project)
    
    # 应用筛选条件
    if status:
        query = query.filter(models.Project.status == status)
    
    # 获取总数
    total = query.count()
    
    # 分页
    projects = query.order_by(models.Project.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "data": projects,
        "total": total,
        "page": (skip // limit) + 1,
        "pageSize": limit
    }


@router.get("/{project_id}", response_model=project_schema.ProjectDetailResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    获取项目详情
    
    包含基本信息、统计信息和最近任务
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 ID {project_id} 不存在"
        )
    
    # 获取任务统计
    task_stats = db.query(
        models.Task.status,
        func.count(models.Task.id).label('count')
    ).filter(
        models.Task.project_id == project_id
    ).group_by(models.Task.status).all()
    
    # 统计各状态任务数
    total_tasks = 0
    pending_tasks = 0
    in_progress_tasks = 0
    completed_tasks = 0
    
    for stat in task_stats:
        total_tasks += stat.count
        if stat.status == models.TaskStatus.PENDING:
            pending_tasks = stat.count
        elif stat.status == models.TaskStatus.IN_PROGRESS:
            in_progress_tasks = stat.count
        elif stat.status == models.TaskStatus.COMPLETED:
            completed_tasks = stat.count
    
    # 最近任务
    recent_tasks = db.query(models.Task).filter(
        models.Task.project_id == project_id
    ).order_by(models.Task.created_at.desc()).limit(10).all()
    
    # 构建响应
    result = {
        **project.__dict__,
        "statistics": {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks
        },
        "recent_tasks": recent_tasks
    }
    
    return result


@router.post("/", response_model=project_schema.ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: project_schema.ProjectCreate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    创建项目
    """
    # 检查项目名称是否已存在
    existing = db.query(models.Project).filter(
        models.Project.name == project_in.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"项目名称 '{project_in.name}' 已存在"
        )
    
    # 创建新项目
    project = models.Project(**project_in.dict())
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.put("/{project_id}", response_model=project_schema.ProjectResponse)
async def update_project(
    project_id: int,
    project_in: project_schema.ProjectUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    更新项目
    
    支持部分字段更新
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 ID {project_id} 不存在"
        )
    
    # 检查新名称是否与其他项目冲突
    if project_in.name and project_in.name != project.name:
        existing = db.query(models.Project).filter(
            models.Project.name == project_in.name,
            models.Project.id != project_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"项目名称 '{project_in.name}' 已被其他项目使用"
            )
    
    # 更新字段
    update_data = project_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    db.commit()
    db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    """
    删除项目
    
    注意：会级联删除项目下的所有任务
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"项目 ID {project_id} 不存在"
        )
    
    # 检查是否有未完成的任务
    active_tasks = db.query(models.Task).filter(
        models.Task.project_id == project_id,
        models.Task.status.in_([
            models.TaskStatus.PENDING,
            models.TaskStatus.IN_PROGRESS,
            models.TaskStatus.REVIEWING
        ])
    ).count()
    
    if active_tasks > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"项目还有 {active_tasks} 个未完成的任务，请先处理或转移"
        )
    
    db.delete(project)
    db.commit()