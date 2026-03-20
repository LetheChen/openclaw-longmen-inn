import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Select,
  Switch,
  Button,
  Tabs,
  Row,
  Col,
  InputNumber,
  message,
  Space,
  Typography,
} from 'antd';
import {
  SettingOutlined,
  NotificationOutlined,
  SafetyOutlined,
  CloudOutlined,
  MailOutlined,
  MobileOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { TabsProps } from 'antd';
import './Settings.css';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;

const Settings: React.FC = () => {
  const [basicForm] = Form.useForm();
  const [notificationForm] = Form.useForm();
  const [securityForm] = Form.useForm();
  const [loading, setLoading] = useState(false);

  // 保存基本设置
  const handleSaveBasic = async () => {
    try {
      const values = await basicForm.validateFields();
      setLoading(true);
      // 模拟API调用
      setTimeout(() => {
        message.success('基本设置已保存');
        setLoading(false);
      }, 500);
    } catch (error) {
      message.error('请检查表单填写是否正确');
    }
  };

  // 保存通知设置
  const handleSaveNotification = async () => {
    try {
      const values = await notificationForm.validateFields();
      setLoading(true);
      setTimeout(() => {
        message.success('通知设置已保存');
        setLoading(false);
      }, 500);
    } catch (error) {
      message.error('请检查表单填写是否正确');
    }
  };

  // 保存安全设置
  const handleSaveSecurity = async () => {
    try {
      const values = await securityForm.validateFields();
      setLoading(true);
      setTimeout(() => {
        message.success('安全设置已保存');
        setLoading(false);
      }, 500);
    } catch (error) {
      message.error('请检查表单填写是否正确');
    }
  };

  // 基本设置Tab内容
  const basicSettingsContent = (
    <Form
      form={basicForm}
      layout="vertical"
      initialValues={{
        systemName: '龙门客栈业务管理系统',
        systemShortName: '龙门客栈',
        companyName: '龙门客栈科技',
        timezone: 'Asia/Shanghai',
        language: 'zh-CN',
        dateFormat: 'YYYY-MM-DD',
        timeFormat: '24h',
      }}
    >
      <Row gutter={24}>
        <Col xs={24} lg={12}>
          <Form.Item
            label="系统名称"
            name="systemName"
            rules={[{ required: true, message: '请输入系统名称' }]}
          >
            <Input 
              prefix={<SettingOutlined style={{ color: '#8c8c8c' }} />} 
              placeholder="请输入系统名称" 
              style={{ borderRadius: 6 }}
            />
          </Form.Item>
        </Col>
        <Col xs={24} lg={12}>
          <Form.Item
            label="系统简称"
            name="systemShortName"
            rules={[{ required: true, message: '请输入系统简称' }]}
          >
            <Input placeholder="请输入系统简称" style={{ borderRadius: 6 }} />
          </Form.Item>
        </Col>
        <Col xs={24} lg={12}>
          <Form.Item
            label="公司名称"
            name="companyName"
            rules={[{ required: true, message: '请输入公司名称' }]}
          >
            <Input placeholder="请输入公司名称" style={{ borderRadius: 6 }} />
          </Form.Item>
        </Col>
        <Col xs={24} lg={12}>
          <Form.Item
            label="时区"
            name="timezone"
            rules={[{ required: true, message: '请选择时区' }]}
          >
            <Select placeholder="请选择时区" style={{ borderRadius: 6 }}>
              <Option value="Asia/Shanghai">亚洲/上海 (GMT+8)</Option>
              <Option value="Asia/Tokyo">亚洲/东京 (GMT+9)</Option>
              <Option value="Asia/Singapore">亚洲/新加坡 (GMT+8)</Option>
              <Option value="America/New_York">美国/纽约 (GMT-5)</Option>
              <Option value="America/Los_Angeles">美国/洛杉矶 (GMT-8)</Option>
              <Option value="Europe/London">欧洲/伦敦 (GMT+0)</Option>
              <Option value="Europe/Paris">欧洲/巴黎 (GMT+1)</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col xs={24} lg={12}>
          <Form.Item
            label="语言"
            name="language"
            rules={[{ required: true, message: '请选择语言' }]}
          >
            <Select placeholder="请选择语言" style={{ borderRadius: 6 }}>
              <Option value="zh-CN">简体中文</Option>
              <Option value="zh-TW">繁体中文</Option>
              <Option value="en-US">English (US)</Option>
              <Option value="ja-JP">日本語</Option>
              <Option value="ko-KR">한국어</Option>
            </Select>
          </Form.Item>
        </Col>
        <Col xs={24} lg={12}>
          <Form.Item
            label="日期格式"
            name="dateFormat"
            rules={[{ required: true, message: '请选择日期格式' }]}
          >
            <Select placeholder="请选择日期格式" style={{ borderRadius: 6 }}>
              <Option value="YYYY-MM-DD">YYYY-MM-DD</Option>
              <Option value="DD/MM/YYYY">DD/MM/YYYY</Option>
              <Option value="MM/DD/YYYY">MM/DD/YYYY</Option>
              <Option value="YYYY年MM月DD日">YYYY年MM月DD日</Option>
            </Select>
          </Form.Item>
        </Col>
      </Row>

      <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSaveBasic}
          loading={loading}
          size="large"
          style={{ 
            background: 'linear-gradient(135deg, #8B0000 0%, #c41a1a 100%)',
            border: 'none',
            borderRadius: 8,
            boxShadow: '0 4px 12px rgba(139, 0, 0, 0.3)'
          }}
        >
          保存基本设置
        </Button>
      </Form.Item>
    </Form>
  );

  // 通知设置Tab内容
  const notificationSettingsContent = (
    <Form
      form={notificationForm}
      layout="vertical"
      initialValues={{
        emailEnabled: true,
        smsEnabled: false,
        pushEnabled: true,
        emailHost: 'smtp.example.com',
        emailPort: 587,
        emailUsername: 'noreply@example.com',
        smsProvider: 'aliyun',
        pushProvider: 'firebase',
      }}
    >
      <Row gutter={24}>
        <Col xs={24} lg={12}>
          <div className="settings-card" style={{ marginBottom: 24 }}>
            <div className="settings-card-header">
              <MailOutlined style={{ color: '#8B0000', fontSize: 18 }} />
              <span className="settings-card-title">邮件通知</span>
            </div>
            <div className="settings-card-body">
              <Form.Item
                label="启用邮件通知"
                name="emailEnabled"
                valuePropName="checked"
              >
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>

              <Form.Item
                label="SMTP服务器"
                name="emailHost"
              >
                <Input placeholder="smtp.example.com" style={{ borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="SMTP端口"
                name="emailPort"
              >
                <InputNumber min={1} max={65535} style={{ width: '100%', borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="SMTP用户名"
                name="emailUsername"
              >
                <Input placeholder="noreply@example.com" style={{ borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="SMTP密码"
                name="emailPassword"
              >
                <Input.Password placeholder="请输入SMTP密码" style={{ borderRadius: 6 }} />
              </Form.Item>
            </div>
          </div>
        </Col>

        <Col xs={24} lg={12}>
          <div className="settings-card" style={{ marginBottom: 24 }}>
            <div className="settings-card-header">
              <MobileOutlined style={{ color: '#8B0000', fontSize: 18 }} />
              <span className="settings-card-title">短信通知</span>
            </div>
            <div className="settings-card-body">
              <Form.Item
                label="启用短信通知"
                name="smsEnabled"
                valuePropName="checked"
              >
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>

              <Form.Item
                label="短信服务商"
                name="smsProvider"
              >
                <Select placeholder="请选择短信服务商" style={{ borderRadius: 6 }}>
                  <Option value="aliyun">阿里云短信</Option>
                  <Option value="tencent">腾讯云短信</Option>
                  <Option value="huawei">华为云短信</Option>
                  <Option value="twilio">Twilio</Option>
                </Select>
              </Form.Item>

              <Form.Item
                label="AccessKey ID"
                name="smsAccessKeyId"
              >
                <Input placeholder="请输入AccessKey ID" style={{ borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="AccessKey Secret"
                name="smsAccessKeySecret"
              >
                <Input.Password placeholder="请输入AccessKey Secret" style={{ borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="短信签名"
                name="smsSignature"
              >
                <Input placeholder="请输入短信签名" style={{ borderRadius: 6 }} />
              </Form.Item>
            </div>
          </div>
        </Col>
      </Row>

      <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSaveNotification}
          loading={loading}
          size="large"
          style={{ 
            background: 'linear-gradient(135deg, #8B0000 0%, #c41a1a 100%)',
            border: 'none',
            borderRadius: 8,
            boxShadow: '0 4px 12px rgba(139, 0, 0, 0.3)'
          }}
        >
          保存通知设置
        </Button>
      </Form.Item>
    </Form>
  );

  // 安全设置Tab内容
  const securitySettingsContent = (
    <Form
      form={securityForm}
      layout="vertical"
      initialValues={{
        passwordMinLength: 8,
        passwordRequireUppercase: true,
        passwordRequireNumber: true,
        passwordRequireSpecial: true,
        maxLoginAttempts: 5,
        lockoutDuration: 30,
        sessionTimeout: 120,
        twoFactorEnabled: false,
      }}
    >
      <Row gutter={24}>
        <Col xs={24} lg={12}>
          <div className="settings-card" style={{ marginBottom: 24 }}>
            <div className="settings-card-header">
              <SafetyOutlined style={{ color: '#8B0000', fontSize: 18 }} />
              <span className="settings-card-title">密码策略</span>
            </div>
            <div className="settings-card-body">
              <Form.Item
                label="最小密码长度"
                name="passwordMinLength"
                rules={[{ required: true, message: '请输入最小密码长度' }]}
              >
                <InputNumber min={6} max={32} style={{ width: '100%', borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="要求大写字母"
                name="passwordRequireUppercase"
                valuePropName="checked"
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>

              <Form.Item
                label="要求数字"
                name="passwordRequireNumber"
                valuePropName="checked"
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>

              <Form.Item
                label="要求特殊字符"
                name="passwordRequireSpecial"
                valuePropName="checked"
              >
                <Switch checkedChildren="是" unCheckedChildren="否" />
              </Form.Item>
            </div>
          </div>
        </Col>

        <Col xs={24} lg={12}>
          <div className="settings-card" style={{ marginBottom: 24 }}>
            <div className="settings-card-header">
              <CloudOutlined style={{ color: '#8B0000', fontSize: 18 }} />
              <span className="settings-card-title">登录安全</span>
            </div>
            <div className="settings-card-body">
              <Form.Item
                label="最大登录尝试次数"
                name="maxLoginAttempts"
                rules={[{ required: true, message: '请输入最大登录尝试次数' }]}
              >
                <InputNumber min={3} max={10} style={{ width: '100%', borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="锁定时间（分钟）"
                name="lockoutDuration"
                rules={[{ required: true, message: '请输入锁定时间' }]}
              >
                <InputNumber min={5} max={60} style={{ width: '100%', borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="会话超时时间（分钟）"
                name="sessionTimeout"
                rules={[{ required: true, message: '请输入会话超时时间' }]}
              >
                <InputNumber min={15} max={480} style={{ width: '100%', borderRadius: 6 }} />
              </Form.Item>

              <Form.Item
                label="启用双因素认证"
                name="twoFactorEnabled"
                valuePropName="checked"
              >
                <Switch checkedChildren="启用" unCheckedChildren="禁用" />
              </Form.Item>
            </div>
          </div>
        </Col>
      </Row>

      <Form.Item style={{ marginBottom: 0, marginTop: 24 }}>
        <Space>
          <Button
            type="primary"
            icon={<SaveOutlined />}
            onClick={handleSaveSecurity}
            loading={loading}
            size="large"
            style={{ 
              background: 'linear-gradient(135deg, #8B0000 0%, #c41a1a 100%)',
              border: 'none',
              borderRadius: 8,
              boxShadow: '0 4px 12px rgba(139, 0, 0, 0.3)'
            }}
          >
            保存安全设置
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => securityForm.resetFields()}
            size="large"
            style={{ borderRadius: 8 }}
          >
            重置
          </Button>
        </Space>
      </Form.Item>
    </Form>
  );

  // Tab配置
  const tabItems: TabsProps['items'] = [
    {
      key: 'basic',
      label: (
        <Space>
          <SettingOutlined />
          基本设置
        </Space>
      ),
      children: basicSettingsContent,
    },
    {
      key: 'notification',
      label: (
        <Space>
          <NotificationOutlined />
          通知配置
        </Space>
      ),
      children: notificationSettingsContent,
    },
    {
      key: 'security',
      label: (
        <Space>
          <SafetyOutlined />
          安全设置
        </Space>
      ),
      children: securitySettingsContent,
    },
  ];

  return (
    <div className="page-container settings-page">
      {/* 页面标题 */}
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h1 className="page-title">
              <SettingOutlined className="page-title-icon" />
              系统设置
            </h1>
            <p className="page-subtitle">配置系统基本参数、通知服务和安全策略</p>
          </div>
        </div>
      </div>

      {/* 设置Tab页 */}
      <div className="content-card">
        <Tabs 
          items={tabItems} 
          type="card" 
          style={{ padding: '0 24px' }}
        />
      </div>
    </div>
  );
};

export default Settings;
