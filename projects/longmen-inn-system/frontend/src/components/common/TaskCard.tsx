import React from 'react';
import { Card, Tag, Avatar, Tooltip, Progress, Space, Typography } from 'antd';
import {
  CalendarOutlined,
  UserOutlined,
  FlagOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import type { Task } from '../../types/task';
import { TaskStatus, TaskPriority } from '../../types/task';
import './TaskCard.css';

const { Text } = Typography;

export interface TaskCardProps {
  task: Task;
  showProgress?: boolean;
  showAssignee?: boolean;
  showDates?: boolean;
  onClick?: (task: Task) => void;
  onStatusChange?: (taskId: string, status: TaskStatus) => void;
  style?: React.CSSProperties;
  className?: string;
  size?: 'small' | 'default' | 'large';
}

const TaskCard: React.FC<TaskCardProps> = ({
  task,
  showProgress = true,
  showAssignee = true,
  showDates = true,
  onClick,
  onStatusChange,
  style,
  className = '',
  size = 'default',
}) => {
  const statusMap: Record<TaskStatus, { color: string; text: string }> = {
    [TaskStatus.PENDING]: { color: 'default', text: '待开工' },
    [TaskStatus.IN_PROGRESS]: { color: 'processing', text: '进行中' },
    [TaskStatus.REVIEWING]: { color: 'warning', text: '待审核' },
    [TaskStatus.COMPLETED]: { color: 'success', text: '已完成' },
    [TaskStatus.BLOCKED]: { color: 'error', text: '阻塞' },
    [TaskStatus.CANCELLED]: { color: 'default', text: '已取消' },
  };

  const priorityMap: Record<TaskPriority, { color: string; text: string }> = {
    [TaskPriority.LOW]: { color: 'default', text: '低' },
    [TaskPriority.MEDIUM]: { color: 'blue', text: '中' },
    [TaskPriority.HIGH]: { color: 'orange', text: '高' },
    [TaskPriority.URGENT]: { color: 'red', text: '紧急' },
  };

  const calculateProgress = (): number => {
    if (task.status === TaskStatus.COMPLETED) return 100;
    if (task.status === TaskStatus.PENDING) return 0;
    if (task.status === TaskStatus.REVIEWING) return 90;
    if (task.actualHours && task.estimatedHours) {
      return Math.min(Math.round((task.actualHours / task.estimatedHours) * 100), 99);
    }
    return task.status === 'in_progress' ? 50 : 0;
  };

  const handleClick = () => {
    if (onClick) {
      onClick(task);
    }
  };

  const sizeConfig = {
    small: { padding: 12, titleSize: 14 },
    default: { padding: 16, titleSize: 16 },
    large: { padding: 20, titleSize: 18 },
  };

  const config = sizeConfig[size];

  return (
    <Card
      className={`task-card ${className} ${onClick ? 'clickable' : ''}`}
      style={{
        borderRadius: 8,
        ...style,
      }}
      bodyStyle={{ padding: config.padding }}
      onClick={handleClick}
    >
      <div style={{ marginBottom: 12, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Text
          strong
          style={{
            fontSize: config.titleSize,
            color: '#262626',
            lineHeight: 1.4,
            flex: 1,
            marginRight: 8,
          }}
        >
          {task.title}
        </Text>
        <Tag color={priorityMap[task.priority].color} style={{ flexShrink: 0 }}>
          <FlagOutlined /> {priorityMap[task.priority].text}
        </Tag>
      </div>

      {task.description && (
        <Text
          type="secondary"
          style={{
            fontSize: 13,
            marginBottom: 12,
            lineHeight: 1.5,
            maxHeight: 39,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {task.description}
        </Text>
      )}

      {showProgress && (
        <div style={{ marginBottom: 12 }}>
          <Progress
            percent={calculateProgress()}
            size="small"
            status={task.status === 'blocked' ? 'exception' : 'active'}
            strokeColor={task.status === 'completed' ? '#52c41a' : '#8B0000'}
          />
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
        <Space size={8}>
          {(() => {
            const statusInfo = statusMap[task.status];
            if (!statusInfo) {
              console.warn(`Unknown task status: ${task.status}`);
              return <Tag color="default">未知</Tag>;
            }
            return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>;
          })()}

          {showAssignee && (
            <Space size={4}>
              {task.creatorName && (
                <Tooltip title={`挂牌人: ${task.creatorName}`}>
                  <Avatar
                    size={24}
                    icon={<UserOutlined />}
                    style={{ 
                      cursor: 'pointer', 
                      backgroundColor: '#8B4513',
                      fontSize: 12,
                    }}
                  >
                    {task.creatorName?.[0]}
                  </Avatar>
                </Tooltip>
              )}
              {task.assigneeName && (
                <Tooltip title={`接手伙计: ${task.assigneeName}`}>
                  <Avatar
                    size={24}
                    icon={<TeamOutlined />}
                    style={{ 
                      cursor: 'pointer',
                      backgroundColor: '#B22222',
                      fontSize: 12,
                    }}
                  >
                    {task.assigneeName?.[0]}
                  </Avatar>
                </Tooltip>
              )}
            </Space>
          )}
        </Space>

        {showDates && task.dueDate && (
          <Tooltip title="截止日期">
            <Text type="secondary" style={{ fontSize: 12 }}>
              <CalendarOutlined style={{ marginRight: 4 }} />
              {new Date(task.dueDate).toLocaleDateString('zh-CN')}
            </Text>
          </Tooltip>
        )}
      </div>
    </Card>
  );
};

export default TaskCard;
