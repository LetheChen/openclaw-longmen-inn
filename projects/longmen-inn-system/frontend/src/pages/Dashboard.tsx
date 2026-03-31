import React, { useState, useEffect, useCallback, useRef } from 'react'
import { Row, Col, Badge, Avatar, Spin, Empty, Progress, Tag, Typography, Button, Tabs } from 'antd'
import {
  CheckCircleOutlined,
  PauseCircleOutlined,
  TeamOutlined,
  TrophyOutlined,
  FireOutlined,
  ReloadOutlined,
  RiseOutlined,
  FallOutlined,
  MinusOutlined,
  UserOutlined,
  ShopOutlined,
  CoffeeOutlined,
  FlagOutlined,
  BookOutlined,
  EditOutlined,
} from '@ant-design/icons'
import TaskWall from '../components/common/TaskWall'
import ActivityFeed from '../components/common/ActivityFeed'
import AuditFeed from '../components/common/AuditFeed'
import LedgerEditor from '../components/common/LedgerEditor'
import RoleDetail from '../components/common/RoleDetail'
import { getOnlineAgents, getAgentActivities, getAgentStatistics } from '../services/agentService'
import { getTaskStatistics, getTasks } from '../services/taskService'
import { getAuditFeed } from '../services/auditLogService'
import type { Task } from '../types/task'
import { subscribeToOpenClawEvents } from '../services/openclawService'
import type { TaskStatus } from '../types/task'
import { AgentActivity, Agent, ActivityType } from '../types/agent'
import type { AuditFeedEntry } from '../types/auditLog'
import './Dashboard.css'

const { Text } = Typography

interface StatCardProps {
  title: string
  value: number
  icon: React.ReactNode
  color: string
  trend?: 'up' | 'down' | 'stable'
  trendValue?: string
}

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, color, trend, trendValue }) => {
  const trendIcon = trend === 'up' ? <RiseOutlined /> : trend === 'down' ? <FallOutlined /> : <MinusOutlined />
  const trendColor = trend === 'up' ? '#228B22' : trend === 'down' ? '#DC143C' : '#7a7a7a'
  
  return (
    <div className="stat-card" style={{ borderLeft: `4px solid ${color}` }}>
      <div className="stat-card-header">
        <div className="stat-card-icon" style={{ background: `${color}15`, color }}>
          {icon}
        </div>
        {trend && (
          <div className="stat-card-trend" style={{ color: trendColor }}>
            {trendIcon}
            <span>{trendValue}</span>
          </div>
        )}
      </div>
      <div className="stat-card-body">
        <div className="stat-card-value" style={{ color: '#1a1a1a' }}>{value.toLocaleString()}</div>
        <div className="stat-card-title">{title}</div>
      </div>
    </div>
  )
}

interface AgentCardProps {
  agent: Agent
  onClick?: (agent: Agent) => void
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, onClick }) => {
  const statusConfig = {
    online: { color: '#228B22', text: '在线', dot: true },
    idle: { color: '#228B22', text: '空闲', dot: true },
    busy: { color: '#DC143C', text: '忙碌', dot: true },
    offline: { color: '#7a7a7a', text: '离线', dot: false },
  }
  
  const config = statusConfig[agent.status as keyof typeof statusConfig] || statusConfig.offline
  
  return (
    <div 
      className={`agent-card ${agent.status === 'busy' ? 'busy' : ''}`}
      onClick={() => onClick?.(agent)}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <div className="agent-card-avatar">
        <Badge dot={config.dot} color={config.color} offset={[-4, 40]}>
          <Avatar
            size={48}
            style={{
              background: 'linear-gradient(135deg, #B22222 0%, #8B0000 100%)',
              boxShadow: `0 4px 12px ${config.color}40`,
              border: '2px solid #D4C4A8',
            }}
            icon={<UserOutlined />}
          >
            {agent.name[0]}
          </Avatar>
        </Badge>
      </div>
      <div className="agent-card-info">
        <div className="agent-card-name">{agent.name}</div>
        <div className="agent-card-status" style={{ color: config.color }}>
          {config.text}
        </div>
      </div>
      {agent.longmenling !== undefined && (
        <div className="agent-card-lml">
          <TrophyOutlined style={{ color: '#DAA520' }} />
          <span>{agent.longmenling}</span>
        </div>
      )}
    </div>
  )
}

const Dashboard: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [onlineAgents, setOnlineAgents] = useState<Agent[]>([])
  const [activities, setActivities] = useState<AgentActivity[]>([])
  const [taskStats, setTaskStats] = useState({
    totalTasks: 0,
    pendingTasks: 0,
    inProgressTasks: 0,
    completedTasks: 0,
    blockedTasks: 0,
  })
  const [agentStats, setAgentStats] = useState({
    total: 0,
    online: 0,
    offline: 0,
    busy: 0,
    idle: 0,
  })
  const [tasks, setTasks] = useState<Task[]>([])
  const [ledgerEditorVisible, setLedgerEditorVisible] = useState(false)
  const [roleDetailVisible, setRoleDetailVisible] = useState(false)
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null)
  const [activeTab, setActiveTab] = useState('activities')
  const [auditFeed, setAuditFeed] = useState<AuditFeedEntry[]>([])

  // 实时活动的模拟数据（后端 API 就绪前先用这个）
  const mockActivities: AgentActivity[] = [
    {
      id: 'mock-1',
      agentId: 'cook',
      agentName: '厨子',
      type: ActivityType.TASK_COMPLETED,
      content: '审计日志 API 开发完成，3个端点已就绪',
      relatedTaskId: 'T-20250323-001',
      relatedTaskTitle: '审计日志API开发',
      createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'mock-2',
      agentId: 'painter',
      agentName: '画师',
      type: ActivityType.TASK_COMPLETED,
      content: 'Dashboard 客栈动态 Tab 前端集成完成',
      relatedTaskId: 'T-20250323-002',
      relatedTaskTitle: '审计动态前端集成',
      createdAt: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'mock-3',
      agentId: 'accountant',
      agentName: '账房先生',
      type: ActivityType.TASK_COMPLETED,
      content: '代码审查通过，pre-upload-check.ps1 完善',
      relatedTaskId: 'T-20250323-003',
      relatedTaskTitle: '代码审查与Git上传前检查',
      createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'mock-4',
      agentId: '老板娘',
      agentName: '老板娘',
      type: ActivityType.LONGMENLING_EARNED,
      content: '安全修复批量完成，JWT+中间件+速率限制，+200龙门令',
      relatedTaskId: 'T-20250321-002~007',
      createdAt: new Date(Date.now() - 22 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'mock-5',
      agentId: 'cook',
      agentName: '厨子',
      type: ActivityType.TASK_STARTED,
      content: '开始 Agent 工作空间可视化 Phase1 后端框架开发',
      relatedTaskId: 'T-20250322-001',
      relatedTaskTitle: 'Agent工作空间后端框架',
      createdAt: new Date(Date.now() - 26 * 60 * 60 * 1000).toISOString(),
    },
    {
      id: 'mock-6',
      agentId: 'storyteller',
      agentName: '说书先生',
      type: ActivityType.LOGIN,
      content: '签到完毕，随时待命',
      createdAt: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    },
  ]

  const wsRef = useRef<WebSocket | null>(null)

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)
    
    try {
      const [agentsData, activitiesData, taskStatistics, agentStatistics, tasksData] = await Promise.all([
        getOnlineAgents().catch(() => []),
        getAgentActivities({ limit: 10 }).catch(() => []),
        getTaskStatistics().catch(() => ({
          total: 0,
          pending: 0,
          inProgress: 0,
          review: 0,
          completed: 0,
          blocked: 0,
        })),
        getAgentStatistics().catch(() => ({
          total: 0,
          online: 0,
          offline: 0,
          busy: 0,
          idle: 0,
        })),
        getTasks({ pageSize: 100 }).catch(() => ({ data: [], total: 0 })),
      ])
      
      if (agentsData && agentsData.length > 0) {
        setOnlineAgents(agentsData)
      }
      
      if (activitiesData && activitiesData.length > 0) {
        setActivities(activitiesData)
      } else {
        // 后端无 agent activities API 时，用模拟数据顶上
        setActivities(mockActivities)
      }
      
      if (tasksData && tasksData.data) {
        setTasks(tasksData.data)
      }
      
      setTaskStats({
        totalTasks: taskStatistics.total || 0,
        pendingTasks: taskStatistics.pending || 0,
        inProgressTasks: taskStatistics.inProgress || 0,
        completedTasks: taskStatistics.completed || 0,
        blockedTasks: taskStatistics.blocked || 0,
      })
      
      setAgentStats(agentStatistics)
    } catch (err: any) {
      console.error('数据加载失败:', err)
      setError(`数据加载失败: ${err.message || '未知错误'}`)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
    
    wsRef.current = subscribeToOpenClawEvents(
      (data: any) => {
        if (data.type === 'agent_status_update') {
          loadData()
        }
      },
      (error) => {
        console.error('WebSocket连接错误:', error)
      }
    )
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [loadData])

  // 获取版本动态
  useEffect(() => {
    if (activeTab === 'updates') {
      getAuditFeed(10)
        .then(setAuditFeed)
        .catch((err) => {
          console.error('获取版本动态失败:', err)
          setAuditFeed([])
        })
    }
  }, [activeTab])

  const completionRate = taskStats.totalTasks > 0 
    ? Math.round((taskStats.completedTasks / taskStats.totalTasks) * 100) 
    : 0

  return (
    <Spin spinning={loading} size="large">
      <div className="page-container dashboard-page">
        {/* 页面标题 - 客栈招牌风格 */}
        <div className="page-header">
          <div className="page-header-content">
            <div className="page-title-wrapper">
              <ShopOutlined className="inn-icon" />
              <div>
                <h1 className="page-title">
                  龙门客栈
                </h1>
                <p className="page-subtitle">掌柜仪表盘 · 概览客栈运营状态</p>
              </div>
            </div>
            <div className="inn-decoration">
              <span className="decoration-text">生意兴隆</span>
            </div>
          </div>
        </div>

        {/* 统计卡片 - 木牌风格 */}
        <div className="stats-grid" style={{ marginBottom: 24 }}>
          <StatCard
            title="今日任务"
            value={taskStats.totalTasks}
            icon={<BookOutlined />}
            color="#B22222"
            trend="up"
            trendValue="上升"
          />
          <StatCard
            title="进行中"
            value={taskStats.inProgressTasks}
            icon={<FireOutlined />}
            color="#4682B4"
            trend="stable"
            trendValue="平稳"
          />
          <StatCard
            title="已完成"
            value={taskStats.completedTasks}
            icon={<CheckCircleOutlined />}
            color="#228B22"
            trend="up"
            trendValue="增长"
          />
          <StatCard
            title="阻塞任务"
            value={taskStats.blockedTasks}
            icon={<PauseCircleOutlined />}
            color="#DC143C"
            trend="down"
            trendValue="减少"
          />
        </div>

        <Row gutter={[24, 24]}>
          <Col xs={24} lg={16}>
            {/* 在线伙计 - 伙计花名册 */}
            <div className="content-card agents-card" style={{ marginBottom: 24 }}>
              <div className="content-card-header">
                <span className="content-card-title">
                  <TeamOutlined style={{ color: '#B22222' }} />
                  伙计花名册
                  <Tag className="seal-tag" style={{ marginLeft: 8 }}>
                    {agentStats.online || onlineAgents.length} 人在岗
                  </Tag>
                </span>
                <button className="text-btn refresh-btn" onClick={loadData}>
                  <ReloadOutlined />
                  <span>刷新名册</span>
                </button>
              </div>
              <div className="content-card-body">
                <div className="agents-grid">
                  {onlineAgents.length > 0 ? (
                    onlineAgents.map((agent) => (
                      <AgentCard 
                        key={agent.agent_id} 
                        agent={agent} 
                        onClick={(a) => {
                          setSelectedAgent(a)
                          setRoleDetailVisible(true)
                        }}
                      />
                    ))
                  ) : (
                    <div className="empty-agents">
                      <Empty
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                        description="暂无伙计在岗"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* 任务看板 - 任务墙 */}
            <div className="content-card taskwall-card">
              <div className="content-card-header">
                <span className="content-card-title">
                  <FlagOutlined style={{ color: '#B22222' }} />
                  任务墙
                </span>
                <Button
                  type="text"
                  size="small"
                  icon={<EditOutlined />}
                  onClick={() => setLedgerEditorVisible(true)}
                  style={{ color: '#B22222' }}
                >
                  编辑账本
                </Button>
              </div>
              <div className="content-card-body" style={{ padding: 0 }}>
                <TaskWall tasks={tasks} loading={loading} />
              </div>
            </div>
          </Col>

          <Col xs={24} lg={8}>
            {/* 完成进度 - 业绩榜 */}
            <div className="content-card achievement-card" style={{ marginBottom: 24 }}>
              <div className="content-card-header">
                <span className="content-card-title">
                  <TrophyOutlined style={{ color: '#B22222' }} />
                  业绩榜
                </span>
              </div>
              <div className="content-card-body" style={{ textAlign: 'center' }}>
                <div style={{ marginBottom: 24 }}>
                  <Progress
                    type="circle"
                    percent={completionRate}
                    strokeColor={{
                      '0%': '#B22222',
                      '100%': '#228B22',
                    }}
                    trailColor="#E8DCC8"
                    strokeWidth={10}
                    width={160}
                    format={(percent) => (
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 32, fontWeight: 'bold', color: '#B22222', fontFamily: 'var(--font-family-serif)' }}>
                          {percent}%
                        </div>
                        <div style={{ fontSize: 12, color: '#7a7a7a', marginTop: 4 }}>完成率</div>
                      </div>
                    )}
                  />
                </div>
                <div className="stats-row">
                  <div className="stat-item">
                    <div className="stat-number" style={{ color: '#228B22' }}>{taskStats.completedTasks}</div>
                    <div className="stat-label">已完成</div>
                  </div>
                  <div className="stat-divider" />
                  <div className="stat-item">
                    <div className="stat-number" style={{ color: '#4682B4' }}>{taskStats.inProgressTasks}</div>
                    <div className="stat-label">进行中</div>
                  </div>
                  <div className="stat-divider" />
                  <div className="stat-item">
                    <div className="stat-number" style={{ color: '#7a7a7a' }}>{taskStats.pendingTasks}</div>
                    <div className="stat-label">待开始</div>
                  </div>
                </div>
              </div>
            </div>

            {/* 动态活动 - 客栈动态 */}
            <div className="content-card activity-card">
              <div className="content-card-header">
                <span className="content-card-title">
                  <CoffeeOutlined style={{ color: '#B22222' }} />
                  客栈动态
                </span>
              </div>
              <div className="content-card-body" style={{ padding: 0 }}>
                <Tabs 
                  activeKey={activeTab} 
                  onChange={setActiveTab}
                  className="inn-tabs"
                >
                  <Tabs.TabPane tab="实时活动" key="activities">
                    <ActivityFeed activities={activities} />
                  </Tabs.TabPane>
                  <Tabs.TabPane tab="版本动态" key="updates">
                    <AuditFeed items={auditFeed} loading={loading} />
                  </Tabs.TabPane>
                </Tabs>
              </div>
            </div>
          </Col>
        </Row>

        <LedgerEditor
          visible={ledgerEditorVisible}
          onClose={() => setLedgerEditorVisible(false)}
          onRefresh={loadData}
        />

        <RoleDetail
          visible={roleDetailVisible}
          agent={selectedAgent}
          onClose={() => {
            setRoleDetailVisible(false)
            setSelectedAgent(null)
          }}
        />
      </div>
    </Spin>
  )
}

export default Dashboard
