import api from './api';
import type {
  Project,
  ProjectMember,
  ProjectStatistics,
  CreateProjectRequest,
  UpdateProjectRequest,
  ProjectFilter,
} from '../types/project';

export interface ProjectListResponse {
  data: Project[];
  total: number;
  page: number;
  pageSize: number;
}

// 获取项目列表
export const getProjects = async (
  params?: ProjectFilter & { page?: number; pageSize?: number }
): Promise<ProjectListResponse> => {
  const response = await api.get('/projects', { params });
  return response.data;
};

// 获取单个项目
export const getProjectById = async (id: string): Promise<Project> => {
  const response = await api.get(`/projects/${id}`);
  return response.data;
};

// 创建项目
export const createProject = async (data: CreateProjectRequest): Promise<Project> => {
  const response = await api.post('/projects', data);
  return response.data;
};

// 更新项目
export const updateProject = async (
  id: string,
  data: UpdateProjectRequest
): Promise<Project> => {
  const response = await api.put(`/projects/${id}`, data);
  return response.data;
};

// 删除项目
export const deleteProject = async (id: string): Promise<void> => {
  await api.delete(`/projects/${id}`);
};

// 获取项目统计
export const getProjectStatistics = async (): Promise<ProjectStatistics> => {
  const response = await api.get('/projects/statistics');
  return response.data;
};

// 获取项目成员列表
export const getProjectMembers = async (projectId: string): Promise<ProjectMember[]> => {
  const response = await api.get(`/projects/${projectId}/members`);
  return response.data;
};

// 添加项目成员
export const addProjectMember = async (
  projectId: string,
  userId: string,
  role: string
): Promise<ProjectMember> => {
  const response = await api.post(`/projects/${projectId}/members`, { userId, role });
  return response.data;
};

// 更新项目成员角色
export const updateProjectMemberRole = async (
  projectId: string,
  memberId: string,
  role: string
): Promise<ProjectMember> => {
  const response = await api.put(`/projects/${projectId}/members/${memberId}`, { role });
  return response.data;
};

// 移除项目成员
export const removeProjectMember = async (
  projectId: string,
  memberId: string
): Promise<void> => {
  await api.delete(`/projects/${projectId}/members/${memberId}`);
};

// 获取我参与的项目
export const getMyProjects = async (
  params?: { status?: string; page?: number; pageSize?: number }
): Promise<ProjectListResponse> => {
  const response = await api.get('/projects/my', { params });
  return response.data;
};

// 更新项目进度
export const updateProjectProgress = async (
  id: string,
  progress: number
): Promise<Project> => {
  const response = await api.patch(`/projects/${id}/progress`, { progress });
  return response.data;
};
