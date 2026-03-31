import React, { useState, useEffect } from 'react';
import {
  Card,
  Typography,
  Button,
  Tag,
  Space,
  Progress,
  Avatar,
  Tooltip,
  Input,
  Select,
  Empty,
  message,
  Modal,
  Form,
  DatePicker,
} from 'antd';
import {
  FolderOutlined,
  PlusOutlined,
  SearchOutlined,
  CalendarOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  FireOutlined,
  ArrowRightOutlined,
  StarOutlined,
  UserOutlined,
  FilterOutlined,
  TeamOutlined,
  CheckSquareOutlined,
  FlagOutlined,
  PushpinOutlined,
  BuildOutlined,
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { getProjects, createProject } from '../services/projectService';
import { getAgents } from '../services/agentService';
import { getTasks } from '../services/taskService';
import { getReadme } from '../services/fileService';
import ReactMarkdown from 'react-markdown';
import './Projects.css';

const { Text } = Typography;
const { Option } = Select;

interface APIProject {
  id: number;
  name: string;
  description: string | null;
  code: string | null;
  status: string;
  owner_agent_id: string | null;
  start_date: string | null;
  end_date: string | null;
  progress: number;
  created_at: string;
  updated_at: string;
}

interface ProjectDisplay {
  id: string;
  name: string;
  description: string;
  status: string;
  progress: number;
  startDate: string;
  endDate: string;
  manager: { name: string; avatar: string };
  members: { name: string; avatar: string }[];
  taskCount: { total: number; completed: number; inProgress: number; pending: number };
  tags: string[];
  isFavorite: boolean;
}

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<ProjectDisplay[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [stats, setStats] = useState({
    total: 0,
    inProgress: 0,
    completed: 0,
    pending: 0,
  });
  const [readmeVisible, setReadmeVisible] = useState(false);
  const [readmeContent, setReadmeContent] = useState('');
  const [readmeLoading, setReadmeLoading] = useState(false);

  // 项目立项 Modal
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [createForm] = Form.useForm();

  // 状态映射 - 江湖风
  const statusMap: Record<string, { color: string; text: string; icon: React.ReactNode; bgColor: string }> = {
    pending: { 
      color: '#8B4513', 
      text: '待启动', 
      icon: <ClockCircleOutlined />,
      bgColor: 'rgba(139, 69, 19, 0.1)'
    },
    in_progress: { 
      color: '#4682B4', 
      text: '进行中', 
      icon: <FireOutlined />,
      bgColor: 'rgba(70, 130, 180, 0.1)'
    },
    active: { 
      color: '#4682B4', 
      text: '进行中', 
      icon: <FireOutlined />,
      bgColor: 'rgba(70, 130, 180, 0.1)'
    },
    completed: { 
      color: '#228B22', 
      text: '已完成', 
      icon: <CheckCircleOutlined />,
      bgColor: 'rgba(34, 139, 34, 0.1)'
    },
    archived: { 
      color: '#7a7a7a', 
      text: '已归档', 
      icon: <FlagOutlined />,
      bgColor: 'rgba(122, 122, 122, 0.1)'
    },
  };

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [projectsRes, agentsRes, tasksRes] = await Promise.all([
        getProjects({ page: 1, pageSize: 100 }),
        getAgents(),
        getTasks({ page: 1, pageSize: 100 }),
      ]);

      const agentMap: Record<string, string> = {};
      agentsRes.forEach((agent: any) => {
        agentMap[agent.agent_id] = agent.name;
      });

      const projectTaskStats: Record<number, { total: number; completed: number; inProgress: number; pending: number }> = {};
      tasksRes.data.forEach((task: any) => {
        const projectId = task.projectId ? parseInt(task.projectId) : null;
        if (projectId) {
          if (!projectTaskStats[projectId]) {
            projectTaskStats[projectId] = { total: 0, completed: 0, inProgress: 0, pending: 0 };
          }
          projectTaskStats[projectId].total++;
          if (task.status === 'completed') {
            projectTaskStats[projectId].completed++;
          } else if (task.status === 'in_progress') {
            projectTaskStats[projectId].inProgress++;
          } else if (task.status === 'pending') {
            projectTaskStats[projectId].pending++;
          }
        }
      });

      const convertedProjects: ProjectDisplay[] = (projectsRes.data as unknown as APIProject[]).map((apiProject: APIProject) => {
        const taskCount = projectTaskStats[apiProject.id] || { total: 0, completed: 0, inProgress: 0, pending: 0 };
        const managerName = apiProject.owner_agent_id ? agentMap[apiProject.owner_agent_id] || '未分配' : '未分配';
        const calculatedProgress = taskCount.total > 0 ? Math.round((taskCount.completed / taskCount.total) * 100) : 0;
        
        return {
          id: String(apiProject.id),
          name: apiProject.name,
          description: apiProject.description || '暂无描述',
          status: apiProject.status,
          progress: calculatedProgress,
          startDate: apiProject.start_date ? apiProject.start_date.split('T')[0] : '',
          endDate: apiProject.end_date ? apiProject.end_date.split('T')[0] : '',
          manager: { name: managerName, avatar: '' },
          members: [],
          tags: ['龙门客栈'],
          isFavorite: false,
          taskCount: taskCount,
        };
      });

      setProjects(convertedProjects);
      setStats({
        total: convertedProjects.length,
        inProgress: convertedProjects.filter((p) => p.status === 'in_progress' || p.status === 'active').length,
        completed: convertedProjects.filter((p) => p.status === 'completed').length,
        pending: convertedProjects.filter((p) => p.status === 'pending').length,
      });
    } catch (error) {
      message.error('加载项目数据失败');
      console.error('加载项目数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = () => {
    createForm.resetFields();
    setCreateModalVisible(true);
  };

  const handleCreateSubmit = async () => {
    try {
      const values = await createForm.validateFields();
      const payload: any = {
        name: values.name,
        description: values.description,
        status: values.status || 'pending',
      };
      // 如果后端支持 start_date 和 end_date，则添加
      if (values.startDate) {
        payload.startDate = values.startDate.format('YYYY-MM-DD');
      }
      if (values.endDate) {
        payload.endDate = values.endDate.format('YYYY-MM-DD');
      }
      await createProject(payload);
      message.success('项目创建成功');
      setCreateModalVisible(false);
      loadData();
    } catch (error: any) {
      if (error.errorFields) {
        return; // 表单验证失败
      }
      message.error('创建项目失败');
      console.error('创建项目失败:', error);
    }
  };

  const filteredProjects = projects.filter((project) => {
    const matchSearch =
      project.name.toLowerCase().includes(searchText.toLowerCase()) ||
      project.description.toLowerCase().includes(searchText.toLowerCase()) ||
      project.tags.some((tag) => tag.toLowerCase().includes(searchText.toLowerCase()));
    const matchStatus = statusFilter === 'all' || project.status === statusFilter;
    return matchSearch && matchStatus;
  });

  const handleViewReadme = async () => {
    setReadmeLoading(true);
    setReadmeVisible(true);
    try {
      const result = await getReadme();
      setReadmeContent(result.content);
    } catch (error) {
      message.error('加载README失败');
      setReadmeContent('# 暂无README内容');
    } finally {
      setReadmeLoading(false);
    }
  };

  const statCards = [
    { title: '总项目', value: stats.total, icon: <FolderOutlined />, color: '#8B0000', desc: '江湖项目总数' },
    { title: '进行中', value: stats.inProgress, icon: <FireOutlined />, color: '#4682B4', desc: '正在执行的项目' },
    { title: '已完成', value: stats.completed, icon: <CheckCircleOutlined />, color: '#228B22', desc: '已交付的项目' },
    { title: '待启动', value: stats.pending, icon: <ClockCircleOutlined />, color: '#DAA520', desc: '筹备中的项目' },
  ];

  return (
    <div className="page-container projects-page">
      {/* 页面标题 - 项目堂 */}
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div className="page-title-wrapper">
            <h1 className="page-title">
              <BuildOutlined className="page-title-icon" />
              项目堂
            </h1>
            <p className="page-subtitle">统筹江湖大业，运筹帷幄，决胜千里</p>
          </div>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            size="large"
            className="create-project-btn"
            onClick={handleCreateProject}
          >
            立项
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
          placeholder="搜索项目名称、描述或标签"
          prefix={<SearchOutlined style={{ color: '#8c8c8c' }} />}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ width: 320, borderRadius: 6 }}
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
          <Option value="pending">待启动</Option>
          <Option value="in_progress">进行中</Option>
          <Option value="completed">已完成</Option>
        </Select>
      </div>

      {/* 项目卡片网格 - 木牌风格 */}
      <div className="card-grid">
        {filteredProjects.map((project) => {
          const statusInfo = statusMap[project.status] || statusMap.pending;
          return (
            <Card
              key={project.id}
              className="card-item project-card"
              hoverable
              bodyStyle={{ padding: 0 }}
            >
              {/* 卡片头部 */}
              <div className="card-item-header">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                  <Text strong style={{ fontSize: 17, flex: 1, marginRight: 8, color: '#262626', fontFamily: 'var(--font-family-serif)' }}>
                    {project.isFavorite && <StarOutlined style={{ color: '#DAA520', marginRight: 6 }} />}
                    {project.name}
                  </Text>
                  <Tag 
                    color={statusInfo.color} 
                    icon={statusInfo.icon} 
                    style={{ 
                      borderRadius: 4, 
                      fontSize: 11,
                      background: statusInfo.bgColor,
                      border: `1px solid ${statusInfo.color}`,
                      fontFamily: 'var(--font-family-serif)',
                    }}
                  >
                    {statusInfo.text}
                  </Tag>
                </div>
                <Text 
                  type="secondary" 
                  style={{ 
                    fontSize: 13, 
                    overflow: 'hidden', 
                    textOverflow: 'ellipsis', 
                    whiteSpace: 'nowrap', 
                    display: 'block',
                    fontFamily: 'var(--font-family-serif)',
                  }}
                >
                  {project.description}
                </Text>
              </div>

              {/* 卡片主体 */}
              <div className="card-item-body">
                {/* 进度条 - 血条风格 */}
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                    <Text type="secondary" style={{ fontSize: 12, fontFamily: 'var(--font-family-serif)' }}>项目进度</Text>
                    <Text strong style={{ fontSize: 12, color: '#8B0000', fontFamily: 'var(--font-family-serif)' }}>{project.progress}%</Text>
                  </div>
                  <Progress
                    percent={project.progress}
                    size="small"
                    status={project.progress === 100 ? 'success' : 'active'}
                    strokeColor={project.progress === 100 ? '#228B22' : {
                      '0%': '#B22222',
                      '100%': '#8B0000',
                    }}
                    trailColor="#f0f0f0"
                    className="project-progress"
                  />
                </div>

                {/* 任务统计 - 令牌风格 */}
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-around',
                    padding: '12px 0',
                    background: 'linear-gradient(180deg, #F5E6C8 0%, #EBD5B3 100%)',
                    borderRadius: 8,
                    marginBottom: 16,
                    border: '1px solid #D4C4A8',
                  }}
                >
                  <div style={{ textAlign: 'center' }}>
                    <Text strong style={{ fontSize: 20, color: '#262626', fontFamily: 'var(--font-family-serif)' }}>
                      {project.taskCount.total}
                    </Text>
                    <div>
                      <Text type="secondary" style={{ fontSize: 11, fontFamily: 'var(--font-family-serif)' }}>总任务</Text>
                    </div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Text strong style={{ fontSize: 20, color: '#228B22', fontFamily: 'var(--font-family-serif)' }}>
                      {project.taskCount.completed}
                    </Text>
                    <div>
                      <Text type="secondary" style={{ fontSize: 11, fontFamily: 'var(--font-family-serif)' }}>已完成</Text>
                    </div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <Text strong style={{ fontSize: 20, color: '#4682B4', fontFamily: 'var(--font-family-serif)' }}>
                      {project.taskCount.inProgress}
                    </Text>
                    <div>
                      <Text type="secondary" style={{ fontSize: 11, fontFamily: 'var(--font-family-serif)' }}>进行中</Text>
                    </div>
                  </div>
                </div>

                {/* 负责人和团队 */}
                <div style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', marginBottom: 8 }}>
                    <UserOutlined style={{ color: '#8c8c8c', marginRight: 8, fontSize: 12 }} />
                    <Text type="secondary" style={{ fontSize: 12, marginRight: 8, fontFamily: 'var(--font-family-serif)' }}>负责人</Text>
                    <Avatar 
                      size={24} 
                      icon={<UserOutlined />} 
                      style={{ 
                        backgroundColor: '#8B0000', 
                        marginRight: 6,
                        border: '2px solid #D4C4A8',
                      }}
                    >
                      {project.manager.name[0]}
                    </Avatar>
                    <Text style={{ fontSize: 12, color: '#595959', fontFamily: 'var(--font-family-serif)' }}>{project.manager.name}</Text>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center' }}>
                    <TeamOutlined style={{ color: '#8c8c8c', marginRight: 8, fontSize: 12 }} />
                    <Text type="secondary" style={{ fontSize: 12, marginRight: 8, fontFamily: 'var(--font-family-serif)' }}>团队</Text>
                    <Avatar.Group maxCount={3} size="small">
                      {project.members.length > 0 ? project.members.map((member, index) => (
                        <Avatar 
                          key={index} 
                          icon={<UserOutlined />} 
                          style={{ backgroundColor: '#8B0000', border: '2px solid #D4C4A8' }}
                        >
                          {member.name[0]}
                        </Avatar>
                      )) : (
                        <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#d9d9d9' }}>?</Avatar>
                      )}
                    </Avatar.Group>
                  </div>
                </div>

                {/* 截止日期和标签 */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Space size={4} wrap>
                    {project.tags.map((tag, index) => (
                      <Tag 
                        key={index} 
                        style={{ 
                          fontSize: 11, 
                          padding: '2px 8px', 
                          borderRadius: 4, 
                          margin: 0,
                          background: 'linear-gradient(180deg, #F5E6C8 0%, #EBD5B3 100%)',
                          borderColor: '#D4C4A8',
                          fontFamily: 'var(--font-family-serif)',
                        }}
                      >
                        <PushpinOutlined style={{ marginRight: 4, color: '#8B4513' }} />
                        {tag}
                      </Tag>
                    ))}
                  </Space>
                  <Text type="secondary" style={{ fontSize: 11, fontFamily: 'var(--font-family-serif)' }}>
                    <CalendarOutlined style={{ marginRight: 4, color: '#8B0000' }} />
                    {project.endDate ? new Date(project.endDate).toLocaleDateString('zh-CN') : '未设置'}
                  </Text>
                </div>
              </div>

              {/* 卡片底部 */}
              <div className="card-item-footer" style={{ display: 'flex', justifyContent: 'space-between' }}>
                <Button 
                  type="link" 
                  icon={<ArrowRightOutlined />} 
                  className="view-detail-btn"
                  style={{ color: '#8B0000', padding: 0, fontFamily: 'var(--font-family-serif)' }}
                  onClick={handleViewReadme}
                >
                  查看详情
                </Button>
                <Button 
                  type="text" 
                  size="small" 
                  className="edit-btn"
                  style={{ color: '#595959', fontFamily: 'var(--font-family-serif)' }}
                >
                  编辑
                </Button>
              </div>
            </Card>
          );
        })}
      </div>

      {filteredProjects.length === 0 && !loading && (
        <div className="empty-state">
          <Empty 
            description={<span style={{ fontFamily: 'var(--font-family-serif)' }}>没有找到匹配的项目</span>} 
            image={Empty.PRESENTED_IMAGE_SIMPLE} 
          />
        </div>
      )}

      <Modal
        title={
          <span style={{ fontFamily: 'var(--font-family-serif)', fontSize: 18, color: '#8B0000' }}>
            <BuildOutlined style={{ marginRight: 8 }} />
            项目详情 - README.md
          </span>
        }
        open={readmeVisible}
        onCancel={() => setReadmeVisible(false)}
        footer={null}
        width={800}
        style={{ top: 40 }}
        bodyStyle={{ 
          maxHeight: '70vh', 
          overflow: 'auto',
          background: 'linear-gradient(180deg, #FDF8F0 0%, #F5E6C8 100%)',
          padding: 24,
        }}
      >
        {readmeLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Text type="secondary">加载中...</Text>
          </div>
        ) : (
          <div 
            className="markdown-body"
            style={{
              fontFamily: 'var(--font-family-serif)',
              lineHeight: 1.8,
              color: '#262626',
            }}
          >
            <ReactMarkdown>{readmeContent}</ReactMarkdown>
          </div>
        )}
      </Modal>

      {/* 项目立项 Modal */}
      <Modal
        title={
          <span style={{ fontFamily: 'var(--font-family-serif)', fontSize: 18, color: '#8B0000' }}>
            <BuildOutlined style={{ marginRight: 8 }} />
            项目立项
          </span>
        }
        open={createModalVisible}
        onOk={handleCreateSubmit}
        onCancel={() => setCreateModalVisible(false)}
        okText="创建项目"
        cancelText="取消"
        width={600}
        bodyStyle={{ padding: '24px' }}
      >
        <Form
          form={createForm}
          layout="vertical"
          initialValues={{ status: 'pending' }}
        >
          <Form.Item
            name="name"
            label="项目名称"
            rules={[{ required: true, message: '请输入项目名称' }]}
          >
            <Input placeholder="请输入项目名称" maxLength={200} />
          </Form.Item>
          <Form.Item
            name="description"
            label="项目描述"
          >
            <Input.TextArea placeholder="请输入项目描述（可选）" rows={3} maxLength={1000} showCount />
          </Form.Item>
          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="status"
              label="项目状态"
              style={{ flex: 1 }}
            >
              <Select>
                <Option value="pending">🟤 待启动</Option>
                <Option value="active">🔵 进行中</Option>
                <Option value="completed">🟢 已完成</Option>
              </Select>
            </Form.Item>
          </div>
          <div style={{ display: 'flex', gap: 16 }}>
            <Form.Item
              name="startDate"
              label="开始日期"
              style={{ flex: 1 }}
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择开始日期（可选）" />
            </Form.Item>
            <Form.Item
              name="endDate"
              label="结束日期"
              style={{ flex: 1 }}
            >
              <DatePicker style={{ width: '100%' }} placeholder="请选择结束日期（可选）" />
            </Form.Item>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

// [F04] 项目立项表单 - 已实现：立项按钮 + CreateProject Modal + 表单验证（支持 startDate/endDate）

export default Projects;
