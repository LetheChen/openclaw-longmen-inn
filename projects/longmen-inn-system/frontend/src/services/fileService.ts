import api from './api';

export interface LedgerContent {
  success: boolean;
  content: string;
  path: string;
}

export interface RoleContent {
  success: boolean;
  content: string;
  agent_id: string;
  file_path: string;
  file_type: string;
}

export interface RoleFile {
  name: string;
  path: string;
  type: string;
  size: number;
}

export interface RoleFileList {
  success: boolean;
  agent_id: string;
  files: RoleFile[];
}

export interface SaveResult {
  success: boolean;
  message: string;
  path: string;
  mode: 'generated';
}

export const getLedger = async (): Promise<LedgerContent> => {
  const response = await api.get('/files/ledger');
  return response.data;
};

export const generateLedger = async (includeCompleted: boolean = true): Promise<SaveResult> => {
  // 从 DB 导出生成 LEDGER.md（唯一写入入口）
  const response = await api.post('/files/ledger/generate', null, {
    params: { include_completed: includeCompleted }
  });
  return response.data;
};

// 兼容旧调用：现在改为从 DB 生成
export const saveLedger = async (): Promise<SaveResult> => {
  return generateLedger(true);
};

export const getRoleFile = async (agentId: string, filePath: string = 'IDENTITY.md'): Promise<RoleContent> => {
  const response = await api.get(`/files/role/${agentId}/file`, {
    params: { file_path: filePath }
  });
  return response.data;
};

export const listAgentRoleFiles = async (agentId: string): Promise<RoleFileList> => {
  const response = await api.get(`/files/role/${agentId}/files`);
  return response.data;
};

export const listRoleFiles = async (): Promise<{ success: boolean; roles: Array<{ agent_id: string; path: string; has_identity: boolean }> }> => {
  const response = await api.get('/files/roles');
  return response.data;
};

export const getReadme = async (): Promise<LedgerContent> => {
  const response = await api.get('/files/readme');
  return response.data;
};
