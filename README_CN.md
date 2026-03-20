# 龙门客栈 - 多Agent协作管理系统

## 项目简介

龙门客栈是一个基于OpenClaw框架的多Agent协作管理系统，灵感来自中国传统客栈文化。系统通过角色分工和规则约束，实现AI智能体之间的高效协作。

## 核心功能

- **多角色协作**：老板娘、大掌柜、店小二、厨子、画师、账房先生、说书先生等7个角色，各司其职
- **任务管理**：可视化任务看板，支持任务创建、分配、状态流转
- **龙门令积分**：工作量积分系统，量化贡献，激励团队
- **实时监控**：Agent状态实时展示，任务进度可视化
- **项目看板**：项目进度、统计数据一目了然

## 技术架构

### 后端技术栈
- Python 3.10+
- FastAPI（高性能Web框架）
- SQLite / PostgreSQL（数据库）
- WebSocket（实时通信）

### 前端技术栈
- React 18
- TypeScript
- Ant Design 5.x
- Zustand（状态管理）
- Vite（构建工具）

## 快速开始

```bash
# 克隆项目
git clone https://github.com/LetheChen/openclaw-longmen-inn.git

# 进入项目目录
cd openclaw-longmen-inn/projects/longmen-inn-system

# 一键启动（Windows）
.\start-services.ps1
```

## 功能截图

- Dashboard看板：系统总览、数据统计
- 任务管理：任务看板、状态流转
- Agent管理：智能体状态、角色配置
- 项目管理：项目列表、进度跟踪
- 龙门令排行榜：积分排名、贡献统计

## 适用场景

1. **软件开发团队**：多角色协作开发项目
2. **AI Agent研究**：多智能体协作实验平台
3. **任务管理系统**：可视化任务分配与跟踪
4. **敏捷开发看板**：类似Trello的任务管理

## 项目特色

- **角色分工明确**：每个Agent有清晰的职责边界
- **规则驱动协作**：通过规则文件定义协作流程
- **可视化看板**：任务状态透明化
- **积分激励系统**：量化贡献，激励团队
- **OpenClaw原生集成**：深度集成，开箱即用

## 开源协议

本项目采用MIT开源协议，欢迎学习和贡献代码。

## 相关链接

- GitHub仓库：https://github.com/LetheChen/openclaw-longmen-inn
- OpenClaw官网：https://openclaw.ai
- 问题反馈：https://github.com/LetheChen/openclaw-longmen-inn/issues

---

**关键词**：OpenClaw, 多Agent协作, AI智能体, 任务管理, 项目管理, FastAPI, React, TypeScript, Python, 敏捷开发, 团队协作, 角色分工, 工作流管理, Agent调度, 智能体协作, 多智能体系统