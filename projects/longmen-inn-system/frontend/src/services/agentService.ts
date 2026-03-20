import api from './api';
import type {
  Agent,
  AgentActivity,
  AgentStatistics,
  CreateAgentRequest,
  UpdateAgentRequest,
} from '../types/agent';

// 获取Agent列表
export const getAgents = async (
  params?: { status?: string; role?: string; keyword?: string }
): Promise<Agent[]> => {
  const response = await api.get('/agents', { params });
  return response.data;
};

// 获取单个Agent
export const getAgentById = async (id: string): Promise<Agent> => {
  const response = await api.get(`/agents/${id}`);
  return response.data;
};

// 创建Agent
export const createAgent = async (data: CreateAgentRequest): Promise<Agent> => {
  const response = await api.post('/agents', data);
  return response.data;
};

// 更新Agent
export const updateAgent = async (
  id: string,
  data: UpdateAgentRequest
): Promise<Agent> => {
  const response = await api.put(`/agents/${id}`, data);
  return response.data;
};

// 删除Agent
export const deleteAgent = async (id: string): Promise<void> => {
  await api.delete(`/agents/${id}`);
};

// 获取Agent统计
export const getAgentStatistics = async (): Promise<AgentStatistics> => {
  const response = await api.get('/agents/statistics');
  return response.data;
};

// 获取Agent活动记录
export const getAgentActivities = async (
  params?: { agentId?: string; type?: string; limit?: number }
): Promise<AgentActivity[]> => {
  const response = await api.get('/agents/activities', { params });
  return response.data;
};

// 获取在线Agent
export const getOnlineAgents = async (): Promise<Agent[]> => {
  const response = await api.get('/agents/online');
  return response.data;
};

// 更新Agent状态
export const updateAgentStatus = async (
  id: string,
  status: string
): Promise<Agent> => {
  const response = await api.patch(`/agents/${id}/status`, { status });
  return response.data;
};

// 获取我的Agent信息
export const getMyAgentInfo = async (): Promise<Agent> => {
  const response = await api.get('/agents/me');
  return response.data;
};
