import React, { useState, useEffect, useCallback } from 'react';
import { 
  Card, 
  Tabs, 
  Calendar, 
  DatePicker, 
  Input, 
  Spin, 
  Empty, 
  Typography, 
  Badge,
  Tag,
  Button,
  Space,
  List,
  Modal,
  Collapse,
  Divider
} from 'antd';
import {
  BellOutlined,
  SearchOutlined,
  CalendarOutlined,
  RobotOutlined,
  FireOutlined,
  ThunderboltOutlined,
  StarOutlined,
  ToolOutlined,
  RocketOutlined,
  GlobalOutlined,
  ExperimentOutlined,
  SettingOutlined,
  EyeOutlined,
  LeftOutlined,
  RightOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import dayjs, { Dayjs } from 'dayjs';
import api from '../services/api';
import './Intelligence.css';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;
const { RangePicker } = DatePicker;

// 10大分类
const CATEGORIES = [
  { key: 'all', emoji: '📋', name: '全部', icon: <BellOutlined /> },
  { key: 'product', emoji: '🆕', name: '产品发布', icon: <RocketOutlined /> },
  { key: 'opensource', emoji: '🐙', name: 'GitHub开源', icon: <StarOutlined /> },
  { key: 'tools', emoji: '🛠️', name: '编程工具', icon: <ToolOutlined /> },
  { key: 'tips', emoji: '🔥', name: 'OpenClaw技巧', icon: <FireOutlined /> },
  { key: 'design', emoji: '🎨', name: 'AI设计', icon: <ThunderboltOutlined /> },
  { key: 'automation', emoji: '⚙️', name: '自动化', icon: <SettingOutlined /> },
  { key: 'labs', emoji: '🧪', name: 'Google Labs', icon: <ExperimentOutlined /> },
  { key: 'agent', emoji: '🤖', name: 'AI Agent', icon: <RobotOutlined /> },
  { key: 'global', emoji: '🌍', name: '全球AI动态', icon: <GlobalOutlined /> },
  { key: 'skills', emoji: '👤', name: 'Claude Skills', icon: <StarOutlined /> },
];

interface ReportItem {
  date: string;
  title: string;
  content: string;
  category: string;
  category_name: string;
  category_emoji: string;
  source_url?: string;
  snippet?: string;
  highlight?: string;
}

interface ReportFile {
  date: string;
  filename: string;
  path: string;
  exists: boolean;
}

interface DailyReportResponse {
  success: boolean;
  date: string;
  report_date: string;
  title: string;
  items: ReportItem[];
  categories: typeof CATEGORIES;
}

interface ReportListResponse {
  success: boolean;
  reports: ReportFile[];
  available_dates: string[];
}

interface SearchResult {
  success: boolean;
  keyword: string;
  results: ReportItem[];
  total: number;
}

const Intelligence: React.FC = () => {
  // 重定向到 AI 资讯页面（原有 /intelligence 路由已废弃）
  useEffect(() => {
    window.location.href = '/intelligence/ai-news';
  }, []);

  return null;

  // 以下为旧版代码，已迁移至各专门页面：
  // - /intelligence/ai-news  → AINews.tsx
  // - /intelligence/news     → NewsPage.tsx
  // - /intelligence/red-news → RedNews.tsx
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>(dayjs().format('YYYY-MM-DD'));
  const [reportData, setReportData] = useState<DailyReportResponse | null>(null);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [searchResults, setSearchResults] = useState<ReportItem[]>([]);
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [previewItem, setPreviewItem] = useState<ReportItem | null>(null);
  const [activeTab, setActiveTab] = useState<string>('browse');

  // 加载可用日期列表
  const loadAvailableDates = useCallback(async () => {
    try {
      const response = await api.get<ReportListResponse>('/intelligence/reports');
      if (response.data.success) {
        setAvailableDates(response.data.available_dates);
      }
    } catch (error) {
      console.error('加载日期列表失败:', error);
    }
  }, []);

  // 加载指定日期的日报
  const loadReport = useCallback(async (date: string, category?: string) => {
    setLoading(true);
    try {
      const params: any = {};
      if (category && category !== 'all') {
        params.category = category;
      }
      const response = await api.get<DailyReportResponse>(`/intelligence/reports/${date}`, { params });
      if (response.data.success) {
        setReportData(response.data);
      }
    } catch (error) {
      console.error('加载日报失败:', error);
      setReportData(null);
    } finally {
      setLoading(false);
    }
  }, []);

  // 搜索
  const searchReports = useCallback(async (keyword: string, category?: string) => {
    if (!keyword.trim()) {
      setSearchResults([]);
      setIsSearching(false);
      return;
    }
    
    setIsSearching(true);
    setSearchLoading(true);
    try {
      const params: any = { keyword };
      if (category && category !== 'all') {
        params.category = category;
      }
      const response = await api.get<SearchResult>('/intelligence/search', { params });
      if (response.data.success) {
        setSearchResults(response.data.results);
      }
    } catch (error) {
      console.error('搜索失败:', error);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  }, []);

  // 初始化
  useEffect(() => {
    loadAvailableDates();
    loadReport(selectedDate);
  }, [loadAvailableDates, loadReport, selectedDate]);

  // 日期变化
  const handleDateChange = (date: Dayjs | null) => {
    if (date) {
      setSelectedDate(date.format('YYYY-MM-DD'));
      setSearchKeyword('');
      setSearchResults([]);
      setIsSearching(false);
    }
  };

  // 分类切换
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category);
    if (isSearching && searchKeyword) {
      searchReports(searchKeyword, category);
    } else {
      loadReport(selectedDate, category);
    }
  };

  // 搜索
  const handleSearch = (value: string) => {
    setSearchKeyword(value);
    if (value.trim()) {
      searchReports(value, selectedCategory);
    } else {
      setSearchResults([]);
      setIsSearching(false);
    }
  };

  // Tab切换
  const handleTabChange = (key: string) => {
    setActiveTab(key);
    if (key === 'browse') {
      setSearchKeyword('');
      setSearchResults([]);
      setIsSearching(false);
    }
  };

  // 日期单元格渲染
  const dateCellRender = (date: Dayjs) => {
    const dateStr = date.format('YYYY-MM-DD');
    const hasReport = availableDates.includes(dateStr);
    return hasReport ? (
      <div className="calendar-dot">
        <Badge status="success" />
      </div>
    ) : null;
  };

  // 渲染日报条目
  const renderReportItem = (item: ReportItem, index: number) => {
    const categoryInfo = CATEGORIES.find(c => c.key === item.category) || CATEGORIES[0];
    
    return (
      <div key={`${item.category}-${index}`} className="report-item">
        <div className="report-item-header">
          <Tag color="red" icon={categoryInfo.icon}>
            {categoryInfo.emoji} {categoryInfo.name}
          </Tag>
          {item.source_url && (
            <Button 
              type="link" 
              size="small" 
              icon={<EyeOutlined />}
              onClick={() => window.open(item.source_url, '_blank')}
            >
              查看原文
            </Button>
          )}
        </div>
        <div className="report-item-title">
          <a 
            href={item.source_url || '#'} 
            target="_blank" 
            rel="noopener noreferrer"
            onClick={(e) => {
              if (!item.source_url) e.preventDefault();
              if (item.source_url) {
                // 高亮显示
              } else {
                setPreviewItem(item);
                e.preventDefault();
              }
            }}
          >
            {item.title}
          </a>
        </div>
        {item.content && (
          <div className="report-item-content">
            {item.snippet ? (
              <Text type="secondary">{item.snippet}</Text>
            ) : (
              <Paragraph 
                ellipsis={{ rows: 2, expandable: true, symbol: '更多' }}
                className="report-item-body"
              >
                {item.content}
              </Paragraph>
            )}
          </div>
        )}
        <Divider className="report-item-divider" />
      </div>
    );
  };

  // 分类Tab items
  const categoryTabItems = CATEGORIES.map(cat => ({
    key: cat.key,
    label: (
      <span className="category-tab">
        {cat.emoji} {cat.name}
      </span>
    ),
  }));

  return (
    <div className="page-container intelligence-page">
      {/* 页面标题 */}
      <div className="page-header">
        <div className="page-title-wrapper">
          <div className="inn-decoration">
            <FireOutlined />
          </div>
          <div>
            <h1 className="page-title">
              <BellOutlined className="page-title-icon" />
              客栈情报
            </h1>
            <p className="page-subtitle">AI 每日简报，洞察行业动态</p>
          </div>
        </div>
      </div>

      {/* 工具栏 */}
      <div className="intelligence-toolbar">
        <div className="toolbar-left">
          <DatePicker
            value={dayjs(selectedDate)}
            onChange={handleDateChange}
            disabledDate={(current) => !availableDates.includes(current.format('YYYY-MM-DD'))}
            format="YYYY-MM-DD"
            placeholder="选择日期"
            allowClear={false}
            className="date-picker"
          />
          <Text type="secondary" className="date-hint">
            {availableDates.length > 0 ? `共 ${availableDates.length} 期日报` : '暂无日报数据'}
          </Text>
        </div>
        <div className="toolbar-right">
          <Input.Search
            placeholder="搜索关键词..."
            allowClear
            enterButton={
              <Button type="primary" icon={<SearchOutlined />}>
                搜索
              </Button>
            }
            value={searchKeyword}
            onChange={(e) => handleSearch(e.target.value)}
            onSearch={handleSearch}
            className="search-input"
          />
        </div>
      </div>

      {/* 内容区域 */}
      <div className="intelligence-content">
        {/* 左侧日历 */}
        <div className="calendar-sidebar">
          <Card className="calendar-card" title={<><CalendarOutlined /> 日期选择</>}>
            <Calendar
              fullscreen={false}
              value={dayjs(selectedDate)}
              onSelect={handleDateChange}
              cellRender={dateCellRender}
              disabledDate={(current) => !availableDates.includes(current.format('YYYY-MM-DD'))}
            />
            <div className="calendar-legend">
              <Badge status="success" text="有日报" />
            </div>
          </Card>

          <Card className="dates-card" title="近期日报">
            <div className="dates-list">
              {availableDates.slice(0, 10).map(date => (
                <div 
                  key={date}
                  className={`date-item ${date === selectedDate ? 'active' : ''}`}
                  onClick={() => handleDateChange(dayjs(date))}
                >
                  <CalendarOutlined />
                  <span>{date}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* 右侧内容 */}
        <div className="content-main">
          <Card className="report-card">
            {/* Tab切换 */}
            <Tabs
              activeKey={activeTab}
              onChange={handleTabChange}
              items={[
                {
                  key: 'browse',
                  label: '📖 浏览',
                  children: (
                    <>
                      <Tabs
                        activeKey={selectedCategory}
                        onChange={handleCategoryChange}
                        type="card"
                        items={categoryTabItems}
                        className="category-tabs"
                      />
                      <div className="report-list">
                        {loading ? (
                          <div className="loading-container">
                            <Spin size="large" tip="加载中..." />
                          </div>
                        ) : reportData && reportData.items.length > 0 ? (
                          <div className="items-container">
                            {reportData.items.map((item, index) => renderReportItem(item, index))}
                          </div>
                        ) : (
                          <Empty description="该日期暂无日报数据" />
                        )}
                      </div>
                    </>
                  ),
                },
                {
                  key: 'search',
                  label: '🔍 搜索结果',
                  children: (
                    <div className="search-results">
                      {isSearching ? (
                        <div className="loading-container">
                          <Spin size="large" tip="搜索中..." />
                        </div>
                      ) : searchResults.length > 0 ? (
                        <>
                          <div className="search-summary">
                            找到 <strong>{searchResults.length}</strong> 条相关内容
                          </div>
                          <div className="items-container">
                            {searchResults.map((item, index) => renderReportItem(item, index))}
                          </div>
                        </>
                      ) : searchKeyword ? (
                        <Empty description={`未找到"${searchKeyword}"相关结果`} />
                      ) : (
                        <Empty description="请输入搜索关键词" />
                      )}
                    </div>
                  ),
                },
              ]}
            />
          </Card>
        </div>
      </div>

      {/* 预览弹窗 */}
      <Modal
        title={
          <Space>
            <span>{previewItem?.category_emoji}</span>
            <span>{previewItem?.title}</span>
          </Space>
        }
        open={!!previewItem}
        onCancel={() => setPreviewItem(null)}
        footer={[
          previewItem?.source_url && (
            <Button 
              key="source" 
              type="primary"
              icon={<EyeOutlined />}
              onClick={() => window.open(previewItem.source_url, '_blank')}
            >
              查看原文
            </Button>
          ),
          <Button key="close" onClick={() => setPreviewItem(null)}>
            关闭
          </Button>,
        ]}
        width={700}
      >
        {previewItem && (
          <div className="preview-content">
            <Tag color="red" icon={CATEGORIES.find(c => c.key === previewItem.category)?.icon}>
              {previewItem.category_emoji} {previewItem.category_name}
            </Tag>
            <Paragraph className="preview-body" style={{ marginTop: 16 }}>
              {previewItem.content}
            </Paragraph>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Intelligence;
