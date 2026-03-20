"""
龙门客栈业务管理系统 - 文件管理API
===============================
作者: 厨子 (神厨小福贵)

提供LEDGER.md等文件的读取、编辑功能
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path

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
    """读取LEDGER.md文件内容"""
    ledger_path = LONGMEN_INN_ROOT / "LEDGER.md"
    
    if not ledger_path.exists():
        raise HTTPException(status_code=404, detail="LEDGER.md 文件不存在")
    
    try:
        with open(ledger_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return {
            "success": True,
            "content": content,
            "path": str(ledger_path)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取文件失败: {str(e)}")


@router.post("/ledger")
async def save_ledger(data: SaveFileRequest):
    """保存LEDGER.md文件内容并同步到数据库"""
    ledger_path = LONGMEN_INN_ROOT / "LEDGER.md"
    
    try:
        with open(ledger_path, "w", encoding="utf-8") as f:
            f.write(data.content)
        
        from app.db.import_production_data import ProductionDataImporter
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        try:
            importer = ProductionDataImporter(db)
            results = importer.import_all()
        finally:
            db.close()
        
        return {
            "success": True,
            "message": "文件保存成功，数据已同步",
            "sync_results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")


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
    role_dir = ROLES_DIR / agent_id
    
    if not role_dir.exists():
        raise HTTPException(status_code=404, detail=f"角色目录不存在: {agent_id}")
    
    file_full_path = role_dir / file_path
    
    if not file_full_path.exists():
        raise HTTPException(status_code=404, detail=f"文件不存在: {file_path}")
    
    if not str(file_full_path.resolve()).startswith(str(role_dir.resolve())):
        raise HTTPException(status_code=403, detail="无权访问此文件")
    
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
