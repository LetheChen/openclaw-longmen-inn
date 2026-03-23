/**
 * 龙门客栈业务管理系统 - 认证状态管理
 * ===============================
 * 作者: 厨子 (神厨小福贵)
 * 
 * 使用 Zustand 管理用户认证状态
 */

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { message } from 'antd';
import api, { getCurrentUser, login as apiLogin, logout as apiLogout } from '../services/api';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
  agent_id: string | null;
  created_at: string;
  last_login_at: string | null;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (username: string, password: string, rememberMe?: boolean) => Promise<boolean>;
  logout: () => Promise<void>;
  fetchCurrentUser: () => Promise<User | null>;
  setUser: (user: User | null) => void;
  clearError: () => void;
}

/**
 * 认证状态Store
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (username: string, password: string, rememberMe: boolean = false) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await apiLogin(username, password, rememberMe);
          const user = response.user;
          
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          message.success(`欢迎回来，${user.full_name || user.username}！`);
          return true;
          
        } catch (error: any) {
          const errorMessage = error.response?.data?.detail || '登录失败，请检查用户名和密码';
          set({
            isLoading: false,
            error: errorMessage,
            user: null,
            isAuthenticated: false,
          });
          message.error(errorMessage);
          return false;
        }
      },
      
      logout: async () => {
        set({ isLoading: true });
        
        try {
          await apiLogout();
        } catch (error) {
          // 忽略登出错误
          console.warn('Logout request failed:', error);
        }
        
        set({
          user: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
        
        message.info('已退出登录');
      },
      
      fetchCurrentUser: async () => {
        set({ isLoading: true });
        
        try {
          const user = await getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          return user;
        } catch (error) {
          // Token失效或未登录
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
          return null;
        }
      },
      
      setUser: (user: User | null) => {
        set({
          user,
          isAuthenticated: !!user,
        });
      },
      
      clearError: () => {
        set({ error: null });
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => sessionStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        if (state && state.isAuthenticated && !state.user) {
          state.isAuthenticated = false;
        }
      },
    }
  )
);

/**
 * 认证状态Hook
 */
export function useAuth() {
  const { user, isAuthenticated, isLoading, error, login, logout, fetchCurrentUser, clearError } = useAuthStore();
  
  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    fetchCurrentUser,
    clearError,
    
    // 辅助方法
    isAdmin: user?.role === 'admin' || user?.role === 'superuser',
    isManager: user?.role === 'admin' || user?.role === 'manager' || user?.role === 'superuser',
  };
}

export default useAuthStore;