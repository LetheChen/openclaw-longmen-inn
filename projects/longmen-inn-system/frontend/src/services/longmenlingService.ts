import api from './api';

export interface LongmenlingRankingItem {
  rank: number;
  agent_id: string;
  name: string;
  title: string | null;
  avatar_url: string | null;
  level: number;
  longmenling: number;
}

export interface LongmenlingRanking {
  total_count: number;
  top_agents: LongmenlingRankingItem[];
  my_rank: LongmenlingRankingItem | null;
  generated_at: string;
}

export interface LongmenlingHistoryItem {
  id: number;
  amount: number;
  reason: string;
  description: string | null;
  task_id: number | null;
  created_at: string;
}

export interface AgentLongmenlingDetail {
  agent_id: string;
  name: string;
  title: string | null;
  avatar_url: string | null;
  level: number;
  longmenling: number;
  next_level_required: number;
  points_to_next_level: number;
  total_earned: number;
  total_spent: number;
  recent_history: LongmenlingHistoryItem[];
  rank_in_all: number;
  generated_at: string;
}

/**
 * 获取龙门令排行榜
 */
export const getLongmenlingRanking = async (topN: number = 100): Promise<LongmenlingRanking> => {
  const response = await api.get(`/longmenling/ranking?top_n=${topN}`);
  return response.data;
};

/**
 * 获取Agent龙门令详情
 */
export const getAgentLongmenlingDetail = async (agentId: string): Promise<AgentLongmenlingDetail> => {
  const response = await api.get(`/longmenling/${agentId}`);
  return response.data;
};
