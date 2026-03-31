"""
龙门客栈业务管理系统 - 文件管理API
===============================
作者: 厨子 (神厨小福贵)

提供LEDGER.md等文件的读取、编辑功能
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user_required
from app.models.user import User
from typing import Optional, List
from pathlib import Path
import os

from app.core.config import settings

router = APIRouter()

LONGMEN_INN_ROOT = settings.LONGMEN_INN_ROOT
ROLES_DIR = LONGMEN_INN_ROOT / "roles"


class FileContent(BaseModel):
    content: str
    path: str


class SaveFileRequest(BaseModel):
    content: str
    path: Optional[str] = "LEDGER.md"


class RoleFile(BaseModel):
    name: str
    path: str
    type: str
    size: int


class RoleFileList(BaseModel):
    agent_id: str
    files: List[RoleFile]


@router.get("/ledger")
async def get_ledger():
    """
    读取 LEDGER.md 文件内容（纯展示用途）
    
    注意：此端点直接读取 markdown 文件。任务操作请使用 POST /tasks/ 。
    如需生成最新账本，请调用 POST /files/ledger/generate 。
    """
    ledger_path = LONGMEN_INN_ROOT / "LEDGER.md"
    
    if not ledger_path.exists():
        raise HTTPException(status_code=404, detail="LEDGER.md 文件不存在，请先调用 POST /files/ledger/generate 生成")
    
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "path": str(ledger_path),
            "mode": "file"  # 标识来源：file=markdown文件
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.post("/ledger/generate")
async def generate_ledger(
    include_completed: bool = True,
    current_user: User = Depends(get_current_user_required),
):
    """
    从数据库生成 LEDGER.md 文件（单一写入入口）
    
    这是任务数据的唯一写入路径。
    LEDGER.md 由 DB 状态导出，作为纯展示/日报用途。
    """
    from app.db.session import SessionLocal
    from app.cli.ledger_generator import export_ledger_to_file
    
    try:
        path = export_ledger_to_file(include_completed=include_completed)
        return {
            "success": True,
            "message": "LEDGER.md 已从数据库生成",
            "path": path,
            "mode": "generated"  # 标识来源：generated=由DB导出
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/ledger")  # 兼容旧调用
async def regenerate_ledger_alias(
    current_user: User = Depends(get_current_user_required),
):
    """
    POST /files/ledger（兼容旧接口）
    
    旧接口会写入 markdown 后同步到 DB。
    现在改为由 DB 导出为 markdown（单向）。
    如需手动编辑账本内容，请使用 inn ledger generate 命令。
    """
    from app.cli.ledger_generator import export_ledger_to_file
    
    try:
        path = export_ledger_to_file(include_completed=True)
        return {
            "success": True,
            "message": "LEDGER.md 已从数据库生成（旧接口已废弃，请使用 POST /files/ledger/generate）",
            "path": path,
            "mode": "generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.get("/role/{agent_id}/files")
async def list_agent_role_files(agent_id: str):
    """列出指定agent的角色文件列表"""
    role_dir = ROLES_DIR / agent_id
    
    if not role_dir.exists():
        raise HTTPException(status_code=404, detail=f"角色目录不存在: {agent_id}")
    
    files = []
    
    def scan_directory(dir_path: Path, prefix: str = ""):
        for item in sorted(dir_path.iterdir()):
            if item.is_file():
                if item.suffix in ['.md', '.json']:
                    rel_path = item.relative_to(role_dir)
                    files.append({
                        "name": item.name,
                        "path": str(rel_path),
                        "type": item.suffix[1:],
                        "size": item.stat().st_size
                    })
            elif item.is_dir() and item.name != "__pycache__":
                scan_directory(item, prefix + item.name + "/")
    
    scan_directory(role_dir)
    
    return {
        "success": True,
        "agent_id": agent_id,
        "files": files
    }


@router.get("/role/{agent_id}/file")
async def get_agent_role_file(agent_id: str, file_path: str = "IDENTITY.md"):
    """读取指定agent的角色文件内容"""
    role_dir = (ROLES_DIR / agent_id).resolve()
    
    if not role_dir.exists():
        raise HTTPException(status_code=404, detail=f"角色目录不存在: {agent_id}")
    
    # 安全检查：禁止路径遍历
    # 清理 file_path，去除任何 .. 或绝对路径成分
    safe_file_path = os.path.normpath(file_path)
    if safe_file_path.startswith("..") or os.path.isabs(safe_file_path):
        raise HTTPException(status_code=400, detail="无效的文件路径")
    
    file_full_path = (role_dir / safe_file_path).resolve()
    
    # 严格检查：确保解析后的路径在 role_dir 内
    try:
        file_full_path.relative_to(role_dir)
    except ValueError:
        raise HTTPException(status_code=403, detail="无权访问此文件")
    
    if not file_full_path.exists():
        raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
    
    try:
        with open(file_full_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "agent_id": agent_id,
            "file_path": file_path,
            "file_type": file_full_path.suffix[1:]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.get("/role/{agent_id}")
async def get_role_file(agent_id: str):
    """读取角色身份文件（默认IDENTITY.md）"""
    return await get_agent_role_file(agent_id, "IDENTITY.md")


@router.get("/roles")
async def list_role_files():
    """列出所有角色文件"""
    roles = []
    
    if not ROLES_DIR.exists():
        return {"success": True, "roles": []}
    
    for item in ROLES_DIR.iterdir():
        if item.is_dir():
            identity_file = item / "IDENTITY.md"
            roles.append({
                "agent_id": item.name,
                "path": str(identity_file) if identity_file.exists() else str(item),
                "has_identity": identity_file.exists()
            })
    
    return {
        "success": True,
        "roles": sorted(roles, key=lambda x: x["agent_id"])
    }


@router.get("/readme")
async def get_readme():
    """读取项目README.md文件内容"""
    readme_path = LONGMEN_INN_ROOT / "README.md"
    
    if not readme_path.exists():
        raise HTTPException(status_code=404, detail="README.md 文件不存在")
    
    try:
        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "path": str(readme_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")
