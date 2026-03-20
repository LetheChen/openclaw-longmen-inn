import React from 'react';
import { Card, Avatar, Badge, Tag, Space, Typography, Tooltip, Progress } from 'antd';
import {
  UserOutlined,
  TrophyOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import type { Agent } from '../../types/agent';
import { AgentStatus } from '../../types/agent';
import { getLevelByPoints, getLevelProgress } from '../../types/longmenling';
import './AgentCard.css';

const { Text, Title } = Typography;

export interface AgentCardProps {
  agent: Agent;
  showLevel?: boolean;
  showStats?: boolean;
  showSkills?: boolean;
  showOnlineTime?: boolean;
  size?: 'small' | 'default' | 'large';
  onClick?: (agent: Agent) => void;
  className?: string;
  style?: React.CSSProperties;
}

const AgentCard: React.FC<AgentCardProps> = ({
  agent,
  showLevel = true,
  showStats = true,
  showSkills = true,
  showOnlineTime = false,
  size = 'default',
  onClick,
  className = '',
  style,
}) => {
  // 状态映射
  const statusMap: Record<AgentStatus, { color: string; text: string }> = {
    [AgentStatus.IDLE]: { color: '#52c41a', text: '在线' },
    [AgentStatus.OFFLINE]: { color: '#d9d9d9', text: '离线' },
    [AgentStatus.BUSY]: { color: '#ff4d4f', text: '忙碌' },
  };

  // 获取等级信息
  const levelInfo = getLevelByPoints(agent.longmenling);
  const progress = getLevelProgress(agent.longmenling);

  // 格式化在线时间
  const formatOnlineTime = (minutes: number): string => {
    if (minutes < 60) return `${minutes}分钟`;
    if (minutes < 1440) return `${Math.floor(minutes / 60)}小时`;
    return `${Math.floor(minutes / 1440)}天`;
  };

  const handleClick = () => {
    if (onClick) {
      onClick(agent);
    }
  };

  const sizeConfig = {
    small: { avatarSize: 48, titleSize: 16, padding: 16 },
    default: { avatarSize: 64, titleSize: 18, padding: 20 },
    large: { avatarSize: 80, titleSize: 20, padding: 24 },
  };

  const config = sizeConfig[size];

  return (
    <Card
      className={`agent-card ${className} ${onClick ? 'clickable' : ''}`}
      style={{
        borderRadius: 12,
        ...style,
      }}
      bodyStyle={{ padding: config.padding }}
      onClick={handleClick}
    >
      {/* 头部：头像和基本信息 */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: 16 }}>
        <Badge
          dot
          color={statusMap[agent.status].color}
          offset={[-5, config.avatarSize - 10]}
        >
          <Avatar
            size={config.avatarSize}
            src={agent.avatar}
            icon={!agent.avatar && <UserOutlined />}
            style={{
              backgroundColor: agent.avatar ? undefined : '#8B0000',
              border: `2px solid ${statusMap[agent.status].color}`,
            }}
          >
            {agent.name?.[0]}
          </Avatar>
        </Badge>
        <div style={{ marginLeft: 16, flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Title level={5} style={{ margin: 0, fontSize: config.titleSize }}>
              {agent.name}
            </Title>
            <Tag color={statusMap[agent.status].color} style={{ fontSize: 12, padding: '0 4px' }}>
              {statusMap[agent.status].text}
            </Tag>
          </div>
          {agent.nickname && (
            <Text type="secondary" style={{ fontSize: 13 }}>
              {agent.nickname}
            </Text>
          )}
        </div>
      </div>

      {/* 等级和龙门令 */}
      {showLevel && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
            <Space>
              <TrophyOutlined style={{ color: '#FFD700' }} />
              <Text strong style={{ color: levelInfo.color }}>
                {levelInfo.title}
              </Text>
              <Tag color="gold" style={{ fontSize: 12, padding: '0 4px' }}>Lv.{levelInfo.level}</Tag>
            </Space>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {agent.longmenling} 龙门令
            </Text>
          </div>
          <Tooltip title={`距离下一级还需 ${levelInfo.maxPoints - agent.longmenling} 龙门令`}>
            <Progress
              percent={progress}
              size="small"
              strokeColor={levelInfo.color}
              showInfo={false}
            />
          </Tooltip>
        </div>
      )}

      {/* 统计信息 */}
      {showStats && (
        <div style={{ display: 'flex', gap: 16, marginBottom: 16, flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            <CheckCircleOutlined style={{ color: '#52c41a' }} />
            <Text type="secondary" style={{ fontSize: 12 }}>
              已完成 {agent.completedTasks}
            </Text>
          </div>
          {showOnlineTime && (
            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <ClockCircleOutlined style={{ color: '#1890ff' }} />
              <Text type="secondary" style={{ fontSize: 12 }}>
                在线 {formatOnlineTime(agent.onlineTime)}
              </Text>
            </div>
          )}
        </div>
      )}

      {/* 技能标签 */}
      {showSkills && agent.skills && agent.skills.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <Space size={4} wrap>
            {agent.skills.map((skill, index) => (
              <Tag key={index} style={{ fontSize: 11, padding: '0px 4px' }}>
                {skill}
              </Tag>
            ))}
          </Space>
        </div>
      )}
    </Card>
  );
};

export default AgentCard;
