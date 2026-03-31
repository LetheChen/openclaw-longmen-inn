"""
龙门客栈业务管理系统 - 客栈情报 API (三类独立版)
================================================
作者: 画师

提供三类情报的读取和展示功能:
- AI资讯 (ai-news): 36氪/科技新媒体风格
- 时事要闻 (news): 纽约时报/经典日报风格
- 红色印记 (red-news): 人民日报/党政风风格
"""

import re
import os
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()

# ===========================================
# 三类情报的分类配置
# ===========================================
REPORT_CATEGORIES = {
    "ai-news": {
        "key": "ai-news",
        "name": "AI资讯",
        "subdir": "ai-news",
        "description": "科技新媒体，36氪风格",
        "emoji": "🤖",
        "icon": "robot",
        "config_key": "ai_news_enabled",
    },
    "news": {
        "key": "news",
        "name": "时事要闻",
        "subdir": "news",
        "description": "经典日报，纽约时报风格",
        "emoji": "📰",
        "icon": "file-text",
        "config_key": "news_enabled",
    },
    "red-news": {
        "key": "red-news",
        "name": "红色印记",
        "subdir": "red-news",
        "description": "党政风格，人民日报风格",
        "emoji": "🔴",
        "icon": "flag",
        "config_key": "red_news_enabled",
    },
}

# 配置文件路径（与 openclaw.py 保持一致）
OPENCLAW_CONFIG_FILE = settings.LONGMEN_INN_ROOT / "openclaw_config.json"


def _load_openclaw_config() -> dict:
    """从JSON文件加载OpenClaw配置"""
    if OPENCLAW_CONFIG_FILE.exists():
        try:
            with open(OPENCLAW_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def is_category_enabled(category: str) -> bool:
    """检查指定分类是否启用（F09 情报开关）"""
    if category not in REPORT_CATEGORIES:
        return True  # 未知分类默认启用
    config_key = REPORT_CATEGORIES[category]["config_key"]
    saved = _load_openclaw_config()
    return saved.get(config_key, True)  # 默认启用


# 获取客栈情报根目录
def get_reports_root() -> Path:
    """获取日报存储根目录"""
    reports_path = os.environ.get("AI_DAILY_REPORTS_PATH", "")
    if reports_path:
        return Path(reports_path)
    return settings.LONGMEN_INN_ROOT / "ai-daily-reports"


def get_category_path(category: str) -> Path:
    """获取指定分类的存储目录"""
    root = get_reports_root()
    if category not in REPORT_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"未知分类: {category}")
    return root / REPORT_CATEGORIES[category]["subdir"]


# ===========================================
# Pydantic Models
# ===========================================
class NewsItem(BaseModel):
    """单条新闻"""
    date: str
    title: str
    content: str
    source: Optional[str] = None
    source_url: Optional[str] = None
    category: str = ""


class ReportFile(BaseModel):
    """日报文件信息"""
    date: str
    filename: str
    path: str
    exists: bool


class CategoryInfo(BaseModel):
    """分类信息"""
    key: str
    name: str
    description: str
    emoji: str
    icon: str
    available_dates: List[str] = []


class CategoryReportResponse(BaseModel):
    """分类日报响应"""
    success: bool
    category: str
    category_name: str
    date: str
    title: str
    items: List[NewsItem]
    total: int


class CategoryListResponse(BaseModel):
    """分类列表响应"""
    success: bool
    categories: List[CategoryInfo]


class ReportListResponse(BaseModel):
    """日报列表响应"""
    success: bool
    reports: List[ReportFile]
    available_dates: List[str]


class SearchResult(BaseModel):
    """搜索结果"""
    success: bool
    keyword: str
    results: List[Dict[str, Any]]
    total: int


# ===========================================
# 解析器：通用Markdown解析
# ===========================================
def parse_markdown_news(content: str, date_str: str, category: str) -> List[NewsItem]:
    """
    解析Markdown格式的新闻内容
    支持格式:
    - # 标题
    - ## 子标题
    - **标题**
    - [标题](url)
    - - 列表项
    - > 引用
    """
    items = []
    
    # 尝试按 ## 分割（每条新闻）
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
    
    for section in sections[1:]:  # 跳过第一个空部分
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        # 提取标题（第一行）
        title_line = lines[0].strip()
        # 去除 ** 或 ## 或 [] 标记
        title = re.sub(r'^[*#\[\]]+|[*#\[\]]+$', '', title_line).strip()
        
        # 提取URL
        url_match = re.search(r'\[([^\]]+)\]\((https?://[^\)]+)\)', title_line)
        source_url = url_match.group(2) if url_match else None
        
        # 提取来源（如果有）
        source_match = re.search(r'来源[：:]\s*([^\n]+)', section)
        source = source_match.group(1).strip() if source_match else None
        
        # 提取正文（去掉标题行）
        body_lines = []
        in_code_block = False
        for line in lines[1:]:
            # 跳过代码块
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            # 跳过URL行
            if re.match(r'^https?://', line.strip()):
                continue
            # 跳过元信息行
            if re.match(r'^(来源|发布|日期|标签)[:：]', line.strip()):
                continue
            body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        # 清理多余空行
        body = re.sub(r'\n{3,}', '\n\n', body)
        
        if title:
            items.append(NewsItem(
                date=date_str,
                title=title,
                content=body,
                source=source,
                source_url=source_url,
                category=category
            ))
    
    return items


def parse_newspaper_news(content: str, date_str: str, category: str) -> List[NewsItem]:
    """
    解析报纸风格的新闻内容
    支持格式:
    - ## 区域标题
    - ### 新闻标题
    - 正文内容
    """
    items = []
    
    # 按 ## 分割
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
    
    for section in sections[1:]:
        lines = section.strip().split('\n')
        if not lines:
            continue
        
        title_line = lines[0].strip()
        title = re.sub(r'^[*#\[\]]+|[*#\[\]]+$', '', title_line).strip()
        
        # 提取URL
        url_match = re.search(r'\[([^\]]+)\]\((https?://[^\)]+)\)', title_line)
        source_url = url_match.group(2) if url_match else None
        
        # 提取来源
        source_match = re.search(r'来源[：:]\s*([^\n]+)', section)
        source = source_match.group(1).strip() if source_match else None
        
        # 提取正文
        body_lines = []
        for line in lines[1:]:
            if re.match(r'^https?://', line.strip()):
                continue
            if re.match(r'^(来源|发布|日期|标签)[:：]', line.strip()):
                continue
            body_lines.append(line)
        
        body = '\n'.join(body_lines).strip()
        body = re.sub(r'\n{3,}', '\n\n', body)
        
        if title:
            items.append(NewsItem(
                date=date_str,
                title=title,
                content=body,
                source=source,
                source_url=source_url,
                category=category
            ))
    
    return items


def get_report_content(category: str, date_str: str) -> Optional[str]:
    """根据分类和日期获取报告内容"""
    category_path = get_category_path(category)
    filepath = category_path / f"{date_str}.md"
    
    if filepath.exists():
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            return None
    return None


def list_available_dates(category: str) -> List[str]:
    """列出指定分类的所有可用日期"""
    try:
        category_path = get_category_path(category)
        if not category_path.exists():
            return []
        
        dates = []
        for filepath in sorted(category_path.glob("*.md"), reverse=True):
            # 从文件名提取日期: YYYY-MM-DD.md
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', filepath.name)
            if date_match:
                dates.append(date_match.group(1))
        return dates
    except Exception:
        return []


# ===========================================
# API Endpoints
# ===========================================
@router.get("/categories", response_model=CategoryListResponse)
async def get_all_categories():
    """
    获取所有情报分类及其可用日期
    
    根据配置开关返回分类启用状态（F09）
    """
    categories = []
    for key, info in REPORT_CATEGORIES.items():
        available_dates = list_available_dates(key)
        enabled = is_category_enabled(key)
        categories.append(CategoryInfo(
            key=key,
            name=info["name"],
            description=info["description"],
            emoji=info["emoji"],
            icon=info["icon"],
            available_dates=available_dates if enabled else []
        ))
    
    return CategoryListResponse(success=True, categories=categories)


@router.get("/reports/{category}", response_model=CategoryReportResponse)
async def get_category_report(
    category: str,
    date: Optional[str] = Query(None, description="日期，格式 YYYY-MM-DD，默认今天")
):
    """
    获取指定分类的日报内容
    
    - category: 分类标识 (ai-news / news / red-news)
    - date: 可选，日期格式 YYYY-MM-DD，默认今天
    """
    if category not in REPORT_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"未知分类: {category}")
    
    # F09 情报开关检查
    if not is_category_enabled(category):
        return CategoryReportResponse(
            success=True,
            category=category,
            category_name=REPORT_CATEGORIES[category]["name"],
            date=datetime.now().strftime("%Y-%m-%d"),
            title=f"{REPORT_CATEGORIES[category]['name']} - 已关闭",
            items=[],
            total=0
        )
    
    # 默认日期
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # 验证日期格式
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD 格式")
    
    content = get_report_content(category, date)
    
    if not content:
        # 尝试找最近一个有内容的日期
        available = list_available_dates(category)
        if available:
            content = get_report_content(category, available[0])
            date = available[0]
    
    if not content:
        return CategoryReportResponse(
            success=True,
            category=category,
            category_name=REPORT_CATEGORIES[category]["name"],
            date=date,
            title=f"{REPORT_CATEGORIES[category]['name']} - {date}",
            items=[],
            total=0
        )
    
    # 提取标题（第一行）
    title_match = re.search(r'^#\s+(.+?)$', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else f"{REPORT_CATEGORIES[category]['name']} {date}"
    
    # 解析内容
    items = parse_markdown_news(content, date, category)
    
    return CategoryReportResponse(
        success=True,
        category=category,
        category_name=REPORT_CATEGORIES[category]["name"],
        date=date,
        title=title,
        items=items,
        total=len(items)
    )


@router.get("/reports/{category}/list", response_model=ReportListResponse)
async def list_category_reports(category: str):
    """
    列出指定分类的所有可用日报
    """
    if category not in REPORT_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"未知分类: {category}")
    
    # F09 情报开关检查
    if not is_category_enabled(category):
        return ReportListResponse(success=True, reports=[], available_dates=[])
    
    category_path = get_category_path(category)
    
    if not category_path.exists():
        return ReportListResponse(success=True, reports=[], available_dates=[])
    
    reports = []
    available_dates = []
    
    for filepath in sorted(category_path.glob("*.md"), reverse=True):
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', filepath.name)
        if date_match:
            date_str = date_match.group(1)
            available_dates.append(date_str)
            reports.append(ReportFile(
                date=date_str,
                filename=filepath.name,
                path=str(filepath),
                exists=True
            ))
    
    return ReportListResponse(
        success=True,
        reports=reports,
        available_dates=available_dates
    )


@router.get("/reports/{category}/search", response_model=SearchResult)
async def search_category_reports(
    category: str,
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    搜索指定分类中的关键词
    """
    if category not in REPORT_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"未知分类: {category}")
    
    # F09 情报开关检查
    if not is_category_enabled(category):
        return SearchResult(success=True, keyword=keyword, results=[], total=0)
    
    category_path = get_category_path(category)
    
    if not category_path.exists():
        return SearchResult(success=True, keyword=keyword, results=[], total=0)
    
    all_items = []
    
    # 遍历该分类所有文件
    for filepath in sorted(category_path.glob("*.md"), reverse=True):
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', filepath.name)
        if not date_match:
            continue
        date_str = date_match.group(1)
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception:
            continue
        
        # 关键词匹配
        if keyword.lower() not in content.lower():
            continue
        
        items = parse_markdown_news(content, date_str, category)
        
        for item in items:
            if keyword.lower() in item.title.lower() or keyword.lower() in item.content.lower():
                # 高亮摘要
                if keyword.lower() in item.content.lower():
                    idx = item.content.lower().find(keyword.lower())
                    start = max(0, idx - 40)
                    end = min(len(item.content), idx + len(keyword) + 60)
                    snippet = ("..." if start > 0 else "") + item.content[start:end] + ("..." if end < len(item.content) else "")
                else:
                    snippet = item.content[:100] + ("..." if len(item.content) > 100 else "")
                
                all_items.append({
                    **item.model_dump(),
                    "snippet": snippet,
                    "highlight": keyword
                })
    
    # 限制数量
    all_items = all_items[:limit]
    
    return SearchResult(
        success=True,
        keyword=keyword,
        results=all_items,
        total=len(all_items)
    )


@router.get("/search")
async def search_all_reports(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    category: Optional[str] = Query(None, description="分类筛选"),
    limit: int = Query(30, ge=1, le=100, description="返回数量限制")
):
    """
    跨分类搜索所有日报
    
    F09：未启用的分类不参与搜索
    """
    if category and category not in REPORT_CATEGORIES:
        raise HTTPException(status_code=400, detail=f"未知分类: {category}")
    
    # 确定搜索范围
    search_categories = [category] if category else list(REPORT_CATEGORIES.keys())
    
    all_items = []
    
    for cat_key in search_categories:
        # F09 情报开关检查：跳过未启用的分类
        if not is_category_enabled(cat_key):
            continue
        
        category_path = get_category_path(cat_key)
        
        if not category_path.exists():
            continue
        
        for filepath in sorted(category_path.glob("*.md"), reverse=True):
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})\.md', filepath.name)
            if not date_match:
                continue
            date_str = date_match.group(1)
            
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception:
                continue
            
            if keyword.lower() not in content.lower():
                continue
            
            items = parse_markdown_news(content, date_str, cat_key)
            
            for item in items:
                if keyword.lower() in item.title.lower() or keyword.lower() in item.content.lower():
                    if keyword.lower() in item.content.lower():
                        idx = item.content.lower().find(keyword.lower())
                        start = max(0, idx - 40)
                        end = min(len(item.content), idx + len(keyword) + 60)
                        snippet = ("..." if start > 0 else "") + item.content[start:end] + ("..." if end < len(item.content) else "")
                    else:
                        snippet = item.content[:100] + ("..." if len(item.content) > 100 else "")
                    
                    all_items.append({
                        **item.model_dump(),
                        "category_name": REPORT_CATEGORIES[cat_key]["name"],
                        "category_emoji": REPORT_CATEGORIES[cat_key]["emoji"],
                        "snippet": snippet,
                        "highlight": keyword
                    })
    
    all_items = all_items[:limit]
    
    return {
        "success": True,
        "keyword": keyword,
        "category": category or "all",
        "results": all_items,
        "total": len(all_items)
    }
