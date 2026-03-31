# 龙门客栈 - Git工作流程指南

> 本地开发数据与GitHub代码分离的最佳实践

## 核心原则

**本地数据不上传，代码模板公开**

- `longmen_inn.db` - 本地业务数据，保留在本地，不提交
- `node_modules/` - 依赖目录，通过 `npm install` 恢复
- `MEMORY_LOG.md` - 个人工作记忆，可选择是否上传

---

## 📁 目录结构

```
.longmen_inn/
├── .gitignore              # 排除本地数据
├── README.md               # 项目说明
├── LICENSE                 # MIT许可证
├── INN_RULES.md           # 客栈总规
├── LEDGER.md              # 任务看板（由 DB 导出，纯展示用途）
├── roles/                  # 角色定义
│   └── */MEMORY_LOG.md    # 工作记忆（可选排除）
├── projects/
│   └── longmen-inn-system/
│       ├── backend/
│       │   ├── data/          # 数据目录（已排除）
│       │   ├── init_db.py     # 数据库初始化脚本
│       │   └── requirements.txt
│       └── frontend/
│           └── package.json
├── scripts/
│   ├── pre-upload-check.ps1   # 上传前检查
│   └── backup-local.ps1       # 本地数据备份
└── backups/                    # 本地备份目录（已排除）
```

---

## 🚀 首次上传GitHub

### 步骤1：备份本地数据

```powershell
# 进入项目目录
cd .longmen_inn

# 运行备份脚本
.\projects\longmen-inn-system\backup-local.ps1 backup
```

### 步骤2：初始化Git

```powershell
# 初始化
git init

# 检查将要提交的文件
git status

# 添加所有文件（.gitignore会自动排除）
git add .

# 确认排除的文件未被添加
git status
```

### 步骤3：创建首次提交

```powershell
git commit -m "Initial commit: Longmen Inn multi-agent collaboration system

- Multi-agent role-based collaboration framework
- FastAPI backend with SQLite
- React frontend dashboard
- Task management and龙泉令 point system

Features:
- 7 agent roles with clear responsibilities
- INN_RULES.md for collaboration rules
- LEDGER.md for task tracking
- Memory and context management"
```

### 步骤4：推送GitHub

```powershell
# 创建GitHub仓库后
git remote add origin https://github.com/YOUR_USERNAME/longmen-inn.git
git branch -M main
git push -u origin main
```

---

## 🔄 日常开发流程

### 开始工作前

```powershell
# 拉取最新代码
git pull origin main

# 恢复依赖
cd projects/longmen-inn-system/frontend
npm install

cd ../backend
pip install -r requirements.txt
```

### 开发完成后

```powershell
# 备份本地数据
.\projects\longmen-inn-system\backup-local.ps1 backup

# 提交代码
git add .
git commit -m "feat: 添加新功能"

# 推送
git push origin main
```

### 克隆项目（其他开发者）

```powershell
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/longmen-inn.git
cd longmen-inn

# 安装依赖
cd projects/longmen-inn-system/frontend
npm install

cd ../backend
pip install -r requirements.txt

# 初始化数据库
python init_db.py --seed
```

---

## 🛡️隐私设置（可选）

### 选项1：完全公开

适合开源项目，所有文件上传。

### 选项2：排除个人记忆

在`.gitignore`中取消注释：

```gitignore
# 排除个人工作记忆
roles/*/MEMORY_LOG.md
```

### 选项3：排除任务看板

LEDGER.md 现由数据库实时导出（`inn ledger generate`），不包含本地开发数据，通常可以提交。

如需排除：

```gitignore
# 排除任务看板
LEDGER.md
```

---

## 📋 常用命令速查

| 操作 | 命令 |
|------|------|
| 备份数据 | `.\backup-local.ps1 backup` |
| 恢复数据 | `.\backup-local.ps1 restore` |
| 清理旧备份 | `.\backup-local.ps1 clean` |
| 上传前检查 | `.\pre-upload-check.ps1` |
| 初始化数据库 | `python init_db.py --seed` |
| 重置数据库 | `python init_db.py --reset` |
| **列出任务** | `cd backend && python -m app.cli task list [--status=pending]` |
| **创建任务** | `python -m app.cli task create --title="xxx" --assignee=chef` |
| **更新状态** | `python -m app.cli task status <id> completed` |
| **导出账本** | `python -m app.cli ledger generate` |

---

## ⚠️ 注意事项

1. **永远不要提交数据库文件** - 已在`.gitignore`中排除
2. **上传前运行检查脚本** - `.\scripts\pre-upload-check.ps1`
3. **定期备份本地数据** - 每次重大更新前后
4. **敏感信息脱敏** - 检查MEMORY_LOG.md；LEDGER.md 由 DB 导出，通常不含敏感本地数据
5. **任务操作** - 通过 `python -m app.cli task ...` 或 API（`POST /tasks/`）写入 DB，不要直接编辑 LEDGER.md

---

## 🔧 问题排查

### Q: git status 显示数据库文件？
A: 运行 `git rm --cached *.db` 然后重新 `git add .`

### Q: node_modules 被追踪了？
A: 运行 `git rm -r --cached node_modules`

### Q: 想恢复某个文件的历史版本？
A: 运行 `git checkout HEAD~1 -- path/to/file`

---

**版本**: v2.0
**更新日期**: 2026-03-31