import React, { useState, useEffect } from 'react';
import {
  Table,
  Card,
  Button,
  Tag,
  Space,
  Input,
  Select,
  Avatar,
  Tooltip,
  Typography,
  message,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CalendarOutlined,
  UserOutlined,
  CheckSquareOutlined,
  FileTextOutlined,
  FilterOutlined,
  BookOutlined,
  FireOutlined,
  FlagOutlined,
  ExclamationCircleOutlined,
  PushpinOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { TaskStatus, TaskPriority } from '../types/task';
import type { Task } from '../types/task';
import { getTasks, getTaskStatistics } from '../services/taskService';
import { getAgents } from '../services/agentService';
import { getProjects } from '../services/projectService';
import './Tasks.css';

const { Text } = Typography;
const { Option } = Select;

interface APITask {
  id: number;
  task_no: string;
  title: string;
  description: string | null;
  status: string;
  priority: string;
  assignee_agent_id: string | null;
  creator_agent_id: string;
  project_id: number | null;
  estimated_hours: number | null;
  actual_hours: number | null;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
}

const Tasks: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [statistics, setStatistics] = useState({
    total: 0,
    pending: 0,
    inProgress: 0,
    review: 0,
    completed: 0,
    blocked: 0,
  });
  const [agentsMap, setAgentsMap] = useState<Record<string, string>>({});
  const [projectsMap, setProjectsMap] = useState<Record<number, string>>({});

  // 状态映射 - 江湖风
  const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode; bgColor: string }> = {
    pending: { 
      color: '#8B4513', 
      text: '待开工', 
      icon: <ClockCircleOutlined />,
      bgColor: 'rgba(139, 69, 19, 0.1)'
    },
    in_progress: { 
      color: '#4682B4', 
      text: '进行中', 
      icon: <FireOutlined />,
      bgColor: 'rgba(70, 130, 180, 0.1)'
    },
    reviewing: { 
      color: '#DAA520', 
      text: '待审核', 
      icon: <EyeOutlined />,
      bgColor: 'rgba(218, 165, 32, 0.1)'
    },
    completed: { 
      color: '#228B22', 
      text: '已完成', 
      icon: <CheckCircleOutlined />,
      bgColor: 'rgba(34, 139, 34, 0.1)'
    },
    blocked: { 
      color: '#DC143C', 
      text: '阻塞', 
      icon: <ExclamationCircleOutlined />,
      bgColor: 'rgba(220, 20, 60, 0.1)'
    },
    cancelled: { 
      color: '#7a7a7a', 
      text: '已取消', 
      icon: <ClockCircleOutlined />,
      bgColor: 'rgba(122, 122, 122, 0.1)'
    },
  };

  // 优先级映射 - 江湖风
  const priorityMap: Record<string, { color: string; text: string; bgColor: string; dotColor: string }> = {
    low: { 
      color: '#7a7a7a', 
      text: '低', 
      bgColor: 'rgba(122, 122, 122, 0.1)',
      dotColor: '#7a7a7a'
    },
    medium: { 
      color: '#4682B4', 
      text: '中', 
      bgColor: 'rgba(70, 130, 180, 0.1)',
      dotColor: '#4682B4'
    },
    high: { 
      color: '#FF8C00', 
      text: '高', 
      bgColor: 'rgba(255, 140, 0, 0.1)',
      dotColor: '#FF8C00'
    },
    urgent: { 
      color: '#DC143C', 
      text: '紧急', 
      bgColor: 'rgba(220, 20, 60, 0.1)',
      dotColor: '#DC143C'
    },
  };

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [tasksRes, statsRes, agentsRes, projectsRes] = await Promise.all([
        getTasks({ page: 1, pageSize: 100 }),
        getTaskStatistics(),
        getAgents(),
        getProjects({ page: 1, pageSize: 100 }),
      ]);

      const agentMap: Record<string, string> = {};
      agentsRes.forEach((agent: any) => {
        agentMap[agent.agent_id] = agent.name;
      });
      setAgentsMap(agentMap);

      const projectMap: Record<number, string> = {};
      projectsRes.data.forEach((project: any) => {
        projectMap[project.id] = project.name;
      });
      setProjectsMap(projectMap);

      const tasksWithNames = tasksRes.data.map((task: Task) => ({
        ...task,
        creatorName: task.creatorName || agentMap[task.creatorId || ''] || '未知',
        assigneeName: task.assigneeName || agentMap[task.assigneeId || ''] || '未分配',
        projectName: task.projectName || '龙门客栈系统',
      }));

      setTasks(tasksWithNames);
      setStatistics(statsRes);
    } catch (error) {
      message.error('加载任务数据失败');
      console.error('加载任务数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredTasks = tasks.filter(task => {
    const matchSearch = task.title.toLowerCase().includes(searchText.toLowerCase()) ||
                       task.assigneeName?.toLowerCase().includes(searchText.toLowerCase());
    const matchStatus = statusFilter === 'all' || task.status === statusFilter;
    const matchPriority = priorityFilter === 'all' || task.priority === priorityFilter;
    return matchSearch && matchStatus && matchPriority;
  });

  const columns: ColumnsType<Task> = [
    {
      title: '任务号',
      dataIndex: 'taskNo',
      key: 'taskNo',
      width: 140,
      fixed: 'left',
      render: (text: string) => (
        <Text strong style={{ color: '#8B0000', fontFamily: 'var(--font-family-serif)' }}>
          {text}
        </Text>
      ),
    },
    {
      title: '任务内容',
      dataIndex: 'title',
      key: 'title',
      width: 280,
      render: (text, record) => (
        <div>
          <Text className="task-name-link" strong>{text}</Text>
          {record.description && (
            <div>
              <Text type="secondary" style={{ fontSize: 12 }} ellipsis>
                {record.description}
              </Text>
            </div>
          )}
        </div>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => {
        const statusInfo = statusMap[status] || statusMap.pending;
        return (
          <Tag 
            icon={statusInfo.icon} 
            style={{ 
              borderRadius: 4,
              color: statusInfo.color,
              background: statusInfo.bgColor,
              border: `1px solid ${statusInfo.color}`,
              fontWeight: 600,
            }}
          >
            {statusInfo.text}
          </Tag>
        );
      },
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 80,
      render: (priority: string) => {
        const priorityInfo = priorityMap[priority] || priorityMap.medium;
        return (
          <Tag 
            className="priority-tag"
            style={{ 
              borderRadius: 4,
              color: priorityInfo.color,
              background: priorityInfo.bgColor,
              border: `1px solid ${priorityInfo.color}`,
              paddingLeft: 16,
              fontWeight: 600,
            }}
          >
            <span 
              style={{
                position: 'absolute',
                left: 6,
                top: '50%',
                transform: 'translateY(-50%)',
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: priorityInfo.dotColor,
              }}
            />
            {priorityInfo.text}
          </Tag>
        );
      },
    },
    {
      title: '挂单人',
      dataIndex: 'creatorName',
      key: 'creatorName',
      width: 100,
      render: (name) => (
        <Space>
          <Avatar 
            size="small" 
            icon={<UserOutlined />} 
            className="creator-avatar"
            style={{ backgroundColor: '#B22222', border: '2px solid #D4C4A8' }}
          >
            {name?.[0]}
          </Avatar>
          <Text style={{ color: '#595959', fontFamily: 'var(--font-family-serif)' }}>{name}</Text>
        </Space>
      ),
    },
    {
      title: '负责人',
      dataIndex: 'assigneeName',
      key: 'assigneeName',
      width: 100,
      render: (name) => (
        <Space>
          <Avatar 
            size="small" 
            icon={<UserOutlined />} 
            className="assignee-avatar"
            style={{ backgroundColor: '#8B0000', border: '2px solid #D4C4A8' }}
          >
            {name?.[0]}
          </Avatar>
          <Text style={{ color: '#595959', fontFamily: 'var(--font-family-serif)' }}>{name}</Text>
        </Space>
      ),
    },
    {
      title: '挂牌时间',
      dataIndex: 'createdAt',
      key: 'createdAt',
      width: 100,
      render: (date) => {
        if (!date) return <Text type="secondary">-</Text>;
        return (
          <Text style={{ fontSize: 12, fontFamily: 'var(--font-family-serif)', color: '#595959' }}>
            {new Date(date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
          </Text>
        );
      },
    },
    {
      title: '完成时间',
      dataIndex: 'completedAt',
      key: 'completedAt',
      width: 100,
      render: (date) => {
        if (!date) return <Text type="secondary">-</Text>;
        return (
          <Text style={{ fontSize: 12, fontFamily: 'var(--font-family-serif)', color: '#228B22' }}>
            {new Date(date).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })}
          </Text>
        );
      },
    },
    {
      title: '项目名称',
      dataIndex: 'projectName',
      key: 'projectName',
      width: 120,
      render: (name) => (
        <Tag 
          className="project-tag"
          style={{ 
            fontSize: 12, 
            padding: '2px 8px', 
            borderRadius: 4, 
            background: 'linear-gradient(180deg, #F5E6C8 0%, #EBD5B3 100%)',
            borderColor: '#D4C4A8',
            fontFamily: 'var(--font-family-serif)',
          }}
        >
          <PushpinOutlined style={{ marginRight: 4, color: '#8B4513' }} />
          {name}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 80,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => handleEdit(record)}
              style={{ color: '#8B0000' }}
            />
          </Tooltip>
          <Tooltip title="查看">
            <Button
              type="text"
              icon={<EyeOutlined />}
              style={{ color: '#595959' }}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const handleEdit = (task: Task) => {
    console.log('编辑任务:', task);
  };

  const overdueCount = tasks.filter(t => 
    t.dueDate && new Date(t.dueDate) < new Date() && t.status !== 'completed'
  ).length;

  const statCards = [
    { title: '总任务', value: statistics.total, icon: <FileTextOutlined />, color: '#8B0000', desc: '江湖任务总数' },
    { title: '进行中', value: statistics.inProgress, icon: <FireOutlined />, color: '#4682B4', desc: '正在执行的任务' },
    { title: '已完成', value: statistics.completed, icon: <CheckCircleOutlined />, color: '#228B22', desc: '已交付的任务' },
    { title: '已逾期', value: overdueCount, icon: <CalendarOutlined />, color: '#DC143C', desc: '需紧急处理' },
  ];

  return (
    <div className="page-container tasks-page">
      {/* 页面标题 - 任务榜 */}
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div className="page-title-wrapper">
            <h1 className="page-title">
              <BookOutlined className="page-title-icon" />
              任务榜
            </h1>
            <p className="page-subtitle">发布江湖任务，调配伙计，追踪进度</p>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            className="publish-task-btn"
          >
            发布任务
          </Button>
        </div>
      </div>

      {/* 统计卡片 - 木牌风格 */}
      <div className="stats-grid">
        {statCards.map((stat, index) => (
          <div key={index} className="stat-card">
            <div className="stat-card-header">
              <div className="stat-card-icon" style={{ color: stat.color }}>
                {stat.icon}
              </div>
            </div>
            <div className="stat-card-value" style={{ color: stat.color }}>
              {stat.value}
            </div>
            <div className="stat-card-title">{stat.title}</div>
            <div style={{ fontSize: 11, color: '#999', marginTop: 4, fontFamily: 'var(--font-family-serif)' }}>
              {stat.desc}
            </div>
          </div>
        ))}
      </div>

      {/* 搜索和筛选 - 案台风格 */}
      <div className="filter-bar">
        <Input
          placeholder="搜索任务名称或负责人"
          prefix={<SearchOutlined style={{ color: '#8c8c8c' }} />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ width: 280, borderRadius: 6 }}
        />
        <Select
          placeholder="状态筛选"
          value={statusFilter}
          onChange={setStatusFilter}
          style={{ width: 140, borderRadius: 6 }}
          allowClear
          suffixIcon={<FilterOutlined />}
        >
          <Option value="all">全部状态</Option>
          <Option value="pending">待开工</Option>
          <Option value="in_progress">进行中</Option>
          <Option value="reviewing">待审核</Option>
          <Option value="completed">已完成</Option>
          <Option value="blocked">阻塞</Option>
        </Select>
        <Select
          placeholder="优先级筛选"
          value={priorityFilter}
          onChange={setPriorityFilter}
          style={{ width: 140, borderRadius: 6 }}
          allowClear
          suffixIcon={<FilterOutlined />}
        >
          <Option value="all">全部优先级</Option>
          <Option value="urgent">紧急</Option>
          <Option value="high">高</Option>
          <Option value="medium">中</Option>
          <Option value="low">低</Option>
        </Select>
      </div>

      {/* 任务列表 - 卷轴风格 */}
      <div className="content-card">
        <div className="content-card-header">
          <span className="content-card-title">
            <FileTextOutlined style={{ color: '#8B0000' }} />
            任务列表
          </span>
          <Text type="secondary" style={{ fontSize: 12, fontFamily: 'var(--font-family-serif)' }}>
            共 {filteredTasks.length} 条记录
          </Text>
        </div>
        <div className="content-card-body" style={{ padding: 0 }}>
          <Table
            className="data-table"
            columns={columns}
            dataSource={filteredTasks}
            rowKey="id"
            pagination={{ 
              pageSize: 10, 
              showSizeChanger: true, 
              showTotal: (total) => `共 ${total} 条`,
              style: { margin: '16px 24px' }
            }}
            loading={loading}
            scroll={{ x: 900 }}
          />
        </div>
      </div>
    </div>
  );
};

export default Tasks;
