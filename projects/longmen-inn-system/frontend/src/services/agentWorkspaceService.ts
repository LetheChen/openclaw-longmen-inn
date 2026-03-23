/**
 * Agent工作空间 API服务
 */

import api from './api';
import type { AgentWorkspace, AgentListResponse, ActivityRecord } from '../types/agentWorkspace';

const API_PREFIX = '/agent-workspace';

/**
 * 获取所有Agent列表
 */
export async function getAgentList(): Promise<AgentListResponse> {
  const response = await api.get<AgentListResponse>(`${API_PREFIX}/`);
  return response.data;
}

/**
 * 获取Agent工作空间详情
 */
export async function getAgentWorkspace(agentId: string): Promise<AgentWorkspace> {
  const response = await api.get<AgentWorkspace>(`${API_PREFIX}/${agentId}`);
  return response.data;
}

/**
 * 获取Agent活动记录
 */
export interface ActivityQueryParams {
  limit?: number;
  action_type?: string;
  session_id?: string;
}

export async function getAgentActivities(
  agentId: string,
  params: ActivityQueryParams = {}
): Promise<ActivityRecord[]> {
  const response = await api.get<ActivityRecord[]>(
    `${API_PREFIX}/${agentId}/activities`,
    { params }
  );
  return response.data;
}

/**
 * 获取Agent任务列表
 */
export async function getAgentTasks(
  agentId: string,
  status?: 'pending' | 'in_progress' | 'completed'
): Promise<any[]> {
  const response = await api.get(`${API_PREFIX}/${agentId}/tasks`, {
    params: status ? { status } : {}
  });
  return response.data;
}

/**
 * 获取Agent工作空间文件
 */
export async function getAgentFiles(agentId: string): Promise<any[]> {
  const response = await api.get(`${API_PREFIX}/${agentId}/files`);
  return response.data;
}