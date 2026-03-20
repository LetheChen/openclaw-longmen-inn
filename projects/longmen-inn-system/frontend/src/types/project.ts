// 项目状态枚举
export enum ProjectStatus {
  DRAFT = 'draft',
  ACTIVE = 'active',
  PAUSED = 'paused',
  COMPLETED = 'completed',
  ARCHIVED = 'archived',
}

// 项目优先级枚举
export enum ProjectPriority {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// 项目成员角色
export enum ProjectMemberRole {
  OWNER = 'owner',
  MANAGER = 'manager',
  MEMBER = 'member',
  VIEWER = 'viewer',
}

// 项目类型
export interface Project {
  id: string;
  name: string;
  description?: string;
  status: ProjectStatus;
  priority: ProjectPriority;
  ownerId: string;
  ownerName: string;
  ownerAvatar?: string;
  progress: number;
  startDate?: string;
  endDate?: string;
  estimatedHours?: number;
  actualHours?: number;
  taskCount: number;
  completedTaskCount: number;
  memberCount: number;
  tags?: string[];
  coverImage?: string;
  createdAt: string;
  updatedAt: string;
}

// 项目成员
export interface ProjectMember {
  id: string;
  projectId: string;
  userId: string;
  userName: string;
  userAvatar?: string;
  role: ProjectMemberRole;
  joinedAt: string;
  taskCount: number;
  completedTaskCount: number;
}

// 创建项目请求
export interface CreateProjectRequest {
  name: string;
  description?: string;
  priority?: ProjectPriority;
  startDate?: string;
  endDate?: string;
  estimatedHours?: number;
  tags?: string[];
  coverImage?: string;
}

// 更新项目请求
export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: ProjectStatus;
  priority?: ProjectPriority;
  startDate?: string;
  endDate?: string;
  estimatedHours?: number;
  tags?: string[];
  coverImage?: string;
}

// 项目筛选条件
export interface ProjectFilter {
  status?: ProjectStatus;
  priority?: ProjectPriority;
  ownerId?: string;
  keyword?: string;
  startDate?: string;
  endDate?: string;
}

// 项目统计
export interface ProjectStatistics {
  total: number;
  active: number;
  paused: number;
  completed: number;
  archived: number;
  totalTasks: number;
  completedTasks: number;
}
