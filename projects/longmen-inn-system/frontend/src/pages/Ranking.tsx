import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Avatar,
  Tag,
  Typography,
  Button,
  Space,
  Tabs,
  Tooltip,
  Empty,
  Input,
  Spin,
  message,
} from 'antd';
import {
  TrophyOutlined,
  CrownOutlined,
  FireOutlined,
  StarOutlined,
  RiseOutlined,
  UserOutlined,
  SearchOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined,
  MinusOutlined,
  GoldOutlined,
  FlagOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { getLongmenlingRanking, LongmenlingRankingItem } from '../services/longmenlingService';
import './Ranking.css';

const { Text } = Typography;
const { TabPane } = Tabs;

// 等级配置 - 江湖风
const levelConfig: Record<number, { name: string; color: string; icon: React.ReactNode; minScore: number; title: string }> = {
  1: { name: '见习伙计', color: '#8c8c8c', icon: <UserOutlined />, minScore: 0, title: '初入江湖' },
  2: { name: '初级伙计', color: '#52c41a', icon: <StarOutlined />, minScore: 500, title: '小有所成' },
  3: { name: '中级伙计', color: '#4682B4', icon: <StarOutlined />, minScore: 1000, title: '渐入佳境' },
  4: { name: '高级伙计', color: '#722ed1', icon: <TrophyOutlined />, minScore: 2000, title: '炉火纯青' },
  5: { name: '资深伙计', color: '#FF8C00', icon: <TrophyOutlined />, minScore: 3500, title: '独当一面' },
  6: { name: '金牌伙计', color: '#DAA520', icon: <CrownOutlined />, minScore: 5000, title: '名震一方' },
  7: { name: '长老', color: '#DC143C', icon: <CrownOutlined />, minScore: 8000, title: '德高望重' },
  8: { name: '大掌柜', color: '#8B0000', icon: <FireOutlined />, minScore: 12000, title: '一代宗师' },
};

// 前端展示用的数据接口
interface RankingDisplayItem {
  id: string;
  name: string;
  nickname: string;
  avatar: string;
  level: number;
  longmenling: number;
  completedTasks: number;
  trend: 'up' | 'down' | 'same';
  change: number;
}

const Ranking: React.FC = () => {
  const [rankingData, setRankingData] = useState<RankingDisplayItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [activeTab, setActiveTab] = useState('total');

  // 加载排行榜数据
  useEffect(() => {
    loadRankingData();
  }, []);

  const loadRankingData = async () => {
    setLoading(true);
    try {
      // 加载排行榜数据
      const rankingRes = await getLongmenlingRanking(100);

      // 转换数据为展示格式
      const convertedData: RankingDisplayItem[] = rankingRes.top_agents.map((agent: LongmenlingRankingItem) => ({
        id: agent.agent_id,
        name: agent.name,
        nickname: agent.title || '',
        avatar: agent.avatar_url || '',
        level: agent.level,
        longmenling: agent.longmenling,
        completedTasks: 0, // 暂时不统计完成任务数
        trend: 'same',
        change: 0,
      }));

      setRankingData(convertedData);
    } catch (error) {
      message.error('加载排行榜数据失败');
      console.error('加载排行榜数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 过滤数据
  const filteredData = rankingData.filter(
    (item) =>
      item.name.toLowerCase().includes(searchText.toLowerCase()) ||
      item.nickname?.toLowerCase().includes(searchText.toLowerCase())
  );

  // 获取等级信息
  const getLevelInfo = (level: number) => {
    return levelConfig[level] || levelConfig[1];
  };

  // 表格列定义
  const columns: ColumnsType<RankingDisplayItem> = [
    {
      title: '排名',
      key: 'index',
      width: 80,
      render: (_, record, index) => {
        const rank = index + 1;
        let icon = null;
        if (rank === 1) icon = <CrownOutlined className="rank-icon rank-1" />;
        else if (rank === 2) icon = <TrophyOutlined className="rank-icon rank-2" />;
        else if (rank === 3) icon = <TrophyOutlined className="rank-icon rank-3" />;
        
        return (
          <div className="rank-cell">
            {icon || <span className="rank-number">{rank}</span>}
          </div>
        );
      },
    },
    {
      title: '伙计',
      key: 'agent',
      dataIndex: 'name',
      render: (_, record) => (
        <Space>
          <Avatar
            size={48}
            src={record.avatar}
            icon={!record.avatar && <UserOutlined />}
            className="ranking-avatar"
            style={{ backgroundColor: record.avatar ? undefined : '#8B0000' }}
          >
            {record.name[0]}
          </Avatar>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Text strong style={{ fontSize: 16, fontFamily: 'var(--font-family-serif)' }}>{record.name}</Text>
              {record.nickname && (
                <Tag className="nickname-tag">{record.nickname}</Tag>
              )}
            </div>
            <div style={{ marginTop: 4 }}>
              <Tag
                color={getLevelInfo(record.level).color}
                icon={getLevelInfo(record.level).icon}
                className="level-tag"
              >
                {getLevelInfo(record.level).name} Lv.{record.level}
              </Tag>
            </div>
          </div>
        </Space>
      ),
    },
    {
      title: '龙门令',
      key: 'longmenling',
      dataIndex: 'longmenling',
      width: 150,
      sorter: (a, b) => a.longmenling - b.longmenling,
      render: (_, record) => (
        <div className="longmenling-cell">
          <TrophyOutlined className="longmenling-icon" />
          <Text strong className="longmenling-value">
            {record.longmenling.toLocaleString()}
          </Text>
        </div>
      ),
    },
    {
      title: '完成任务',
      key: 'completedTasks',
      dataIndex: 'completedTasks',
      width: 120,
      sorter: (a, b) => a.completedTasks - b.completedTasks,
      render: (value) => (
        <Text strong style={{ fontSize: 16, fontFamily: 'var(--font-family-serif)' }}>{value} 个</Text>
      ),
    },
    {
      title: '趋势',
      key: 'trend',
      dataIndex: 'trend',
      width: 100,
      render: (_, record) => {
        const trendIcons = {
          up: <ArrowUpOutlined className="trend-up" />,
          down: <ArrowDownOutlined className="trend-down" />,
          same: <MinusOutlined className="trend-same" />,
        };
        return (
          <Tooltip title={`较上周${record.trend === 'up' ? '上升' : record.trend === 'down' ? '下降' : '持平'} ${record.change} 名`}>
            <div className="trend-cell">
              {trendIcons[record.trend]}
              <span className={`trend-text trend-${record.trend}`}>
                {record.change > 0 ? record.change : ''}
              </span>
            </div>
          </Tooltip>
        );
      },
    },
  ];

  return (
    <div className="page-container ranking-page">
      {/* 页面标题 - 英雄榜 */}
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div className="page-title-wrapper">
            <h1 className="page-title">
              <FlagOutlined className="page-title-icon" />
              英雄榜
            </h1>
            <p className="page-subtitle">江湖风云录，龙门令排行，见证客栈英雄辈出的荣耀时刻</p>
          </div>
          <Button 
            icon={<RiseOutlined />}
            className="rules-btn"
          >
            查看升级规则
          </Button>
        </div>
      </div>

      <Spin spinning={loading}>
        {/* TOP 3 展示 - 领奖台风格 */}
        {filteredData.length > 0 && (
          <div className="top3-podium">
            <div className="content-card-body">
              <div className="podium-container">
                {filteredData.slice(0, 3).map((agent, index) => {
                  const rank = index + 1;
                  const rankColors = ['#FFD700', '#C0C0C0', '#CD7F32'];
                  const rankIcons = [
                    <CrownOutlined className="podium-icon podium-gold" />,
                    <TrophyOutlined className="podium-icon podium-silver" />,
                    <TrophyOutlined className="podium-icon podium-bronze" />,
                  ];
                  const podiumHeights = ['200px', '170px', '170px'];
                  const podiumOrder = [1, 0, 2]; // 第二名、第一名、第三名的显示顺序
                  
                  return (
                    <div
                      key={agent.id}
                      className={`podium-item podium-rank-${rank}`}
                      style={{
                        order: podiumOrder[index],
                        borderColor: rankColors[index],
                        transform: rank === 1 ? 'scale(1.08)' : 'scale(1)',
                      }}
                    >
                      <div className="podium-rank-icon">{rankIcons[index]}</div>
                      <Avatar
                        size={rank === 1 ? 84 : 72}
                        src={agent.avatar}
                        icon={!agent.avatar && <UserOutlined />}
                        className="podium-avatar"
                        style={{
                          backgroundColor: agent.avatar ? undefined : '#8B0000',
                          borderColor: rankColors[index],
                        }}
                      >
                        {agent.name[0]}
                      </Avatar>
                      <div className="podium-name">
                        <Text strong style={{ fontSize: rank === 1 ? 20 : 18 }}>
                          {agent.name}
                        </Text>
                      </div>
                      {agent.nickname && (
                        <Tag className="podium-nickname">{agent.nickname}</Tag>
                      )}
                      <div className="podium-score">
                        <Text strong className="podium-longmenling">
                          <TrophyOutlined className="podium-trophy-icon" />
                          {agent.longmenling.toLocaleString()}
                        </Text>
                        <div>
                          <Text type="secondary" className="podium-label">龙门令</Text>
                        </div>
                      </div>
                      <div className="podium-level">
                        <Tag color="#8B0000" className="podium-level-tag">Lv.{agent.level}</Tag>
                        <Text type="secondary" className="podium-tasks">
                          {agent.completedTasks} 个任务
                        </Text>
                      </div>
                      <div 
                        className="podium-base"
                        style={{ height: podiumHeights[index], background: rankColors[index] }}
                      >
                        <span className="podium-rank-number">{rank}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* 完整排行榜 */}
        <div className="content-card ranking-table-card">
          <Tabs 
            activeKey={activeTab} 
            onChange={setActiveTab}
            className="ranking-tabs"
          >
            <TabPane tab="总榜" key="total">
              <div className="ranking-search">
                <Input
                  placeholder="搜索姓名或称号"
                  prefix={<SearchOutlined style={{ color: '#8c8c8c' }} />}
                  value={searchText}
                  onChange={(e) => setSearchText(e.target.value)}
                  allowClear
                  className="ranking-search-input"
                />
              </div>
              <Table
                className="data-table ranking-table"
                columns={columns}
                dataSource={filteredData}
                rowKey="id"
                pagination={{ 
                  pageSize: 10, 
                  showSizeChanger: true, 
                  showTotal: (total) => `共 ${total} 人`,
                  style: { margin: '16px 24px' }
                }}
              />
            </TabPane>
            <TabPane tab="本周榜单" key="weekly">
              <div className="empty-state">
                <Empty 
                  description={<span style={{ fontFamily: 'var(--font-family-serif)' }}>本周榜单数据正在统计中...</span>} 
                  image={Empty.PRESENTED_IMAGE_SIMPLE} 
                />
              </div>
            </TabPane>
            <TabPane tab="月度榜单" key="monthly">
              <div className="empty-state">
                <Empty 
                  description={<span style={{ fontFamily: 'var(--font-family-serif)' }}>月度榜单数据正在统计中...</span>} 
                  image={Empty.PRESENTED_IMAGE_SIMPLE} 
                />
              </div>
            </TabPane>
          </Tabs>
        </div>
      </Spin>
    </div>
  );
};

export default Ranking;
