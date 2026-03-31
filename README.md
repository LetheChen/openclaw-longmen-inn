# 龙门客栈

> **OpenClaw 多 Agent 协作系统** | 基于角色协作的 AI 智能体协同平台

[![GitHub stars](https://img.shields.io/github/stars/LetheChen/openclaw-longmen-inn?style=social)](https://github.com/LetheChen/openclaw-longmen-inn/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LetheChen/openclaw-longmen-inn?style=social)](https://github.com/LetheChen/openclaw-longmen-inn/network/members)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**关键词**: OpenClaw | 多Agent协作 | AI自动化 | 智能体 | Agent系统 | Python | React | TypeScript

---

## 项目介绍

**龙门客栈** 是一个新颖的多 Agent 协作系统，灵感来自中国古典客栈的运营模式。通过角色分工和协作约束，实现 AI Agent 之间的高效协同。

### 为什么选择龙门客栈

- **角色分工明确**：每个 Agent 都有专职角色，职责清晰互不越界
- **规则驱动协作**：通过 INN_RULES.md 定义协作规则，防止越权预警
- **可视化看板**：LEDGER.md 作为任务看板，实时追踪所有项目进展
- **开箱即用**：系统提供完整的功能预设，上手即用
- **OpenClaw 原生**：充分利用 OpenClaw Agent 框架能力

### 落地场景

| 场景 | 说明 |
|------|------|
| 多角色协作项目 | 角色协同完成任务 |
| AI Agent 研究 | 探索多 Agent 协作实现 |
| 工作流自动化 | 可视化任务追踪管理 |
| 任务看板管理 | 类似 Trello 的看板视图 |

## 项目结构

```
.longmen_inn/
INN_RULES.md          # 客栈总规则（协作规范）
LEDGER.md             # 任务看板（项目追踪）
roles/                # 角色定义目录
  main/               # 东家（总控）
  innkeeper/          # 掌柜（任务规划）
  waiter/             # 店小二（任务执行）
  chef/               # 大厨（内容创作）
  painter/            # 画师（UI设计）
  accountant/         # 账房先生（财务开支）
  storyteller/        # 说书人（知识输出）
projects/             # 项目目录
  longmen-inn-system/
    backend/          # FastAPI后端
    frontend/         # React前端
scripts/              # 工具脚本
```

## 角色介绍

| 角色 | 职责 | 协作边界 |
|------|------|----------|
| 东家 | 总控·协调分配任务 | 不干预伙计具体工作 |
| 掌柜 | 任务规划与进度把控 | 不直接执行具体事务 |
| 店小二 | 任务执行与信息收集 | 不越级汇报或擅自决策 |
| 大厨 | 内容创作与方案输出 | 不修改产品逻辑 |
| 画师 | UI设计与原型输出 | 不参与代码实现 |
| 账房先生 | 财务开支·成本把控 | 账目透明不可篡改 |
| 说书人 | 故事编写·知识沉淀 | 内容基于已有素材 |

## 快速开始

### 环境要求

| 依赖 | 版本 | 下载地址 |
|------|------|----------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| Git | 最新 | https://git-scm.com/ |

### 一键启动

```powershell
# 1. 克隆仓库
git clone https://github.com/your-username/longmen-inn.git
cd longmen-inn/projects/longmen-inn-system

# 2. 运行启动脚本
.\start-services.ps1
```

### 手动启动

```powershell
# 后端
cd backend
pip install -r requirements.txt
python init_db.py --seed
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端
cd frontend
npm install
npm run dev
```

### 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:8080 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |

## 技术架构

| 技术 | 名称 | 版本 |
|------|------|------|
| 后端框架 | FastAPI | 0.104+ |
| 前端框架 | React | 18+ |
| UI组件库 | Ant Design | 5.x |
| 状态管理 | Zustand | 4.x |
| 数据库 | SQLite / PostgreSQL | - |
| 实时通讯 | WebSocket | - |

## 相关链接

- [OpenClaw官方文档](https://docs.openclaw.ai)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [ClawHub官方平台](https://clawhub.com)

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 开源协议

本项目采用 MIT 开源协议 - 详见 [LICENSE](LICENSE) 文件

---

**版本**: v1.0  
**维护者**: Lethe  
**Star? 请给项目加注星标关注最新动态**