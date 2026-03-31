/**
 * NewsPage - 时事要闻 (经典日报 + 数据新闻风格)
 * 米白纸张色 | 双栏布局 | 进度条可视化
 */
import React, { useState, useEffect, useCallback } from 'react';
import { DatePicker, Spin, Empty, Modal } from 'antd';
import api from '../services/api';
import dayjs from 'dayjs';
import './NewsPage.css';

interface NewsItem {
  date: string;
  title: string;
  content: string;
  source?: string;
  source_url?: string;
  category: string;
}

// 底部数据可视化配置
const pollData = [
  { label: '民众对教育改革支持率', value: 68, color: '#1a237e' },
  { label: '对科技创新政策认同', value: 74, color: '#283593' },
  { label: '对环境保护措施信心', value: 61, color: '#303f9f' },
  { label: '对社会保障体系满意度', value: 55, color: '#3949ab' },
];

const NewsPage: React.FC = () => {
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
      const res = await api.get(`/intelligence/reports/news?date=${date}`);
      const items = res.data?.items || [];
      setNewsItems(items);
      setFilteredItems(items);
    } catch (err) {
      console.error('[NewsPage] Failed to load report:', err);
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
  const formatDateLong = (d: string) => dayjs(d).format('YYYY/MM/DD');

  // 当前期号（简单逻辑）
  const issueNo = dayjs().diff(dayjs('2020-01-01'), 'day');

  return (
    <div className="news-page">
      {/* ===== 大报头 ===== */}
      <div className="news-masthead">
        <div className="masthead-rule" />
        <div className="masthead-inner">
          <div className="masthead-meta masthead-meta--left">
            <span className="masthead-edition">国内版</span>
          </div>
          <div className="masthead-center">
            <div className="masthead-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="32" height="32">
                <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/>
                <path d="M18 14h-8M15 18h-5M10 6h8v4h-8z"/>
              </svg>
            </div>
            <h1 className="masthead-title">时事要闻</h1>
            <div className="masthead-tagline">记录时代 · 见证变革</div>
          </div>
          <div className="masthead-meta masthead-meta--right">
            <span className="masthead-date">{formatDate(selectedDate)}</span>
            <span className="masthead-issue">第 {issueNo} 期</span>
          </div>
        </div>
        <div className="masthead-rule masthead-rule--bold" />
      </div>

      {/* ===== 控制栏 ===== */}
      <div className="news-control-bar">
        <div className="ctrl-left">
          <div className="date-selector">
            <svg className="ctrl-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            <DatePicker
              value={dayjs(selectedDate)}
              onChange={(date) => date && setSelectedDate(date.format('YYYY-MM-DD'))}
              format="YYYY-MM-DD"
              allowClear={false}
            />
          </div>
        </div>
        <div className="ctrl-center">
          <div className="section-pills">
            <span className="pill active">全部</span>
            <span className="pill">政治</span>
            <span className="pill">经济</span>
            <span className="pill">社会</span>
          </div>
        </div>
        <div className="ctrl-right">
          <div className="search-box">
            <svg className="ctrl-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              placeholder="搜索时事要闻..."
              value={searchKeyword}
              onChange={e => setSearchKeyword(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* ===== 双栏主体 ===== */}
      {(loading || reportLoading) && (
        <div className="news-loading">
          <Spin size="large" />
          <p>正在加载时事要闻...</p>
        </div>
      )}

      {!loading && !reportLoading && filteredItems.length > 0 && (
        <>
          <div className="news-body">
            <div className="news-layout">
              {/* 左栏：头条大图+摘要 */}
              <div className="news-main-col">
                {filteredItems.slice(0, 1).map((item, idx) => (
                  <div key={idx} className="lead-story" onClick={() => handlePreview(item)}>
                    <div className="lead-story-img">
                      <div className="lead-img-placeholder">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" width="48" height="48">
                          <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
                          <polyline points="21 15 16 10 5 21"/>
                        </svg>
                      </div>
                      <div className="lead-img-overlay">
                        <span className="lead-img-caption">{item.source || '通讯社'}</span>
                      </div>
                    </div>
                    <div className="lead-story-body">
                      <h2 className="lead-story-title">{item.title}</h2>
                      <p className="lead-story-content">
                        {item.content.length > 280 ? item.content.substring(0, 280) + '…' : item.content}
                      </p>
                      <div className="lead-story-footer">
                        <span className="lead-source">{item.source || '通讯社'}</span>
                        <span className="lead-readmore">阅读全文 →</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* 右栏：要闻列表 */}
              <div className="news-side-col">
                <div className="side-col-header">
                  <span className="side-col-title">其他要闻</span>
                  <span className="side-col-count">{filteredItems.length > 1 ? filteredItems.length - 1 : 0} 条</span>
                </div>
                {filteredItems.slice(1).map((item, idx) => (
                  <div key={idx} className="side-story" onClick={() => handlePreview(item)}>
                    <div className="side-story-num">{String(idx + 2).padStart(2, '0')}</div>
                    <div className="side-story-body">
                      <h3 className="side-story-title">{item.title}</h3>
                      <p className="side-story-excerpt">
                        {item.content.length > 120 ? item.content.substring(0, 120) + '…' : item.content}
                      </p>
                      <div className="side-story-meta">
                        <span>{item.source || '通讯社'}</span>
                        <span>{formatDateLong(item.date)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* ===== 底部数据区 ===== */}
          <div className="news-data-section">
            <div className="data-section-header">
              <div className="data-section-label">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14">
                  <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
                  <line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
                </svg>
                舆情数据
              </div>
              <span className="data-section-sub">数据来源：综合舆情监测 · {formatDateLong(selectedDate)}</span>
            </div>
            <div className="data-polls">
              {pollData.map((poll, i) => (
                <div key={i} className="poll-item">
                  <div className="poll-header">
                    <span className="poll-label">{poll.label}</span>
                    <span className="poll-pct">{poll.value}%</span>
                  </div>
                  <div className="poll-track">
                    <div
                      className="poll-fill"
                      style={{ width: `${poll.value}%`, background: poll.color }}
                    />
                  </div>
                  {/* 左侧大数字 */}
                  <div className="poll-big-num" style={{ color: poll.color }}>{poll.value}</div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {!loading && !reportLoading && filteredItems.length === 0 && (
        <div className="news-empty">
          <Empty description={searchKeyword ? '没有找到相关要闻' : '暂无时事要闻'} />
        </div>
      )}

      {/* 详情弹窗 */}
      <Modal
        title={null}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={760}
        className="news-modal"
      >
        {selectedItem && (
          <div className="preview-wrap">
            <div className="preview-kicker">{selectedItem.source || '通讯社'}</div>
            <h2 className="preview-title">{selectedItem.title}</h2>
            <div className="preview-meta-row">
              <span>{formatDate(selectedItem.date)}</span>
            </div>
            <div className="preview-divider" />
            <div className="preview-body">{selectedItem.content}</div>
            {selectedItem.source_url && (
              <a className="preview-link" href={selectedItem.source_url} target="_blank" rel="noopener noreferrer">
                阅读原文 →
              </a>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default NewsPage;
