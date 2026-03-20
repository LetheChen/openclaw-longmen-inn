import React from 'react';
import { List, Avatar, Tag, Typography, Empty, Spin, Space } from 'antd';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  EditOutlined,
  TrophyOutlined,
  UserOutlined,
  CheckSquareOutlined,
} from '@ant-design/icons';
import type { AgentActivity, ActivityType } from '../../types/agent';
import { ActivityType as ActivityTypeEnum } from '../../types/agent';
import './ActivityFeed.css';

const { Text } = Typography;

export interface ActivityFeedProps {
  activities: AgentActivity[];
  loading?: boolean;
  className?: string;
  style?: React.CSSProperties;
  onActivityClick?: (activity: AgentActivity) => void;
}

const activityTypeConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  task_created: { icon: <PlusOutlined />, color: '#1890ff', label: '创建任务' },
  task_started: { icon: <ClockCircleOutlined />, color: '#faad14', label: '开始任务' },
  task_completed: { icon: <CheckCircleOutlined />, color: '#52c41a', label: '完成任务' },
  task_comment: { icon: <EditOutlined />, color: '#722ed1', label: '评论任务' },
  login: { icon: <CheckCircleOutlined />, color: '#13c2c2', label: '登录系统' },
  logout: { icon: <ClockCircleOutlined />, color: '#8c8c8c', label: '退出系统' },
  longmenling_earned: { icon: <TrophyOutlined />, color: '#FFD700', label: '获得龙门令' },
  level_up: { icon: <TrophyOutlined />, color: '#ff4d4f', label: '等级提升' },
};

const ActivityFeed: React.FC<ActivityFeedProps> = ({
  activities,
  loading = false,
  className = '',
  style,
  onActivityClick,
}) => {
  const formatTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
    
    return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return (
      <div className={`activity-feed ${className}`} style={{ textAlign: 'center', padding: 40, ...style }}>
        <Spin />
      </div>
    );
  }

  if (activities.length === 0) {
    return (
      <div className={`activity-feed ${className}`} style={style}>
        <Empty description="暂无活动记录" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      </div>
    );
  }

  return (
    <div className={`activity-feed ${className}`} style={style}>
      <List
        dataSource={activities}
        renderItem={(activity) => {
          const config = activityTypeConfig[activity.type] || activityTypeConfig.login;
          return (
            <List.Item
              key={activity.id}
              onClick={() => onActivityClick?.(activity)}
              style={{ cursor: onActivityClick ? 'pointer' : 'default', padding: '12px 0' }}
            >
              <List.Item.Meta
                avatar={
                  <Avatar
                    src={activity.agentAvatar}
                    icon={!activity.agentAvatar && <UserOutlined />}
                    style={{ backgroundColor: activity.agentAvatar ? undefined : config.color }}
                  >
                    {activity.agentName?.[0]}
                  </Avatar>
                }
                title={
                  <Space size={8}>
                    <Text strong>{activity.agentName}</Text>
                    <Tag color={config.color} icon={config.icon}>
                      {config.label}
                    </Tag>
                  </Space>
                }
                description={
                  <div>
                    <Text type="secondary">{activity.content}</Text>
                    {activity.relatedTaskTitle && (
                      <div style={{ marginTop: 4 }}>
                        <Tag style={{ fontSize: 11, padding: '2px 6px' }}>
                          <CheckSquareOutlined /> {activity.relatedTaskTitle}
                        </Tag>
                      </div>
                    )}
                  </div>
                }
              />
              <div style={{ textAlign: 'right' }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  {formatTime(activity.createdAt)}
                </Text>
              </div>
            </List.Item>
          );
        }}
      />
    </div>
  );
};

export default ActivityFeed;
