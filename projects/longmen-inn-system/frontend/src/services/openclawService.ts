import api from './api';

export interface GatewayStatus {
  status: 'online' | 'offline' | 'degraded';
  version?: string;
  uptime?: string;
  last_checked: string;
  connected_agents: number;
  active_sessions: number;
  message_queue_size: number;
}

export interface AgentSession {
  id: string;
  agent_id: string;
  agent_name: string;
  status: 'active' | 'idle' | 'busy';
  channel?: string;
  last_activity?: string;
  message_count: number;
  created_at?: string;
}

export interface AgentHeartbeat {
  agent_id: string;
  status: string;
  last_heartbeat?: string;
  next_heartbeat?: string;
  heartbeat_interval: number;
  active_tasks: number;
  memory_usage?: number;
  cpu_usage?: number;
}

export interface RouteConfig {
  id: string;
  name: string;
  source: string;
  target: string;
  enabled: boolean;
  priority: number;
  message_count: number;
}

export interface LiveStatus {
  gateway: GatewayStatus;
  agents: Array<{
    agent_id: string;
    name: string;
    status: string;
    last_activity?: string;
  }>;
  sessions: AgentSession[];
  routes: RouteConfig[];
  statistics: {
    total_agents: number;
    active_sessions: number;
    messages_today: number;
    tasks_completed: number;
  };
  timestamp: string;
}

export const getGatewayStatus = async (): Promise<GatewayStatus> => {
  const response = await api.get('/openclaw/gateway/status');
  return response.data;
};

export const getLiveStatus = async (): Promise<LiveStatus> => {
  const response = await api.get('/openclaw/gateway/live-status');
  return response.data;
};

export const getAgentHeartbeat = async (agentId: string): Promise<AgentHeartbeat> => {
  const response = await api.get(`/openclaw/agents/${agentId}/heartbeat`);
  return response.data;
};

export const getSessions = async (agentId?: string): Promise<AgentSession[]> => {
  const params = agentId ? { agent_id: agentId } : {};
  const response = await api.get('/openclaw/sessions', { params });
  return response.data;
};

export const getRoutes = async (): Promise<RouteConfig[]> => {
  const response = await api.get('/openclaw/routes');
  return response.data;
};

export const getOpenClawStatus = async (): Promise<Record<string, unknown>> => {
  const response = await api.get('/openclaw/status');
  return response.data;
};

export const restartGateway = async (): Promise<{ message: string; output?: string }> => {
  const response = await api.post('/openclaw/gateway/restart');
  return response.data;
};

export const updateOpenClawConfig = async (config: {
  gateway_url?: string;
  ws_url?: string;
  api_key?: string;
  heartbeat_interval?: number;
  ai_news_enabled?: boolean;
  news_enabled?: boolean;
  red_news_enabled?: boolean;
}): Promise<{ message: string; updated: Record<string, unknown> }> => {
  const response = await api.post('/openclaw/config', config);
  return response.data;
};

export const getOpenClawConfig = async (): Promise<{
  gateway_url: string;
  ws_url: string;
  api_key?: string;
  heartbeat_interval: number;
  ai_news_enabled: boolean;
  news_enabled: boolean;
  red_news_enabled: boolean;
}> => {
  const response = await api.get('/openclaw/config');
  return response.data;
};

export const subscribeToOpenClawEvents = (
  onMessage: (data: unknown) => void,
  onError?: (error: Event) => void
): WebSocket => {
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/frontend-client`;
  const ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    ws.send(JSON.stringify({
      type: 'subscribe',
      data: { channel: 'openclaw' }
    }));
  };

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e);
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    onError?.(error);
  };

  return ws;
};

export const getEventsStreamUrl = (): string => {
  return `${api.defaults.baseURL}/openclaw/events/stream`;
};
