import React from 'react';
import { Card, Progress, Tag, Avatar, Space, Typography, Tooltip, Divider } from 'antd';
import {
  CalendarOutlined,
  TeamOutlined,
  CheckSquareOutlined,
  FlagOutlined,
  UserOutlined,
} from '@ant-design/icons';
import type { Project, ProjectStatus, ProjectPriority } from '../../types/project';
import './ProjectCard.css';

const { Text, Title } = Typography;

export interface ProjectCardProps {
  project: Project;
  showProgress?: boolean;
  showStats?: boolean;
  showMembers?: boolean;
  onClick?: (project: Project) => void;
  className?: string;
  style?: React.CSSProperties;
}

const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  showProgress = true,
  showStats = true,
  showMembers = true,
  onClick,
  className = '',
  style,
}) => {
  // 状态映射
  const statusMap: Record<ProjectStatus, { color: string; text: string; icon: React.ReactNode }> = {
    draft: { color: 'default', text: '草稿', icon: '📝' },
    active: { color: 'processing', text: '进行中', icon: '🚀' },
    paused: { color: 'warning', text: '已暂停', icon: '⏸️' },
    completed: { color: 'success', text: '已完成', icon: '✅' },
    archived: { color: 'default', text: '已归档', icon: '📦' },
  };

  // 优先级映射
  const priorityMap: Record<ProjectPriority, { color: string; text: string }> = {
    low: { color: 'default', text: '低' },
    medium: { color: 'blue', text: '中' },
    high: { color: 'orange', text: '高' },
    critical: { color: 'red', text: '紧急' },
  };

  // 计算进度颜色
  const getProgressColor = (progress: number): string => {
    if (progress >= 80) return '#52c41a';
    if (progress >= 50) return '#faad14';
    return '#8B0000';
  };

  // 格式化日期
  const formatDate = (date?: string): string => {
    if (!date) return '未设置';
    return new Date(date).toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric',
    });
  };

  const handleClick = () => {
    if (onClick) {
      onClick(project);
    }
  };

  return (
    <Card
      className={`project-card ${className} ${onClick ? 'clickable' : ''}`}
      style={{
        borderRadius: 12,
        overflow: 'hidden',
        ...style,
      }}
      bodyStyle={{ padding: 20 }}
      onClick={handleClick}
    >
      {/* 头部：标题和状态 */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
          <Title level={5} style={{ margin: 0, flex: 1, marginRight: 8, lineHeight: 1.4 }}>
            {project.name}
          </Title>
          <Space size={4}>
            <Tag color={priorityMap[project.priority].color}>
              <FlagOutlined /> {priorityMap[project.priority].text}
            </Tag>
            <Tag color={statusMap[project.status].color}>
              {statusMap[project.status].icon} {statusMap[project.status].text}
            </Tag>
          </Space>
        </div>
        
        {project.description && (
          <Text type="secondary" style={{ fontSize: 13, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
            {project.description}
          </Text>
        )}
      </div>

      {/* 进度条 */}
      {showProgress && (
        <div style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
            <Text type="secondary" style={{ fontSize: 12 }}>项目进度</Text>
            <Text strong style={{ fontSize: 12, color: getProgressColor(project.progress) }}>
              {project.progress}%
            </Text>
          </div>
          <Progress
            percent={project.progress}
            size="small"
            showInfo={false}
            strokeColor={getProgressColor(project.progress)}
            trailColor="#f0f0f0"
          />
        </div>
      )}

      {/* 统计信息 */}
      {showStats && (
        <div style={{ display: 'flex', gap: 16, marginBottom: 12, flexWrap: 'wrap' }}>
          <Tooltip title="任务数">
            <Space size={4}>
              <CheckSquareOutlined style={{ color: '#8B0000' }} />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {project.completedTaskCount}/{project.taskCount}
              </Text>
            </Space>
          </Tooltip>
          <Tooltip title="成员数">
            <Space size={4}>
              <TeamOutlined style={{ color: '#1890ff' }} />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {project.memberCount}
              </Text>
            </Space>
          </Tooltip>
          <Tooltip title="项目周期">
            <Space size={4}>
              <CalendarOutlined style={{ color: '#52c41a' }} />
              <Text type="secondary" style={{ fontSize: 12 }}>
                {formatDate(project.startDate)} - {formatDate(project.endDate)}
              </Text>
            </Space>
          </Tooltip>
        </div>
      )}

      {/* 负责人 */}
      <Divider style={{ margin: '12px 0' }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Tooltip title={`负责人: ${project.ownerName}`}>
          <Space size={8}>
            <Avatar
              size={24}
              src={project.ownerAvatar}
              icon={!project.ownerAvatar && <UserOutlined />}
            >
              {project.ownerName?.[0]}
            </Avatar>
            <Text type="secondary" style={{ fontSize: 12 }}>
              {project.ownerName}
            </Text>
          </Space>
        </Tooltip>
      </div>
    </Card>
  );
};

export default ProjectCard;
