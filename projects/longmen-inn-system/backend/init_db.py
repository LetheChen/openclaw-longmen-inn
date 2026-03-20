#!/usr/bin/env python3
"""
龙门客栈 - 数据库初始化脚本
首次运行或重置数据库时使用

Usage:
    python init_db.py              # 初始化空数据库
    python init_db.py --seed       # 初始化并填充示例数据
    python init_db.py --reset      # 重置数据库（清空所有数据）
"""

import sqlite3
import pathlib
import argparse
from datetime import datetime

DB_PATH = pathlib.Path(__file__).parent / "data" / "longmen_inn.db"
SCHEMA_SQL = """
-- 项目表
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_key TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    start_date TEXT,
    end_date TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_key TEXT UNIQUE NOT NULL,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    assignee TEXT,
    reporter TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    completed_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Agent表
CREATE TABLE IF NOT EXISTS agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    status TEXT DEFAULT 'idle',
    current_task TEXT,
    last_active TEXT,
    longmen_points INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- 龙门令记录表
CREATE TABLE IF NOT EXISTS longmen_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id TEXT NOT NULL,
    points INTEGER NOT NULL,
    reason TEXT,
    task_key TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_longmen_agent ON longmen_records(agent_id);
"""

SEED_SQL = """
-- 示例项目
INSERT INTO projects (project_key, name, status, start_date) VALUES
('PROJ-001', '龙门客栈系统', 'active', '2026-01-01'),
('PROJ-002', '示例项目', 'planning', '2026-02-01');

-- 示例Agent
INSERT INTO agents (agent_id, name, role, status) VALUES
('main', '老板娘', '总控', 'idle'),
('innkeeper', '大掌柜', '战略', 'idle'),
('waiter', '店小二', '调度', 'idle'),
('chef', '厨子', '开发', 'idle'),
('painter', '画师', '设计', 'idle'),
('accountant', '账房先生', '质控', 'idle'),
('storyteller', '说书先生', '文档', 'idle');

-- 示例任务
INSERT INTO tasks (task_key, project_id, title, status, priority) VALUES
('TASK-001', 1, '搭建项目基础架构', 'completed', 'high'),
('TASK-002', 1, '设计数据库模型', 'completed', 'high'),
('TASK-003', 1, '实现任务管理API', 'completed', 'high'),
('TASK-004', 1, '完善项目文档', 'in_progress', 'medium');
"""

def init_db(seed: bool = False, reset: bool = False):
    """初始化数据库"""
    # 确保data目录存在
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # 如果是重置，删除现有数据库
    if reset and DB_PATH.exists():
        print(f"删除现有数据库: {DB_PATH}")
        DB_PATH.unlink()
    
    # 创建数据库连接
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 创建表结构
        print("创建数据库表结构...")
        cursor.executescript(SCHEMA_SQL)
        
        # 如果需要填充示例数据
        if seed:
            print("填充示例数据...")
            cursor.executescript(SEED_SQL)
        
        conn.commit()
        print(f"数据库初始化完成: {DB_PATH}")
        
        # 显示统计
        cursor.execute("SELECT COUNT(*) FROM projects")
        projects = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM tasks")
        tasks = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM agents")
        agents = cursor.fetchone()[0]
        
        print(f"统计: {projects}个项目, {tasks}个任务, {agents}个Agent")
        
    except Exception as e:
        conn.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="龙门客栈数据库初始化")
    parser.add_argument("--seed", action="store_true", help="填充示例数据")
    parser.add_argument("--reset", action="store_true", help="重置数据库")
    
    args = parser.parse_args()
    init_db(seed=args.seed, reset=args.reset)