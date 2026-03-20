// Agent状态枚举（与后端保持一致）
export enum AgentStatus {
  IDLE = 'idle',
  BUSY = 'busy',
  OFFLINE = 'offline',
}

// Agent角色枚举
export enum AgentRole {
  WORKER = 'worker',
  MANAGER = 'manager',
  ADMIN = 'admin',
}

// Agent类型（与后端API响应格式匹配）
export interface Agent {
  id?: number; // 数据库ID（可选）
  agent_id: string; // Agent唯一标识
  name: string; // 显示名称
  nickname?: string;
  avatar?: string;
  avatar_url?: string; // 头像URL（后端字段）
  title?: string; // 称号
  motto?: string; // 信条
  role_description?: string; // 职责描述
  status: AgentStatus;
  role?: AgentRole;
  longmenling: number;
  level: number;
  skills?: string[];
  currentTaskId?: string;
  currentTaskName?: string;
  completedTasks?: number;
  onlineTime?: number; // 单位：分钟
  lastActiveAt?: string;
  joinedAt?: string;
  created_at?: string; // 创建时间（后端字段）
  bio?: string;
}

// Agent活动记录
export interface AgentActivity {
  id: string;
  agentId: string;
  agentName: string;
  agentAvatar?: string;
  type: ActivityType;
  content: string;
  relatedTaskId?: string;
  relatedTaskTitle?: string;
  metadata?: Record<string, any>;
  createdAt: string;
}

// 活动类型
export enum ActivityType {
  TASK_CREATED = 'task_created',
  TASK_STARTED = 'task_started',
  TASK_COMPLETED = 'task_completed',
  TASK_COMMENT = 'task_comment',
  LOGIN = 'login',
  LOGOUT = 'logout',
  LONGMENLING_EARNED = 'longmenling_earned',
  LEVEL_UP = 'level_up',
}

// Agent统计
export interface AgentStatistics {
  total: number;
  online: number;
  offline: number;
  busy: number;
  idle: number;
}

// 创建Agent请求
export interface CreateAgentRequest {
  name: string;
  nickname?: string;
  avatar?: string;
  role?: AgentRole;
  skills?: string[];
  bio?: string;
}

// 更新Agent请求
export interface UpdateAgentRequest {
  name?: string;
  nickname?: string;
  avatar?: string;
  role?: AgentRole;
  skills?: string[];
  bio?: string;
}
