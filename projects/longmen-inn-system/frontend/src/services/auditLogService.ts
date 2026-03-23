/**
 * 审计日志服务 - 龙门客栈API客户端
 */

import api from './api';
import type { AuditLogEntry, AuditFeedEntry, AuditStats, AuditLogResponse } from '../types/auditLog';

/**
 * 获取审计日志列表
 */
export const getAuditLogs = async (params?: { skip?: number; limit?: number; status?: string }) => {
  const response = await api.get('/audit-logs', { params });
  return response.data as AuditLogResponse;
};

/**
 * 获取版本动态Feed
 */
export const getAuditFeed = async (limit?: number) => {
  const response = await api.get('/audit-logs/feed', { params: { limit } });
  // 返回 feed 数组
  return (response.data as { feed: AuditFeedEntry[] }).feed;
};

/**
 * 获取审计统计信息
 */
export const getAuditStats = async () => {
  const response = await api.get('/audit-logs/stats');
  return response.data as { success: boolean; statistics: AuditStats };
};
