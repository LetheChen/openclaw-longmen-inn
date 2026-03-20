# 龙门客栈系统 - 快速启动指南

> 多Agent协作系统前端后端

## 环境要求

| 依赖 | 版本 | 安装方式 |
|------|------|----------|
| Python | 3.10+ | https://www.python.org/downloads/ |
| Node.js | 18+ | https://nodejs.org/ |
| pip | 最新 | `python -m pip install --upgrade pip` |

---

## 🚀 快速启动

### 方式一：一键启动（推荐）

```powershell
# Windows PowerShell
cd longmen-inn-system
.\start-services.ps1
```

首次运行会自动：
1. 检查依赖
2. 安装npm包
3. 初始化数据库
4. 启动前后端服务

### 方式二：手动启动

```powershell
# 1. 安装后端依赖
cd backend
pip install -r requirements.txt

# 2. 初始化数据库
python init_db.py --seed

# 3. 启动后端
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 4. 新开终端，安装前端依赖
cd ../frontend
npm install

# 5. 启动前端
npm run dev
```

---

## 📍 访问地址

| 服务 | 地址 |
|------|------|
| 前端界面 | http://localhost:8080 |
| 后端API | http://localhost:8000 |
| API文档 | http://localhost:8000/docs |
| API调试 | http://localhost:8000/redoc |

---

## 🛑 停止服务

```powershell
# 方式一：关闭启动窗口

# 方式二：运行停止脚本
.\stop-services.ps1

# 方式三：手动终止
# 后端: Ctrl+C 在后端终端
# 前端: Ctrl+C 在前端终端
```

---

## 📁 项目结构

```
longmen-inn-system/
├── backend/                  # FastAPI后端
│   ├── app/
│   │   └── main.py          # 主入口
│   ├── data/                 # 数据目录
│   │   └── longmen_inn.db    # SQLite数据库
│   ├── init_db.py            # 数据库初始化
│   └── requirements.txt      # Python依赖
│
├── frontend/                 # React前端
│   ├── src/
│   ├── public/
│   ├── package.json          # npm依赖
│   └── vite.config.ts        # Vite配置
│
├── start-services.ps1        # 一键启动
├── stop-services.ps1         # 一键停止
└── README.md                 # 本文件
```

---

## 🔧 常见问题

### Q: 端口被占用怎么办？

```powershell
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8080

# 终止占用进程（替换PID）
Stop-Process -Id <PID> -Force
```

### Q: 数据库初始化失败？

```powershell
# 重置数据库
cd backend
python init_db.py --reset
python init_db.py --seed
```

### Q: 前端启动报错？

```powershell
# 清除缓存重装
cd frontend
Remove-Item -Recurse node_modules
Remove-Item package-lock.json
npm install
```

### Q: pip安装太慢？

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 🔌 API接口

### 项目管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/projects` | 获取所有项目 |
| POST | `/api/projects` | 创建项目 |
| GET | `/api/projects/{id}` | 获取单个项目 |
| PUT | `/api/projects/{id}` | 更新项目 |
| DELETE | `/api/projects/{id}` | 删除项目 |

### 任务管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks` | 获取所有任务 |
| POST | `/api/tasks` | 创建任务 |
| GET | `/api/tasks/{id}` | 获取单个任务 |
| PUT | `/api/tasks/{id}` | 更新任务 |
| DELETE | `/api/tasks/{id}` | 删除任务 |

### Agent管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/agents` | 获取所有Agent |
| GET | `/api/agents/{id}` | 获取单个Agent |
| PUT | `/api/agents/{id}` | 更新Agent状态 |

---

## 🧪 测试

```powershell
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

---

## 📝 开发环境配置

### VS Code 推荐插件

- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- TypeScript Vue Plugin (Volar)

### 调试配置

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Backend",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["app.main:app", "--reload"],
      "cwd": "${workspaceFolder}/backend"
    }
  ]
}
```

---

**版本**: v1.0  
**更新日期**: 2026-03-20