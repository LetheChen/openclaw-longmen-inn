/**
 * 龙门客栈业务管理系统 - 登录页面
 * ===============================
 * 作者: 厨子 (神厨小福贵)
 * 
 * 江湖风登录界面
 */

import React, { useState, useEffect } from 'react';
import { Form, Input, Button, Checkbox, message, Typography, Card } from 'antd';
import { UserOutlined, LockOutlined, ShopOutlined } from '@ant-design/icons';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../stores/authStore';
import type { User } from '../stores/authStore';
import './Login.css';

const { Title, Text, Paragraph } = Typography;

interface LoginFormValues {
  username: string;
  password: string;
  rememberMe: boolean;
}

const LoginPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isAuthenticated } = useAuth();
  
  const from = (location.state as any)?.from?.pathname || '/';
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);
  
  const handleSubmit = async (values: LoginFormValues) => {
    setLoading(true);
    
    try {
      const success = await login(values.username, values.password, values.rememberMe);
      
      if (success) {
        navigate(from, { replace: true });
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="login-page">
      {/* 背景装饰 */}
      <div className="login-background">
        <div className="inn-sign">
          <ShopOutlined className="inn-sign-icon" />
          <span className="inn-sign-text">龙门客栈</span>
        </div>
      </div>
      
      {/* 登录表单卡片 */}
      <Card className="login-card" bordered={false}>
        <div className="login-header">
          <div className="login-logo">
            <ShopOutlined />
          </div>
          <Title level={2} className="login-title">
            龙门客栈
          </Title>
          <Text type="secondary" className="login-subtitle">
            江湖路远，客栈欢迎
          </Text>
        </div>
        
        <Form
          form={form}
          name="login-form"
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
          className="login-form"
          initialValues={{ rememberMe: true }}
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              size="large"
              autoComplete="username"
            />
          </Form.Item>
          
          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
              autoComplete="current-password"
            />
          </Form.Item>
          
          <Form.Item name="rememberMe" valuePropName="checked" noStyle>
            <Checkbox>记住我（7天内免登录）</Checkbox>
          </Form.Item>
          
          <Form.Item style={{ marginBottom: 8 }}>
            <Button
              type="primary"
              htmlType="submit"
              size="large"
              block
              loading={loading}
              className="login-button"
            >
              {loading ? '登录中...' : '登 录'}
            </Button>
          </Form.Item>
          
          {/* 开发环境提示（不显示具体密码） */}
          {import.meta.env.DEV && (
            <div className="dev-hint">
              <Paragraph type="secondary" style={{ marginBottom: 8, fontSize: 12 }}>
                开发环境请联系东家获取测试账户
              </Paragraph>
            </div>
          )}
        </Form>
        
        <div className="login-footer">
          <Text type="secondary">
            首次登录请联系掌柜开设账户
          </Text>
        </div>
      </Card>
      
      {/* 底部信息 */}
      <div className="login-bottom">
        <Text type="secondary">
          © 2026 龙门客栈 · 基于OpenClaw架构
        </Text>
      </div>
    </div>
  );
};

export default LoginPage;