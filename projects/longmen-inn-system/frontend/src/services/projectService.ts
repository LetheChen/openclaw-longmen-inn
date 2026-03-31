import api from './api';
import type {
  Project,
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

// 更新项目进度
export const updateProjectProgress = async (
  id: string,
  progress: number
): Promise<Project> => {
  const response = await api.patch(`/projects/${id}/progress`, { progress });
  return response.data;
};
