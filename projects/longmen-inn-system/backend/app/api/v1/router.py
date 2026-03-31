"""
龙门客栈业务管理系统 - API路由
===============================
作者: 厨子 (神厨小福贵)
"""

from fastapi import APIRouter

from app.api.v1.endpoints import agents, projects, tasks, longmenling, openclaw, data, files, auth, agent_workspace, daily_reports

api_router = APIRouter()

# 认证路由（无需认证）
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])

# 业务路由（可能需要认证）
api_router.include_router(agents.router, prefix="/agents", tags=["Agent管理"])
api_router.include_router(projects.router, prefix="/projects", tags=["项目管理"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["任务管理"])
api_router.include_router(longmenling.router, prefix="/longmenling", tags=["龙门令"])
api_router.include_router(openclaw.router, prefix="/openclaw", tags=["OpenClaw服务"])
api_router.include_router(data.router, prefix="/data", tags=["数据管理"])
api_router.include_router(files.router, prefix="/files", tags=["文件管理"])

# Agent工作空间路由（新增）
api_router.include_router(agent_workspace.router, tags=["Agent工作空间"])

# 客栈情报路由
api_router.include_router(daily_reports.router, prefix="/intelligence", tags=["客栈情报"])
