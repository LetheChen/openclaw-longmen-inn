/**
 * 龙门客栈业务管理系统 - API客户端
 * ===============================
 * 作者: 厨子 (神厨小福贵)
 * 
 * 安全的HTTP客户端，使用Cookie进行认证
 * - Cookie HttpOnly：防止XSS攻击
 * - SameSite Strict：防止CSRF攻击
 * - 自动刷新令牌
 */

import axios, { AxiosInstance, AxiosError, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { message } from 'antd';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000, // 缩短超时时间
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // 重要：发送Cookie
});

// CSRF Token 缓存
let csrfToken: string | null = null;

/**
 * 获取CSRF Token
 */
async function getCsrfToken(): Promise<string> {
  if (csrfToken) {
    return csrfToken;
  }
  
  try {
    const response = await axios.get('/api/v1/auth/csrf-token', {
      withCredentials: true,
    });
    csrfToken = response.data.csrf_token;
    return csrfToken || '';
  } catch (error) {
    console.error('获取CSRF Token失败:', error);
    return '';
  }
}

/**
 * 刷新访问令牌
 */
async function refreshAccessToken(): Promise<boolean> {
  try {
    const response = await axios.post('/api/v1/auth/refresh', {}, {
      withCredentials: true,
    });
    
    // 更新CSRF Token
    const newCsrfToken = response.headers['x-csrf-token'];
    if (newCsrfToken) {
      csrfToken = newCsrfToken;
    }
    
    return true;
  } catch (error) {
    // 刷新失败，清除状态
    csrfToken = null;
    return false;
  }
}

// 请求拦截器
api.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
    // 获取并设置CSRF Token（仅对需要修改的操作）
    const method = config.method?.toUpperCase();
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method || '')) {
      if (!csrfToken) {
        csrfToken = await getCsrfToken();
      }
      if (csrfToken) {
        config.headers['X-CSRF-Token'] = csrfToken;
      }
    }
    
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 从响应头更新CSRF Token
    const newCsrfToken = response.headers['x-csrf-token'];
    if (newCsrfToken) {
      csrfToken = newCsrfToken;
    }
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    if (!error.response) {
      // 网络错误
      message.error('网络连接失败，请检查网络');
      return Promise.reject(error);
    }
    
    const { status, data } = error.response;
    
    switch (status) {
      case 401:
        // 未授权
        if (originalRequest && !(originalRequest as any)._retry) {
          // 尝试刷新令牌
          (originalRequest as any)._retry = true;
          
          const refreshed = await refreshAccessToken();
          
          if (refreshed) {
            // 刷新成功，重试原请求
            return api(originalRequest);
          }
        }
        
        // 刷新失败或已是刷新请求，跳转到登录页
        if (window.location.pathname !== '/login') {
          message.warning('登录已过期，请重新登录');
          window.location.href = '/login';
        }
        break;
        
      case 403:
        // 权限不足
        const forbiddenMsg = (data as any)?.detail || '没有权限执行此操作';
        message.error(forbiddenMsg);
        break;
        
      case 404:
        // 资源不存在
        console.error('请求的资源不存在');
        break;
        
      case 422:
        // 验证错误
        const validationErrors = (data as any)?.detail;
        if (Array.isArray(validationErrors)) {
          const messages = validationErrors.map((e: any) => e.msg).join(', ');
          message.error(messages);
        } else if (typeof validationErrors === 'string') {
          message.error(validationErrors);
        }
        break;
        
      case 429:
        // 请求过于频繁
        message.error('请求过于频繁，请稍后再试');
        break;
        
      case 500:
        // 服务器错误
        message.error('服务器内部错误，请稍后再试');
        break;
        
      case 502:
      case 503:
      case 504:
        // 服务不可用
        message.error('服务暂时不可用，请稍后再试');
        break;
        
      default:
        console.error(`请求错误: ${status}`, data);
    }
    
    return Promise.reject(error);
  }
);

/**
 * 登录
 */
export async function login(username: string, password: string, rememberMe: boolean = false) {
  const response = await api.post('/auth/login', {
    username,
    password,
    remember_me: rememberMe,
  }, {
    withCredentials: true,
  });
  
  // 获取CSRF Token
  await getCsrfToken();
  
  return response.data;
}

/**
 * 登出
 */
export async function logout() {
  const response = await api.post('/auth/logout', {}, {
    withCredentials: true,
  });
  
  // 清除CSRF Token
  csrfToken = null;
  
  return response.data;
}

/**
 * 获取当前用户信息
 */
export async function getCurrentUser() {
  const response = await api.get('/auth/me', {
    withCredentials: true,
  });
  return response.data;
}

/**
 * 注册（仅开发环境或管理员可用）
 */
export async function register(userData: {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}) {
  const response = await api.post('/auth/register', userData, {
    withCredentials: true,
  });
  return response.data;
}

/**
 * 刷新令牌
 */
export async function refreshToken() {
  const response = await api.post('/auth/refresh', {}, {
    withCredentials: true,
  });
  return response.data;
}

/**
 * 修改密码
 */
export async function changePassword(currentPassword: string, newPassword: string) {
  const response = await api.post('/auth/change-password', {
    current_password: currentPassword,
    new_password: newPassword,
  }, {
    withCredentials: true,
  });
  return response.data;
}

/**
 * 登出所有设备
 */
export async function logoutAllDevices() {
  const response = await api.post('/auth/logout-all', {}, {
    withCredentials: true,
  });
  
  // 清除CSRF Token
  csrfToken = null;
  
  return response.data;
}

/**
 * 获取CSRF Token
 */
export async function fetchCsrfToken() {
  await getCsrfToken();
  return csrfToken;
}

export default api;