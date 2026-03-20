import React, { useState, useCallback } from 'react';
import { Card, Empty, Badge, Spin, Space, Typography } from 'antd';
import {
  PlusOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import type { Task, TaskStatus } from '../../types/task';
import TaskCard from './TaskCard';
import './KanbanBoard.css';

export interface KanbanColumn {
  id: TaskStatus;
  title: string;
  tasks: Task[];
  color?: string;
  icon?: React.ReactNode;
}

export interface KanbanBoardProps {
  columns: KanbanColumn[];
  loading?: boolean;
  onTaskMove?: (taskId: string, sourceColumn: TaskStatus, targetColumn: TaskStatus) => void;
  onTaskClick?: (task: Task) => void;
  onAddTask?: (columnId: TaskStatus) => void;
  onColumnMore?: (columnId: TaskStatus) => void;
  className?: string;
  style?: React.CSSProperties;
  cardSize?: 'small' | 'default' | 'large';
  showAddButton?: boolean;
  draggable?: boolean;
}

const KanbanBoard: React.FC<KanbanBoardProps> = ({
  columns,
  loading = false,
  onTaskMove,
  onTaskClick,
  onAddTask,
  onColumnMore,
  className = '',
  style,
  cardSize = 'default',
  showAddButton = true,
  draggable = false,
}) => {
  const [draggedTask, setDraggedTask] = useState<Task | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<TaskStatus | null>(null);

  const handleDragStart = useCallback((task: Task) => {
    if (!draggable) return;
    setDraggedTask(task);
  }, [draggable]);

  const handleDragOver = useCallback((e: React.DragEvent, columnId: TaskStatus) => {
    if (!draggable) return;
    e.preventDefault();
    setDragOverColumn(columnId);
  }, [draggable]);

  const handleDragLeave = useCallback(() => {
    if (!draggable) return;
    setDragOverColumn(null);
  }, [draggable]);

  const handleDrop = useCallback((e: React.DragEvent, columnId: TaskStatus) => {
    if (!draggable || !draggedTask) return;
    e.preventDefault();
    
    if (draggedTask.status !== columnId && onTaskMove) {
      onTaskMove(draggedTask.id, draggedTask.status, columnId);
    }
    
    setDraggedTask(null);
    setDragOverColumn(null);
  }, [draggable, draggedTask, onTaskMove]);

  const getColumnStyle = (columnId: TaskStatus): React.CSSProperties => {
    const isDragOver = dragOverColumn === columnId;
    return {
      backgroundColor: isDragOver ? 'rgba(139, 0, 0, 0.05)' : '#f5f5f5',
      border: isDragOver ? '2px dashed #8B0000' : '2px solid transparent',
      borderRadius: 8,
      transition: 'all 0.2s ease',
    };
  };

  return (
    <div className={`kanban-board ${className}`} style={style}>
      <div className="kanban-columns" style={{ display: 'flex', gap: 16, overflowX: 'auto' }}>
        {columns.map((column) => (
          <div
            key={column.id}
            className="kanban-column"
            style={{
              minWidth: 280,
              maxWidth: 320,
              flex: 1,
              display: 'flex',
              flexDirection: 'column',
              ...getColumnStyle(column.id),
            }}
            onDragOver={(e) => handleDragOver(e, column.id)}
            onDragLeave={handleDragLeave}
            onDrop={(e) => handleDrop(e, column.id)}
          >
            {/* 列头部 */}
            <div
              className="kanban-column-header"
              style={{
                padding: '12px 16px',
                borderBottom: '1px solid rgba(0,0,0,0.06)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 16 }}>{column.icon}</span>
                <Typography.Text strong style={{ fontSize: 14, color: column.color || '#262626' }}>
                  {column.title}
                </Typography.Text>
                <Badge
                  count={column.tasks.length}
                  style={{
                    backgroundColor: column.color || '#8B0000',
                    fontSize: 11,
                    minWidth: 18,
                    height: 18,
                    lineHeight: '18px',
                  }}
                />
              </div>
              {onColumnMore && (
                <MoreOutlined
                  style={{ cursor: 'pointer', color: '#8c8c8c' }}
                  onClick={(e) => {
                    e.stopPropagation();
                    onColumnMore(column.id);
                  }}
                />
              )}
            </div>

            {/* 任务列表 */}
            <div
              className="kanban-column-content"
              style={{
                flex: 1,
                padding: 12,
                overflowY: 'auto',
                maxHeight: 'calc(100vh - 300px)',
              }}
            >
              {loading ? (
                <div style={{ textAlign: 'center', padding: 40 }}>
                  <Spin />
                </div>
              ) : column.tasks.length === 0 ? (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="暂无任务"
                  style={{ marginTop: 20 }}
                />
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                  {column.tasks.map((task) => (
                    <div
                      key={task.id}
                      draggable={draggable}
                      onDragStart={() => handleDragStart(task)}
                      style={{ cursor: draggable ? 'grab' : 'pointer' }}
                    >
                      <TaskCard
                        task={task}
                        size={cardSize}
                        showProgress={false}
                        onClick={onTaskClick}
                      />
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 添加按钮 */}
            {showAddButton && onAddTask && (
              <div
                className="kanban-column-footer"
                style={{
                  padding: '12px 16px',
                  borderTop: '1px solid rgba(0,0,0,0.06)',
                }}
              >
                <div
                  className="add-task-button"
                  onClick={() => onAddTask(column.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '8px 0',
                    color: '#8B0000',
                    cursor: 'pointer',
                    borderRadius: 6,
                    transition: 'all 0.2s',
                  }}
                >
                  <PlusOutlined style={{ marginRight: 8 }} />
                  <span>添加任务</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default KanbanBoard;
