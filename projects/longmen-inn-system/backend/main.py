#!/usr/bin/env python3
"""
龙门客栈 - Agent 监控与项目管理系统
Backend: FastAPI + SQLite + WebSocket
"""

import json
import pathlib
import datetime
import asyncio
from contextlib import asynccontextmanager
from typing import List, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import aiosqlite

# ============ 配置 ============
DB_PATH = pathlib.Path(__file__).parent / "data" / "longmen_inn.db"
OCLAW_AGENTS = pathlib.Path.home() / ".openclaw" / "agents"

# 角色映射
ROLE_MAPPING = {
    "main": {"title": "老板娘", "dept": "总经办", "icon": "👩‍💼", "type": "manager"},
    "innkeeper": {"title": "大掌柜", "dept": "战略部", "icon": "🦊", "type": "manager"},
    "waiter": {"title": "店小二", "dept": "调度部", "icon": "🏃", "type": "support"},
    "chef": {"title": "厨子", "dept": "研发部", "icon": "👨‍🍳", "type": "developer"},
    "painter": {"title": "画师", "dept": "设计部", "icon": "🎨", "type": "designer"},
    "accountant": {"title": "账房先生", "dept": "质控部", "icon": "🧮", "type": "qa"},
    "storyteller": {"title": "说书先生", "dept": "文档部", "icon": "✍️", "type": "writer"},
}

# ============ 数据模型 ============
class Project(BaseModel):
    id: Optional[int] = None
    project_key: str
    name: str
    status: str = "active"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class Task(BaseModel):
    id: Optional[int] = None
    task_key: str
    project_id: int
    title: str
    description: Optional[str] = None
    assignee: str
    status: str = "todo"
    priority: str = "medium"
    skill_used: Optional[str] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None

class WorkLog(BaseModel):
    id: Optional[int] = None
    task_id: int
    agent_id: str
    log_type: str
    content: str
    tokens_used: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None

# ============ 数据库管理 ============
async def init_db():
    """初始化数据库"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # 项目表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_key TEXT UNIQUE,
                name TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                start_date TEXT,
                end_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 任务表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_key TEXT UNIQUE,
                project_id INTEGER,
                title TEXT NOT NULL,
                description TEXT,
                assignee TEXT,
                status TEXT DEFAULT 'todo',
                priority TEXT DEFAULT 'medium',
                skill_used TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id)
            )
        """)
        
        # 工作日志表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS work_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                agent_id TEXT,
                log_type TEXT,
                content TEXT,
                tokens_used INTEGER DEFAULT 0,
                start_time TEXT,
                end_time TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id) REFERENCES tasks(id)
            )
        """)
        
        await db.commit()
        print("✅ 数据库初始化完成")

# ============ FastAPI 应用 ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    await init_db()
    yield
    # 关闭时
    print("👋 应用关闭")

app = FastAPI(
    title="龙门客栈 - Agent 监控与项目管理系统",
    description="FastAPI + SQLite + WebSocket 实时监控系统",
    version="2.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
static_dir = pathlib.Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ============ API 路由 ============
@app.get("/", response_class=HTMLResponse)
async def root():
    """前端看板页面"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🏮 龙门客栈 - Agent 监控看板</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            backdrop-filter: blur(10px);
        }
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .stat-card h3 {
            font-size: 2.5rem;
            margin-bottom: 8px;
            color: #1890ff;
        }
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .agent-card {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .agent-header {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 20px;
        }
        .agent-icon {
            font-size: 48px;
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
        }
        .status-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }
        .status-active { background: rgba(82,196,26,0.2); color: #52c41a; }
        .status-idle { background: rgba(250,173,20,0.2); color: #faad14; }
        .status-offline { background: rgba(255,77,79,0.2); color: #ff4d4f; }
        .loading {
            text-align: center;
            padding: 60px;
            color: rgba(255,255,255,0.5);
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏮 龙门客栈</h1>
        <p>Agent 实时监控看板 - 各伙计工作状态一目了然</p>
    </div>
    
    <div class="stats-grid" id="