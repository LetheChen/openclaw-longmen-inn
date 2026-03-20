# 龙门客栈- 多Agent协作系统

> 一个基于角色分工的多Agent协作框架，灵感来自中国客栈文化。

## 🏘️ 项目简介

龙门客栈是一个创新的多Agent协作系统，通过角色分工和规则约束，实现AI Agent之间的高效协作。

### 核心特点

- **角色分工**：每个Agent有明确的职责边界（厨子编码、画师设计、账房先生质控...）
- **规则约束**：通过INN_RULES.md定义协作规则，避免越权干预
- **任务看板**：LEDGER.md作为中央任务看板，透明化任务状态
- **龙门令**：工作量积分系统，激励贡献

## 📂 项目结构

```
.longmen_inn/
├── INN_RULES.md          # 客栈总规（协作规则）
├── LEDGER.md             # 任务看板（中央协调）
├── .gitignore            # Git忽略规则
├── roles/                # 角色定义目录
│   ├── main/             # 老板娘（总控）
│   ├── innkeeper/        # 大掌柜（战略）
│   ├── waiter/           # 店小二（调度）
│   ├── chef/             # 厨子（开发）
│   ├── painter/          # 画师（设计）
│   ├── accountant/       # 账房先生（质控）
│   └── storyteller/      # 说书先生（文档）
├── projects/             # 项目代码
│   └── longmen-inn-system/
│       ├── backend/      # FastAPI后端
│       └── frontend/      # React前端
└── scripts/              # 辅助脚本
```

## 🎭 角色介绍

| 角色 | 职责 | 禁止事项 |
|------|------|----------|
| 老板娘 | 总控、协调、兜底 | 无事干预伙计工作 |
| 大掌柜 | 战略规划、需求分析 | 不插手具体编码 |
| 店小二 | 调度、进度跟踪 | 不做战略决策 |
| 厨子 | 编码、测试、调试 | 不修改产品需求 |
| 画师 | UI设计、原型制作 | 不干涉后端架构 |
| 账房先生 | 代码审查、质量把控 | 不直接写代码 |
| 说书先生 | 文档编写、知识管理 | 不参与需求决策 |

## 🚀 快速开始

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

# 2. 启动服务（自动安装依赖、初始化数据库）
.\start-services.ps1
```

首次运行会自动：
- ✅ 检查Python和Node.js环境
- ✅ 安装后端Python依赖
- ✅ 安装前端npm依赖
- ✅ 初始化SQLite数据库（含示例数据）
- ✅ 启动前后端服务

### 手动启动

```powershell
# 后端
cd backend
pip install -r requirements.txt
python init_db.py --seed          # 初始化数据库
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 前端（新终端）
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

## 📸 界面截图

### Dashboard看板
![Dashboard](./screenshots/dashboard.png)

### 任务管理
![Tasks](./screenshots/tasks.png)

### Agent管理
![Agents](./screenshots/agents.png)

### 项目管理
![Projects](./screenshots/projects.png)

### 龙门令排行榜
![Ranking](./screenshots/ranking.png)

---

## 📖 文档

- [客栈总规](./INN_RULES.md) - 协作规则
- [角色定义](./roles/) - 各角色详细说明
- [API文档](./docs/api.md) - 后端API接口

## 🤝 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交Pull Request

## 📜 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- 灵感来源：中国传统客栈文化
- 技术支持：OpenClaw Agent Framework

---

**版本**: v1.0
**最后更新**: 2026年3月