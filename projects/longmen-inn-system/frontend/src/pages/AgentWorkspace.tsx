/**
 * 龙门客栈 - Agent工作空间页面
 * 布局：上方场景 62vh + 下方双卡片（对话 + 输出日志）
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Avatar,
  Badge,
  Tag,
  Typography,
  Button,
  Input,
  Empty,
  Spin,
  message,
  Collapse,
  Alert,
} from 'antd';
import {
  ClockCircleOutlined,
  FireOutlined,
  CheckCircleOutlined,
  SendOutlined,
  ReloadOutlined,
  ArrowLeftOutlined,
  ToolOutlined,
  MessageOutlined,
  CodeOutlined,
  RightOutlined,
  DownOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import type { AgentWorkspace, ActivityRecord } from '../types/agentWorkspace';
import { getAgentWorkspace, getAgentActivities } from '../services/agentWorkspaceService';
import './AgentWorkspace.css';

const { TextArea } = Input;
const { Text } = Typography;
const { Panel } = Collapse;

// 状态配置
const statusConfig = {
  busy: { color: '#DC143C', text: '忙碌', icon: <FireOutlined /> },
  idle: { color: '#228B22', text: '空闲', icon: <CheckCircleOutlined /> },
  offline: { color: '#7a7a7a', text: '离线', icon: <ClockCircleOutlined /> },
  error: { color: '#8B0000', text: '异常', icon: <FireOutlined /> },
};

// 场景背景（优先用本地宫廷图）
const sceneBackgrounds: Record<string, string> = {
  '内堂雅间': '/scenes/boss-scene.png',
  '客房柜台': '/scenes/court-scene.png',
  '大堂茶座': '/scenes/court-scene.png',
  '后厨灶台': '/scenes/court-scene.png',
  '账房': '/scenes/court-scene.png',
  '画室': '/scenes/court-scene.png',
  '书房茶座': '/scenes/court-scene.png',
};

// 默认背景
const defaultBackground = '/scenes/court-scene.png';

const AgentWorkspacePage: React.FC = () => {
  const { agentId } = useParams<{ agentId: string }>();
  const navigate = useNavigate();
  const [workspace, setWorkspace] = useState<AgentWorkspace | null>(null);
  const [activities, setActivities] = useState<ActivityRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [inputValue, setInputValue] = useState('');
  const [chatMessages, setChatMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string; time: string }>>([]);
  const [sending, setSending] = useState(false);
  const [expandedLogs, setExpandedLogs] = useState<string[]>([]);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const loadWorkspace = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAgentWorkspace(agentId);
      setWorkspace(data);
      const activityData = await getAgentActivities(agentId, { limit: 80 });
      setActivities(activityData);

      // 从历史活动中提取对话消息
      const historyMsgs = (data.recent_activities || [])
        .filter((a: ActivityRecord) => a.action_type === 'message')
        .map((a: ActivityRecord) => ({
          role: (a.role === 'user' ? 'user' : 'assistant') as 'user' | 'assistant',
          content: a.action_detail,
          time: new Date(a.timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
          }),
        }));
      setChatMessages(historyMsgs);
    } catch (err: any) {
      console.error('加载工作空间失败:', err);
      message.error('加载工作空间失败');
    } finally {
      setLoading(false);
    }
  }, [agentId]);

  useEffect(() => {
    loadWorkspace();
  }, [loadWorkspace]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const handleSend = () => {
    if (!inputValue.trim() || !workspace) return;
    const now = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    setChatMessages(prev => [...prev, { role: 'user', content: inputValue, time: now }]);
    setInputValue('');
    setSending(true);
    setTimeout(() => {
      const replyTime = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: `收到指令：「${inputValue}」，正在处理中...`,
        time: replyTime,
      }]);
      setSending(false);
    }, 1200);
  };

  // 按 session_id 分组活动记录
  const groupedActivities = activities.reduce<Record<string, ActivityRecord[]>>((acc, a) => {
    const key = a.timestamp;
    if (!acc[key]) acc[key] = [];
    acc[key].push(a);
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="workspace-loading">
        <Spin size="large" tip="加载工作空间..." />
      </div>
    );
  }

  if (!workspace) {
    return (
      <div className="workspace-empty">
        <Empty description="未找到该Agent的工作空间" />
        <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/agents')}>
          返回列表
        </Button>
      </div>
    );
  }

  const statusInfo = statusConfig[workspace.status] || statusConfig.offline;
  const sceneBg = sceneBackgrounds[workspace.role.scene] || defaultBackground;

  // 工具调用的展示配置
  const toolActionLabels: Record<string, string> = {
    read_file: '读取文件',
    write_file: '写入文件',
    exec: '执行命令',
    browser: '浏览器操作',
    search: '搜索',
    api: 'API调用',
    memory: '记忆操作',
  };

  return (
    <div className="agent-workspace-page">
      {/* ========== 上方：场景展示区（62vh）========== */}
      <div
        className="workspace-scene"
        style={{ backgroundImage: `url(${sceneBg})` }}
      >
        <div className="scene-overlay">
          <div className="scene-topbar">
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/agents')} type="text" className="scene-back-btn">
              返回
            </Button>
            <Tag color={statusInfo.color} icon={statusInfo.icon} className="scene-status-tag">
              {statusInfo.text}
            </Tag>
          </div>

          <div className="scene-char-bar">
            <Badge dot color={statusInfo.color} offset={[0, 8]}>
              <Avatar
                size={52}
                className="avatar-glow"
                style={{
                  backgroundColor: '#8B0000',
                  border: '3px solid #D4C4A8',
                  boxShadow: '0 0 20px rgba(139, 0, 0, 0.6)',
                }}
              >
                {workspace.role.name[0]}
              </Avatar>
            </Badge>
            <div className="scene-char-info">
              <div className="scene-char-name">{workspace.role.name}</div>
              <div className="scene-char-title">{workspace.role.title}</div>
            </div>
            <Tag color="#DAA520" className="scene-char-tag">{workspace.role.scene}</Tag>
          </div>

          <div className="scene-bottombar">
            <div className="scene-desc">{workspace.role.description}</div>
            <div className="scene-bottom-actions">
              {workspace.role.motto && (
                <Text className="scene-motto" italic>"{workspace.role.motto}"</Text>
              )}
              <Button icon={<ReloadOutlined />} onClick={loadWorkspace} size="small" className="scene-refresh-btn">
                刷新
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* ========== 下方：双卡片 ========== */}
      <div className="workspace-bottom">
        {/* 左侧：对话卡片 */}
        <div className="ws-card ws-chat-card">
          <div className="ws-card-header">
            <span className="ws-card-dot" />
            <span className="ws-card-title">与 {workspace.role.name} 对话</span>
            <Badge status={workspace.status === 'busy' ? 'error' : 'success'} text={<span style={{ fontSize: 11, color: 'rgba(61,43,31,0.45)' }}>{statusInfo.text}</span>} />
          </div>

          <div className="ws-chat-messages">
            {chatMessages.length === 0 ? (
              <div className="ws-chat-tip">
                <Text type="secondary">向左向右皆江湖，有何吩咐尽管提～</Text>
              </div>
            ) : (
              chatMessages.map((msg, idx) => (
                <div key={idx} className={`ws-msg-row ws-msg-${msg.role}`}>
                  {msg.role === 'assistant' && (
                    <Avatar size={28} style={{ backgroundColor: '#8B0000', flexShrink: 0 }}>
                      {workspace.role.name[0]}
                    </Avatar>
                  )}
                  <div className="ws-msg-bubble-wrap">
                    <div className={`ws-msg-bubble ws-bubble-${msg.role}`}>{msg.content}</div>
                    <div className="ws-msg-time">{msg.time}</div>
                  </div>
                  {msg.role === 'user' && (
                    <Avatar size={28} style={{ backgroundColor: '#DAA520', flexShrink: 0 }}>我</Avatar>
                  )}
                </div>
              ))
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="ws-chat-input-area">
            <TextArea
              className="ws-chat-input"
              placeholder="输入任务指令，按 Enter 发送..."
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onPressEnter={e => {
                if (!e.shiftKey) { e.preventDefault(); handleSend(); }
              }}
              autoSize={{ minRows: 1, maxRows: 3 }}
            />
            <Button type="primary" icon={<SendOutlined />} className="ws-send-btn" onClick={handleSend} loading={sending}>
              发送
            </Button>
          </div>
        </div>

        {/* 右侧：输出日志卡片 */}
        <div className="ws-card ws-log-card">
          <div className="ws-card-header">
            <span className="ws-card-dot ws-card-dot-green" />
            <span className="ws-card-title">输出日志</span>
            <span className="ws-card-count">{activities.length} 条记录</span>
          </div>

          <div className="ws-log-entries">
            {activities.length === 0 ? (
              <div className="ws-log-empty">
                <Text type="secondary">暂无输出日志</Text>
              </div>
            ) : (
              <Collapse
                className="ws-log-collapse"
                activeKey={expandedLogs}
                onChange={keys => setExpandedLogs(keys as string[])}
                expandIcon={({ isActive }) => isActive ? <DownOutlined /> : <RightOutlined />}
              >
                {activities.map((activity, idx) => {
                  const key = `${idx}`;
                  const isTool = activity.action_type === 'tool_use' || activity.action_type === 'tool_result';
                  const isError = activity.is_error;

                  return (
                    <Panel
                      key={key}
                      header={
                        <div className="ws-log-panel-header">
                          <span className={`ws-log-icon ${isError ? 'ws-log-icon-error' : isTool ? 'ws-log-icon-tool' : 'ws-log-icon-msg'}`}>
                            {isTool ? <ToolOutlined /> : <MessageOutlined />}
                          </span>
                          <span className="ws-log-action">{activity.action_detail}</span>
                          {isError && <WarningOutlined style={{ color: '#DC143C', marginLeft: 6 }} />}
                        </div>
                      }
                    >
                      <div className="ws-log-panel-body">
                        <div className="ws-log-meta">
                          <Tag color={activity.action_type === 'tool_use' ? 'blue' : activity.action_type === 'tool_result' ? 'purple' : 'default'}>
                            {activity.action_type === 'tool_use' ? '工具调用' : activity.action_type === 'tool_result' ? '执行结果' : '消息'}
                          </Tag>
                          {activity.tool_name && (
                            <Tag color="cyan">{toolActionLabels[activity.tool_name] || activity.tool_name}</Tag>
                          )}
                          <Text type="secondary" style={{ fontSize: 11 }}>
                            {new Date(activity.timestamp).toLocaleString('zh-CN')}
                          </Text>
                        </div>

                        {activity.output_preview && (
                          <div className="ws-log-output">
                            <Text strong style={{ fontSize: 11, color: 'rgba(61,43,31,0.55)' }}>输出结果：</Text>
                            <pre className={`ws-log-pre ${isError ? 'ws-log-pre-error' : ''}`}>
                              {activity.output_preview}
                            </pre>
                          </div>
                        )}
                      </div>
                    </Panel>
                  );
                })}
              </Collapse>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentWorkspacePage;
