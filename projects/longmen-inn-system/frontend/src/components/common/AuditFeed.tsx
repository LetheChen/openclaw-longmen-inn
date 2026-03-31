import React from 'react';
import { Typography, Empty, Spin, Space } from 'antd';
import { 
  CheckCircleOutlined, 
  WarningOutlined, 
  FireOutlined,
  FileTextOutlined,
  ClockCircleOutlined,
  PlusOutlined,
  MinusOutlined,
  LockOutlined,
  RocketOutlined,
} from '@ant-design/icons';
import './AuditFeed.css';

const { Text } = Typography;

// 后端返回的Feed条目格式
interface AuditFeedEntry {
  id?: string;
  timestamp: string;
  date_str?: string;
  title: string;
  status: string;
  status_emoji?: string;
  lines_added: number;
  lines_deleted: number;
  lines_info?: string;
  files_count: number;
  files_info?: string;
  issues: string[];
  issues_count: number;
  tasks_found: string[];
  type: string;
  agent?: string;
  details?: string;
}

interface AuditFeedProps {
  items: AuditFeedEntry[];
  loading?: boolean;
}

// 根据 type 确定样式
const getDotClass = (type: string): string => {
  if (type === 'task_completion') return 'task';
  if (type === 'security_improvement') return 'security';
  if (type === 'deploy' || type === 'success') return 'success';
  if (type === 'warning' || type === 'git_audit') return 'warning';
  return 'default';
};

// 获取图标
const getTypeIcon = (type: string) => {
  if (type === 'task_completion') return <FileTextOutlined style={{ fontSize: 9 }} />;
  if (type === 'security_improvement') return <LockOutlined style={{ fontSize: 9 }} />;
  if (type === 'deploy') return <RocketOutlined style={{ fontSize: 9 }} />;
  if (type === 'git_audit') return <FireOutlined style={{ fontSize: 9 }} />;
  return <CheckCircleOutlined style={{ fontSize: 9 }} />;
};

const AuditFeed: React.FC<AuditFeedProps> = ({ items, loading = false }) => {
  const formatTime = (dateStr: string): string => {
    if (!dateStr) return '';
    
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr;
    }
    
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
      <div className="audit-feed" style={{ textAlign: 'center', padding: 40 }}>
        <Spin size="large" />
        <div style={{ marginTop: 16, color: '#8B4513', fontFamily: 'var(--font-family-serif)' }}>
          正在读取版本动态...
        </div>
      </div>
    );
  }

  if (!items || items.length === 0) {
    return (
      <div className="audit-feed">
        <Empty 
          description={
            <span style={{ color: '#8B4513', fontFamily: 'var(--font-family-serif)' }}>
              暂无版本动态
            </span>
          }
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </div>
    );
  }

  return (
    <div className="audit-feed">
      <div className="audit-feed-timeline">
        {items.map((item, index) => {
          const dotClass = getDotClass(item.type);
          const icon = getTypeIcon(item.type);
          const statusEmoji = item.status_emoji || (item.status === 'passed' || item.status === 'completed' ? '✅' : '⚠️');
          
          return (
            <div 
              key={`${item.timestamp}-${index}`}
              className={`audit-timeline-item ${item.type === 'task_completion' ? 'task' : item.type === 'security_improvement' ? 'security' : ''}`}
            >
              <div className={`audit-timeline-dot ${dotClass}`}>
                {icon}
              </div>
              
              <div className="audit-timeline-content">
                <div className="audit-timeline-header">
                  <span className="audit-timeline-title">
                    {statusEmoji} {item.title}
                  </span>
                  <span className="audit-timeline-time">
                    <ClockCircleOutlined style={{ marginRight: 3, fontSize: 10 }} />
                    {formatTime(item.date_str || item.timestamp)}
                  </span>
                </div>
                
                <div className="audit-timeline-meta">
                  {/* 统计信息 */}
                  <div className="audit-timeline-stats">
                    {(item.lines_added > 0 || item.lines_deleted > 0) && (
                      <span className="audit-timeline-stat">
                        <PlusOutlined style={{ color: '#52c41a', fontSize: 10 }} />
                        <span style={{ color: '#52c41a' }}>{item.lines_added}</span>
                        <MinusOutlined style={{ color: '#DC143C', fontSize: 10, marginLeft: 2 }} />
                        <span style={{ color: '#DC143C' }}>{item.lines_deleted}</span>
                      </span>
                    )}
                    
                    {item.files_count > 0 && (
                      <span className="audit-timeline-stat">
                        <FileTextOutlined style={{ color: '#1890ff', fontSize: 10 }} />
                        <span style={{ color: '#1890ff' }}>{item.files_count}</span>
                      </span>
                    )}
                    
                    {item.issues_count > 0 && (
                      <span className="audit-timeline-stat">
                        <WarningOutlined style={{ color: '#faad14', fontSize: 10 }} />
                        <span style={{ color: '#faad14' }}>{item.issues_count}</span>
                      </span>
                    )}
                  </div>
                  
                  {/* 任务标签 */}
                  {item.tasks_found && item.tasks_found.length > 0 && (
                    <div className="audit-timeline-tags">
                      {item.tasks_found.slice(0, 3).map((task, tagIndex) => (
                        <span 
                          key={tagIndex}
                          className="audit-timeline-tag"
                        >
                          {task}
                        </span>
                      ))}
                      {item.tasks_found.length > 3 && (
                        <span className="audit-timeline-tag">+{item.tasks_found.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AuditFeed;
