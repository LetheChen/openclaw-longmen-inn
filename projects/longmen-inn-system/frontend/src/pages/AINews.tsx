/**
 * AINews - AI资讯页面 (DIE ZEIT / 高端科技编辑风)
 * 深蓝科技感 + 三栏数据可视化布局
 */
import React, { useState, useEffect, useCallback } from 'react';
import { DatePicker, Spin, Empty, Modal } from 'antd';
import api from '../services/api';
import dayjs from 'dayjs';
import './AINews.css';

interface NewsItem {
  date: string;
  title: string;
  content: string;
  source?: string;
  source_url?: string;
  category: string;
}

// 模拟数据统计（用于数据可视化区）
const mockStats = [
  { label: '本年获投 AI 公司', value: 847, unit: '家', color: '#42a5f5' },
  { label: '全球 AI 融资金额', value: 128, unit: '亿美元', color: '#ff6d00' },
  { label: '大模型发布数量', value: 234, unit: '个', color: '#66bb6a' },
  { label: '中国 AI 专利增长', value: 67, unit: '%', color: '#ffca28' },
];

const AINews: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [reportLoading, setReportLoading] = useState(false);
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(dayjs().format('YYYY-MM-DD'));
  const [searchKeyword, setSearchKeyword] = useState('');
  const [filteredItems, setFilteredItems] = useState<NewsItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<NewsItem | null>(null);
  const [previewVisible, setPreviewVisible] = useState(false);

  const loadReport = useCallback(async (date: string) => {
    setReportLoading(true);
    try {
      const res = await api.get(`/intelligence/reports/ai-news?date=${date}`);
      const items = res.data?.items || [];
      setNewsItems(items);
      setFilteredItems(items);
    } catch (err) {
      console.error('[AINews] Failed to load report:', err);
    } finally {
      setLoading(false);
      setReportLoading(false);
    }
  }, []);

  useEffect(() => {
    loadReport(selectedDate);
  }, [selectedDate, loadReport]);

  useEffect(() => {
    if (searchKeyword.trim()) {
      const kw = searchKeyword.toLowerCase();
      setFilteredItems(newsItems.filter(
        item => item.title.toLowerCase().includes(kw) || item.content.toLowerCase().includes(kw)
      ));
    } else {
      setFilteredItems(newsItems);
    }
  }, [searchKeyword, newsItems]);

  const handlePreview = (item: NewsItem) => {
    setSelectedItem(item);
    setPreviewVisible(true);
  };

  const formatDate = (d: string) => dayjs(d).format('YYYY年MM月DD日');
  const formatDateShort = (d: string) => dayjs(d).format('MM/DD');

  // 辅助：将数字转为本地化字符串
  const fmt = (n: number) => n.toLocaleString('zh-CN');

  return (
    <div className="ainews-page">
      {/* ===== 顶部大 Banner ===== */}
      <div className="ainews-banner">
        <div className="banner-bg-lines" aria-hidden="true">
          {Array.from({ length: 8 }).map((_, i) => <div key={i} className="bg-line" />)}
        </div>
        <div className="banner-inner">
          <div className="banner-kicker">
            <span className="banner-tag">INTELLIGENCE</span>
            <span className="banner-date">{dayjs().format('YYYY.MM.DD')}</span>
          </div>
          <h1 className="banner-title">2026 AI 十大趋势</h1>
          <p className="banner-subtitle">从基础模型到行业落地，AI 正在重塑每一个产业</p>
          <div className="banner-stats">
            {mockStats.map((s, i) => (
              <div key={i} className="banner-stat">
                <div className="stat-value" style={{ color: s.color }}>{fmt(s.value)}</div>
                <div className="stat-unit">{s.unit}</div>
                <div className="stat-label">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ===== 控制栏 ===== */}
      <div className="ainews-control-bar">
        <div className="ctrl-left">
          <span className="ctrl-section-label">AI 资讯</span>
        </div>
        <div className="ctrl-center">
          <div className="date-selector">
            <svg className="ctrl-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            <DatePicker
              value={dayjs(selectedDate)}
              onChange={(date) => date && setSelectedDate(date.format('YYYY-MM-DD'))}
              format="YYYY-MM-DD"
              allowClear={false}
            />
          </div>
        </div>
        <div className="ctrl-right">
          <div className="search-box">
            <svg className="ctrl-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              placeholder="搜索 AI 资讯..."
              value={searchKeyword}
              onChange={e => setSearchKeyword(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* ===== 三栏主体 ===== */}
      {(loading || reportLoading) && (
        <div className="ainews-loading">
          <Spin size="large" />
          <p>正在加载 AI 资讯...</p>
        </div>
      )}

      {!loading && !reportLoading && filteredItems.length > 0 && (
        <>
          {/* 三栏区 */}
          <div className="ainews-three-col">
            {/* 左栏：头条大卡 */}
            <div className="ainews-col-left">
              <div className="col-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                今日头条
              </div>
              {filteredItems.slice(0, 1).map((item, idx) => (
                <div key={idx} className="hero-card" onClick={() => handlePreview(item)}>
                  <div className="hero-card-img">
                    <div className="hero-card-overlay">
                      <span className="hero-card-source">{item.source || 'AI 前沿'}</span>
                    </div>
                    <svg className="hero-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                      <circle cx="12" cy="12" r="10"/><path d="M8 12h8M12 8v8"/>
                    </svg>
                  </div>
                  <div className="hero-card-body">
                    <h2 className="hero-card-title">{item.title}</h2>
                    <p className="hero-card-excerpt">
                      {item.content.length > 200 ? item.content.substring(0, 200) + '…' : item.content}
                    </p>
                    <div className="hero-card-foot">
                      <span className="hero-card-date">{formatDate(item.date)}</span>
                      <span className="hero-card-read">阅读全文 →</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* 中栏：数据可视化 */}
            <div className="ainews-col-center">
              <div className="col-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                  <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
                数据透视
              </div>
              <div className="dataviz-panel">
                {/* 大数字区 */}
                <div className="big-numbers">
                  {mockStats.map((s, i) => (
                    <div key={i} className="big-num-item">
                      <div className="big-num-value" style={{ color: s.color }}>{s.value}</div>
                      <div className="big-num-unit">{s.unit}</div>
                      <div className="big-num-label">{s.label}</div>
                    </div>
                  ))}
                </div>
                {/* 迷你条形图 */}
                <div className="mini-bars">
                  <div className="bar-row">
                    <span className="bar-label">美国</span>
                    <div className="bar-track"><div className="bar-fill" style={{ width: '82%', background: '#42a5f5' }}/></div>
                    <span className="bar-val">82%</span>
                  </div>
                  <div className="bar-row">
                    <span className="bar-label">中国</span>
                    <div className="bar-track"><div className="bar-fill" style={{ width: '67%', background: '#ff6d00' }}/></div>
                    <span className="bar-val">67%</span>
                  </div>
                  <div className="bar-row">
                    <span className="bar-label">欧盟</span>
                    <div className="bar-track"><div className="bar-fill" style={{ width: '48%', background: '#66bb6a' }}/></div>
                    <span className="bar-val">48%</span>
                  </div>
                  <div className="bar-row">
                    <span className="bar-label">其他</span>
                    <div className="bar-track"><div className="bar-fill" style={{ width: '31%', background: '#ffca28' }}/></div>
                    <span className="bar-val">31%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 右栏：快讯列表 */}
            <div className="ainews-col-right">
              <div className="col-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><polyline points="13 2 13 9 20 9"/>
                </svg>
                快讯速递
              </div>
              <div className="quick-list">
                {filteredItems.slice(1, 6).map((item, idx) => (
                  <div key={idx} className="quick-item" onClick={() => handlePreview(item)}>
                    <div className="quick-item-num">{String(idx + 2).padStart(2, '0')}</div>
                    <div className="quick-item-body">
                      <div className="quick-item-title">{item.title}</div>
                      <div className="quick-item-meta">
                        <span>{item.source || 'AI前沿'}</span>
                        <span>{formatDateShort(item.date)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* 底部更多内容 */}
          {filteredItems.length > 6 && (
            <div className="ainews-more-section">
              <div className="more-section-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="16" height="16">
                  <circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                </svg>
                更多 AI 资讯
              </div>
              <div className="more-grid">
                {filteredItems.slice(6).map((item, idx) => (
                  <div key={idx} className="more-card" onClick={() => handlePreview(item)}>
                    <div className="more-card-tag">{item.source || 'AI前沿'}</div>
                    <h4 className="more-card-title">{item.title}</h4>
                    <p className="more-card-excerpt">
                      {item.content.length > 100 ? item.content.substring(0, 100) + '…' : item.content}
                    </p>
                    <span className="more-card-date">{formatDate(item.date)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}

      {!loading && !reportLoading && filteredItems.length === 0 && (
        <div className="ainews-empty">
          <Empty description={searchKeyword ? '没有找到相关 AI 资讯' : '暂无 AI 资讯'} />
        </div>
      )}

      {/* 详情弹窗 */}
      <Modal
        title={null}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={720}
        className="ainews-modal"
      >
        {selectedItem && (
          <div className="preview-wrap">
            <div className="preview-kicker">{selectedItem.source || 'AI 前沿'}</div>
            <h2 className="preview-title">{selectedItem.title}</h2>
            <div className="preview-meta-row">
              <span>{formatDate(selectedItem.date)}</span>
              {selectedItem.source && <span>{selectedItem.source}</span>}
            </div>
            <div className="preview-divider" />
            <div className="preview-body">{selectedItem.content}</div>
            {selectedItem.source_url && (
              <a className="preview-link" href={selectedItem.source_url} target="_blank" rel="noopener noreferrer">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
                阅读原文
              </a>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default AINews;
