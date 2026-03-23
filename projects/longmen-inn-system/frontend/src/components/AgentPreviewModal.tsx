/**
 * 龙门客栈 - Agent工作空间预览弹窗
 * 快速查看Agent状态，点击"进入工作空间"跳转详情
 */

import React, { useState, useEffect } from 'react';
import { Modal, Avatar, Badge, Tag, Typography, Button, Space, Spin, Descriptions, Timeline } from 'antd';
import {
  UserOutlined,
  ClockCircleOutlined,
  FireOutlined,
  CheckCircleOutlined,
  ArrowRightOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { AgentWorkspace, ActivityRecord } from '../types/agentWorkspace';
import { getAgentWorkspace, getAgentActivities } from '../services/agentWorkspaceService';
import '../pages/AgentWorkspace.css';

const { Text, Title, Paragraph } = Typography;

// 状态配置
const statusConfig = {
  busy: { color: '#DC143C', text: '忙碌', icon: <FireOutlined />, bgColor: 'rgba(220, 20, 60, 0.1)' },
  idle: { color: '#228B22', text: '空闲', icon: <CheckCircleOutlined />, bgColor: 'rgba(34, 139, 34, 0.1)' },
  offline: { color: '#7a7a7a', text: '离线', icon: <ClockCircleOutlined />, bgColor: 'rgba(122, 122, 122, 0.1)' },
  error: { color: '#8B0000', text: '异常', icon: <FireOutlined />, bgColor: 'rgba(139, 0, 0, 0.1)' },
};

// 场景背景缩略图
const sceneThumbnails: Record<string, string> = {
  '内堂雅间': 'linear-gradient(135deg, #2c1810 0%, #8b4513 100%)',
  '客房柜台': 'linear-gradient(135deg, #1a1a2e 0%, #4a3728 100%)',
  '大堂茶座': 'linear-gradient(135deg, #3d2914 0%, #8b6914 100%)',
  '后厨灶台': 'linear-gradient(135deg, #4a1c1c 0%, #8b4513 100%)',
  '账房': 'linear-gradient(135deg, #1e3a5f 0%, #2c1810 100%)',
  '画室': 'linear-gradient(135deg, #4a3728 0%, #6b4423 100%)',
  '书房茶座': 'linear-gradient(135deg, #2c1810 0%, #5d4e37 100%)',
};

interface AgentPreviewModalProps {
  agentId: string | null;
  visible: boolean;
  onClose: () => void;
  onEnterWorkspace: (agentId: string) => void;
}

const AgentPreviewModal: React.FC<AgentPreviewModalProps> = ({
  agentId,
  visible,
  onClose,
  onEnterWorkspace,
}) => {
  const [workspace, setWorkspace] = useState<AgentWorkspace | null>(null);
  const [activities, setActivities] = useState<ActivityRecord[]>([]);
  const [loading, setLoading] = useState(false);

  // 加载数据
  useEffect(() => {
    if (agentId && visible) {
      setLoading(true);
      Promise.all([
        getAgentWorkspace(agentId),
        getAgentActivities(agentId, { limit: 5 }),
      ])
        .then(([workspaceData, activityData]) => {
          setWorkspace(workspaceData);
          setActivities(activityData);
        })
        .catch((err) => {
          console.error('加载Agent数据失败:', err);
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setWorkspace(null);
      setActivities([]);
    }
  }, [agentId, visible]);

  const statusInfo = workspace ? (statusConfig[workspace.status] || statusConfig.offline) : statusConfig.offline;
  const sceneBg = workspace ? (sceneThumbnails[workspace.role.scene] || 'linear-gradient(135deg, #2c1810 0%, #8b6914 100%)') : 'linear-gradient(135deg, #2c1810 0%, #8b6914 100%)';

  const handleEnterWorkspace = () => {
    if (agentId) {
      onClose();
      onEnterWorkspace(agentId);
    }
  };

  return (
    <Modal
      open={visible}
      onCancel={onClose}
      footer={null}
      width={600}
      className="agent-preview-modal"
      styles={{
        body: { padding: 0 },
      }}
    >
      {loading ? (
        <div className="preview-loading">
          <Spin size="large" tip="加载中..." />
        </div>
      ) : !workspace ? (
        <div className="preview-empty">
          <Text>未找到Agent信息</Text>
        </div>
      ) : (
        <div className="preview-content">
          {/* 场景背景 */}
          <div 
            className="preview-header"
            style={{ background: sceneBg }}
          >
            <div className="preview-header-overlay">
              <div className="preview-character">
                <Badge dot color={statusInfo.color} offset={[-4, 4]}>
                  <Avatar
                    size={64}
                    style={{
                      backgroundColor: '#8B0000',
                      border: '3px solid #D4C4A8',
                      boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                    }}
                  >
                    {workspace.role.name[0]}
                  </Avatar>
                </Badge>
                <div className="preview-info">
                  <Title level={4} style={{ margin: 0, color: '#D4C4A8' }}>
                    {workspace.role.name}
                  </Title>
                  <Text style={{ color: '#DAA520', fontSize: 12 }}>
                    {workspace.role.title}
                  </Text>
                  <div className="preview-tags">
                    <Tag color={statusInfo.color} icon={statusInfo.icon}>
                      {statusInfo.text}
                    </Tag>
                    <Tag color="#8B4513">{workspace.role.scene}</Tag>
                  </div>
                </div>
              </div>
              <div className="preview-level">
                <Text style={{ color: '#DAA520' }}>Lv.{workspace.role.level}</Text>
              </div>
            </div>
          </div>

          {/* 角色描述 */}
          <div className="preview-description">
            <Text type="secondary">{workspace.role.description}</Text>
            {workspace.role.motto && (
              <Paragraph 
                italic 
                style={{ marginTop: 8, marginBottom: 0, color: '#8B0000', fontSize: 12 }}
              >
                "{workspace.role.motto}"
              </Paragraph>
            )}
          </div>

          {/* 快速统计 */}
          <div className="preview-stats">
            <div className="stat-item">
              <Text type="secondary">进行中</Text>
              <Text strong style={{ fontSize: 20, color: '#DC143C' }}>
                {workspace.current_tasks.length}
              </Text>
            </div>
            <div className="stat-item">
              <Text type="secondary">待办</Text>
              <Text strong style={{ fontSize: 20, color: '#DAA520' }}>
                {workspace.pending_tasks.length}
              </Text>
            </div>
            <div className="stat-item">
              <Text type="secondary">已完成</Text>
              <Text strong style={{ fontSize: 20, color: '#228B22' }}>
                {workspace.completed_tasks.length}
              </Text>
            </div>
            <div className="stat-item">
              <Text type="secondary">文件数</Text>
              <Text strong style={{ fontSize: 20, color: '#8B4513' }}>
                {workspace.workspace_files.length}
              </Text>
            </div>
          </div>

          {/* 最近活动 */}
          {activities.length > 0 && (
            <div className="preview-activities">
              <Text strong style={{ marginBottom: 8, display: 'block' }}>最近活动</Text>
              <div className="activity-list">
                {activities.slice(0, 3).map((activity, index) => (
                  <div key={index} className="activity-item-preview">
                    <Tag color={activity.is_error ? 'red' : 'green'}>
                      {activity.action_type === 'message' ? '消息' : 
                       activity.action_type === 'tool_use' ? '工具' : '返回'}
                    </Tag>
                    <Text ellipsis className="activity-text">
                      {activity.action_detail}
                    </Text>
                    <Text type="secondary" style={{ fontSize: 10 }}>
                      {new Date(activity.timestamp).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                    </Text>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 操作按钮 */}
          <div className="preview-actions">
            <Button onClick={onClose}>
              关闭
            </Button>
            <Button type="primary" icon={<ArrowRightOutlined />} onClick={handleEnterWorkspace}>
              进入工作空间
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
};

export default AgentPreviewModal;