# 龙门客栈 - Agent工作空间可视化方案

> 版本：v1.0
> 日期：丙午年二月初三
> 作者：老板娘（凤老板）

---

## 一、方案概述

### 1.1 目标

将抽象的Agent协作体系可视化为沉浸式的"客栈场景"，让用户能够：

1. **直观了解**每个Agent的工作状态、任务进度、历史活动
2. **实时监控** Agent的执行过程、工具调用、输出内容
3. **沉浸体验**客栈角色扮演的氛围感，增强协作乐趣
4. **未来扩展** Agent间协作动画、任务交接可视化

### 1.2 核心价值

- **降低认知负担**：从"系统日志"到"场景化呈现"
- **增强协作感知**：清楚知道谁在做什么、做到什么程度
- **提升趣味性**：把枯燥的开发管理变成有趣的客栈经营

---

## 二、角色与场景设计

### 2.1 角色场景映射

|角色 | 专属场所 | 场景描述 | 视觉风格 |
|------|----------|----------|----------|
| **老板娘** | 内堂雅间 | 账桌居中，墙上挂着客栈总规，侧边是任务看板，茶具精致 | 暖色调、典雅、掌控感 |
| **大掌柜** | 客房柜台 | 正对大门，算盘房号牌，登记簿堆叠，视野开阔 | 稳重、权威、战略感 |
| **店小二** | 大堂茶座 | 八仙桌、长凳，托盘穿梭，热闹非凡 | 活泼、灵动、忙碌感 |
| **厨子** | 后厨灶台 | 炒锅菜刀，香料架，半成品码放，火光映照 | 充实、实用、技术感 |
| **画师** | 画室画室 | 画架颜料，设计稿铺展，成品上墙 | 艺术、创意、美感 |
| **账房先生** | 账房 | 簿册成架，算珠在手，油灯一盏，严肃认真 | 专业、严谨、细节 |
| **说书先生** | 书房茶座 | 折扇笔墨，茶席待客，故事册展开 |优雅、文气、叙事感 |

### 2.2 统一场景模板

```
┌─────────────────────────────────────────────────────────────┐
│ ┌─────────────────────────────────────────────────────────┐ │
│ │                    场景背景图                           │ │
│ │  ┌───┐                      │ │
│ │  │   │  角色形象区           │ │
│ │  │👤 │  (可动画)             │    ┌─────────────────────┐│ │
│ │  │   │                      │    │ 当前任务│ │
│ │  └───┘                      │    │ ○ 进行中: xxx     ││ │
│ │                             │    │ ○ 待办: xxx│ │
│ │        [场景装饰元素]        │    │ ○ 已完成: xxx     ││ │
│ │                             │    └─────────────────────┘│ │
│ │                             │    ┌─────────────────────┐│ │
│ │                             │    │ 最近活动│ │
│ │        [工具/物品]          │    │ • 执行了read命令   ││ │
│ │                             │    │ • 创建了文件xxx   ││ │
│ │                             │    │ • 10:30 输出报告  │ │
│ │                             │    └─────────────────────┘│ │
│ └─────────────────────────────────────────────────────────┘ │
│┌───────────────────────────────────────────────────────────┐│
││ 工作空间预览[展开详情→]              │
││ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
││ │工作文件  │ │ 对话记录 │ │ 工具调用│ │
││ └──────────┘ └──────────┘ └──────────┘                       │
│└───────────────────────────────────────────────────────────┘│
│                    [状态栏: 空闲/忙碌/离线]│
└─────────────────────────────────────────────────────────────┘
```

---

## 三、数据模型设计

### 3.1 Agent信息数据结构

```python
# schemas/agent_workspace.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class AgentStatus(str, Enum):
    IDLE = "idle"# 空闲
    BUSY = "busy"          # 忙碌
    OFFLINE = "offline"    # 离线
    ERROR = "error"         # 异常

class AgentRole(BaseModel):
    """角色信息"""
    id: str                 # chef, main, innkeeper, etc.
    name: str               # 厨子、老板娘、大掌柜
    title: str              # 称号：李师傅、凤老板
    scene: str              # 场所：后厨、内堂、柜台
    description: str        # 职责描述
    avatar: str             # 形象图片URL
    scene_image: str        # 场景背景图URL

class TaskInfo(BaseModel):
    """任务信息"""
    id: str
    content: str
    status: str             # pending, in_progress, completed
    priority: str           # high, medium, low
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

class ActivityRecord(BaseModel):
    """活动记录"""
    timestamp: datetime
    action_type: str        # tool_use, message, file_op, etc.
    action_detail: str      # 动作详情
    output_preview: Optional[str]  # 输出预览（截断）

class WorkspaceFile(BaseModel):
    """工作空间文件"""
    path: str
    type: str               # code, doc, design, config
    last_modified: datetime
    size: int

class AgentWorkspace(BaseModel):
    """Agent工作空间完整信息"""
    role: AgentRole
    status: AgentStatus
    current_tasks: List[TaskInfo]
    pending_tasks: List[TaskInfo]
    completed_tasks: List[TaskInfo]
    recent_activities: List[ActivityRecord]
    workspace_files: List[WorkspaceFile]
    last_active: datetime
    
    # 会话信息
    session_id: Optional[str]
    session_start: Optional[datetime]
    
    # 统计信息
    stats: dict             # 任务完成数、工具调用次数等
```

### 3.2 数据来源

| 数据项 | 来源 | 获取方式 |
|--------|------|----------|
| 角色信息 | `ROSTER.md` + `roles/*/IDENTITY.md` | 文件解析 |
| 任务状态 | `LEDGER.md` | 文件解析 + 实时更新 |
| 活动记录 | `~/.openclaw/agents/<agent>/sessions/*.jsonl` | JSONL解析 |
| 工作空间文件 | `~/.openclaw/agents/<agent>/workspace/` | 目录扫描|
| 当前状态 | 内存状态 + 最近活动时间 | 推断计算 |

---

## 四、后端API设计

### 4.1 API端点

```python
# routers/agent_workspace.py

from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(prefix="/api/v1/agents", tags=["Agent Workspace"])

@router.get("/", response_model=List[AgentSummary])
async def list_agents():
    """
    获取所有Agent列表（含简要状态）
    用于花名册页面展示
    """
    pass

@router.get("/{agent_id}", response_model=AgentWorkspace)
async def get_agent_workspace(agent_id: str):
    """
    获取指定Agent的完整工作空间信息
    """
    pass

@router.get("/{agent_id}/activities", response_model=List[ActivityRecord])
async def get_agent_activities(
    agent_id: str,
    limit: int = 50,
    action_type: Optional[str] = None
):
    """
    获取Agent活动记录（支持分页和类型过滤）
    """
    pass

@router.get("/{agent_id}/tasks", response_model=List[TaskInfo])
async def get_agent_tasks(
    agent_id: str,
    status: Optional[str] = None
):
    """
    获取Agent任务列表
    """
    pass

@router.get("/{agent_id}/files", response_model=List[WorkspaceFile])
async def get_agent_files(agent_id: str):
    """
    获取Agent工作空间文件列表
    """
    pass

@router.get("/{agent_id}/session/{session_id}", response_model=SessionDetail)
async def get_session_detail(agent_id: str, session_id: str):
    """
    获取特定会话的完整对话记录
    """
    pass

@router.websocket("/ws/{agent_id}/events")
async def agent_events_websocket(websocket: WebSocket, agent_id: str):
    """
    WebSocket实时事件推送
    - 任务状态变更
    - 新活动记录
    - 状态切换（空闲/忙碌）
    """
    pass
```

### 4.2 数据聚合服务

```python
# services/agent_workspace_service.py

class AgentWorkspaceService:
    def __init__(self):
        self.roster_parser = RosterParser()
        self.ledger_parser = LedgerParser()
        self.session_parser = SessionParser()
    
    async def get_agent_workspace(self, agent_id: str) -> AgentWorkspace:
        """聚合所有数据源"""
        # 1. 解析角色信息
        role = await self.roster_parser.get_role(agent_id)
        
        # 2. 解析任务状态
        tasks = await self.ledger_parser.get_agent_tasks(agent_id)
        
        # 3. 解析会话活动
        activities = await self.session_parser.get_recent_activities(
            agent_id, limit=50
        )
        
        # 4. 扫描工作空间文件
        files = await self.scan_workspace_files(agent_id)
        
        # 5. 计算当前状态
        status = self.calculate_status(activities)
        
        return AgentWorkspace(
            role=role,
            status=status,
            current_tasks=[t for t in tasks if t.status == "in_progress"],
            pending_tasks=[t for t in tasks if t.status == "pending"],
            completed_tasks=[t for t in tasks if t.status == "completed"],
            recent_activities=activities,
            workspace_files=files,
            last_active=activities[0].timestamp if activities else None,
            stats=self.calculate_stats(activities, tasks)
        )
    
    def calculate_status(self, activities: List[ActivityRecord]) -> AgentStatus:
        """根据最近活动推断状态"""
        if not activities:
            return AgentStatus.OFFLINE
        
        last_activity = activities[0].timestamp
        now = datetime.now()
        
        if (now - last_activity).total_seconds() < 300:  # 5分钟内
            return AgentStatus.BUSY
        elif (now - last_activity).total_seconds() < 3600:  # 1小时内
            return AgentStatus.IDLE
        else:
            return AgentStatus.OFFLINE
```

---

## 五、前端组件设计

### 5.1 组件结构

```
src/components/agent-workspace/
├── AgentWorkspace.tsx          # 主容器组件
├── AgentScene.tsx             # 场景背景组件
├── AgentAvatar.tsx            # 角色形象组件
├── TaskPanel.tsx              # 任务面板
├── ActivityFeed.tsx           # 活动动态流
├── WorkspacePreview.tsx        # 工作空间预览
├── SessionDetail.tsx          # 会话详情弹窗
├── AgentStatusBadge.tsx       # 状态徽章
└── styles/
    ├── AgentWorkspace.module.scss
    └── scenes/                   # 各角色场景样式
        ├── boss-lady.scss
        ├── chef.scss
        ├── innkeeper.scss
        └── ...
```

### 5.2 主容器组件

```tsx
// AgentWorkspace.tsx

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { AgentScene } from './AgentScene';
import { TaskPanel } from './TaskPanel';
import { ActivityFeed } from './ActivityFeed';
import { WorkspacePreview } from './WorkspacePreview';
import { AgentStatusBadge } from './AgentStatusBadge';
import './AgentWorkspace.module.scss';

interface AgentWorkspaceProps {
  agentId: string;
}

export const AgentWorkspace: React.FC<AgentWorkspaceProps> = ({ agentId }) => {
  const { data: workspace, isLoading } = useQuery({
    queryKey: ['agent-workspace', agentId],
    queryFn: () => fetch(`/api/v1/agents/${agentId}`).then(r => r.json()),
    refetchInterval: 5000, // 5秒刷新
  });

  if (isLoading) return <div className="loading">加载中...</div>;

  return (
    <div className="agent-workspace">
      {/* 头部：角色信息 */}
      <header className="workspace-header">
        <div className="role-info">
          <h2>{workspace.role.name}</h2>
          <span className="title">{workspace.role.title}</span>
        </div>
        <AgentStatusBadge status={workspace.status} />
      </header>

      {/* 主体：场景 + 信息面板 */}
      <main className="workspace-main">
        <div className="scene-container">
          <AgentScene 
            scene={workspace.role.scene}
            sceneImage={workspace.role.scene_image}
          >
            {/* 场景内嵌信息 */}
            <div className="scene-overlay">
              <TaskPanel 
                currentTasks={workspace.current_tasks}
                pendingTasks={workspace.pending_tasks}
              />
            </div>
          </AgentScene>
        </div>

        {/* 右侧面板 */}
        <aside className="info-panel">
          <ActivityFeed activities={workspace.recent_activities} />
          <WorkspacePreview files={workspace.workspace_files} />
        </aside>
      </main>
    </div>
  );
};
```

### 5.3 场景组件

```tsx
// AgentScene.tsx

import React from 'react';
import classNames from 'classnames';
import styles from './scenes';

interface AgentSceneProps {
  scene: string;           // '后厨' | '内堂' | '柜台' | ...
  sceneImage: string;
  children: React.ReactNode;
}

export const AgentScene: React.FC<AgentSceneProps> = ({ 
  scene,sceneImage, 
  children 
}) => {
  const sceneStyle = styles[scene] || styles.default;
  
  return (
    <div className={classNames('agent-scene', sceneStyle)}>
      {/* 场景背景 */}
      <div 
        className="scene-background"
        style={{ backgroundImage: `url(${sceneImage})` }}
      >
        {/* 可交互元素 */}
        <div className="scene-elements">
          {renderSceneElements(scene)}
        </div>
        
        {/* 信息叠加层 */}
        <div className="scene-overlay">
          {children}
        </div>
      </div>
    </div>
  );
};

function renderSceneElements(scene: string) {
  switch (scene) {
    case '后厨':
      return (
        <>
          <div className="element wok" data-tooltip="代码烹饪中..." />
          <div className="element spices" data-tooltip="调料架：依赖库" />
          <div className="element knife" data-tooltip="菜刀：调试工具" />
        </>
      );
    case '内堂':
      return (
        <>
          <div className="element ledger" data-tooltip="账簿：任务看板" />
          <div className="element tea" data-tooltip="茶具：沟通记录" />
        </>
      );
    // ... 其他场景
  }
}
```

---

## 六、JSONL会话解析器

### 6.1 解析器实现

```python
# services/session_parser.py

import json
from pathlib import Path
from typing import List, Generator
from datetime import datetime

class SessionParser:
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or Path.home() / ".openclaw" / "agents")
    
    def get_session_files(self, agent_id: str) -> List[Path]:
        """获取Agent所有会话文件"""
        sessions_dir = self.base_path / agent_id / "sessions"
        if not sessions_dir.exists():
            return []
        # 按时间倒序排列
        return sorted(
            sessions_dir.glob("*.jsonl"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
    
    def parse_activity(self, line: str) -> dict:
        """解析单行JSONL活动记录"""
        try:
            data = json.loads(line)
            event_type = data.get("type")
            
            if event_type == "message":
                return self._parse_message(data)
            elif event_type == "tool_use":
                return self._parse_tool_use(data)
            elif event_type == "tool_result":
                return self._parse_tool_result(data)
            else:
                return {"type": "other", "raw": data}
        except json.JSONDecodeError:
            return {"type": "error", "raw": line}
    
    def _parse_message(self, data: dict) -> dict:
        """解析对话消息"""
        message = data.get("message", {})
        role = message.get("role")
        content = message.get("content", [])
        
        text_content = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_content += item.get("text", "")
            elif isinstance(item, str):
                text_content += item
        
        return {
            "type": "message",
            "role": role,
            "content": text_content[:500],  # 截断预览
            "timestamp": data.get("timestamp"),
            "full_content": message
        }
    
    def _parse_tool_use(self, data: dict) -> dict:
        """解析工具调用"""
        tool_name = data.get("name")
        tool_input = data.get("input", {})
        
        return {
            "type": "tool_use",
            "tool": tool_name,
            "input_preview": json.dumps(tool_input, ensure_ascii=False)[:200],
            "timestamp": data.get("timestamp"),
            "full_input": tool_input
        }
    
    def _parse_tool_result(self, data: dict) -> dict:
        """解析工具返回"""
        return {
            "type": "tool_result",
            "tool_use_id": data.get("tool_use_id"),
            "result_preview": str(data.get("content", ""))[:200],
            "timestamp": data.get("timestamp"),
            "is_error": data.get("is_error", False)
        }
    
    def get_recent_activities(
        self, 
        agent_id: str, 
        limit: int = 50
    ) -> List[dict]:
        """获取最近活动记录"""
        files = self.get_session_files(agent_id)
        activities = []
        
        for file_path in files:
            if len(activities) >= limit:
                break
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(activities) >= limit:
                        break
                    activity = self.parse_activity(line)
                    if activity["type"] in ["message", "tool_use", "tool_result"]:
                        activities.append(activity)
        
        return activities
```

---

## 七、实时状态推送

### 7.1 WebSocket服务

```python
# services/event_pusher.py

from fastapi import WebSocket
from typing import Dict, Set
import asyncio

class AgentEventPusher:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, agent_id: str, websocket: WebSocket):
        """建立WebSocket连接"""
        await websocket.accept()
        if agent_id not in self.connections:
            self.connections[agent_id] = set()
        self.connections[agent_id].add(websocket)
    
    async def disconnect(self, agent_id: str, websocket: WebSocket):
        """断开连接"""
        if agent_id in self.connections:
            self.connections[agent_id].discard(websocket)
    
    async def push_event(self, agent_id: str, event: dict):
        """推送事件到所有订阅者"""
        if agent_id in self.connections:
            disconnected = set()
            for ws in self.connections[agent_id]:
                try:
                    await ws.send_json(event)
                except:
                    disconnected.add(ws)
            # 清理断开的连接
            self.connections[agent_id] -= disconnected

# 全局实例
pusher = AgentEventPusher()

# 在event_router中注册
async def on_agent_activity(agent_id: str, activity: dict):
    """Agent活动时调用"""
    await pusher.push_event(agent_id, {
        "type": "new_activity",
        "data": activity
    })
```

---

## 八、场景资源设计规范

### 8.1 背景图规格

| 属性 | 规格 |
|------|------|
| 尺寸 | 1920x1080 (16:9) |
| 格式 | WebP（压缩） + PNG（备选） |
| 风格 | 国风水墨 / 扁平插画 |
| 色调 | 根据角色气质定调 |

### 8.2 角色形象规格

| 属性 | 规格 |
|------|------|
| 尺寸 | 200x300 (站立) / 150x150 (头像) |
| 格式 | PNG (透明背景) |
| 状态 | 空闲/忙碌/离线 三种动画帧|
| 动画 | 可选：眨眼、手势等微动效 |

### 8.3 存放路径

```
public/assets/agents/
├── scenes/                    # 场景背景
│   ├── boss-lady.webp
│   ├── chef.webp
│   ├── innkeeper.webp
│   └── ...
├── avatars/                   # 角色形象
│   ├── boss-lady/
│   │   ├── idle.png
│   │   ├── busy.png
│   │   └── offline.png
│   └── ...├── icons/                    # 场景内图标
│   ├── task-board.svg
│   ├── tools.svg
│   └── files.svg
└── animations/                # 动画资源
    ├── visit-transition.json
    └── task-complete.json
```

---

## 九、实现路线图

### Phase 1: 基础框架 (第1-2周)

- [ ] 后端API框架搭建
- [ ] 数据模型定义
- [ ] JSONL解析器实现
- [ ] 基础前端组件

### Phase 2: 核心功能 (第3-4周)

- [ ] 角色信息展示
- [ ] 任务状态同步
- [ ] 活动记录解析
- [ ] 工作空间文件预览

### Phase 3: 视觉优化 (第5-6周)

- [ ] 场景背景图设计
- [ ] 角色形象设计
- [ ] 动画效果实现
- [ ] 响应式适配

### Phase 4: 高级功能 (第7-8周)

- [ ] WebSocket实时推送
- [ ] Agent互访动画
- [ ] 会话详情弹窗
- [ ] 搜索过滤功能

---

## 十、扩展构想：Agent互访动画

### 10.1 场景描述

```
当店小二需要向大掌柜汇报进度时：
1. 大堂场景中，店小二形象"走出"画面
2. 柜台场景中，"店小二走进"动画
3. 出现对话气泡："大掌柜，任务拆解完毕"
4. 大掌柜点头回应动画
5. 店小二"返回"大堂场景
```

### 10.2 技术实现

```typescript
// 角色移动动画状态机
interface AgentVisitState {
  visitor: AgentRole;
  host: AgentRole;
  stage: 'departing' | 'transitioning' | 'arriving' | 'interacting' | 'returning';
  message?: string;
}

// 触发互访动画
function triggerAgentVisit(visitorId: string, hostId: string, message: string) {
  // 1. 在访客场景触发"离开"动画
  // 2. 在目标场景触发"到达"动画
  // 3. 显示对话气泡
  // 4. 播放回应动画// 5. 访客返回
}
```

---

## 十一、总结

这个方案将龙门客栈的Agent协作体系从"抽象数据"变成"生动场景"：

1. **数据聚合**：整合角色定义、任务状态、会话日志、工作空间文件
2. **可视化呈现**：场景化界面 + 实时状态 + 活动流
3. **交互体验**：点击查看详情、实时推送更新
4. **未来扩展**：Agent互访动画、协作过程可视化

**第一步建议**：先实现Phase 1的基础框架，验证数据流和基本展示，再逐步完善视觉和交互效果。

---

*方案制定：老板娘（凤老板）*
*日期：丙午年二月初三*