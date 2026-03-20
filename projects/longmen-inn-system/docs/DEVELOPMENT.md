# 龙门客栈业务管理系统 - 开发指南

> 🏮 文档版本: v1.0.0 | 最后更新: 2026-03-15

## 📚 目录

- [开发环境搭建](#开发环境搭建)
- [代码规范](#代码规范)
- [Git工作流](#git工作流)
- [提交信息规范](#提交信息规范)
- [分支管理策略](#分支管理策略)
- [代码审查流程](#代码审查流程)

---

## 开发环境搭建

### 前提条件

确保您的系统已安装以下软件：

- **Python** 3.9 或更高版本
- **Node.js** 18 或更高版本
- **Git** 2.30 或更高版本
- **Docker** (可选，用于数据库和缓存)

### 环境检查

```bash
# 检查Python版本
python --version

# 检查Node.js版本
node --version
npm --version

# 检查Git版本
git --version
```

### 项目克隆与初始化

#### 1. 克隆项目仓库

```bash
# 克隆主仓库
git clone https://github.com/your-org/longmen-inn-system.git

# 进入项目目录
cd longmen-inn-system
```

#### 2. 初始化后端环境

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 3. 初始化前端环境

```bash
# 进入前端目录
cd ../frontend

# 安装依赖（使用pnpm推荐）
pnpm install

# 或使用npm
npm install
```

#### 4. 配置环境变量

```bash
# 后端环境配置
cd ../backend
cp .env.example .env

# 编辑 .env 文件，配置数据库连接等信息
# vim .env
```

### 数据库设置

#### 方式一：使用SQLite（开发环境推荐）

```bash
# SQLite配置已在 .env 中默认启用
# DATABASE_URL=sqlite:///./longmen_inn.db

# 初始化数据库
python scripts/init_db.py
```

#### 方式二：使用PostgreSQL + Docker

```bash
# 启动PostgreSQL容器
docker run -d \
  --name longmen-postgres \
  -e POSTGRES_DB=longmen_inn_db \
  -e POSTGRES_USER=longmen_user \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15-alpine

# 更新 .env 文件
# DATABASE_URL=postgresql://longmen_user:your_password@localhost:5432/longmen_inn_db

# 执行迁移
alembic upgrade head

# 初始化数据
python scripts/init_data.py
```

### 启动开发服务器

#### 启动后端服务

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate  # Windows

# 启动开发服务器
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 服务将在 http://localhost:8000 启动
# API文档 http://localhost:8000/docs
```

#### 启动前端服务

```bash
cd frontend

# 启动开发服务器
npm run dev
# 或
pnpm dev

# 服务将在 http://localhost:5173 启动
```

### 验证安装

1. **后端API**: 访问 http://localhost:8000/docs 查看Swagger文档
2. **前端应用**: 访问 http://localhost:5173 查看前端界面
3. **数据库**: 使用DBeaver或pgAdmin连接到数据库验证表结构

---

## 代码规范

### Python代码规范

#### 风格指南

项目遵循 **PEP 8** 风格指南，并采用以下附加规则：

- **行长度**: 最大100字符
- **缩进**: 使用4个空格（禁止使用Tab）
- **引号**: 优先使用双引号
- **导入排序**: 标准库 > 第三方库 > 本地模块

#### 代码示例

```python
"""
龙门客栈业务管理系统 - Agent服务
===============================
提供Agent的CRUD操作、状态管理、配置更新等功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db import models
from app.schemas import agent as agent_schema


router = APIRouter()


@router.get("/", response_model=List[agent_schema.AgentResponse])
async def get_agents(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=500, description="返回记录数"),
) -> List[agent_schema.AgentResponse]:
    """
    获取Agent列表
    
    支持分页、状态筛选、等级筛选
    """
    query = db.query(models.Agent)
    agents = query.offset(skip).limit(limit).all()
    return agents
```

#### 文档字符串规范

使用 **Google风格** 文档字符串：

```python
def process_payment(order_id: int, amount: float, method: str = "alipay") -> dict:
    """
    处理订单支付
    
    Args:
        order_id: 订单ID
        amount: 支付金额
        method: 支付方式，可选值：alipay, wechat, card
        
    Returns:
        包含支付结果的字典
        {
            "success": bool,
            "transaction_id": str,
            "message": str
        }
        
    Raises:
        OrderNotFoundError: 订单不存在
        PaymentFailedError: 支付处理失败
        InvalidAmountError: 金额无效
    """
    pass
```

### TypeScript/JavaScript代码规范

#### 风格指南

项目使用 **ESLint + Prettier** 进行代码规范检查：

- **缩进**: 2个空格
- **行长度**: 最大120字符
- **分号**: 必需
- **引号**: 单引号

#### React组件示例

```typescript
/**
 * Agent卡片组件
 * 
 * 展示Agent基本信息、状态和等级
 */
import React, { useCallback } from 'react';
import { Card, Avatar, Tag, Space, Progress } from 'antd';
import { UserOutlined, TrophyOutlined } from '@ant-design/icons';
import type { Agent } from '@/types/agent';
import styles from './AgentCard.module.less';

interface AgentCardProps {
  /** Agent数据 */
  agent: Agent;
  /** 是否选中 */
  selected?: boolean;
  /** 点击回调 */
  onClick?: (agent: Agent) => void;
  /** 更多操作回调 */
  onMore?: (agent: Agent) => void;
}

export const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  selected = false,
  onClick,
  onMore,
}) => {
  const handleClick = useCallback(() => {
    onClick?.(agent);
  }, [agent, onClick]);

  const getStatusColor = (status: Agent['status']): string => {
    const colorMap: Record<Agent['status'], string> = {
      idle: 'green',
      busy: 'blue',
      offline: 'default',
    };
    return colorMap[status];
  };

  const getStatusText = (status: Agent['status']): string => {
    const textMap: Record<Agent['status'], string> = {
      idle: '空闲',
      busy: '忙碌',
      offline: '离线',
    };
    return textMap[status];
  };

  return (
    <Card
      className={`${styles.card} ${selected ? styles.selected : ''}`}
      onClick={handleClick}
      hoverable
    >
      <div className={styles.header}>
        <Avatar
          size={64}
          src={agent.avatar_url}
          icon={<UserOutlined />}
        />
        <div className={styles.info}>
          <h3 className={styles.name}>{agent.name}</h3>
          <span className={styles.title}>{agent.title}</span>
        </div>
        <Tag color={getStatusColor(agent.status)}>
          {getStatusText(agent.status)}
        </Tag>
      </div>

      <div className={styles.stats}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div className={styles.statItem}>
            <TrophyOutlined />
            <span>龙门令: {agent.longmenling}</span>
            <Tag color="gold">Lv.{agent.level}</Tag>
          </div>
          <Progress
            percent={(agent.longmenling % 100)}
            showInfo={false}
            strokeColor="#ffd700"
          />
        </Space>
      </div>

      <p className={styles.motto}>{agent.motto}</p>
    </Card>
  );
};

export default AgentCard;
```

---

## Git工作流

### 分支模型

项目采用 **Git Flow** 分支模型：

```
main        生产分支，始终可部署
  │
  ├── develop    开发分支，集成所有功能
  │     │
  │     ├── feature/*    功能分支
  │     │
  │     ├── release/*    发布分支
  │
  ├── hotfix/*   紧急修复分支
```

### 分支命名规范

| 分支类型 | 命名格式 | 示例 |
|----------|----------|------|
| 主分支 | `main` | `main` |
| 开发分支 | `develop` | `develop` |
| 功能分支 | `feature/<功能描述>` | `feature/agent-management` |
| 修复分支 | `fix/<问题描述>` | `fix/login-timeout` |
| 发布分支 | `release/<版本号>` | `release/1.2.0` |
| 热修复分支 | `hotfix/<描述>` | `hotfix/security-patch` |

### 工作流程

#### 1. 开始新功能开发

```bash
# 1. 确保本地develop分支是最新的
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/user-authentication

# 3. 开发功能并提交
# ... 编写代码 ...
git add .
git commit -m "feat(auth): 实现用户登录功能

- 添加JWT认证中间件
- 实现登录/登出接口
- 添加密码加密存储"

# 4. 推送到远程
git push origin feature/user-authentication
```

#### 2. 创建Pull Request

```bash
# 1. 确保分支是最新的
git checkout feature/user-authentication
git pull origin develop

# 2. 解决可能的冲突后推送
git push origin feature/user-authentication

# 3. 在GitHub/GitLab上创建Pull Request
# 目标分支: develop
# 填写PR模板，添加描述和截图
```

#### 3. 代码审查通过后合并

```bash
# 方式1: 在GitHub/GitLab上使用界面合并（推荐）
# - 使用 "Squash and merge"
# - 确保提交信息符合规范

# 方式2: 命令行合并
git checkout develop
git pull origin develop
git merge --no-ff feature/user-authentication -m "feat(auth): 合并用户认证功能

- 实现JWT认证
- 添加登录/登出功能"

# 删除已合并的功能分支
git branch -d feature/user-authentication
git push origin --delete feature/user-authentication
```

---

## 提交信息规范

项目采用 **Conventional Commits** 规范，提交信息必须遵循以下格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### 提交类型 (Type)

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(auth): 添加用户登录` |
| `fix` | 修复Bug | `fix(api): 修复任务状态更新错误` |
| `docs` | 文档更新 | `docs(readme): 更新部署说明` |
| `style` | 代码格式调整（不影响功能） | `style(lint): 修复代码格式` |
| `refactor` | 重构代码 | `refactor(models): 优化数据库模型` |
| `perf` | 性能优化 | `perf(api): 优化查询速度` |
| `test` | 添加测试 | `test(auth): 添加登录测试` |
| `chore` | 构建/工具链变动 | `chore(deps): 更新依赖版本` |
| `revert` | 回滚提交 | `revert: 回滚"feat(auth): 添加用户登录"` |

### 作用域 (Scope)

作用域表示提交影响的模块或组件：

| 作用域 | 说明 |
|--------|------|
| `api` | API接口 |
| `auth` | 认证授权 |
| `agent` | Agent管理 |
| `task` | 任务管理 |
| `project` | 项目管理 |
| `db` | 数据库 |
| `ui` | 用户界面 |
| `docs` | 文档 |
| `config` | 配置文件 |
| `deps` | 依赖 |

### 主题 (Subject)

- 使用**祈使句**，以动词开头
- 首字母**小写**
- 结尾**不加句号**
- 长度控制在50个字符以内

✅ 正确的示例:
- `feat(auth): 添加用户登录功能`
- `fix(api): 修复任务状态更新错误`
- `docs(readme): 更新API文档链接`

❌ 错误的示例:
- ~~`feat(auth): 添加了用户登录功能`~~ (使用了过去时)
- ~~`feat(auth): 添加用户登录功能。`~~ (结尾有句号)
- ~~`feat(auth): 添加用户登录`~~ (描述不完整)

### 正文 (Body)

当需要详细说明时，在主题后添加正文：

```
feat(auth): 实现JWT认证系统

- 添加JWT token生成和验证中间件
- 实现用户登录/登出API
- 添加密码加密存储（bcrypt）
- 添加token刷新机制

相关 issue: #123
```

### 页脚 (Footer)

用于引用相关问题或破坏性变更说明：

```
fix(api): 修正任务查询参数

修复了任务列表查询时状态筛选不生效的问题。

修复 #456
```

#### 破坏性变更 (Breaking Changes)

```
feat(auth): 重构认证API

BREAKING CHANGE: 认证API接口路径从 /auth/ 改为 /api/v1/auth/
旧接口将在v2.0中移除，请尽快迁移。
```

### 提交示例

```bash
# 简单的功能提交
git commit -m "feat(agent): 添加Agent状态批量更新功能"

# 带正文的提交
git commit -m "feat(task): 实现任务依赖关系管理

- 添加任务依赖表和关联模型
- 实现依赖循环检测算法
- 添加依赖关系可视化展示
- 更新任务状态流转逻辑

相关 issue: #234, #235"

# 修复bug
git commit -m "fix(api): 修复任务分页查询时总数计算错误

修复了当使用状态筛选时，返回的总数与实际不符的问题。

修复 #567"

# 重构代码
git commit -m "refactor(db): 优化数据库查询性能

- 为任务表添加复合索引 (status, created_at)
- 优化Agent统计查询，减少N+1查询问题
- 添加查询缓存机制

性能提升约40%"

# 破坏性变更
git commit -m "feat(auth): 升级JWT认证库到v2版本

BREAKING CHANGE: JWT配置格式已变更
- 移除了 JWT_ALGORITHM 环境变量
- 新增 JWT_SIGNING_KEY 必需配置
- token载荷格式变化，请更新客户端解析逻辑

迁移指南: docs/migration/jwt-v2.md"
```

---

## 分支管理策略

