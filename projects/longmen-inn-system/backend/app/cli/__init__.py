"""
龙门客栈业务管理系统 - CLI 工具
========================================
作者: 老板娘

提供 inn 命令行工具，供 Agent 和东家操作客栈任务。

Usage:
    python -m app.cli task list [--assignee=ID] [--status=STATUS]
    python -m app.cli task create --title="xxx" --assignee=chef --creator=main [--priority=HIGH]
    python -m app.cli task status <task_id> <status>
    python -m app.cli task get <task_id>
    python -m app.cli ledger generate [--include-completed]
    python -m app.cli ledger preview [--include-completed]
"""

import argparse
import sys
import io

# Windows 控制台 UTF-8 模式
if sys.platform == "win32":
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


def cmd_task_list(args):
    """列出任务"""
    from app.db.session import SessionLocal
    from app.db import models
    from app.cli.ledger_generator import status_to_emoji, priority_to_str
    
    db = SessionLocal()
    try:
        query = db.query(models.Task)
        
        if args.assignee:
            query = query.filter(models.Task.assignee_agent_id == args.assignee)
        if args.status:
            try:
                status_val = getattr(models.TaskStatus, args.status.upper())
                query = query.filter(models.Task.status == status_val)
            except AttributeError:
                print(f"❌ 未知状态: {args.status}", file=sys.stderr)
                return 1
        
        tasks = query.order_by(models.Task.created_at.desc()).all()
        
        if not tasks:
            print("📋 暂无任务")
            return 0
        
        print(f"📋 任务清单（共 {len(tasks)} 项）：")
        print(f"{'ID':>4} | {'任务号':<20} | {'标题':<30} | {'状态':<16} | {'优先级':<4} | {'负责人':<8} | {'创建时间'}")
        print("-" * 120)
        
        for t in tasks:
            status_icon = status_to_emoji(t.status)
            priority_str = priority_to_str(t.priority) if t.priority else "中"
            created = t.created_at.strftime("%m-%d %H:%M") if t.created_at else "-"
            title = (t.title or "无标题")[:28]
            task_no = (t.task_no or "-")[:18]
            assignee = t.assignee_agent_id or "-"
            print(f"{t.id:>4} | {task_no:<20} | {title:<30} | {status_icon:<16} | {priority_str:<4} | {assignee:<8} | {created}")
        
        return 0
    finally:
        db.close()


def cmd_task_create(args):
    """创建任务"""
    from app.db.session import SessionLocal
    from app.db import models
    from datetime import datetime
    
    db = SessionLocal()
    try:
        # 生成任务号
        today = datetime.utcnow().strftime("%Y%m%d")
        existing = db.query(models.Task).filter(
            models.Task.task_no.like(f"T-{today}-%")
        ).count()
        task_no = f"T-{today}-{existing + 1:03d}"
        
        # 映射优先级
        priority_map = {
            "HIGH": models.TaskPriority.HIGH,
            "MEDIUM": models.TaskPriority.MEDIUM,
            "LOW": models.TaskPriority.LOW,
            "URGENT": models.TaskPriority.URGENT,
        }
        priority = priority_map.get(args.priority.upper(), models.TaskPriority.MEDIUM)
        
        task = models.Task(
            task_no=task_no,
            title=args.title,
            description=args.description or args.title,
            creator_agent_id=args.creator,
            assignee_agent_id=args.assignee,
            priority=priority,
            status=models.TaskStatus.PENDING,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        print(f"✅ 任务创建成功！")
        print(f"   任务号：{task.task_no}")
        print(f"   标题：{task.title}")
        print(f"   状态：⏳ 待开始")
        print(f"   负责人：{task.assignee_agent_id}")
        print(f"   ID：{task.id}（用于后续操作）")
        
        return 0
    except Exception as e:
        print(f"❌ 创建任务失败: {e}", file=sys.stderr)
        db.rollback()
        return 1
    finally:
        db.close()


def cmd_task_status(args):
    """更新任务状态"""
    from app.db.session import SessionLocal
    from app.db import models
    from datetime import datetime
    
    status_map = {
        "pending": models.TaskStatus.PENDING,
        "in_progress": models.TaskStatus.IN_PROGRESS,
        "reviewing": models.TaskStatus.REVIEWING,
        "completed": models.TaskStatus.COMPLETED,
        "blocked": models.TaskStatus.BLOCKED,
    }
    
    if args.status not in status_map:
        print(f"❌ 未知状态: {args.status}", file=sys.stderr)
        print(f"   可用状态: {', '.join(status_map.keys())}", file=sys.stderr)
        return 1
    
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(models.Task.id == int(args.task_id)).first()
        if not task:
            print(f"❌ 任务不存在: {args.task_id}", file=sys.stderr)
            return 1
        
        old_status = task.status
        new_status = status_map[args.status]
        task.status = new_status
        
        # 更新时间字段
        now = datetime.utcnow()
        if new_status == models.TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = now
        elif new_status == models.TaskStatus.COMPLETED:
            task.completed_at = now
            if task.started_at:
                delta = task.completed_at - task.started_at
                task.actual_hours = int(delta.total_seconds() / 3600)
        
        # 记录 TaskLog
        log = models.TaskLog(
            task_id=task.id,
            from_status=old_status,
            to_status=new_status,
            operator_agent_id=args.operator or "cli",
            comment=f"CLI更新状态: {old_status.value} -> {new_status.value}"
        )
        db.add(log)
        db.commit()
        
        from app.cli.ledger_generator import status_to_emoji
        print(f"✅ 任务 {task.task_no} 状态已更新")
        print(f"   {status_to_emoji(old_status)} → {status_to_emoji(new_status)}")
        
        return 0
    except Exception as e:
        print(f"❌ 更新状态失败: {e}", file=sys.stderr)
        db.rollback()
        return 1
    finally:
        db.close()


def cmd_task_get(args):
    """查看任务详情"""
    from app.db.session import SessionLocal
    from app.db import models
    from app.cli.ledger_generator import status_to_emoji, priority_to_str
    
    db = SessionLocal()
    try:
        task = db.query(models.Task).filter(models.Task.id == int(args.task_id)).first()
        if not task:
            print(f"❌ 任务不存在: {args.task_id}", file=sys.stderr)
            return 1
        
        print(f"📋 任务详情")
        print(f"{'─' * 50}")
        print(f"  ID：{task.id}")
        print(f"  任务号：{task.task_no or '-'}")
        print(f"  标题：{task.title}")
        print(f"  描述：{task.description or '-'}")
        print(f"  状态：{status_to_emoji(task.status)}")
        print(f"  优先级：{priority_to_str(task.priority)}")
        print(f"  创建者：{task.creator_agent_id}")
        print(f"  负责人：{task.assignee_agent_id}")
        print(f"  创建时间：{task.created_at.strftime('%Y-%m-%d %H:%M') if task.created_at else '-'}")
        print(f"  开始时间：{task.started_at.strftime('%Y-%m-%d %H:%M') if task.started_at else '-'}")
        print(f"  完成时间：{task.completed_at.strftime('%Y-%m-%d %H:%M') if task.completed_at else '-'}")
        print(f"  预估工时：{task.estimated_hours}h")
        print(f"  实际工时：{task.actual_hours}h")
        
        # 关联项目
        if task.project_id:
            project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
            if project:
                print(f"  项目：{project.name}")
        
        # 操作日志
        logs = db.query(models.TaskLog).filter(models.TaskLog.task_id == task.id).order_by(models.TaskLog.created_at.desc()).limit(5).all()
        if logs:
            print(f"  最近操作日志：")
            for log in logs:
                ts = log.created_at.strftime("%m-%d %H:%M") if log.created_at else "-"
                print(f"    [{ts}] {log.operator_agent_id}: {log.from_status.value if log.from_status else '新建'} → {log.to_status.value} | {log.comment}")
        
        return 0
    finally:
        db.close()


def cmd_ledger_generate(args):
    """生成 LEDGER.md"""
    try:
        from app.cli.ledger_generator import export_ledger_to_file
        path = export_ledger_to_file(include_completed=not args.exclude_completed)
        print(f"✅ LEDGER.md 已生成：{path}")
        return 0
    except Exception as e:
        print(f"❌ 生成失败: {e}", file=sys.stderr)
        return 1


def cmd_ledger_preview(args):
    """预览 LEDGER.md（不写入文件）"""
    from app.db.session import SessionLocal
    from app.cli.ledger_generator import generate_ledger_from_db
    
    db = SessionLocal()
    try:
        content = generate_ledger_from_db(db, include_completed=not args.exclude_completed)
        print(content)
        return 0
    except Exception as e:
        print(f"❌ 生成失败: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(
        description="🏮 龙门客栈 CLI 工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # === task 子命令 ===
    task_parser = subparsers.add_parser("task", help="任务管理")
    task_subparsers = task_parser.add_subparsers(dest="subcommand")
    
    # task list
    list_parser = task_subparsers.add_parser("list", help="列出任务")
    list_parser.add_argument("--assignee", help="按负责人过滤 (agent_id)")
    list_parser.add_argument("--status", help="按状态过滤 (pending/in_progress/reviewing/completed/blocked)")
    list_parser.set_defaults(func=cmd_task_list)
    
    # task create
    create_parser = task_subparsers.add_parser("create", help="创建任务")
    create_parser.add_argument("--title", required=True, help="任务标题")
    create_parser.add_argument("--description", help="任务描述")
    create_parser.add_argument("--assignee", required=True, help="负责人 agent_id")
    create_parser.add_argument("--creator", default="main", help="创建者 agent_id")
    create_parser.add_argument("--priority", default="MEDIUM", help="优先级 (HIGH/MEDIUM/LOW/URGENT)")
    create_parser.set_defaults(func=cmd_task_create)
    
    # task status
    status_parser = task_subparsers.add_parser("status", help="更新任务状态")
    status_parser.add_argument("task_id", help="任务 ID")
    status_parser.add_argument("status", help="新状态 (pending/in_progress/reviewing/completed/blocked)")
    status_parser.add_argument("--operator", help="操作者 agent_id")
    status_parser.set_defaults(func=cmd_task_status)
    
    # task get
    get_parser = task_subparsers.add_parser("get", help="查看任务详情")
    get_parser.add_argument("task_id", help="任务 ID")
    get_parser.set_defaults(func=cmd_task_get)
    
    # === ledger 子命令 ===
    ledger_parser = subparsers.add_parser("ledger", help="LEDGER.md 管理")
    ledger_subparsers = ledger_parser.add_subparsers(dest="subcommand")
    
    gen_parser = ledger_subparsers.add_parser("generate", help="生成 LEDGER.md（写入文件）")
    gen_parser.add_argument("--exclude-completed", action="store_true", help="排除已完成任务")
    gen_parser.set_defaults(func=cmd_ledger_generate)
    
    preview_parser = ledger_subparsers.add_parser("preview", help="预览 LEDGER.md（输出到终端，不写入）")
    preview_parser.add_argument("--exclude-completed", action="store_true", help="排除已完成任务")
    preview_parser.set_defaults(func=cmd_ledger_preview)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
