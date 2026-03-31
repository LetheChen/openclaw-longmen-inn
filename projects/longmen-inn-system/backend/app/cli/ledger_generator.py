"""
龙门客栈业务管理系统 - LEDGER.md 生成器
========================================
作者: 老板娘

将 DB 中的任务数据导出为 LEDGER.md 格式（纯展示/日报用途）
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.db import models
from app.db.session import SessionLocal


# 干支纪年（简化映射，够用到 2100 年）
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def gregorian_to_chinese(gregorian_date: str) -> str:
    """将公历日期字符串转换为干支纪年（粗略，用于展示）"""
    try:
        dt = datetime.fromisoformat(gregorian_date.replace("Z", "+00:00"))
        year = dt.year
        month = dt.month
        day = dt.day
        
        # 简化干支计算（基于 1984 年甲子年的偏移）
        # 1984-01-01 是甲子年正月初一
        base_year = 1984
        base_stem_idx = 0  # 甲子
        base_branch_idx = 0
        
        years_diff = year - base_year
        stem_idx = (base_stem_idx + years_diff) % 10
        branch_idx = (base_branch_idx + years_diff) % 12
        
        # 简化为年干支 + 月干支（极简化）
        year_stem = HEAVENLY_STEMS[stem_idx]
        year_branch = EARTHLY_BRANCHES[branch_idx]
        
        # 月份干支（简化，正月=寅月）
        month_branch = (dt.month + 1) % 12  # 正月寅，二月卯...
        month_stem = (stem_idx * 2 + month_branch) % 10
        
        # 日干支（极简化）
        days_since_base = (dt - datetime(1984, 1, 1)).days
        day_stem = (base_stem_idx + days_since_base) % 10
        day_branch = (base_branch_idx + days_since_base) % 12
        
        return f"{year_stem}{year_branch}年{HEAVENLY_STEMS[month_stem]}{EARTHLY_BRANCHES[month_branch]}月{dt.day}"
    except Exception:
        return gregorian_date


def status_to_emoji(status: models.TaskStatus) -> str:
    """将任务状态转换为 emoji 标记"""
    mapping = {
        models.TaskStatus.PENDING: "⏳ 待开始",
        models.TaskStatus.IN_PROGRESS: "🔥 进行中",
        models.TaskStatus.REVIEWING: "🔍 审核中",
        models.TaskStatus.COMPLETED: "✅ 已完成",
        models.TaskStatus.BLOCKED: "🚫 已阻塞",
    }
    return mapping.get(status, f"❓{status.value}")


def priority_to_str(priority: models.TaskPriority) -> str:
    """优先级转中文"""
    mapping = {
        models.TaskPriority.HIGH: "高",
        models.TaskPriority.MEDIUM: "中",
        models.TaskPriority.LOW: "低",
        models.TaskPriority.URGENT: "紧急",
    }
    return mapping.get(priority, "中")


def agent_id_to_name(agent_id: str, agent_name_map: dict) -> str:
    """Agent ID 转中文名"""
    return agent_name_map.get(agent_id, agent_id)


def _md_cell(text: str, max_len: int = 0) -> str:
    """
    将文本安全地放入 Markdown 表格单元格
    - 转义管道符 |（表格列分隔符）
    - 移除换行符（避免多行破坏表格）
    - 截断超长内容
    """
    if text is None:
        return ""
    text = str(text).replace("|", "\\|").replace("\n", " ").replace("\r", "")
    if max_len > 0 and len(text) > max_len:
        text = text[:max_len - 1] + "…"
    return text


def generate_ledger_from_db(db: Session, include_completed: bool = True) -> str:
    """
    从数据库生成 LEDGER.md 内容
    
    Args:
        db: 数据库 Session
        include_completed: 是否包含已完成任务（默认包含全部）
    
    Returns:
        LEDGER.md 格式的 markdown 字符串
    """
    # 构建 Agent ID → 中文名 映射
    agents = db.query(models.Agent).all()
    agent_name_map = {a.agent_id: a.name for a in agents}
    
    # 查询任务
    query = db.query(models.Task)
    if not include_completed:
        query = query.filter(models.Task.status != models.TaskStatus.COMPLETED)
    tasks = query.order_by(models.Task.created_at.desc()).all()
    
    # 按状态分组统计
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == models.TaskStatus.COMPLETED)
    in_progress = sum(1 for t in tasks if t.status == models.TaskStatus.IN_PROGRESS)
    pending = sum(1 for t in tasks if t.status == models.TaskStatus.PENDING)
    
    # 当前客栈状态
    if in_progress > 0:
        inn_status = f"🔥 {in_progress} 个任务进行中"
    elif pending > 0:
        inn_status = f"⏳ {pending} 个任务待开工"
    else:
        inn_status = "✅ 全员完工"
    
    now = datetime.utcnow()
    chinese_date = gregorian_to_chinese(now.isoformat())
    
    # Header
    lines = [
        "# 龙门客栈 - 营业总账",
        "",
        f"**今日营业日期**：{chinese_date}",
        f"**当前客栈状态**：{inn_status}",
        f"**统计**：共 {total} 任务 | 🔥进行中 {in_progress} | ✅已完成 {completed} | ⏳待开工 {pending}",
        f"**生成时间**：{now.strftime('%Y-%m-%d %H:%M')}",
        "",
        "---",
        "",
        "## 挂牌任务（任务看板）",
        "",
        "| 任务号 | 任务内容 | 状态 | 优先级 | 挂单人 | 负责人 | 挂牌时间 | 完成时间 | 项目名称 | 备注 |",
        "|--------|----------|------|--------|--------|--------|----------|----------|----------|------|",
    ]
    
    for task in tasks:
        task_no = task.task_no or f"T-{task.id:08d}"
        title = task.title or "无标题"
        status_str = status_to_emoji(task.status)
        priority_str = priority_to_str(task.priority) if task.priority else "中"
        creator = agent_id_to_name(task.creator_agent_id or "unknown", agent_name_map)
        assignee = agent_id_to_name(task.assignee_agent_id or "unknown", agent_name_map)
        
        # 挂牌时间（创建日期）
        create_date = ""
        if task.created_at:
            create_date = task.created_at.strftime("%m月%d日")
        
        # 完成时间
        complete_date = ""
        if task.completed_at:
            complete_date = task.completed_at.strftime("%m月%d日")
        
        # 项目名
        project_name = ""
        if task.project_id:
            project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
            if project:
                project_name = project.name
        
        # 备注（取 description 前30字）
        notes = ""
        if task.description:
            notes = task.description[:40] + ("..." if len(task.description) > 40 else "")
        
        lines.append(
            f"| {task_no} | {_md_cell(title, 40)} | **{status_str}** | {priority_str} "
            f"| {creator} | {assignee} | {create_date} | {complete_date} "
            f"| {_md_cell(project_name, 20)} | {_md_cell(notes, 40)} |"
        )
    
    lines += [
        "",
        "---",
        "",
        "## 伙计状态牌",
        "",
        "| 伙计 | 状态 | 龙门令 | 当前任务 |",
        "|------|------|--------|----------|",
    ]
    
    for agent in agents:
        # 获取该 Agent 当前进行的任务
        current_task = db.query(models.Task).filter(
            models.Task.assignee_agent_id == agent.agent_id,
            models.Task.status == models.TaskStatus.IN_PROGRESS
        ).first()
        
        current_task_str = current_task.title[:20] if current_task else "待命"
        
        status_icon = "✅ 空闲" if agent.status == models.AgentStatus.IDLE else (
            "🔥 忙碌" if agent.status == models.AgentStatus.BUSY else "❌ 离线"
        )
        
        lines.append(
            f"| `{agent.name}` | {status_icon} | {agent.longmenling} | {current_task_str} |"
        )
    
    lines += [
        "",
        "---",
        "",
        "## 龙门令功德簿",
        "",
        "| 伙计 | 本月累计龙门令 | 备注 |",
        "|------|----------------|------|",
    ]
    
    for agent in agents:
        lines.append(
            f"| {agent.name} | {agent.longmenling} | 历史功绩 |"
        )
    
    lines += [
        "",
        "---",
        "",
        "**账本管理员**：老板娘",
        f"**最后更新**：{now.strftime('%Y-%m-%d %H:%M')}",
        f"**生成方式**：inn ledger generate（由数据库自动导出）",
    ]
    
    return "\n".join(lines)


def export_ledger_to_file(include_completed: bool = True) -> str:
    """
    将当前 DB 中的任务导出为 LEDGER.md 文件
    
    Returns:
        生成的 LEDGER.md 文件路径
    """
    from app.core.config import settings
    
    db = SessionLocal()
    try:
        content = generate_ledger_from_db(db, include_completed)
        ledger_path = settings.LONGMEN_INN_ROOT / "LEDGER.md"
        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write(content)
        return str(ledger_path)
    finally:
        db.close()
