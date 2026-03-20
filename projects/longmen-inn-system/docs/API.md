# 龙门客栈业务管理系统 - API接口文档

> 🏮 文档版本: v1.0.0 | 最后更新: 2026-03-15

## 📚 目录

- [认证接口](#认证接口)
- [Agent管理API](#agent管理api)
- [任务管理API](#任务管理api)
- [项目管理API](#项目管理api)
- [龙门令系统API](#龙门令系统api)
- [通用错误码](#通用错误码)

---

## 认证接口

### 登录

获取访问令牌。

```http
POST /api/v1/auth/login
```

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| username | string | 是 | 用户名 |
| password | string | 是 | 密码 |

**请求示例:**

```json
{
  "username": "admin",
  "password": "your_password"
}
```

**响应示例 (成功 - 200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin"
  }
}
```

**错误响应:**

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 401 | INVALID_CREDENTIALS | 用户名或密码错误 |
| 403 | ACCOUNT_LOCKED | 账户已被锁定 |

---

### 刷新令牌

使用刷新令牌获取新的访问令牌。

```http
POST /api/v1/auth/refresh
```

**请求头:**

```
Authorization: Bearer {refresh_token}
```

**响应示例:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### 登出

注销当前用户的会话。

```http
POST /api/v1/auth/logout
```

**请求头:**

```
Authorization: Bearer {access_token}
```

**响应:** `204 No Content`

---

## Agent管理API

### 获取Agent列表

获取所有Agent的列表，支持分页和筛选。

```http
GET /api/v1/agents
```

**查询参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过记录数，默认0 |
| limit | integer | 否 | 返回记录数，默认100，最大500 |
| status | string | 否 | 按状态筛选 (idle, busy, offline) |
| level | integer | 否 | 按等级筛选 (1-6) |

**响应示例 (200 OK):**

```json
{
  "total": 7,
  "items": [
    {
      "id": 1,
      "agent_id": "innkeeper",
      "name": "大掌柜",
      "title": "诸葛掌柜",
      "motto": "不谋全局者，不足谋一域",
      "status": "idle",
      "longmenling": 120,
      "level": 2,
      "created_at": "2026-03-14T12:00:00Z"
    },
    {
      "id": 2,
      "agent_id": "chef",
      "name": "厨子",
      "title": "神厨小福贵",
      "status": "busy",
      "longmenling": 200,
      "level": 3,
      "created_at": "2026-03-14T12:00:00Z"
    }
  ]
}
```

---

### 获取Agent详情

获取单个Agent的详细信息，包括统计数据和最近任务。

```http
GET /api/v1/agents/{agent_id}
```

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| agent_id | string | 是 | Agent唯一标识 |

**响应示例 (200 OK):**

```json
{
  "id": 1,
  "agent_id": "innkeeper",
  "name": "大掌柜",
  "title": "诸葛掌柜",
  "motto": "不谋全局者，不足谋一域",
  "role_description": "洞察先机，定夺方向。出PRD，定技术栈。情报搜集、市场调研、需求分析、战略决策、技术选型、PRD输出",
  "avatar_url": "/avatars/innkeeper.png",
  "status": "idle",
  "longmenling": 120,
  "level": 2,
  "created_at": "2026-03-14T12:00:00Z",
  "task_statistics": {
    "pending": 0,
    "in_progress": 1,
    "reviewing": 0,
    "completed": 5,
    "blocked": 0,
    "cancelled": 0
  },
  "recent_tasks": [
    {
      "id": 1,
      "task_no": "T-20250321-001",
      "title": "调研 AI 编程助手市场趋势",
      "status": "completed",
      "created_at": "2026-03-21T10:00:00Z"
    }
  ],
  "recent_longmenling_logs": [
    {
      "id": 1,
      "amount": 50,
      "reason": "完成市场调研PRD",
      "created_at": "2026-03-21T18:00:00Z"
    }
  ]
}
```

---

### 创建Agent

创建一个新的Agent角色。

```http
POST /api/v1/agents
```

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| agent_id | string | 是 | Agent唯一标识（如：designer） |
| name | string | 是 | Agent名称 |
| title | string | 否 | 称号 |
| motto | string | 否 | 信条 |
| role_description | string | 否 | 职责描述 |
| avatar_url | string | 否 | 头像URL |

**请求示例:**

```json
{
  "agent_id": "tester",
  "name": "测试员",
  "title": "火眼金睛",
  "motto": "不放过任何一个Bug",
  "role_description": "测试验证，质量保证。写用例，跑测试，报Bug。",
  "avatar_url": "/avatars/tester.png"
}
```

**响应示例 (201 Created):**

```json
{
  "id": 8,
  "agent_id": "tester",
  "name": "测试员",
  "title": "火眼金睛",
  "motto": "不放过任何一个Bug",
  "role_description": "测试验证，质量保证。写用例，跑测试，报Bug。",
  "avatar_url": "/avatars/tester.png",
  "status": "idle",
  "longmenling": 0,
  "level": 1,
  "created_at": "2026-03-15T10:00:00Z"
}
```

---

### 更新Agent

更新Agent的基本信息。

```http
PUT /api/v1/agents/{agent_id}
```

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| agent_id | string | 是 | Agent唯一标识 |

**请求参数:** (所有字段均为可选)

| 参数名 | 类型 | 说明 |
|--------|------|------|
| name | string | Agent名称 |
| title | string | 称号 |
| motto | string | 信条 |
| role_description | string | 职责描述 |
| avatar_url | string | 头像URL |
| longmenling | integer | 龙门令积分（更新时自动计算等级） |

**请求示例:**

```json
{
  "title": "超级测试员",
  "motto": "Bug是敌人，消灭它们！",
  "longmenling": 100
}
```

**响应示例 (200 OK):**

```json
{
  "id": 8,
  "agent_id": "tester",
  "name": "测试员",
  "title": "超级测试员",
  "motto": "Bug是敌人，消灭它们！",
  "role_description": "测试验证，质量保证。写用例，跑测试，报Bug。",
  "avatar_url": "/avatars/tester.png",
  "status": "idle",
  "longmenling": 100,
  "level": 2,
  "created_at": "2026-03-15T10:00:00Z"
}
```

---

### 删除Agent

删除一个Agent角色。

```http
DELETE /api/v1/agents/{agent_id}
```

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| agent_id | string | 是 | Agent唯一标识 |

**响应:** `204 No Content`

**错误响应:**

| 状态码 | 错误码 | 说明 |
|--------|--------|------|
| 404 | AGENT_NOT_FOUND | Agent不存在 |
| 400 | ACTIVE_TASKS_EXIST | Agent还有未完成的任务 |

---

### 更新Agent状态

手动更新Agent的工作状态。

```http
POST /api/v1/agents/{agent_id}/status
```

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| agent_id | string | 是 | Agent唯一标识 |

**请求参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 是 | 新状态 (idle/busy/offline) |
| reason | string | 否 | 状态变更原因 |

**请求示例:**

```json
{
  "status": "busy",
  "reason": "正在处理紧急任务"
}
```

**响应示例 (200 OK):**

```json
{
  "id": 1,
  "agent_id": "innkeeper",
  "name": "大掌柜",
  "status": "busy",
  "updated_at": "2026-03-15T12:00:00Z"
}
```

---

### 获取Agent任务列表

获取指定Agent的任务列表。

```http
GET /api/v1/agents/{agent_id}/tasks
```

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| agent_id | string | 是 | Agent唯一标识 |

**查询参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| status | string | 否 | 按状态筛选 |
| skip | integer | 否 | 跳过记录数，默认0 |
| limit | integer | 否 | 返回记录数，默认20 |

**响应示例 (200 OK):**

```json
{
  "total": 5,
  "items": [
    {
      "id": 1,
      "task_no": "T-20250321-001",
      "title": "调研 AI 编程助手市场趋势",
      "status": "completed",
      "priority": "high",
      "created_at": "2026-03-21T10:00:00Z"
    }
  ]
}
```

---

### 获取Agent总体统计

获取所有Agent的汇总统计数据。

```http
GET /api/v1/agents/stats/overview
```

**响应示例 (200 OK):**

```json
{
  "total_agents": 7,
  "status_distribution": {
    "idle": 3,
    "busy": 3,
    "offline": 1
  },
  "level_distribution": {
    "1": 2,
    "2": 3,
    "3": 1,
    "4": 1
  },
  "total_longmenling": 540,
  "average_longmenling": 77.14,
  "top_agents": [
    {
      "id": 3,
      "agent_id": "chef",
      "name": "厨子",
      "longmenling": 200
    }
  ]
}
```

---

## 任务管理API

### 获取任务列表

```http
GET /api/v1/tasks
```

**查询参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| skip | integer | 否 | 跳过记录数，默认0 |
| limit | integer | 否 | 返回记录数，默认20 |
| status | string | 否 | 按状态筛选 |
| priority | string | 否 | 按优先级筛选 |
| assignee | string | 否 | 按执行者筛选 |
| project_id | integer | 否 | 按项目筛选 |

**响应示例 (200 OK):**

```json
{
  "total": 25,
  "items": [
    {
      "id": 1,
      "task_no": "T-20250321-001",
      "title": "调研 AI 编程助手市场趋势",
      "description": "调研 Cursor、GitHub Copilot、Codeium 等产品，分析市场趋势，输出 PRD",
      "project_id": 2,
      "creator_agent_id": "main",
      "assignee_agent_id": "innkeeper",
      "status": "completed",
      "priority": "high",
      "estimated_hours": 8,
      "actual_hours": 7,
      "deliverable_path": "deliverables/prd/ai-coding-assistant-prd.md",
      "created_at": "2026-03-21T10:00:00Z",
      "started_at": "2026-03-21T10:00:00Z",
      "completed_at": "2026-03-21T17:00:00Z"
    }
  ]
}
```

---

### 获取任务详情

```http
GET /api/v1/tasks/{task_id}
```

**路径参数:**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| task_id | integer | 是 | 任务ID |

**响应示例 (200 OK):**

```json
{
  "id": 1,
  "task_no": "T-20250321-001",
  "title": "调研 AI 编程助手市场趋势",
  "description": "调研 Cursor、GitHub Copilot、Codeium 等产品，分析市场趋势，输出 PRD",
  "project_id": 2,
  "project_name": "AI 编程助手市场调研",
  "creator_agent_id": "main",
  "creator_name": "老板娘",
  "assignee_agent_id": "innkeeper",
  "assignee_name": "大掌柜",
  "status": "completed",
  "priority": "high",
  "estimated_hours": 8,
  "actual_hours": 7,
  "deliverable_path": "deliverables/prd/ai-coding-assistant-prd.md",
  "parent_task_id": null,
  "sub_tasks": [],
  "logs": [
    {
      "id": 1,
      "from_status": null,
      "to_status": "pending",
      "operator_agent_id": "main",
      "comment": "创建任务",
      "created_at": "2026-03-21T10:00:00Z"
    },
    {
      "id": 2,
      "from_status": "pending",
      "to_status": "in_progress",
      "operator_agent_id": "innkeeper",
      "comment": "开始调研",
      "created