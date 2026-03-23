/**
 * 龙门客栈业务管理系统 - 路由保护组件
 * ===============================
 * 作者: 厨子 (神厨小福贵)
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../stores/authStore';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAdmin?: boolean;
  requireManager?: boolean;
}

/**
 * 受保护的路由组件
 * - 未登录用户会被重定向到登录页
 * - 需要特定权限的角色会被检查
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireAdmin = false,
  requireManager = false,
}) => {
  const { isAuthenticated, user } = useAuth();
  const location = useLocation();
  
  if (!isAuthenticated || !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  if (requireAdmin && user.role !== 'admin' && !user.is_superuser) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column',
      }}>
        <h2>权限不足</h2>
        <p>您需要管理员权限才能访问此页面</p>
      </div>
    );
  }
  
  if (requireManager) {
    const isManagerRole = ['admin', 'manager'].includes(user.role);
    if (!isManagerRole && !user.is_superuser) {
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column',
        }}>
          <h2>权限不足</h2>
          <p>您需要管理层权限才能访问此页面</p>
        </div>
      );
    }
  }
  
  return <>{children}</>;
};

/**
 * 公开路由组件（不需要认证）
 * - 已登录用户访问登录页会被重定向到首页
 */
export const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, user } = useAuth();
  
  if (isAuthenticated && user) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

export default ProtectedRoute;