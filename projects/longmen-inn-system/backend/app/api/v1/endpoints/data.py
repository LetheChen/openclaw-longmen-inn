"""
龙门客栈业务管理系统 - 数据管理API
===============================
作者: 厨子 (神厨小福贵)

提供数据导入、同步等管理功能
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.import_production_data import ProductionDataImporter

router = APIRouter()


@router.post("/import")
async def import_data(db: Session = Depends(get_db)):
    """
    手动导入/更新生产数据
    
    从 LEDGER.md 和 ROSTER.md 读取数据并更新数据库
    - Agent: 存在则更新（跳过状态），不存在则创建
    - Task: 存在则更新，不存在则创建
    - Project: 不存在才创建
    """
    try:
        importer = ProductionDataImporter(db)
        results = importer.import_all()
        return {
            "success": True,
            "message": "数据导入成功",
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据导入失败: {str(e)}")


@router.post("/import/tasks")
async def import_tasks(db: Session = Depends(get_db)):
    """仅导入/更新任务数据"""
    try:
        importer = ProductionDataImporter(db)
        count = importer.import_tasks()
        return {
            "success": True,
            "message": f"任务数据导入成功，共 {count} 条",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"任务导入失败: {str(e)}")


@router.post("/import/agents")
async def import_agents(db: Session = Depends(get_db)):
    """仅导入/更新Agent数据"""
    try:
        importer = ProductionDataImporter(db)
        count = importer.import_agents()
        return {
            "success": True,
            "message": f"Agent数据导入成功，共 {count} 条",
            "count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent导入失败: {str(e)}")
