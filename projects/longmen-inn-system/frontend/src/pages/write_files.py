import os, sys

base = r'C:\Users\GS11DZ02279\.openclaw\workspace\.longmen_inn\projects\longmen-inn-system\frontend\src\pages'

# File 1: AINews.tsx
ainews_tsx = '''import React, { useState, useEffect, useMemo } from 'react';
import { DatePicker, Input, Spin, Empty, Modal } from 'antd';
import { api } from '$../services/api';
import dayjs, { Dayjs } from 'dayjs';
import './AINews.css';

interface CategoryInfo {
  id: number;
  name: string;
  description: string;
}

interface NewsItem {
  id: number;
  title: string;
  summary: string;
  source: string;
  publishDate: string;
  category: string;
  content: string;
  url?: string;
}

const AINews: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [reportLoading, setReportLoading] = useState<boolean>(false);
  const [categoryInfo, setCategoryInfo] = useState<CategoryInfo | null>(null);
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(dayjs().format('YYYY-MM-DD'));
  const [availableDates, setAvailableDates] = useState<Dayjs[]>([]);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [selectedItem, setSelectedItem] = useState<NewsItem | null>(null);
  const [previewVisible, setPreviewVisible] = useState<boolean>(false);

  const filteredItems = useMemo(() => {
    if (!searchKeyword.trim()) return newsItems;
    const kw = searchKeyword.toLowerCase();
    return newsItems.filter(
      (item) =>
        item.title.toLowerCase().includes(kw) ||
        item.summary.toLowerCase().includes(kw) ||
        item.source.toLowerCase().includes(kw)
    );
  }, [newsItems, searchKeyword]);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        setLoading(true);
        const res = await api.get('/intelligence/categories');
        const cats: CategoryInfo[] = res.data || [];
        const aiCat = cats.find((c: CategoryInfo) => c.name === 'AI资讯' || c.name === 'ai-news');
        if (aiCat) setCategoryInfo(aiCat);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    loadCategories();

    const dates: Dayjs[] = [];
    for (let i = 0; i < 30; i++) {
      dates.push(dayjs().subtract(i, 'day'));
    }
    setAvailableDates(dates);
  }, []);

  useEffect(() => {
    const loadReports = async (date: string) => {
      try {
        setReportLoading(true);
        const res = await api.get(`/intelligence/reports/ai-news?date=${date}`);
        const items: NewsItem[] = res.data || [];
        setNewsItems(items);
      } catch {
        setNewsItems([]);
      } finally {
        setReportLoading(false);
      }
    };
    loadReports(selectedDate);
  }, [selectedDate]);

  const handleDateChange = (_date: Dayjs | null, dateString: string) => {
    if (dateString) setSelectedDate(dateString);
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchKeyword(e.target.value);
  };

  const handleItemClick = (item: NewsItem) => {
    setSelectedItem(item);
    setPreviewVisible(true);
  };

  return (
    <div className="ainews-page">
      <div className="ainews-header">
        <div className="ainews-title-row">
          <h1 className="ainews-title">AI 资讯</h1>
          {categoryInfo && <span className="ainews-category-desc">{categoryInfo.description}</span>}
        </div>
        <div className="ainews-controls">
          <DatePicker
            className="ainews-date-picker"
            value={dayjs(selectedDate)}
            onChange={handleDateChange}
            format="YYYY年MM月DD日"
            allowClear={false}
          />
          <Input
            className="ainews-search"
            placeholder="搜索AI资讯..."
            prefix={<span className="ainews-search-icon">🔍</span>}
            value={searchKeyword}
            onChange={handleSearch}
            allowClear
          />
        </div>
      </div>

      <div className="ainews-content">
        {loading ? (
          <div className="ainews-loading">
            <Spin size="large" />
            <p className="ainews-loading-text">加载失败</p>
          </div>
        ) : reportLoading ? (
          <div className="ainews-loading">
            <Spin size="large" />
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="ainews-empty">
            {searchKeyword ? <Empty description="没有找到相关资讯" /> : <Empty description="暂无AI资讯" />}
          </div>
        ) : (
          <div className="ainews-grid">
            {filteredItems.map((item) => (
              <div key={item.id} className="ainews-card" onClick={() => handleItemClick(item)}>
                <div className="ainews-card-meta">
                  <span className="ainews-card-source">{item.source}</span>
                  <span className="ainews-card-date">{item.publishDate}</span>
                  <span className="ainews-card-category">{item.category}</span>
                </div>
                <h3 className="ainews-card-title">{item.title}</h3>
                <p className="ainews-card-summary">{item.summary}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal
        open={previewVisible}
        title={selectedItem?.title}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={720}
        className="ainews-modal"
      >
        {selectedItem && (
          <div className="ainews-modal-body">
            <div className="ainews-modal-meta">
              <span>{selectedItem.source}</span>
              <span>{selectedItem.publishDate}</span>
              <span>{selectedItem.category}</span>
            </div>
            <div className="ainews-modal-content">{selectedItem.content}</div>
            {selectedItem.url && (
              <a href={selectedItem.url} target="_blank" rel="noopener noreferrer" className="ainews-modal-link">
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
'''

with open(os.path.join(base, 'AINews.tsx'), 'w', encoding='utf-8') as f:
    f.write(ainews_tsx)
print('AINews.tsx written OK')

# File 2: AINews.css
ainews_css = '''/* AINews — 深色科技风格 (36氪风格) */
.ainews-page {
  min-height: 100vh;
  background: #060b14;
  color: #e8eaed;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  padding: 0 24px 48px;
}

.ainews-header {
  background: linear-gradient(180deg, #0d1525 0%, #060b14 100%);
  padding: 32px 0 24px;
  border-bottom: 1px solid #1a2744;
  margin-bottom: 32px;
}

.ainews-title-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 20px;
}

.ainews-title {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
  text-shadow: 0 0 20px rgba(66, 165, 245, 0.3);
  letter-spacing: 2px;
}

.ainews-category-desc {
  font-size: 14px;
  color: #78909c;
}

.ainews-controls {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.ainews-date-picker .ant-picker {
  background: #0d1f3c !important;
  border-color: #1e3a5f !important;
  color: #e8eaed !important;
}

.ainews-date-picker .ant-picker-input > input {
  color: #e8eaed !important;
}

.ainews-search {
  flex: 1;
  min-width: 240px;
  max-width: 400px;
  background: #0d1f3c !important;
  border-color: #1e3a5f !important;
  border-radius: 6px;
}

.ainews-search input {
  background: transparent !important;
  color: #e8eaed !important;
}

.ainews-search .ant-input-prefix {
  color: #78909c;
}

.ainews-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 16px;
}

.ainews-loading-text {
  color: #78909c;
  font-size: 14px;
  margin: 0;
}

.ainews-empty {
  padding: 80px 0;
  text-align: center;
}

.ainews-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.ainews-card {
  background: #0d1f3c;
  border: 1px solid #1e3a5f;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s, transform 0.15s;
}

.ainews-card:hover {
  border-color: #42a5f5;
  box-shadow: 0 4px 24px rgba(66, 165, 245, 0.15);
  transform: translateY(-2px);
}

.ainews-card-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.ainews-card-source {
  font-size: 12px;
  color: #42a5f5;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.ainews-card-date {
  font-size: 12px;
  color: #78909c;
}

.ainews-card-category {
  font-size: 11px;
  color: #78909c;
  background: #1a2744;
  padding: 2px 8px;
  border-radius: 10px;
}

.ainews-card-title {
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
  margin: 0 0 10px;
  line-height: 1.4;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
}

.ainews-card-summary {
  font-size: 13px;
  color: #b0bec5;
  margin: 0;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.ainews-modal-body {
  font-family: system-ui, -apple-system, sans-serif;
}

.ainews-modal-meta {
  display: flex;
  gap: 16px;
  color: #78909c;
  font-size: 13px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #1e3a5f;
}

.ainews-modal-content {
  color: #e8eaed;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.ainews-modal-link {
  display: inline-block;
  margin-top: 16px;
  color: #42a5f5;
  font-size: 14px;
}
'''

with open(os.path.join(base, 'AINews.css'), 'w', encoding='utf-8') as f:
    f.write(ainews_css)
print('AINews.css written OK')

# File 3: NewsPage.tsx
newspage_tsx = '''import React, { useState, useEffect, useMemo } from 'react';
import { DatePicker, Input, Spin, Empty, Modal } from 'antd';
import { api } from '$../services/api';
import dayjs, { Dayjs } from 'dayjs';
import './NewsPage.css';

interface CategoryInfo {
  id: number;
  name: string;
  description: string;
}

interface NewsItem {
  id: number;
  title: string;
  summary: string;
  source: string;
  publishDate: string;
  category: string;
  content: string;
  url?: string;
}

const NewsPage: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [reportLoading, setReportLoading] = useState<boolean>(false);
  const [categoryInfo, setCategoryInfo] = useState<CategoryInfo | null>(null);
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(dayjs().format('YYYY-MM-DD'));
  const [availableDates, setAvailableDates] = useState<Dayjs[]>([]);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [selectedItem, setSelectedItem] = useState<NewsItem | null>(null);
  const [previewVisible, setPreviewVisible] = useState<boolean>(false);

  const filteredItems = useMemo(() => {
    if (!searchKeyword.trim()) return newsItems;
    const kw = searchKeyword.toLowerCase();
    return newsItems.filter(
      (item) =>
        item.title.toLowerCase().includes(kw) ||
        item.summary.toLowerCase().includes(kw) ||
        item.source.toLowerCase().includes(kw)
    );
  }, [newsItems, searchKeyword]);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        setLoading(true);
        const res = await api.get('/intelligence/categories');
        const cats: CategoryInfo[] = res.data || [];
        const newsCat = cats.find((c: CategoryInfo) => c.name === '时事要闻' || c.name === 'news');
        if (newsCat) setCategoryInfo(newsCat);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    loadCategories();

    const dates: Dayjs[] = [];
    for (let i = 0; i < 30; i++) {
      dates.push(dayjs().subtract(i, 'day'));
    }
    setAvailableDates(dates);
  }, []);

  useEffect(() => {
    const loadReports = async (date: string) => {
      try {
        setReportLoading(true);
        const res = await api.get(`/intelligence/reports/news?date=${date}`);
        const items: NewsItem[] = res.data || [];
        setNewsItems(items);
      } catch {
        setNewsItems([]);
      } finally {
        setReportLoading(false);
      }
    };
    loadReports(selectedDate);
  }, [selectedDate]);

  const handleDateChange = (_date: Dayjs | null, dateString: string) => {
    if (dateString) setSelectedDate(dateString);
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchKeyword(e.target.value);
  };

  const handleItemClick = (item: NewsItem) => {
    setSelectedItem(item);
    setPreviewVisible(true);
  };

  return (
    <div className="newspage">
      <div className="newspage-header">
        <div className="newspage-title-row">
          <h1 className="newspage-title">时事要闻</h1>
          {categoryInfo && <span className="newspage-category-desc">{categoryInfo.description}</span>}
        </div>
        <div className="newspage-controls">
          <DatePicker
            className="newspage-date-picker"
            value={dayjs(selectedDate)}
            onChange={handleDateChange}
            format="YYYY年MM月DD日"
            allowClear={false}
          />
          <Input
            className="newspage-search"
            placeholder="搜索要闻..."
            prefix={<span className="newspage-search-icon">🔍</span>}
            value={searchKeyword}
            onChange={handleSearch}
            allowClear
          />
        </div>
      </div>

      <div className="newspage-content">
        {loading ? (
          <div className="newspage-loading">
            <Spin size="large" />
            <p className="newspage-loading-text">加载失败</p>
          </div>
        ) : reportLoading ? (
          <div className="newspage-loading">
            <Spin size="large" />
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="newspage-empty">
            {searchKeyword ? <Empty description="没有找到相关要闻" /> : <Empty description="暂无时事要闻" />}
          </div>
        ) : (
          <div className="newspage-list">
            {filteredItems.map((item) => (
              <div key={item.id} className="newspage-item" onClick={() => handleItemClick(item)}>
                <div className="newspage-item-meta">
                  <span className="newspage-item-source">{item.source}</span>
                  <span className="newspage-item-date">{item.publishDate}</span>
                  <span className="newspage-item-category">{item.category}</span>
                </div>
                <h3 className="newspage-item-title">{item.title}</h3>
                <p className="newspage-item-summary">{item.summary}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal
        open={previewVisible}
        title={selectedItem?.title}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={800}
        className="newspage-modal"
      >
        {selectedItem && (
          <div className="newspage-modal-body">
            <div className="newspage-modal-meta">
              <span>{selectedItem.source}</span>
              <span>{selectedItem.publishDate}</span>
              <span>{selectedItem.category}</span>
            </div>
            <div className="newspage-modal-content">{selectedItem.content}</div>
            {selectedItem.url && (
              <a href={selectedItem.url} target="_blank" rel="noopener noreferrer" className="newspage-modal-link">
                阅读原文
              </a>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default NewsPage;
'''

with open(os.path.join(base, 'NewsPage.tsx'), 'w', encoding='utf-8') as f:
    f.write(newspage_tsx)
print('NewsPage.tsx written OK')

# File 4: NewsPage.css
newspage_css = '''/* NewsPage — 纽约时报/经典日报风格 (米白纸张色) */
.newspage {
  min-height: 100vh;
  background: #f5f1eb;
  color: #1a1a1a;
  font-family: Georgia, 'Times New Roman', Times, serif;
  padding: 0 24px 64px;
}

.newspage-header {
  background: #f5f1eb;
  padding: 40px 0 28px;
  border-bottom: 2px solid #c8bfb0;
  margin-bottom: 40px;
}

.newspage-title-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 20px;
}

.newspage-title {
  font-family: Georgia, 'Times New Roman', Times, serif;
  font-size: 36px;
  font-weight: 400;
  color: #1a1a1a;
  margin: 0;
  letter-spacing: 1px;
}

.newspage-category-desc {
  font-size: 14px;
  color: #555;
  font-family: system-ui, -apple-system, sans-serif;
}

.newspage-controls {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.newspage-date-picker .ant-picker {
  background: #ffffff !important;
  border-color: #c8bfb0 !important;
  border-radius: 3px;
}

.newspage-search {
  flex: 1;
  min-width: 240px;
  max-width: 400px;
  background: #ffffff !important;
  border-color: #c8bfb0 !important;
  border-radius: 3px;
  font-family: system-ui, -apple-system, sans-serif;
}

.newspage-search input {
  background: transparent !important;
  color: #1a1a1a !important;
  font-family: system-ui, -apple-system, sans-serif !important;
}

.newspage-search .ant-input-prefix {
  color: #888;
}

.newspage-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 16px;
}

.newspage-loading-text {
  color: #555;
  font-size: 14px;
  margin: 0;
  font-family: system-ui, -apple-system, sans-serif;
}

.newspage-empty {
  padding: 80px 0;
  text-align: center;
}

.newspage-list {
  max-width: 780px;
  margin: 0 auto;
}

.newspage-item {
  border-bottom: 1px solid #ddd8cc;
  padding: 28px 0;
  cursor: pointer;
  transition: background 0.15s;
}

.newspage-item:first-child {
  border-top: 1px solid #ddd8cc;
}

.newspage-item:hover {
  background: rgba(0, 0, 0, 0.025);
}

.newspage-item-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.newspage-item-source {
  font-size: 13px;
  color: #c41230;
  font-weight: bold;
  font-family: system-ui, -apple-system, sans-serif;
  letter-spacing: 0.5px;
}

.newspage-item-date {
  font-size: 13px;
  color: #888;
  font-family: system-ui, -apple-system, sans-serif;
}

.newspage-item-category {
  font-size: 12px;
  color: #888;
  font-family: system-ui, -apple-system, sans-serif;
}

.newspage-item-title {
  font-family: Georgia, 'Times New Roman', Times, serif;
  font-size: 22px;
  font-weight: 400;
  color: #1a1a1a;
  margin: 0 0 10px;
  line-height: 1.35;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

.newspage-item-summary {
  font-family: Georgia, 'Times New Roman', Times, serif;
  font-size: 15px;
  color: #444;
  margin: 0;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.newspage-modal-body {
  font-family: Georgia, 'Times New Roman', Times, serif;
}

.newspage-modal-meta {
  display: flex;
  gap: 16px;
  color: #888;
  font-size: 13px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ddd8cc;
  font-family: system-ui, -apple-system, sans-serif;
}

.newspage-modal-content {
  color: #1a1a1a;
  font-size: 16px;
  line-height: 1.85;
  white-space: pre-wrap;
}

.newspage-modal-link {
  display: inline-block;
  margin-top: 16px;
  color: #c41230;
  font-size: 14px;
  font-family: system-ui, -apple-system, sans-serif;
}
'''

with open(os.path.join(base, 'NewsPage.css'), 'w', encoding='utf-8') as f:
    f.write(newspage_css)
print('NewsPage.css written OK')

# File 5: RedNews.tsx
rednews_tsx = '''import React, { useState, useEffect, useMemo } from 'react';
import { DatePicker, Input, Spin, Empty, Modal } from 'antd';
import { api } from '$../services/api';
import dayjs, { Dayjs } from 'dayjs';
import './RedNews.css';

interface CategoryInfo {
  id: number;
  name: string;
  description: string;
}

interface NewsItem {
  id: number;
  title: string;
  summary: string;
  source: string;
  publishDate: string;
  category: string;
  content: string;
  url?: string;
}

const RedNews: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [reportLoading, setReportLoading] = useState<boolean>(false);
  const [categoryInfo, setCategoryInfo] = useState<CategoryInfo | null>(null);
  const [newsItems, setNewsItems] = useState<NewsItem[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>(dayjs().format('YYYY-MM-DD'));
  const [availableDates, setAvailableDates] = useState<Dayjs[]>([]);
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  const [selectedItem, setSelectedItem] = useState<NewsItem | null>(null);
  const [previewVisible, setPreviewVisible] = useState<boolean>(false);

  const filteredItems = useMemo(() => {
    if (!searchKeyword.trim()) return newsItems;
    const kw = searchKeyword.toLowerCase();
    return newsItems.filter(
      (item) =>
        item.title.toLowerCase().includes(kw) ||
        item.summary.toLowerCase().includes(kw) ||
        item.source.toLowerCase().includes(kw)
    );
  }, [newsItems, searchKeyword]);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        setLoading(true);
        const res = await api.get('/intelligence/categories');
        const cats: CategoryInfo[] = res.data || [];
        const redCat = cats.find((c: CategoryInfo) => c.name === '红色印记' || c.name === 'red-news');
        if (redCat) setCategoryInfo(redCat);
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    loadCategories();

    const dates: Dayjs[] = [];
    for (let i = 0; i < 30; i++) {
      dates.push(dayjs().subtract(i, 'day'));
    }
    setAvailableDates(dates);
  }, []);

  useEffect(() => {
    const loadReports = async (date: string) => {
      try {
        setReportLoading(true);
        const res = await api.get(`/intelligence/reports/red-news?date=${date}`);
        const items: NewsItem[] = res.data || [];
        setNewsItems(items);
      } catch {
        setNewsItems([]);
      } finally {
        setReportLoading(false);
      }
    };
    loadReports(selectedDate);
  }, [selectedDate]);

  const handleDateChange = (_date: Dayjs | null, dateString: string) => {
    if (dateString) setSelectedDate(dateString);
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchKeyword(e.target.value);
  };

  const handleItemClick = (item: NewsItem) => {
    setSelectedItem(item);
    setPreviewVisible(true);
  };

  return (
    <div className="rednews-page">
      <div className="rednews-header">
        <div className="rednews-title-row">
          <h1 className="rednews-title">红色印记</h1>
          {categoryInfo && <span className="rednews-category-desc">{categoryInfo.description}</span>}
        </div>
        <div className="rednews-controls">
          <DatePicker
            className="rednews-date-picker"
            value={dayjs(selectedDate)}
            onChange={handleDateChange}
            format="YYYY年MM月DD日"
            allowClear={false}
          />
          <Input
            className="rednews-search"
            placeholder="搜索红色印记..."
            prefix={<span className="rednews-search-icon">🔍</span>}
            value={searchKeyword}
            onChange={handleSearch}
            allowClear
          />
        </div>
      </div>

      <div className="rednews-content">
        {loading ? (
          <div className="rednews-loading">
            <Spin size="large" />
            <p className="rednews-loading-text">加载失败</p>
          </div>
        ) : reportLoading ? (
          <div className="rednews-loading">
            <Spin size="large" />
          </div>
        ) : filteredItems.length === 0 ? (
          <div className="rednews-empty">
            {searchKeyword ? <Empty description="没有找到相关内容" /> : <Empty description="暂无红色印记" />}
          </div>
        ) : (
          <div className="rednews-list">
            {filteredItems.map((item) => (
              <div key={item.id} className="rednews-item" onClick={() => handleItemClick(item)}>
                <div className="rednews-item-meta">
                  <span className="rednews-item-source">{item.source}</span>
                  <span className="rednews-item-date">{item.publishDate}</span>
                  <span className="rednews-item-category">{item.category}</span>
                </div>
                <h3 className="rednews-item-title">{item.title}</h3>
                <p className="rednews-item-summary">{item.summary}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <Modal
        open={previewVisible}
        title={selectedItem?.title}
        onCancel={() => setPreviewVisible(false)}
        footer={null}
        width={720}
        className="rednews-modal"
      >
        {selectedItem && (
          <div className="rednews-modal-body">
            <div className="rednews-modal-meta">
              <span>{selectedItem.source}</span>
              <span>{selectedItem.publishDate}</span>
              <span>{selectedItem.category}</span>
            </div>
            <div className="rednews-modal-content">{selectedItem.content}</div>
            {selectedItem.url && (
              <a href={selectedItem.url} target="_blank" rel="noopener noreferrer" className="rednews-modal-link">
                阅读原文
              </a>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default RedNews;
'''

with open(os.path.join(base, 'RedNews.tsx'), 'w', encoding='utf-8') as f:
    f.write(rednews_tsx)
print('RedNews.tsx written OK')

# File 6: RedNews.css
rednews_css = '''/* RedNews — 红色主调风格 */
.rednews-page {
  min-height: 100vh;
  background: #fafafa;
  color: #1a1a1a;
  font-family: system-ui, -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  padding: 0 24px 64px;
}

.rednews-header {
  background: linear-gradient(180deg, #fff5f5 0%, #fafafa 100%);
  border-bottom: 2px solid #c41230;
  padding: 32px 0 24px;
  margin-bottom: 32px;
}

.rednews-title-row {
  display: flex;
  align-items: baseline;
  gap: 16px;
  margin-bottom: 20px;
}

.rednews-title {
  font-size: 28px;
  font-weight: 700;
  color: #c41230;
  margin: 0;
  letter-spacing: 3px;
  text-shadow: 0 1px 6px rgba(196, 18, 48, 0.2);
}

.rednews-category-desc {
  font-size: 14px;
  color: #666;
}

.rednews-controls {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.rednews-date-picker .ant-picker {
  background: #ffffff !important;
  border-color: #e8b4b4 !important;
  border-radius: 4px;
}

.rednews-search {
  flex: 1;
  min-width: 240px;
  max-width: 400px;
  background: #ffffff !important;
  border-color: #e8b4b4 !important;
  border-radius: 4px;
}

.rednews-search input {
  background: transparent !important;
  color: #1a1a1a !important;
}

.rednews-search .ant-input-prefix {
  color: #c41230;
}

.rednews-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 16px;
}

.rednews-loading-text {
  color: #888;
  font-size: 14px;
  margin: 0;
}

.rednews-empty {
  padding: 80px 0;
  text-align: center;
}

.rednews-list {
  max-width: 800px;
  margin: 0 auto;
}

.rednews-item {
  background: #ffffff;
  border: 1px solid #f0e0e0;
  border-left: 4px solid #c41230;
  border-radius: 4px;
  padding: 20px 24px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s, border-color 0.2s;
}

.rednews-item:hover {
  box-shadow: 0 4px 20px rgba(196, 18, 48, 0.12);
  transform: translateY(-1px);
  border-left-color: #8b0000;
}

.rednews-item-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.rednews-item-source {
  font-size: 12px;
  color: #c41230;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.rednews-item-date {
  font-size: 12px;
  color: #888;
}

.rednews-item-category {
  font-size: 11px;
  color: #888;
  background: #fff0f0;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #f0d0d0;
}

.rednews-item-title {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 10px;
  line-height: 1.4;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.rednews-item-summary {
  font-size: 14px;
  color: #555;
  margin: 0;
  line-height: 1.65;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.rednews-modal-body {
  font-family: system-ui, -apple-system, sans-serif;
}

.rednews-modal-meta {
  display: flex;
  gap: 16px;
  color: #888;
  font-size: 13px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0e0e0;
}

.rednews-modal-content {
  color: #1a1a1a;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
}

.rednews-modal-link {
  display: inline-block;
  margin-top: 16px;
  color: #c41230;
  font-size: 14px;
}
'''

with open(os.path.join(base, 'RedNews.css'), 'w', encoding='utf-8') as f:
    f.write(rednews_css)
print('RedNews.css written OK')

print('All 6 files written!')
print('')
print('=== Verification ===')
# Verify Chinese
files = ['AINews.tsx', 'AINews.css', 'NewsPage.tsx', 'NewsPage.css', 'RedNews.tsx', 'RedNews.css']
keywords = ['加载失败', '暂无AI资讯', '没有找到相关资讯', '搜索AI资讯', '暂无时事要闻', '没有找到相关要闻', '搜索要闻', '暂无红色印记', '没有找到相关内容', '搜索红色印记']
for fname in files:
    fpath = os.path.join(base, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    print(f'{fname}: {len(content)} chars')
    for kw in keywords:
        if kw in content:
            print(f'  ✓ Found: {kw}')
