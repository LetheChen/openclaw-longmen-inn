import React from 'react';
import { Tag, Typography, Empty, Spin, Card, Space, Divider } from 'antd';
import { 
  CheckCircleOutlined, 
  WarningOutlined, 
  RocketOutlined,
  FileTextOutlined,
  BugOutlined,
  ClockCircleOutlined,
  FireOutlined,
  ToolOutlined,
  PlusOutlined,
  MinusOutlined,
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
}

interface AuditFeedProps {
  items: AuditFeedEntry[];
  loading?: boolean;
}

const feedTypeConfig: Record<string, { icon: React.ReactNode; color: string; bgGradient: string; label: string }> = {
  deploy: { 
    icon: <RocketOutlined />, 
    color: '#52c41a', 
    bgGradient: 'linear-gradient(135deg, #52c41a 0%, #238636 100%)',
    label: '部署'
  },
  success: { 
    icon: <CheckCircleOutlined />, 
    color: '#228B22', 
    bgGradient: 'linear-gradient(135deg, #228B22 0%, #1a6b1a 100%)',
    label: '成功'
  },
  warning: { 
    icon: <WarningOutlined />, 
    color: '#faad14', 
    bgGradient: 'linear-gradient(135deg, #faad14 0%, #d48806 100%)',
    label: '警告'
  },
  error: { 
    icon: <BugOutlined />, 
    color: '#DC143C', 
    bgGradient: 'linear-gradient(135deg, #DC143C 0%, #8B0000 100%)',
    label: '错误'
  },
  task: { 
    icon: <FileTextOutlined />, 
    color: '#1890ff', 
    bgGradient: 'linear-gradient(135deg, #1890ff 0%, #096dd9 100%)',
    label: '任务'
  },
  build: { 
    icon: <ToolOutlined />, 
    color: '#722ed1', 
    bgGradient: 'linear-gradient(135deg, #722ed1 0%, #53186e 100%)',
    label: '构建'
  },
  git_audit: { 
    icon: <FireOutlined />, 
    color: '#B22222', 
    bgGradient: 'linear-gradient(135deg, #B22222 0%, #8B0000 100%)',
    label: '审计'
  },
  audit: { 
    icon: <FireOutlined />, 
    color: '#B22222', 
    bgGradient: 'linear-gradient(135deg, #B22222 0%, #8B0000 100%)',
    label: '审计'
  },
};

const AuditFeed: React.FC<AuditFeedProps> = ({ items, loading = false }) => {
  const formatTime = (dateStr: string): string => {
    if (!dateStr) return '';
    
    // 尝试解析 ISO 格式
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      // 如果已经是格式化好的日期字符串（如 "03月23日 21:36"）
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
      <div className="audit-feed-list">
        {items.map((item, index) => {
          const config = feedTypeConfig[item.type] || feedTypeConfig.git_audit;
          const statusEmoji = item.status_emoji || (item.status === 'passed' ? '✅' : '⚠️');
          
          return (
            <Card 
              key={`${item.timestamp}-${index}`}
              className="audit-feed-card"
              size="small"
            >
              <div className="audit-feed-card-header">
                <div className="audit-feed-type" style={{ background: config.bgGradient }}>
                  {config.icon}
                  <span>{config.label}</span>
                </div>
                <Text type="secondary" className="audit-feed-time">
                  <ClockCircleOutlined style={{ marginRight: 4 }} />
                  {formatTime(item.date_str || item.timestamp)}
                </Text>
              </div>
              
              <div className="audit-feed-card-body">
                <Text strong className="audit-feed-title">
                  {statusEmoji} {item.title}
                </Text>
                
                <div className="audit-feed-stats">
                  {(item.lines_added > 0 || item.lines_deleted > 0) && (
                    <span className="audit-feed-stat-item">
                      <PlusOutlined style={{ color: '#52c41a', fontSize: 10 }} />
                      <span style={{ color: '#52c41a' }}>{item.lines_added}</span>
                      <MinusOutlined style={{ color: '#DC143C', fontSize: 10, marginLeft: 4 }} />
                      <span style={{ color: '#DC143C' }}>{item.lines_deleted}</span>
                    </span>
                  )}
                  
                  {item.files_count > 0 && (
                    <span className="audit-feed-stat-item">
                      <FileTextOutlined style={{ color: '#1890ff', fontSize: 10 }} />
                      <span style={{ color: '#1890ff' }}>{item.files_count} 文件</span>
                    </span>
                  )}
                  
                  {item.issues_count > 0 && (
                    <span className="audit-feed-stat-item">
                      <WarningOutlined style={{ color: '#faad14', fontSize: 10 }} />
                      <span style={{ color: '#faad14' }}>{item.issues_count} 问题</span>
                    </span>
                  )}
                </div>
              </div>
              
              {(item.tasks_found && item.tasks_found.length > 0) && (
                <div className="audit-feed-tags">
                  <Space size={[4, 4]} wrap>
                    {item.tasks_found.map((task, tagIndex) => (
                      <Tag 
                        key={tagIndex}
                        className="audit-feed-tag"
                        style={{ 
                          background: 'rgba(178, 34, 34, 0.08)',
                          borderColor: 'rgba(178, 34, 34, 0.2)',
                          color: '#8B4513'
                        }}
                      >
                        {task}
                      </Tag>
                    ))}
                  </Space>
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default AuditFeed;
