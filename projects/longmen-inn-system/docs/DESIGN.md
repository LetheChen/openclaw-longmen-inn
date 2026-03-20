# 龙门客栈业务管理系统 - 设计文档

## 1. 系统概述

### 1.1 项目背景
基于 OpenClaw 多 Agent 协作平台，构建"龙门客栈"业务管理系统，将软件开发流程隐喻为古代客栈运营，实现 7 个角色（大掌柜、店小二、厨子、账房先生、说书先生、画师、老板娘）的协作管理。

### 1.2 核心功能
1. **Agent 管理** - 7 个角色的配置、监控、调度
2. **项目管理** - 项目创建、进度跟踪、资源分配
3. **任务管理** - 任务派发、流转、审核、归档
4. **龙门令排行榜** - 功勋积分、等级晋升、排行榜
5. **OpenClaw 服务** - Gateway 状态、会话管理、消息路由

## 2. 系统架构

### 2.1 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | React 18 + TypeScript + Vite + Zustand | 现代化前端架构 |
| UI 组件 | Ant Design 5.x | 企业级 UI 组件库 |
| 可视化 | ECharts / D3.js | 图表、数据可视化 |
| 后端 | Python 3.9+ + FastAPI | 高性能异步 Web 框架 |
| 数据库 | SQLite (开发) / PostgreSQL (生产) | 关系型数据库 |
| 缓存 | Redis | 会话、任务队列缓存 |
| 任务队列 | Celery | 异步任务处理 |
| 实时通信 | WebSocket | 实时数据推送 |
| 容器化 | Docker + Docker Compose | 部署运维 |

### 2.2 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户界面层 (Frontend)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │ 实时看板  │  │ 任务管理  │  │ Agent管理 │  │ 龙门令排行榜     │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────────────┐ │
│  │ 项目管理  │  │ 消息中心  │  │ OpenClaw服务监控              │ │
│  └──────────┘  └──────────┘  └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP / WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API 服务层 (Backend)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Agent服务  │  │  任务服务   │  │      项目服务           │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ 龙门令服务  │  │  消息服务   │  │   OpenClaw集成服务     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL / Redis / Celery
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        数据持久层 (Storage)                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │PostgreSQL│  │  Redis   │  │  SQLite  │  │   文件存储       │  │
│  │(主数据库)│  │(缓存队列)│  │(开发环境)│  │ (文档/图片等)    │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ API / WebSocket
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OpenClaw 服务层 (External)                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │  Gateway │  │  Agent   │  │ Session  │  │   Message      │  │
│  │  网关服务 │  │  管理服务 │  │ 会话管理  │  │   消息路由      │  │
│  └──────────┘  └──────────┘  └──────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.3 数据模型

#### 2.3.1 核心实体关系

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│   Project   │───────│    Task     │───────│    Agent    │
│   项目       │  1:N  │    任务      │  N:1  │    Agent    │
└─────────────┘       └──────┬──────┘       └─────────────┘
                             │
                             │ 1:N
                             ▼
                      ┌─────────────┐
                      │    Log      │
                      │   任务日志   │
                      └─────────────┘
```

#### 2.3.2 数据库表结构

```sql
-- 项目表
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'active', -- active, paused, completed, archived
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agent 表
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR(50) UNIQUE NOT NULL, -- innkeeper, waiter, chef, etc.
    name VARCHAR(50) NOT NULL,
    title VARCHAR(50), -- 称号
    motto TEXT, -- 信条
    role_description TEXT,
    avatar_url VARCHAR(255),
    status VARCHAR(20) DEFAULT 'idle', -- idle, busy, offline
    longmenling INTEGER DEFAULT 0, -- 龙门令积分
    level INTEGER DEFAULT 1, -- 等级
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 任务表
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_no VARCHAR(50) UNIQUE NOT NULL, -- T-20250321-001
    project_id INTEGER,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    creator_agent_id VARCHAR(50), -- 创建者
    assignee_agent_id VARCHAR(50), -- 执行者
    status VARCHAR(20) DEFAULT 'pending', -- pending, in_progress, reviewing, completed, blocked, cancelled
    priority VARCHAR(20) DEFAULT 'medium', -- low, medium, high, urgent
    estimated_hours INTEGER,
    actual_hours INTEGER,
    deliverable_path VARCHAR(500), -- 产出物路径
    parent_task_id INTEGER, -- 父任务ID，支持子任务
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assignee_agent_id) REFERENCES agents(agent_id)
);

-- 龙门令记录表
CREATE TABLE longmenling_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR(50) NOT NULL,
    task_id INTEGER,
    amount INTEGER NOT NULL, -- 获得或扣除的龙门令数量
    reason VARCHAR(200), -- 原因
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- 任务流转日志表
CREATE TABLE task_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    from_status VARCHAR(20),
    to_status VARCHAR(20),
    operator_agent_id VARCHAR(50),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);

-- OpenClaw 服务配置表
CREATE TABLE openclaw_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gateway_url VARCHAR(255) DEFAULT 'http://localhost:8080',
    api_key VARCHAR(255),
    ws_url VARCHAR(255) DEFAULT 'ws://localhost:8080/ws',
    status VARCHAR(20) DEFAULT 'disconnected', -- connected, disconnected, error
    last_connected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE system_configs (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT,
    description VARCHAR(255),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 插入默认配置
INSERT INTO system_configs (key, value, description) VALUES
('system_name', '龙门客栈业务管理系统', '系统名称'),
('version', '1.0.0', '系统版本'),
('task_number_prefix', 'T-', '任务编号前缀'),
('auto_assign_enabled', 'true', '是否启用自动分配'),
('default_task_priority', 'medium', '默认任务优先级');

-- 插入默认 Agent 数据
INSERT INTO agents (agent_id, name, title, motto, role_description, avatar_url) VALUES
('innkeeper', '大掌柜', '诸葛掌柜', '不谋全局者，不足谋一域', '洞察先机，定夺方向。出PRD，定技术栈。情报搜集、市场调研、需求分析、战略决策、技术选型、PRD输出', '/avatars/innkeeper.png'),
('waiter', '店小二', '快手阿贵', '客官，您要的热乎任务来喽！楼上楼下，开工咧！', '承上启下，跑腿调度。拆任务，跟进度，催流程。接收PRD、任务拆解、设置优先级、预估工时、分配任务、跟踪进度、协调资源', '/avatars/waiter.png'),
('chef', '厨子', '神厨小福贵', '给我一个需求，还你一段优雅的代码；给我一个Bug，我debug到天亮。', '灶上功夫，代码实现。接任务，写代码，解Bug。编码实现、单元测试、调试修复、代码提交、完成任务', '/avatars/chef.png'),
('accountant', '账房先生', '铁算盘老方', '账目不清，犹如暗夜行舟；代码不审，必致大厦将倾。', '查验稽核，记账发赏。审代码，记工分（龙门令），管交付。代码审查、质量验收、记录龙门令、汇总交付', '/avatars/accountant.png'),
('storyteller', '说书先生', '妙笔生花', '文以载道，字以传神。好的文档能让代码获得生命，好的故事能让产品深入人心。', '妙笔生花，记录传承。写文档，编报告，润文案。文档撰写、内容创作、报告编写、文案润色、品牌传播', '/avatars/storyteller.png'),
('painter', '画师', '墨染先生', '设计并非外观如何，而是如何运作。——史蒂夫·乔布斯', '视觉转化，体验塑造。画界面，定规范，出原型。UI/UX设计、原型制作、视觉规范、设计交付', '/avatars/painter.png'),
('main', '老板娘', '凤老板', '客栈上下，事无巨细，皆在我心。诸位安心做事，后方有我。', '总揽全局，查缺补漏。做协调，管应急，控全场。总控、协调、兜底、对外接口', '/avatars/main.png');

-- 插入示例项目
INSERT INTO projects (name, description, status) VALUES
('龙门客栈业务管理系统', '基于 OpenClaw 的多 Agent 协作管理平台', 'active'),
('AI 编程助手市场调研', '调研 AI 编程助手市场趋势，输出 PRD', 'completed'),
('用户登录模块开发', '实现用户注册、登录、JWT 鉴权功能', 'active');

-- 插入示例任务
INSERT INTO tasks (task_no, project_id, title, description, creator_agent_id, assignee_agent_id, status, priority, estimated_hours, deliverable_path) VALUES
('T-20250321-001', 2, '调研 AI 编程助手市场趋势', '调研 Cursor、GitHub Copilot、Codeium 等产品，分析市场趋势，输出 PRD', 'main', 'innkeeper', 'completed', 'high', 8, 'deliverables/prd/ai-coding-assistant-prd.md'),
('T-20250322-001', 3, '拆解用户登录模块开发任务', '将 PRD 拆解为具体任务卡，评估工时，分配给厨子和画师', 'innkeeper', 'waiter', 'in_progress', 'high', 4, NULL),
('T-20250322-002', 3, '实现登录 API /auth/login', '实现用户登录接口，包含 JWT 鉴权', 'waiter', 'chef', 'pending', 'medium', 6, NULL),
('T-20250322-003', 3, '设计登录页面 UI', '设计登录页面的视觉稿，包含交互状态', 'waiter', 'painter', 'pending', 'medium', 4, NULL);

-- 插入示例龙门令记录
INSERT INTO longmenling_logs (agent_id, task_id, amount, reason, description) VALUES
('innkeeper', 1, 50, '完成市场调研PRD', '高质量完成 AI 编程助手市场调研，输出详细 PRD'),
('waiter', 2, 20, '任务拆解中', '正在积极拆解用户登录模块任务'),
('chef', NULL, 10, '代码审查通过', '登录模块代码一次通过静态扫描'),
('accountant', NULL, 15, '严格代码审查', '在审查中发现并指出关键问题');

-- 更新 Agent 龙门令积分
UPDATE agents SET longmenling = 120 WHERE agent_id = 'innkeeper';
UPDATE agents SET longmenling = 85 WHERE agent_id = 'waiter';
UPDATE agents SET longmenling = 200 WHERE agent_id = 'chef';
UPDATE agents SET longmenling = 60 WHERE agent_id = 'accountant';
UPDATE agents SET longmenling = 45 WHERE agent_id = 'storyteller';
UPDATE agents SET longmenling = 30 WHERE agent_id = 'painter';
UPDATE agents SET longmenling = 0 WHERE agent_id = 'main';

-- 插入示例任务日志
INSERT INTO task_logs (task_id, from_status, to_status, operator_agent_id, comment) VALUES
(1, 'pending', 'in_progress', 'innkeeper', '开始调研 AI 编程助手市场'),
(1, 'in_progress', 'completed', 'innkeeper', '完成调研，输出 PRD'),
(2, 'pending', 'in_progress', 'waiter', '开始拆解用户登录模块任务');
