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
  Modal,
  Form,
  DatePicker,
  Tabs,
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
  DeleteOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import type { ColumnsType } from 'antd/es/table';
import { TaskStatus, TaskPriority } from '../types/task';
import type { Task } from '../types/task';
import { getTasks, getTaskStatistics, createTask, updateTask, deleteTask, getKanbanData, batchUpdateTaskStatus } from '../services/taskService';
import KanbanBoard from '../components/common/KanbanBoard';
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
  const [agents, setAgents] = useState<any[]>([]);
  const [projects, setProjects] = useState<any[]>([]);

  // 新建任务 Modal
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [createForm] = Form.useForm();

  // 任务详情/编辑 Modal
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [detailForm] = Form.useForm();

  // 看板相关
  const [activeTab, setActiveTab] = useState<string>('list');
  const [kanbanData, setKanbanData] = useState<{ pending: Task[]; inProgress: Task[]; review: Task[]; completed: Task[] }>({
    pending: [],
    inProgress: [],
    review: [],
    completed: [],
  });
  const [kanbanLoading, setKanbanLoading] = useState(false);

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
      setAgents(agentsRes);

      const projectMap: Record<number, string> = {};
      projectsRes.data.forEach((project: any) => {
        projectMap[project.id] = project.name;
      });
      setProjectsMap(projectMap);
      setProjects(projectsRes.data);

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
      width: 120,
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
              onClick={() => handleView(record)}
              style={{ color: '#595959' }}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              icon={<DeleteOutlined />}
              onClick={() => handleDelete(record)}
              style={{ color: '#ff4d4f' }}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const handleEdit = (task: Task) => {
    setEditingTask(task);
    detailForm.setFieldsValue({
      title: task.title,
      description: task.description,
      projectId: task.projectId,
      assigneeId: task.assigneeId,
      priority: task.priority,
      dueDate: task.dueDate ? dayjs(task.dueDate) : null,
    });
    setIsEditing(false);
    setDetailModalVisible(true);
  };

  const handleView = (task: Task) => {
    setEditingTask(task);
    detailForm.setFieldsValue({
      title: task.title,
      description: task.description,
      projectId: task.projectId,
      assigneeId: task.assigneeId,
      priority: task.priority,
      dueDate: task.dueDate ? dayjs(task.dueDate) : null,
    });
    setIsEditing(false);
    setDetailModalVisible(true);
  };

  const handleDelete = (task: Task) => {
    Modal.confirm({
      title: '确认删除任务',
      icon: <ExclamationCircleOutlined />,
      content: (
        <div>
          <p style={{ marginBottom: 8 }}>确定要删除任务「{task.title}」吗？</p>
          <p style={{ color: '#ff4d4f', marginBottom: 0 }}>此操作不可恢复</p>
        </div>
      ),
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await deleteTask(task.id);
          message.success('任务删除成功');
          loadData();
        } catch (error) {
          message.error('删除任务失败');
          console.error('删除任务失败:', error);
        }
      },
    });
  };

  const handleCreateTask = () => {
    createForm.resetFields();
    setCreateModalVisible(true);
  };

  const handleCreateSubmit = async () => {
    try {
      const values = await createForm.validateFields();
      const payload: any = {
        title: values.title,
        description: values.description,
        projectId: values.projectId,
        assigneeId: values.assigneeId,
        priority: values.priority || 'medium',
        dueDate: values.dueDate ? values.dueDate.format('YYYY-MM-DD') : undefined,
      };
      await createTask(payload);
      message.success('任务创建成功');
      setCreateModalVisible(false);
      loadData();
    } catch (error: any) {
      if (error.errorFields) {
        return; // 表单验证失败
      }
      message.error('创建任务失败');
      console.error('创建任务失败:', error);
    }
  };

  const handleDetailEdit = () => {
    setIsEditing(true);
  };

  const handleDetailSave = async () => {
    if (!editingTask) return;
    try {
      const values = await detailForm.validateFields();
      const payload: any = {
        title: values.title,
        description: values.description,
        projectId: values.projectId,
        assigneeId: values.assigneeId,
        priority: values.priority,
        dueDate: values.dueDate ? values.dueDate.format('YYYY-MM-DD') : undefined,
      };
      await updateTask(editingTask.id, payload);
      message.success('任务更新成功');
      setDetailModalVisible(false);
      setIsEditing(false);
      loadData();
    } catch (error: any) {
      if (error.errorFields) {
        return;
      }
      message.error('更新任务失败');
      console.error('更新任务失败:', error);
    }
  };

  const handleDetailCancel = () => {
    setDetailModalVisible(false);
    setIsEditing(false);
    setEditingTask(null);
  };

  const handleTabChange = (key: string) => {
    setActiveTab(key);
    if (key === 'kanban') {
      loadKanbanData();
    }
  };

  const loadKanbanData = async () => {
    setKanbanLoading(true);
    try {
      const data = await getKanbanData();
      setKanbanData(data);
    } catch (error) {
      message.error('加载看板数据失败');
      console.error('加载看板数据失败:', error);
    } finally {
      setKanbanLoading(false);
    }
  };

  const handleKanbanTaskMove = async (taskId: string, sourceStatus: string, targetStatus: string) => {
    try {
      await batchUpdateTaskStatus([taskId], targetStatus);
      message.success('任务状态已更新');
      loadKanbanData();
      loadData();
    } catch (error) {
      message.error('更新任务状态失败');
      console.error('更新任务状态失败:', error);
    }
  };

  const handleKanbanTaskClick = (task: Task) => {
    handleView(task);
  };

  const handleKanbanAddTask = (columnId: TaskStatus) => {
    createForm.resetFields();
    createForm.setFieldsValue({ status: columnId });
    setCreateModalVisible(true);
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
            onClick={handleCreateTask}
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

      {/* 任务列表/看板切换 */}
      <Tabs
        activeKey={activeTab}
        onChange={handleTabChange}
        items={[
          {
            key: 'list',
            label: (
              <span>
                <FileTextOutlined style={{ marginRight: 6 }} />
                列表
              </span>
            ),
            children: (
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
            ),
          },
          {
            key: 'kanban',
            label: (
              <span>
                <PushpinOutlined style={{ marginRight: 6 }} />
                看板
              </span>
            ),
            children: (
              <KanbanBoard
                columns={[
                  {
                    id: 'pending' as TaskStatus,
                    title: '待开工',
                    tasks: kanbanData.pending,
                    color: '#8B4513',
                    icon: <ClockCircleOutlined />,
                  },
                  {
                    id: 'in_progress' as TaskStatus,
                    title: '进行中',
                    tasks: kanbanData.inProgress,
                    color: '#4682B4',
                    icon: <FireOutlined />,
                  },
                  {
                    id: 'reviewing' as TaskStatus,
                    title: '待审核',
                    tasks: kanbanData.review,
                    color: '#DAA520',
                    icon: <EyeOutlined />,
                  },
                  {
                    id: 'completed' as TaskStatus,
                    title: '已完成',
                    tasks: kanbanData.completed,
                    color: '#228B22',
                    icon: <CheckCircleOutlined />,
                  },
                ]}
                loading={kanbanLoading}
                draggable={true}
                onTaskMove={handleKanbanTaskMove}
                onTaskClick={handleKanbanTaskClick}
                onAddTask={handleKanbanAddTask}
                cardSize="default"
              />
            ),
          },
        ]}
      />

      {/* 新建任务 Modal */}
      <Modal
        title={
          <span style={{ fontFamily: 'var(--font-family-serif)', fontSize: 18, color: '#8B0000' }}>
            <PlusOutlined style={{ marginRight: 8 }} />
            发布新任务
          </span>
        }
        open={createModalVisible}
        onOk={handleCreateSubmit}
        onCancel={() => setCreateModalVisible(false)}
        okText="发布任务"
        cancelText="取消"
        width={600}
        bodyStyle={{ padding: '24px' }}
      >
        <Form
          form={createForm}
          layout="vertical"
          initialValues={{ priority: 'medium', status: 'pending' }}
        >
          <Form.Item
            name="title"
            label="任务标题"
            rules={[{ required: true, message: '请输入任务标题' }]}
          >
            <Input placeholder="请输入任务标题" maxLength={200} />
          </Form.Item>
          <Form.Item
            name="description"
            label="任务描述"
          >
            <Input.TextArea placeholder="请输入任务描述（可选）" rows={3} maxLength={1000} showCount />
          </Form.Item>
          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="projectId"
              label="所属项目"
              style={{ flex: 1 }}
            >
              <Select placeholder="请选择项目（可选）" allowClear>
                {projects.map((p: any) => (
                  <Option key={p.id} value={String(p.id)}>{p.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="assigneeId"
              label="负责人"
              style={{ flex: 1 }}
            >
              <Select placeholder="请选择负责人（可选）" allowClear>
                {agents.map((agent: any) => (
                  <Option key={agent.agent_id} value={agent.agent_id}>{agent.name}</Option>
                ))}
              </Select>
            </Form.Item>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="priority"
              label="优先级"
              style={{ flex: 1 }}
            >
              <Select>
                <Option value="urgent">🔴 紧急 (P0)</Option>
                <Option value="high">🟠 高 (P1)</Option>
                <Option value="medium">🔵 中 (P2)</Option>
                <Option value="low">⚪ 低 (P3)</Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="dueDate"
              label="截止时间"
              style={{ flex: 1 }}
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择截止时间（可选）" />
            </Form.Item>
          </div>
        </Form>
      </Modal>

      {/* 任务详情/编辑 Modal */}
      <Modal
        title={
          <span style={{ fontFamily: 'var(--font-family-serif)', fontSize: 18, color: '#8B0000' }}>
            {isEditing ? (
              <>
                <EditOutlined style={{ marginRight: 8 }} />
                编辑任务
              </>
            ) : (
              <>
                <EyeOutlined style={{ marginRight: 8 }} />
                任务详情
              </>
            )}
          </span>
        }
        open={detailModalVisible}
        onOk={isEditing ? handleDetailSave : handleDetailEdit}
        onCancel={handleDetailCancel}
        okText={isEditing ? '保存' : '编辑'}
        cancelText="关闭"
        width={600}
        bodyStyle={{ padding: '24px' }}
        footer={isEditing ? (
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <Button
              danger
              icon={<DeleteOutlined />}
              onClick={() => editingTask && handleDelete(editingTask)}
            >
              删除任务
            </Button>
            <Space>
              <Button onClick={handleDetailCancel}>取消</Button>
              <Button type="primary" onClick={handleDetailSave}>保存</Button>
            </Space>
          </div>
        ) : null}
      >
        <Form
          form={detailForm}
          layout="vertical"
          disabled={!isEditing}
        >
          <Form.Item
            name="title"
            label="任务标题"
            rules={[{ required: true, message: '请输入任务标题' }]}
          >
            <Input placeholder="请输入任务标题" />
          </Form.Item>
          <Form.Item
            name="description"
            label="任务描述"
          >
            <Input.TextArea placeholder="请输入任务描述" rows={3} />
          </Form.Item>
          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="projectId"
              label="所属项目"
              style={{ flex: 1 }}
            >
              <Select placeholder="请选择项目" allowClear>
                {projects.map((p: any) => (
                  <Option key={p.id} value={String(p.id)}>{p.name}</Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name="assigneeId"
              label="负责人"
              style={{ flex: 1 }}
            >
              <Select placeholder="请选择负责人" allowClear>
                {agents.map((agent: any) => (
                  <Option key={agent.agent_id} value={agent.agent_id}>{agent.name}</Option>
                ))}
              </Select>
            </Form.Item>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="priority"
              label="优先级"
              style={{ flex: 1 }}
            >
              <Select>
                <Option value="urgent">🔴 紧急 (P0)</Option>
                <Option value="high">🟠 高 (P1)</Option>
                <Option value="medium">🔵 中 (P2)</Option>
                <Option value="low">⚪ 低 (P3)</Option>
              </Select>
            </Form.Item>
            <Form.Item
              name="dueDate"
              label="截止时间"
              style={{ flex: 1 }}
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择截止时间" />
            </Form.Item>
          </div>
          {editingTask && !isEditing && (
            <div style={{ marginTop: 16, padding: 16, background: '#f5f5f5', borderRadius: 8 }}>
              <p style={{ marginBottom: 8 }}>
                <Text type="secondary">任务号：</Text>
                <Text strong style={{ color: '#8B0000' }}>{editingTask.taskNo}</Text>
              </p>
              <p style={{ marginBottom: 8 }}>
                <Text type="secondary">状态：</Text>
                {statusMap[editingTask.status] && (
                  <Tag style={{ background: statusMap[editingTask.status].bgColor, borderColor: statusMap[editingTask.status].color, color: statusMap[editingTask.status].color }}>
                    {statusMap[editingTask.status].icon} {statusMap[editingTask.status].text}
                  </Tag>
                )}
              </p>
              <p style={{ marginBottom: 8 }}>
                <Text type="secondary">创建时间：</Text>
                <Text>{new Date(editingTask.createdAt).toLocaleString('zh-CN')}</Text>
              </p>
              {editingTask.completedAt && (
                <p style={{ marginBottom: 0 }}>
                  <Text type="secondary">完成时间：</Text>
                  <Text style={{ color: '#228B22' }}>{new Date(editingTask.completedAt).toLocaleString('zh-CN')}</Text>
                </p>
              )}
            </div>
          )}
        </Form>
      </Modal>
    </div>
  );
};

// [F01] 任务创建表单 - 已实现：发布任务按钮 + CreateTask Modal + 表单验证
// [F02] 任务详情弹窗 - 已实现：查看任务详情 Modal
// [F03] 任务编辑表单 - 已实现：编辑按钮切换为可编辑表单 + 保存更新
// [F05] 任务删除 - 已实现：删除按钮 + Modal.confirm 二次确认
// [F06/F07] 看板视图 - 已实现：列表/看板 Tab 切换 + KanbanBoard 组件 + 拖拽更新状态

export default Tasks;
