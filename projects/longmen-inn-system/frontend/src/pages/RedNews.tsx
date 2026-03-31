/**
 * RedNews - 红色印记 (党政期刊 + 现代设计风格)
 * 红色主调 | 金色点缀 | 网格布局
 */
import React, { useState, useEffect, useCallback } from 'react';
import { DatePicker, Spin, Empty, Modal } from 'antd';
import api from '../services/api';
import dayjs from 'dayjs';
import './RedNews.css';

interface NewsItem {
  date: string;
  title: string;
  content: string;
  source?: string;
  source_url?: string;
  category: string;
}

const RedNews: React.FC = () => {
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
      const res = await api.get(`/intelligence/reports/red-news?date=${date}`);
      const items = res.data?.items || [];
      setNewsItems(items);
      setFilteredItems(items);
    } catch (err) {
      console.error('[RedNews] Failed to load report:', err);
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

  return (
    <div className="rednews-page">
      {/* ===== 红色横幅 Header ===== */}
      <div className="rednews-header">
        <div className="rednews-header-bg" aria-hidden="true">
          <div className="header-bg-pattern" />
        </div>
        <div className="rednews-header-inner">
          <div className="header-emblem">
            <svg viewBox="0 0 24 24" fill="none" stroke="#ffd700" strokeWidth="1.5" width="36" height="36">
              <path d="M3 21h18M3 7v14M21 7v14M6 7V3h12v4"/>
              <path d="M18 7V3H6v4M9 21v-6h6v6"/>
              <circle cx="12" cy="11" r="1.5" fill="#ffd700" stroke="none"/>
            </svg>
          </div>
          <div className="header-text-group">
            <div className="header-eyebrow">传承红色基因 · 弘扬革命精神</div>
            <h1 className="header-title">红色印记</h1>
            <div className="header-date-line">
              <span className="header-date">{formatDate(selectedDate)}</span>
              <span className="header-sep">|</span>
              <span className="header-issue">党政要闻</span>
            </div>
          </div>
          <div className="header-emblem header-emblem--right">
            <svg viewBox="0 0 24 24" fill="none" stroke="#ffd700" strokeWidth="1.5" width="36" height="36">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
        </div>
        {/* 金色分隔线 */}
        <div className="header-goldline" />
      </div>

      {/* ===== 控制栏 ===== */}
      <div className="rednews-control-bar">
        <div className="ctrl-left">
          <span className="ctrl-label">红色印记</span>
        </div>
        <div className="ctrl-center">
          <div className="date-selector">
            <svg className="ctrl-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
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
              placeholder="搜索红色印记..."
              value={searchKeyword}
              onChange={e => setSearchKeyword(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* ===== 主体内容 ===== */}
      {(loading || reportLoading) && (
        <div className="rednews-loading">
          <Spin size="large" />
          <p>正在加载...</p>
        </div>
      )}

      {!loading && !reportLoading && filteredItems.length > 0 && (
        <div className="rednews-body">
          {/* 左：主推大卡片 */}
          <div className="rednews-main-area">
            {filteredItems.slice(0, 1).map((item, idx) => (
              <div key={idx} className="red-hero-card" onClick={() => handlePreview(item)}>
                <div className="red-hero-bar" />
                <div className="red-hero-body">
                  <div className="red-hero-badge">
                    <svg viewBox="0 0 24 24" fill="#ffd700" width="12" height="12">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                    </svg>
                    今日头条
                  </div>
                  <h2 className="red-hero-title">{item.title}</h2>
                  <p className="red-hero-excerpt">
                    {item.content.length > 300 ? item.content.substring(0, 300) + '…' : item.content}
                  </p>
                  <div className="red-hero-footer">
                    <div className="red-hero-source">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="12" height="12">
                        <path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/>
                      </svg>
                      {item.source || '党政要闻'}
                    </div>
                    <div className="red-hero-date">{formatDate(item.date)}</div>
                    <div className="red-hero-cta">阅读全文 →</div>
                  </div>
                </div>
              </div>
            ))}

            {/* 主推卡片下方更多 */}
            {filteredItems.length > 2 && (
              <div className="red-sub-cards">
                {filteredItems.slice(1, 3).map((item, idx) => (
                  <div key={idx} className="red-sub-card" onClick={() => handlePreview(item)}>
                    <div className="red-sub-bar" />
                    <div className="red-sub-body">
                      <div className="red-sub-source">{item.source || '党政要闻'}</div>
                      <h3 className="red-sub-title">{item.title}</h3>
                      <p className="red-sub-excerpt">
                        {item.content.length > 100 ? item.content.substring(0, 100) + '…' : item.content}
                      </p>
                      <span className="red-sub-date">{formatDate(item.date)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* 右：列表 */}
          <div className="rednews-side-area">
            <div className="side-header">
              <div className="side-header-bar" />
              <span className="side-header-title">更多要闻</span>
            </div>
            {filteredItems.slice(3).map((item, idx) => (
              <div key={idx} className="red-side-item" onClick={() => handlePreview(item)}>
                <div className="red-side-num">{String(idx + 4).padStart(2, '0')}</div>
                <div className="red-side-body">
                  <h4 className="red-side-title">{item.title}</h4>
                  <div className="red-side-meta">
                    <span>{item.source || '党政要闻'}</span>
                    <span>{formatDate(item.date)}</span>
                  </div>
                </div>
              </div>
            ))}

            {/* 底部红色数据强调 */}
            {filteredItems.length > 0 && (
              <div className="red-data-panel">
                <div className="red-data-header">
                  <svg viewBox="0 0 24 24" fill="none" stroke="#ffd700" strokeWidth="2" width="12" height="12">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                  </svg>
                  本期数据
                </div>
                <div className="red-big-numbers">
                  <div className="red-big-num-item">
                    <div className="red-big-num-val">{filteredItems.length}</div>
                    <div className="red-big-num-label">条要闻</div>
                  </div>
                  <div className="red-big-num-divider" />
                  <div className="red-big-num-item">
                    <div className="red-big-num-val">{filteredItems.filter(i => i.source?.includes('人民日报') || i.source?.includes('新华社')).length}</div>
                    <div className="red-big-num-label">权威来源</div>
                  </div>
                  <div className="red-big-num-divider" />
                  <div className="red-big-num-item">
                    <div className="red-big-num-val">100</div>
                    <div className="red-big-num-label">% 原创</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {!loading && !reportLoading && filteredItems.length === 0 && (
        <div className="rednews-empty">
          <Empty description={searchKeyword ? '没有找到相关内容' : '暂无红色印记'} />
        </div>
      )}

      {/* 详情弹窗 */}
      <Modal
        title={null}
        open={previewVisible}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={760}
        className="rednews-modal"
      >
        {selectedItem && (
          <div className="preview-wrap">
            <div className="preview-redbar" />
            <div className="preview-kicker">{selectedItem.source || '党政要闻'}</div>
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

export default RedNews;
