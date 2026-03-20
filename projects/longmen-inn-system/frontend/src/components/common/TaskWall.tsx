import React from 'react';
import { Tag, Avatar, Tooltip, Empty, Spin } from 'antd';
import {
  UserOutlined,
  TeamOutlined,
  ClockCircleOutlined,
  FireOutlined,
} from '@ant-design/icons';
import type { Task } from '../../types/task';
import { TaskStatus } from '../../types/task';
import './TaskWall.css';

export interface TaskWallProps {
  tasks: Task[];
  loading?: boolean;
  onTaskClick?: (task: Task) => void;
}

const TaskWall: React.FC<TaskWallProps> = ({
  tasks,
  loading = false,
  onTaskClick,
}) => {
  const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode }> = {
    [TaskStatus.PENDING]: { color: '#7a7a7a', text: '待开工', icon: <ClockCircleOutlined /> },
    [TaskStatus.IN_PROGRESS]: { color: '#B22222', text: '进行中', icon: <FireOutlined /> },
  };

  const filteredTasks = tasks.filter(
    (t) => t.status === TaskStatus.PENDING || t.status === TaskStatus.IN_PROGRESS
  );

  const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const month = date.getMonth() + 1;
    const day = date.getDate();
    return `${month}月${day}日`;
  };

  if (loading) {
    return (
      <div className="task-wall-loading">
        <Spin />
      </div>
    );
  }

  if (filteredTasks.length === 0) {
    return (
      <div className="task-wall-empty">
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="暂无进行中或待开工的任务"
        />
      </div>
    );
  }

  return (
    <div className="task-wall">
      <div className="task-wall-header-row">
        <span className="col-no">任务号</span>
        <span className="col-title">任务内容</span>
        <span className="col-creator">挂牌人</span>
        <span className="col-assignee">接手伙计</span>
        <span className="col-status">状态</span>
        <span className="col-time">挂牌时间</span>
      </div>
      <div className="task-wall-body">
        {filteredTasks.map((task) => {
          const statusInfo = statusMap[task.status] || statusMap[TaskStatus.PENDING];
          
          return (
            <div
              key={task.id}
              className="task-wall-row"
              onClick={() => onTaskClick?.(task)}
            >
              <span className="col-no">{task.taskNo || '-'}</span>
              <span className="col-title">{task.title}</span>
              <span className="col-creator">
                <Tooltip title={task.creatorName || '未知'}>
                  <Avatar size={20} icon={<UserOutlined />} style={{ backgroundColor: '#8B4513' }}>
                    {task.creatorName?.[0] || '?'}
                  </Avatar>
                </Tooltip>
                <span className="name-text">{task.creatorName || '-'}</span>
              </span>
              <span className="col-assignee">
                <Tooltip title={task.assigneeName || '待分配'}>
                  <Avatar size={20} icon={<TeamOutlined />} style={{ backgroundColor: '#B22222' }}>
                    {task.assigneeName?.[0] || '?'}
                  </Avatar>
                </Tooltip>
                <span className="name-text">{task.assigneeName || '-'}</span>
              </span>
              <span className="col-status">
                <Tag
                  style={{
                    backgroundColor: `${statusInfo.color}15`,
                    color: statusInfo.color,
                    border: `1px solid ${statusInfo.color}30`,
                    margin: 0,
                  }}
                >
                  {statusInfo.text}
                </Tag>
              </span>
              <span className="col-time">
                <ClockCircleOutlined style={{ marginRight: 4 }} />
                {formatDate(task.createdAt)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TaskWall;
