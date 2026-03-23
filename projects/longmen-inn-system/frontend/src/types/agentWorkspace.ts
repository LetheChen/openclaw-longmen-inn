/**
 * Agent工作空间类型定义
 */

export type AgentStatus = 'idle' | 'busy' | 'offline' | 'error';

export interface AgentRole {
  id: string;
  name: string;
  title: string;
  scene: string;
  description: string;
  avatar?: string;
  scene_image?: string;
  motto?: string;
  level: number;
}

export interface TaskInfo {
  id: string;
  content: string;
  status: 'pending' | 'in_progress' | 'completed';
  priority: 'high' | 'medium' | 'low';
  assignee?: string;
  project?: string;
  created_at?: string;
  updated_at?: string;
  completed_at?: string;
  remarks?: string;
}

export interface ActivityRecord {
  timestamp: string;
  action_type: 'message' | 'tool_use' | 'tool_result';
  action_detail: string;
  output_preview?: string;
  role?: string;
  tool_name?: string;
  is_error?: boolean;
}

export interface WorkspaceFile {
  path: string;
  type: 'file' | 'directory';
  file_type?: 'code' | 'doc' | 'design' | 'config' | 'file';
  last_modified?: string;
  size?: number;
}

export interface AgentWorkspace {
  role: AgentRole;
  status: AgentStatus;
  current_tasks: TaskInfo[];
  pending_tasks: TaskInfo[];
  completed_tasks: TaskInfo[];
  recent_activities: ActivityRecord[];
  workspace_files: WorkspaceFile[];
  last_active?: string;
  session_id?: string;
  session_start?: string;
  stats: {
    task_completed?: number;
    task_in_progress?: number;
    task_pending?: number;
    activity_count?: number;
    file_count?: number;
    [key: string]: any;
  };
}

export interface AgentSummary {
  agent_id: string;
  name: string;
  title?: string;
  status: AgentStatus;
  scene?: string;
  level: number;
  longmenling: number;
  current_task?: string;
  last_active?: string;
}

export interface AgentListResponse {
  total: number;
  agents: AgentSummary[];
  statistics: {
    total: number;
    online: number;
    busy: number;
    idle: number;
    offline: number;
  };
}