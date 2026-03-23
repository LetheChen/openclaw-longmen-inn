/**
 * 审计日志类型定义
 */

// 后端返回的审计日志条目
export interface AuditLogEntry {
  timestamp: string;
  type: string;
  files_changed: string[];
  lines_added: number;
  lines_deleted: number;
  tasks_found: string[];
  summary: string;
  status: string;
  issues: string[];
}

// 版本动态Feed条目（后端格式化后的格式）
export interface AuditFeedEntry {
  id?: string;
  timestamp: string;
  date_str?: string;
  title: string;
  status: string;
  status_emoji?: string;
  lines_added: number;
  lines_deleted: number;
  lines_info?: string;
  files_count: number;
  files_info?: string;
  issues: string[];
  issues_count: number;
  tasks_found: string[];
  type: string;
}

// 审计统计信息
export interface AuditStats {
  total_audits: number;
  total_files_changed: number;
  total_lines_added: number;
  total_lines_deleted: number;
  tasks_completed: number;
  issues_found: number;
}

// API响应类型
export interface AuditLogResponse {
  total: number;
  entries: AuditLogEntry[];
  statistics: Record<string, any>;
}

export interface AuditFeedResponse {
  feed: AuditFeedEntry[];
}
