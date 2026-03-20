import api from './api';
import type {
  Task,
  CreateTaskRequest,
  UpdateTaskRequest,
  TaskFilter,
  TaskStatistics,
} from '../types/task';
import { TaskStatus, TaskPriority } from '../types/task';

export interface TaskListResponse {
  data: Task[];
  total: number;
  page: number;
  pageSize: number;
}

const mapTaskFromApi = (apiTask: any): Task => ({
  id: String(apiTask.id),
  taskNo: apiTask.task_no,
  title: apiTask.title,
  description: apiTask.description,
  status: apiTask.status as TaskStatus,
  priority: apiTask.priority as TaskPriority,
  projectId: apiTask.project_id ? String(apiTask.project_id) : undefined,
  projectName: apiTask.project_name,
  assigneeId: apiTask.assignee_agent_id,
  assigneeName: apiTask.assignee_name,
  assigneeAvatar: undefined,
  creatorId: apiTask.creator_agent_id,
  creatorName: apiTask.creator_name,
  dueDate: undefined,
  estimatedHours: apiTask.estimated_hours,
  actualHours: apiTask.actual_hours,
  progress: apiTask.progress || 0,
  tags: apiTask.tags,
  createdAt: apiTask.created_at,
  updatedAt: apiTask.updated_at,
  startedAt: apiTask.started_at,
  completedAt: apiTask.completed_at,
});

export const getTasks = async (
  params?: TaskFilter & { page?: number; pageSize?: number }
): Promise<TaskListResponse> => {
  const response = await api.get('/tasks', { params });
  const data = response.data.data?.map(mapTaskFromApi) || [];
  return {
    data,
    total: response.data.total || 0,
    page: response.data.page || 1,
    pageSize: response.data.pageSize || 20,
  };
};

export const getTaskById = async (id: string): Promise<Task> => {
  const response = await api.get(`/tasks/${id}`);
  return mapTaskFromApi(response.data);
};

export const createTask = async (data: CreateTaskRequest): Promise<Task> => {
  const response = await api.post('/tasks', data);
  return mapTaskFromApi(response.data);
};

export const updateTask = async (
  id: string,
  data: UpdateTaskRequest
): Promise<Task> => {
  const response = await api.put(`/tasks/${id}`, data);
  return mapTaskFromApi(response.data);
};

export const deleteTask = async (id: string): Promise<void> => {
  await api.delete(`/tasks/${id}`);
};

export const batchUpdateTaskStatus = async (
  ids: string[],
  status: string
): Promise<void> => {
  await api.patch('/tasks/batch/status', { ids, status });
};

export const getTaskStatistics = async (): Promise<TaskStatistics> => {
  const response = await api.get('/tasks/statistics');
  return response.data;
};

export const getMyTasks = async (
  params?: { status?: string; page?: number; pageSize?: number }
): Promise<TaskListResponse> => {
  const response = await api.get('/tasks/my', { params });
  const data = response.data.data?.map(mapTaskFromApi) || [];
  return {
    data,
    total: response.data.total || 0,
    page: response.data.page || 1,
    pageSize: response.data.pageSize || 20,
  };
};

export const getKanbanData = async (): Promise<{
  pending: Task[];
  inProgress: Task[];
  review: Task[];
  completed: Task[];
}> => {
  const response = await api.get('/tasks/kanban');
  return {
    pending: response.data.pending?.map(mapTaskFromApi) || [],
    inProgress: response.data.inProgress?.map(mapTaskFromApi) || [],
    review: response.data.review?.map(mapTaskFromApi) || [],
    completed: response.data.completed?.map(mapTaskFromApi) || [],
  };
};
