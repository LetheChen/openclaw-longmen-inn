/**
 * 龙门客栈业务管理系统 - 个人中心页面
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Avatar,
  Space,
  Typography,
  Divider,
  message,
  Row,
  Col,
  Tag,
  Spin,
  Popconfirm,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  LockOutlined,
  SafetyOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  SaveOutlined,
  EditOutlined,
  CloseOutlined,
  ReloadOutlined,
  EnvironmentOutlined,
} from '@ant-design/icons';
import { useAuth, User } from '../stores/authStore';
import { getCurrentUser, changePassword } from '../services/api';
import './Profile.css';

const { Title, Text } = Typography;

/**
 * 角色标签颜色映射
 */
const roleColors: Record<string, string> = {
  admin: '#c41a1a',
  manager: '#fa8c16',
  worker: '#1890ff',
  guest: '#999',
};

/**
 * 角色中文映射
 */
const roleLabels: Record<string, string> = {
  admin: '管理员',
  manager: '管理层',
  worker: '伙计',
  guest: '访客',
};

const Profile: React.FC = () => {
  const { user: authUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [userInfo, setUserInfo] = useState<User | null>(null);
  const [passwordForm] = Form.useForm();
  const [infoForm] = Form.useForm();

  // 获取最新用户信息
  const fetchUserInfo = async () => {
    try {
      const user = await getCurrentUser();
      setUserInfo(user);
      infoForm.setFieldsValue({
        full_name: user.full_name,
        email: user.email,
      });
    } catch (error) {
      message.error('获取用户信息失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserInfo();
  }, []);

  // 格式化时间
  const formatDateTime = (dateString: string | null) => {
    if (!dateString) return '暂无记录';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 保存个人信息编辑
  const handleSaveEdit = async () => {
    try {
      const values = await infoForm.validateFields();
      setSaving(true);
      
      // TODO: 调用更新个人信息API
      // await updateProfile(values);
      
      message.success('个人信息更新成功');
      setIsEditing(false);
      fetchUserInfo();
    } catch (error) {
      // 表单验证失败
    } finally {
      setSaving(false);
    }
  };

  // 修改密码
  const handlePasswordChange = async () => {
    try {
      const values = await passwordForm.validateFields();
      setSaving(true);
      
      await changePassword(values.current_password, values.new_password);
      
      message.success('密码修改成功！请使用新密码重新登录。');
      passwordForm.resetFields();
      setShowPasswordForm(false);
      
      setTimeout(() => {
        window.location.href = '/login';
      }, 1500);
      
    } catch (error: any) {
      if (error.errorFields) return;
      const errorMsg = error.response?.data?.detail || '密码修改失败';
      message.error(errorMsg);
    } finally {
      setSaving(false);
    }
  };

  // 取消编辑
  const handleCancelEdit = () => {
    infoForm.setFieldsValue({
      full_name: userInfo?.full_name,
      email: userInfo?.email,
    });
    setIsEditing(false);
  };

  if (loading) {
    return (
      <div className="page-container profile-page">
        <div className="profile-loading">
          <Spin size="large" />
          <Text className="loading-text">正在加载...</Text>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container profile-page">
      {/* 页面标题 */}
      <div className="page-header">
        <div className="header-content">
          <div>
            <h1 className="page-title">
              <UserOutlined className="page-title-icon" />
              个人中心
            </h1>
            <p className="page-subtitle">查看和管理您的账户信息</p>
          </div>
          <Space size={12} className="header-actions">
            {!isEditing ? (
              <Button
                type="primary"
                icon={<EditOutlined />}
                onClick={() => setIsEditing(true)}
                className="edit-btn"
              >
                编辑信息
              </Button>
            ) : (
              <Space size={8}>
                <Button
                  icon={<CloseOutlined />}
                  onClick={handleCancelEdit}
                >
                  取消
                </Button>
                <Button
                  type="primary"
                  icon={<SaveOutlined />}
                  onClick={handleSaveEdit}
                  loading={saving}
                  className="save-btn"
                >
                  保存
                </Button>
              </Space>
            )}
            {!showPasswordForm ? (
              <Button
                icon={<LockOutlined />}
                onClick={() => setShowPasswordForm(true)}
                className="password-btn"
              >
                修改密码
              </Button>
            ) : (
              <Popconfirm
                title="取消修改密码？"
                description="确定要放弃当前的密码修改吗？"
                onConfirm={() => {
                  passwordForm.resetFields();
                  setShowPasswordForm(false);
                }}
                okText="确定"
                cancelText="取消"
              >
                <Button icon={<CloseOutlined />}>取消修改</Button>
              </Popconfirm>
            )}
          </Space>
        </div>
      </div>

      <Row gutter={[24, 24]}>
        {/* 左侧：个人信息 */}
        <Col xs={24} lg={showPasswordForm ? 12 : 24}>
          <Card className="profile-card info-card">
            <div className="info-card-header">
              <Avatar 
                size={72} 
                icon={<UserOutlined />} 
                className="profile-avatar"
              />
              <div className="profile-basic">
                <Text className="profile-name">
                  {isEditing ? (
                    <Form.Item name="full_name" style={{ marginBottom: 0 }}>
                      <Input 
                        placeholder="请输入姓名" 
                        className="name-input"
                      />
                    </Form.Item>
                  ) : (
                    userInfo?.full_name || userInfo?.username || '未设置'
                  )}
                </Text>
                <Space size={8} className="profile-tags">
                  <Tag color={roleColors[userInfo?.role || 'worker']}>
                    {roleLabels[userInfo?.role || 'worker']}
                  </Tag>
                  {userInfo?.is_superuser && (
                    <Tag color="gold">超级管理员</Tag>
                  )}
                </Space>
              </div>
            </div>

            <Divider className="card-divider" />

            <Form
              form={infoForm}
              layout="vertical"
              className={`info-form ${isEditing ? 'editing' : ''}`}
            >
              <div className="info-list">
                <div className="info-row">
                  <div className="info-label">
                    <UserOutlined /> 用户名
                  </div>
                  <div className="info-value readonly">{userInfo?.username}</div>
                </div>
                
                <div className="info-row">
                  <div className="info-label">
                    <MailOutlined /> 邮箱
                  </div>
                  <div className="info-value">
                    {isEditing ? (
                      <Form.Item name="email" style={{ marginBottom: 0 }}>
                        <Input placeholder="请输入邮箱" className="value-input" />
                      </Form.Item>
                    ) : (
                      userInfo?.email
                    )}
                  </div>
                </div>
                
                <div className="info-row">
                  <div className="info-label">
                    <EnvironmentOutlined /> 姓名
                  </div>
                  <div className="info-value">
                    {isEditing ? (
                      <Form.Item name="full_name" style={{ marginBottom: 0 }} className="hidden-item">
                        <Input placeholder="请输入姓名" className="value-input" />
                      </Form.Item>
                    ) : (
                      userInfo?.full_name || '-'
                    )}
                  </div>
                </div>
                
                <div className="info-row">
                  <div className="info-label">
                    <ClockCircleOutlined /> 上次登录
                  </div>
                  <div className="info-value readonly">{formatDateTime(userInfo?.last_login_at || null)}</div>
                </div>
                
                <div className="info-row">
                  <div className="info-label">
                    <CheckCircleOutlined /> 账户状态
                  </div>
                  <div className="info-value">
                    <Tag color={userInfo?.is_active ? 'success' : 'error'}>
                      {userInfo?.is_active ? '已激活' : '已禁用'}
                    </Tag>
                  </div>
                </div>

                <div className="info-row">
                  <div className="info-label">
                    <SafetyOutlined /> 账户类型
                  </div>
                  <div className="info-value readonly">
                    {roleLabels[userInfo?.role || 'worker']}
                  </div>
                </div>
              </div>
            </Form>
          </Card>
        </Col>

        {/* 右侧：修改密码表单（条件显示） */}
        {showPasswordForm && (
          <Col xs={24} lg={12}>
            <Card className="profile-card password-card">
              <div className="password-card-header">
                <LockOutlined className="password-icon" />
                <div>
                  <Title level={4} className="password-title">修改密码</Title>
                  <Text className="password-subtitle">定期更换密码，保障账户安全</Text>
                </div>
              </div>

              <Divider className="card-divider" />

              <Form
                form={passwordForm}
                layout="vertical"
                className="password-form"
              >
                <Form.Item
                  name="current_password"
                  label="当前密码"
                  rules={[{ required: true, message: '请输入当前密码' }]}
                >
                  <Input.Password
                    prefix={<LockOutlined className="input-icon" />}
                    placeholder="请输入当前密码"
                    size="large"
                  />
                </Form.Item>

                <Form.Item
                  name="new_password"
                  label="新密码"
                  rules={[
                    { required: true, message: '请输入新密码' },
                    { min: 6, message: '密码至少6位' },
                    { max: 32, message: '密码最多32位' },
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined className="input-icon" />}
                    placeholder="请输入新密码（6-32位）"
                    size="large"
                  />
                </Form.Item>

                <Form.Item
                  name="confirm_password"
                  label="确认新密码"
                  dependencies={['new_password']}
                  rules={[
                    { required: true, message: '请确认新密码' },
                    ({ getFieldValue }) => ({
                      validator(_, value) {
                        if (!value || getFieldValue('new_password') === value) {
                          return Promise.resolve();
                        }
                        return Promise.reject(new Error('两次输入的密码不一致'));
                      },
                    }),
                  ]}
                >
                  <Input.Password
                    prefix={<LockOutlined className="input-icon" />}
                    placeholder="请再次输入新密码"
                    size="large"
                  />
                </Form.Item>

                <div className="password-tips">
                  <SafetyOutlined className="tips-icon" />
                  <Text className="tips-text">
                    修改密码后，您需要使用新密码重新登录。所有已登录的设备将自动登出。
                  </Text>
                </div>

                <Form.Item className="form-actions">
                  <Space size={12}>
                    <Button
                      type="primary"
                      icon={<SaveOutlined />}
                      onClick={handlePasswordChange}
                      loading={saving}
                      size="large"
                      className="submit-btn"
                    >
                      确认修改
                    </Button>
                    <Button
                      icon={<ReloadOutlined />}
                      onClick={() => passwordForm.resetFields()}
                      size="large"
                    >
                      重置
                    </Button>
                  </Space>
                </Form.Item>
              </Form>
            </Card>
          </Col>
        )}
      </Row>
    </div>
  );
};

export default Profile;
