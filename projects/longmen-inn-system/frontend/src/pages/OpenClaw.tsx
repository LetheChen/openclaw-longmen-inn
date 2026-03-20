import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Card,
  Table,
  Switch,
  Badge,
  Tag,
  Button,
  Space,
  Row,
  Col,
  Statistic,
  message,
  Typography,
  Spin,
  Alert,
} from 'antd';
import {
  CloudOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  ApiOutlined,
  MessageOutlined,
  NodeIndexOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import {
  getLiveStatus,
  getGatewayStatus,
  subscribeToOpenClawEvents,
  type GatewayStatus,
  type AgentSession,
  type RouteConfig,
  type LiveStatus,
} from '../services/openclawService';
import './OpenClaw.css';

const { Title, Text } = Typography;

const OpenClaw: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [gatewayStatus, setGatewayStatus] = useState<GatewayStatus>({
    status: 'offline',
    last_checked: new Date().toISOString(),
    connected_agents: 0,
    active_sessions: 0,
    message_queue_size: 0,
  });
  
  const [sessions, setSessions] = useState<AgentSession[]>([]);
  const [routes, setRoutes] = useState<RouteConfig[]>([]);
  const [statistics, setStatistics] = useState({
    total_agents: 0,
    active_sessions: 0,
    messages_today: 0,
    tasks_completed: 0,
  });

  const wsRef = useRef<WebSocket | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [liveStatus, gwStatus] = await Promise.all([
        getLiveStatus(),
        getGatewayStatus(),
      ]);
      
      setGatewayStatus(gwStatus);
      setSessions(liveStatus.sessions || []);
      setRoutes(liveStatus.routes || []);
      setStatistics(liveStatus.statistics || {
        total_agents: 0,
        active_sessions: 0,
        messages_today: 0,
        tasks_completed: 0,
      });
    } catch (err: any) {
      console.error('加载数据失败:', err);
      setError(err.message || '加载数据失败');
      message.error('数据加载失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    
    wsRef.current = subscribeToOpenClawEvents(
      (data: any) => {
        if (data.type === 'openclaw_status' || data.type === 'openclaw_heartbeat') {
          const eventData = data.data;
          if (eventData.gateway) {
            setGatewayStatus(eventData.gateway);
          }
          if (eventData.sessions) {
            setSessions(eventData.sessions);
          }
          if (eventData.connected_agents !== undefined) {
            setStatistics(prev => ({
              ...prev,
              total_agents: eventData.connected_agents,
              active_sessions: eventData.active_sessions || prev.active_sessions,
            }));
          }
        }
      },
      (error) => {
        console.error('WebSocket连接错误:', error);
      }
    );
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [fetchData]);

  const handleRefreshStatus = () => {
    message.loading({ content: '正在检查Gateway状态...', key: 'refresh' });
    fetchData();
  };

  const handleToggleRoute = (routeId: string, enabled: boolean) => {
    setRoutes(routes.map(route =>
      route.id === routeId ? { ...route, enabled } : route
    ));
    message.success(`路由已${enabled ? '启用' : '禁用'}`);
  };

  const sessionColumns = [
    {
      title: '会话ID',
      dataIndex: 'id',
      key: 'id',
      width: 150,
      render: (text: string) => <Text code style={{ fontSize: 12 }}>{text.slice(0, 12)}...</Text>,
    },
    {
      title: 'Agent名称',
      dataIndex: 'agent_name',
      key: 'agent_name',
      render: (text: string) => (
        <Space>
          <CloudOutlined style={{ color: '#8B0000' }} />
          <Text strong style={{ color: '#262626' }}>{text}</Text>
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          active: { color: 'success', text: '活跃' },
          idle: { color: 'default', text: '空闲' },
          busy: { color: 'processing', text: '忙碌' },
        };
        const { color, text } = statusMap[status] || { color: 'default', text: status };
        return <Badge status={color as any} text={text} />;
      },
    },
    {
      title: '消息数',
      dataIndex: 'message_count',
      key: 'message_count',
      render: (count: number) => (
        <Tag style={{ fontSize: 12, padding: '2px 8px', borderRadius: 4 }}>{count}</Tag>
      ),
    },
    {
      title: '最后活动',
      dataIndex: 'last_activity',
      key: 'last_activity',
      render: (text: string) => (
        <Text type="secondary" style={{ fontSize: 12 }}>
          {text ? new Date(text).toLocaleString('zh-CN') : '-'}
        </Text>
      ),
    },
  ];

  const routeColumns = [
    {
      title: '路由名称',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => (
        <Space>
          <NodeIndexOutlined style={{ color: '#8B0000' }} />
          <Text strong style={{ color: '#262626' }}>{text}</Text>
        </Space>
      ),
    },
    {
      title: '源',
      dataIndex: 'source',
      key: 'source',
      render: (text: string) => <Tag style={{ fontSize: 12, borderRadius: 4 }}>{text}</Tag>,
    },
    {
      title: '目标',
      dataIndex: 'target',
      key: 'target',
      render: (text: string) => <Text code style={{ fontSize: 12 }}>{text}</Text>,
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority: number) => (
        <Tag color={priority === 1 ? 'gold' : priority === 2 ? 'blue' : 'default'} style={{ fontSize: 12, borderRadius: 4 }}>
          {priority}
        </Tag>
      ),
    },
    {
      title: '消息数',
      dataIndex: 'message_count',
      key: 'message_count',
      render: (count: number) => (
        <Space>
          <MessageOutlined style={{ color: '#8B0000' }} />
          <Text>{count.toLocaleString()}</Text>
        </Space>
      ),
    },
    {
      title: '状态',
      key: 'status',
      render: (_: any, record: RouteConfig) => (
        <Switch
          checked={record.enabled}
          onChange={(checked) => handleToggleRoute(record.id, checked)}
          checkedChildren="启用"
          unCheckedChildren="禁用"
        />
      ),
    },
  ];

  const getStatusIcon = () => {
    switch (gatewayStatus.status) {
      case 'online':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'degraded':
        return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
      default:
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
    }
  };

  const getStatusText = () => {
    switch (gatewayStatus.status) {
      case 'online':
        return '在线';
      case 'degraded':
        return '降级';
      default:
        return '离线';
    }
  };

  const getStatusColor = () => {
    switch (gatewayStatus.status) {
      case 'online':
        return '#52c41a';
      case 'degraded':
        return '#faad14';
      default:
        return '#ff4d4f';
    }
  };

  // 统计卡片数据
  const statCards = [
    {
      title: 'Gateway状态',
      value: getStatusText(),
      icon: getStatusIcon(),
      color: getStatusColor(),
    },
    {
      title: '版本号',
      value: gatewayStatus.version || 'unknown',
      icon: <ApiOutlined />,
      color: '#8B0000',
    },
    {
      title: '运行时间',
      value: gatewayStatus.uptime || '-',
      icon: <CloudOutlined />,
      color: '#1890ff',
    },
    {
      title: '活跃会话',
      value: statistics.active_sessions || sessions.filter(s => s.status === 'active').length,
      icon: <CloudOutlined />,
      color: '#52c41a',
    },
  ];

  if (error) {
    return (
      <div className="page-container openclaw-page">
        <Alert
          message="数据加载失败"
          description={error}
          type="error"
          showIcon
          action={
            <Button 
              type="primary" 
              onClick={fetchData}
              style={{ 
                background: 'linear-gradient(135deg, #8B0000 0%, #c41a1a 100%)',
                border: 'none',
                borderRadius: 8,
              }}
            >
              重试
            </Button>
          }
        />
      </div>
    );
  }

  return (
    <Spin spinning={loading} size="large" tip="数据加载中...">
      <div className="page-container openclaw-page">
        {/* 页面标题 */}
        <div className="page-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h1 className="page-title">
                <CloudOutlined className="page-title-icon" />
                OpenClaw 服务管理
              </h1>
              <p className="page-subtitle">管理OpenClaw Gateway、Agent会话和消息路由配置</p>
            </div>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              size="large"
              onClick={handleRefreshStatus}
              style={{ 
                background: 'linear-gradient(135deg, #8B0000 0%, #c41a1a 100%)',
                border: 'none',
                borderRadius: 8,
                boxShadow: '0 4px 12px rgba(139, 0, 0, 0.3)'
              }}
            >
              刷新状态
            </Button>
          </div>
        </div>

        {/* 统计卡片 */}
        <div className="stats-grid">
          {statCards.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-card-header">
                <div className="stat-card-icon" style={{ color: stat.color }}>
                  {stat.icon}
                </div>
              </div>
              <div className="stat-card-value" style={{ color: stat.color, fontSize: typeof stat.value === 'number' ? 32 : 20 }}>
                {stat.value}
              </div>
              <div className="stat-card-title">{stat.title}</div>
            </div>
          ))}
        </div>

        {/* Agent会话列表 */}
        <div className="content-card" style={{ marginBottom: 24 }}>
          <div className="content-card-header">
            <span className="content-card-title">
              <CloudOutlined style={{ color: '#8B0000' }} />
              Agent会话列表
              <Badge count={sessions.length} style={{ backgroundColor: '#8B0000' }} />
            </span>
          </div>
          <div className="content-card-body" style={{ padding: 0 }}>
            {sessions.length > 0 ? (
              <Table
                className="data-table"
                columns={sessionColumns}
                dataSource={sessions}
                rowKey="id"
                pagination={{ 
                  pageSize: 5,
                  showSizeChanger: true,
                  showTotal: (total) => `共 ${total} 条`,
                  style: { margin: '16px 24px' }
                }}
                size="small"
              />
            ) : (
              <div className="empty-state">
                <CloudOutlined style={{ fontSize: 48, marginBottom: 16, color: '#bfbfbf' }} />
                <p>暂无活跃会话</p>
                <Text type="secondary">OpenClaw Gateway可能未启动或无Agent连接</Text>
              </div>
            )}
          </div>
        </div>

        {/* 消息路由配置 */}
        <div className="content-card">
          <div className="content-card-header">
            <span className="content-card-title">
              <NodeIndexOutlined style={{ color: '#8B0000' }} />
              消息路由配置
              <Badge count={routes.length} style={{ backgroundColor: '#8B0000' }} />
            </span>
          </div>
          <div className="content-card-body" style={{ padding: 0 }}>
            {routes.length > 0 ? (
              <Table
                className="data-table"
                columns={routeColumns}
                dataSource={routes}
                rowKey="id"
                pagination={{ 
                  pageSize: 5,
                  showSizeChanger: true,
                  showTotal: (total) => `共 ${total} 条`,
                  style: { margin: '16px 24px' }
                }}
                size="small"
              />
            ) : (
              <div className="empty-state">
                <NodeIndexOutlined style={{ fontSize: 48, marginBottom: 16, color: '#bfbfbf' }} />
                <p>暂无路由配置</p>
                <Text type="secondary">请配置消息路由规则</Text>
              </div>
            )}
          </div>
        </div>
      </div>
    </Spin>
  );
};

export default OpenClaw;
