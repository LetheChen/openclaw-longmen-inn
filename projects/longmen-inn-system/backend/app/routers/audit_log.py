"""
龙门客栈业务管理系统 - 审计日志 API 路由
========================================
作者: 厨子 (神厨小福贵)

提供审计日志读取接口，支持版本动态Feed展示
"""

import os
import json
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.schemas.audit_log import (
    AuditLogEntry,
    AuditLogResponse,
    AuditFeedResponse,
)

router = APIRouter(prefix="/audit-logs", tags=["Audit Log"])

# 审计日志文件路径
AUDIT_LOG_PATH = os.path.expanduser(
    "~/.openclaw/workspace/.longmen_inn/audit_log.jsonl"
)


def read_audit_logs() -> List[dict]:
    """读取审计日志文件所有条目"""
    if not os.path.exists(AUDIT_LOG_PATH):
        return []
    
    entries = []
    try:
        with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except Exception:
        return []
    
    # 按时间倒序
    entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return entries


def compute_statistics(entries: List[dict]) -> dict:
    """计算审计日志统计信息"""
    if not entries:
        return {
            "total_entries": 0,
            "total_lines_added": 0,
            "total_lines_deleted": 0,
            "total_files_changed": 0,
            "status_counts": {},
            "type_counts": {},
            "issues_count": 0,
            "recent_activity": None,
        }
    
    total_lines_added = 0
    total_lines_deleted = 0
    all_files = set()
    status_counts = {}
    type_counts = {}
    issues_count = 0
    
    for entry in entries:
        total_lines_added += entry.get("lines_added", 0) or 0
        total_lines_deleted += entry.get("lines_deleted", 0) or 0
        
        files = entry.get("files_changed", []) or []
        all_files.update(files)
        
        status = entry.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
        
        entry_type = entry.get("type", "unknown")
        type_counts[entry_type] = type_counts.get(entry_type, 0) + 1
        
        issues = entry.get("issues", []) or []
        issues_count += len(issues)
    
    return {
        "total_entries": len(entries),
        "total_lines_added": total_lines_added,
        "total_lines_deleted": total_lines_deleted,
        "total_files_changed": len(all_files),
        "status_counts": status_counts,
        "type_counts": type_counts,
        "issues_count": issues_count,
        "recent_activity": entries[0].get("timestamp") if entries else None,
    }


def build_feed_item(entry: dict) -> dict:
    """将审计日志条目转换为版本动态Feed格式"""
    timestamp = entry.get("timestamp", "")
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        date_str = dt.strftime("%m月%d日 %H:%M")
    except Exception:
        date_str = timestamp
    
    summary = entry.get("summary", "无描述")
    status = entry.get("status", "passed")
    lines_added = entry.get("lines_added", 0) or 0
    lines_deleted = entry.get("lines_deleted", 0) or 0
    files_changed = entry.get("files_changed", []) or []
    issues = entry.get("issues", []) or []
    tasks_found = entry.get("tasks_found", []) or []
    
    # 构建动态描述
    status_emoji = "✅" if status == "passed" else "⚠️"
    lines_info = ""
    if lines_added > 0 or lines_deleted > 0:
        lines_info = f" (+{lines_added} -{lines_deleted})"
    
    files_info = ""
    if files_changed:
        files_info = f" · {len(files_changed)} 个文件变更"
    
    return {
        "id": timestamp,
        "timestamp": timestamp,
        "date_str": date_str,
        "title": summary,
        "status": status,
        "status_emoji": status_emoji,
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "lines_info": lines_info,
        "files_count": len(files_changed),
        "files_info": files_info,
        "issues": issues,
        "issues_count": len(issues),
        "tasks_found": tasks_found,
        "type": entry.get("type", "git_audit"),
    }


@router.get("", response_model=AuditLogResponse)
async def get_audit_logs(
    skip: int = Query(default=0, ge=0, description="跳过条目数（分页）"),
    limit: int = Query(default=20, ge=1, le=100, description="返回条目数量"),
    status: Optional[str] = Query(default=None, description="按状态过滤 (passed, failed)"),
    type_filter: Optional[str] = Query(default=None, alias="type", description="按类型过滤"),
) -> AuditLogResponse:
    """
    获取审计日志列表
    
    支持分页和过滤，返回完整条目信息
    """
    all_entries = read_audit_logs()
    
    # 过滤
    if status:
        all_entries = [e for e in all_entries if e.get("status") == status]
    if type_filter:
        all_entries = [e for e in all_entries if e.get("type") == type_filter]
    
    total = len(all_entries)
    
    # 分页
    page_entries = all_entries[skip : skip + limit]
    
    # 转换为模型
    entries = [AuditLogEntry(**e) for e in page_entries]
    
    # 统计（基于全部过滤后数据）
    statistics = compute_statistics(all_entries)
    
    return AuditLogResponse(
        total=total,
        entries=entries,
        statistics=statistics,
    )


@router.get("/feed", response_model=AuditFeedResponse)
async def get_audit_feed(
    limit: int = Query(default=20, ge=1, le=100, description="返回动态数量"),
) -> AuditFeedResponse:
    """
    获取版本动态Feed
    
    用于Dashboard"客栈动态"展示，返回格式化的动态列表
    """
    all_entries = read_audit_logs()
    
    # 取前N条
    recent = all_entries[:limit]
    
    # 构建Feed
    feed = [build_feed_item(e) for e in recent]
    
    return AuditFeedResponse(feed=feed)


@router.get("/stats")
async def get_audit_stats():
    """
    获取审计日志统计信息
    
    返回整体统计汇总
    """
    all_entries = read_audit_logs()
    statistics = compute_statistics(all_entries)
    
    return {
        "success": True,
        "statistics": statistics,
    }
