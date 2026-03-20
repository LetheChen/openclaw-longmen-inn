import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Avatar,
  Badge,
  Tag,
  Typography,
  Button,
  Space,
  Tooltip,
  Input,
  Select,
  Empty,
  Spin,
  message,
} from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  TrophyOutlined,
  FireOutlined,
  SearchOutlined,
  PlusOutlined,
  MessageOutlined,
  StarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  FilterOutlined,
  CrownOutlined,
  IdcardOutlined,
} from '@ant-design/icons';
import type { Agent } from '../types/agent';
import { getAgents, getAgentStatistics } from '../services/agentService';
import './Agents.css';

const { Text } = Typography;
const { Option } = Select;

const Agents: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [stats, setStats] = useState({
    total: 0,
    online: 0,
    busy: 0,
    offline: 0,
  });

  const loadAgents = useCallback(async () => {
    setLoading(true);
    try {
      const [agentsData, statistics] = await Promise.all([
        getAgents().catch(() => []),
        getAgentStatistics().catch(() => ({ total: 0, online: 0, offline: 0, busy: 0, idle: 0 })),
      ]);
      
      if (agentsData && agentsData.length > 0) {
        setAgents(agentsData);
      }
      
      setStats({
        total: statistics.total || 0,
        online: statistics.online || 0,
        busy: statistics.busy || 0,
        offline: statistics.offline || 0,
      });
    } catch (err: any) {
      console.error('加载伙计数据失败:', err);
      message.error('加载伙计数据失败');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAgents();
  }, [loadAgents]);

  // 状态配置 - 江湖风
  const statusConfig = {
    idle: { 
      color: '#228B22', 
      text: '空闲', 
      icon: <CheckCircleOutlined />,
      bgColor: 'rgba(34, 139, 34, 0.1)'
    },
    busy: { 
      color: '#DC143C', 
      text: '忙碌', 
      icon: <FireOutlined />,
      bgColor: 'rgba(220, 20, 60, 0.1)'
    },
    offline: { 
      color: '#7a7a7a', 
      text: '离线', 
      icon: <ClockCircleOutlined />,
      bgColor: 'rgba(122, 122, 122, 0.1)'
    },
  };

  const filteredAgents = agents.filter((agent) => {
    const matchSearch =
      agent.name.toLowerCase().includes(searchText.toLowerCase()) ||
      (agent.title && agent.title.toLowerCase().includes(searchText.toLowerCase()));
    const matchStatus = statusFilter === 'all' || agent.status === statusFilter;
    return matchSearch && matchStatus;
  });

  // 等级名称 - 江湖风
  const getLevelName = (level: number): string => {
    const levelNames: Record<number, string> = {
      1: '新手伙计',
      2: '熟练工',
      3: '老师傅',
      4: '大管家',
      5: '传奇掌柜',
      6: '龙门传说',
    };
    return levelNames[level] || '未知等级';
  };

  const statCards = [
    { title: '总伙计', value: stats.total, icon: <TeamOutlined />, color: '#8B0000', desc: '客栈伙计总数' },
    { title: '在线', value: stats.online, icon: <CheckCircleOutlined />, color: '#228B22', desc: '可接任务的伙计' },
    { title: '忙碌中', value: stats.busy, icon: <FireOutlined />, color: '#DC143C', desc: '正在执行任务的伙计' },
    { title: '离线', value: stats.offline, icon: <ClockCircleOutlined />, color: '#7a7a7a', desc: '暂时离线的伙计' },
  ];

  return (
    <Spin spinning={loading} size="large" tip="加载伙计数据...">
      <div className="page-container agents-page">
        {/* 页面标题 - 伙计堂 */}
        <div className="page-header">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div className="page-title-wrapper">
              <h1 className="page-title">
                <IdcardOutlined className="page-title-icon" />
                伙计堂
              </h1>
              <p className="page-subtitle">招揽江湖好汉，管理客栈人手，分配江湖任务</p>
            </div>
            <Space>
              <Button 
                icon={<ReloadOutlined />} 
                onClick={loadAgents}
                className="refresh-btn"
              >
                刷新
              </Button>
              <Button 
                type="primary" 
                icon={<PlusOutlined />}
                className="add-agent-btn"
              >
                招募伙计
              </Button>
            </Space>
          </div>
        </div>

        {/* 统计卡片 - 木牌风格 */}
        <div className="stats-grid">
          {statCards.map((stat, index) => (
            <div key={index} className="stat-card">
              <div className="stat-card-header">
                <div className="stat-card-icon" style={{ color: stat.color }}>
                  {stat.icon}
                </div>
              </div>
              <div className="stat-card-value" style={{ color: stat.color }}>
                {stat.value}
              </div>
              <div className="stat-card-title">{stat.title}</div>
              <div style={{ fontSize: 11, color: '#999', marginTop: 4, fontFamily: 'var(--font-family-serif)' }}>
                {stat.desc}
              </div>
            </div>
          ))}
        </div>

        {/* 搜索和筛选 - 案台风格 */}
        <div className="filter-bar">
          <Input
            placeholder="搜索伙计名称或称号"
            prefix={<SearchOutlined style={{ color: '#8c8c8c' }} />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
            style={{ width: 280, borderRadius: 6 }}
          />
          <Select
            placeholder="状态筛选"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 140, borderRadius: 6 }}
            allowClear
            suffixIcon={<FilterOutlined />}
          >
            <Option value="all">全部状态</Option>
            <Option value="idle">空闲</Option>
            <Option value="busy">忙碌</Option>
            <Option value="offline">离线</Option>
          </Select>
        </div>

        {/* Agent卡片网格 - 木牌风格 */}
        {filteredAgents.length > 0 ? (
          <div className="card-grid">
            {filteredAgents.map((agent) => {
              const statusInfo = statusConfig[agent.status as keyof typeof statusConfig] || statusConfig.offline;
              return (
                <Card
                  key={agent.agent_id}
                  className="card-item agent-card"
                  hoverable
                  bodyStyle={{ padding: 0 }}
                >
                  {/* 卡片头部 - 头像和基本信息 */}
                  <div className="card-item-header agent-card-header">
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <Badge
                        dot
                        color={statusInfo.color}
                        offset={[-4, 4]}
                      >
                        <Avatar
                          size={56}
                          className="agent-avatar"
                          style={{
                            backgroundColor: '#8B0000',
                            fontSize: 24,
                            border: '3px solid #D4C4A8',
                          }}
                        >
                          {agent.name[0]}
                        </Avatar>
                      </Badge>
                      <div style={{ marginLeft: 14, flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <Text strong style={{ fontSize: 17, color: '#262626', fontFamily: 'var(--font-family-serif)' }}>
                            {agent.name}
                          </Text>
                        </div>
                        <div style={{ marginTop: 6 }}>
                          <Tag
                            color={statusInfo.color}
                            icon={statusInfo.icon}
                            style={{ 
                              fontSize: 11, 
                              borderRadius: 4,
                              background: statusInfo.bgColor,
                              border: `1px solid ${statusInfo.color}`,
                              fontFamily: 'var(--font-family-serif)',
                            }}
                          >
                            {statusInfo.text}
                          </Tag>
                          {agent.title && (
                            <Tag 
                              color="#DAA520" 
                              style={{ 
                                marginLeft: 4, 
                                fontSize: 11, 
                                borderRadius: 4,
                                background: 'rgba(218, 165, 32, 0.1)',
                                border: '1px solid #DAA520',
                                fontFamily: 'var(--font-family-serif)',
                              }}
                            >
                              <CrownOutlined /> {agent.title}
                            </Tag>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* 卡片主体 */}
                  <div className="card-item-body">
                    {/* 职责描述 */}
                    {agent.role_description && (
                      <div className="role-description">
                        <Text type="secondary" style={{ fontSize: 11, fontFamily: 'var(--font-family-serif)' }}>
                          职责描述
                        </Text>
                        <div style={{ marginTop: 4 }}>
                          <Text style={{ fontSize: 13, color: '#262626', fontFamily: 'var(--font-family-serif)' }}>
                            {agent.role_description}
                          </Text>
                        </div>
                      </div>
                    )}

                    {/* 统计数据 - 令牌风格 */}
                    <div className="agent-stats">
                      <div style={{ textAlign: 'center' }}>
                        <Text strong style={{ fontSize: 22, color: '#8B0000', fontFamily: 'var(--font-family-serif)' }}>
                          {agent.longmenling || 0}
                        </Text>
                        <div>
                          <Text type="secondary" style={{ fontSize: 11, fontFamily: 'var(--font-family-serif)' }}>
                            <TrophyOutlined style={{ color: '#DAA520' }} /> 龙门令
                          </Text>
                        </div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <Text strong style={{ fontSize: 22, color: '#228B22', fontFamily: 'var(--font-family-serif)' }}>
                          Lv.{agent.level || 1}
                        </Text>
                        <div>
                          <Text type="secondary" style={{ fontSize: 11, fontFamily: 'var(--font-family-serif)' }}>
                            {getLevelName(agent.level || 1)}
                          </Text>
                        </div>
                      </div>
                    </div>

                    {/* 座右铭 */}
                    {agent.motto && (
                      <div className="agent-motto">
                        <Text style={{ fontSize: 12, fontStyle: 'italic', color: '#8B0000', fontFamily: 'var(--font-family-serif)' }}>
                          "{agent.motto}"
                        </Text>
                      </div>
                    )}
                  </div>

                  {/* 卡片底部 */}
                  <div className="card-item-footer agent-card-footer" style={{ display: 'flex', gap: 8 }}>
                    <Button 
                      type="primary" 
                      icon={<MessageOutlined />} 
                      block
                      className="contact-btn"
                    >
                      联系
                    </Button>
                    <Tooltip title="分配任务">
                      <Button icon={<PlusOutlined />} className="assign-btn" />
                    </Tooltip>
                  </div>
                </Card>
              );
            })}
          </div>
        ) : (
          <div className="empty-state">
            <Empty
              description={
                <span style={{ fontFamily: 'var(--font-family-serif)' }}>
                  {loading ? '加载中...' : '暂无伙计数据'}
                  <br />
                  <Text type="secondary" style={{ fontSize: 12, fontFamily: 'var(--font-family-serif)' }}>
                    请确保后端服务已启动并初始化数据
                  </Text>
                </span>
              }
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
          </div>
        )}
      </div>
    </Spin>
  );
};

export default Agents;
