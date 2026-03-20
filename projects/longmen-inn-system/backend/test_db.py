#!/usr/bin/env python3
"""
测试数据库查询和API路由
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal, engine
from app.db import models
from app.schemas import agent as agent_schema
from sqlalchemy.orm import Session

def test_db_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("测试数据库连接...")
    print("=" * 60)
    
    try:
        # 测试连接
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_agents_query():
    """测试Agent查询"""
    print("\n" + "=" * 60)
    print("测试Agent查询...")
    print("=" * 60)
    
    try:
        db: Session = SessionLocal()
        
        # 查询所有Agent
        agents = db.query(models.Agent).all()
        print(f"✅ 查询到 {len(agents)} 个Agent")
        
        for agent in agents:
            print(f"  - {agent.name} ({agent.agent_id}): {agent.status}")
        
        # 测试在线Agent查询
        online_agents = db.query(models.Agent).filter(models.Agent.status != models.AgentStatus.OFFLINE).all()
        print(f"\n✅ 查询到 {len(online_agents)} 个在线Agent")
        
        # 测试序列化
        from app.schemas.agent import AgentResponse
        for agent in online_agents:
            try:
                response = AgentResponse.model_validate(agent)
                print(f"  ✅ {agent.name} 序列化成功")
            except Exception as e:
                print(f"  ❌ {agent.name} 序列化失败: {e}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Agent查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_statistics():
    """测试统计查询"""
    print("\n" + "=" * 60)
    print("测试统计查询...")
    print("=" * 60)
    
    try:
        db: Session = SessionLocal()
        
        total = db.query(models.Agent).count()
        offline = db.query(models.Agent).filter(models.Agent.status == models.AgentStatus.OFFLINE).count()
        busy = db.query(models.Agent).filter(models.Agent.status == models.AgentStatus.BUSY).count()
        idle = db.query(models.Agent).filter(models.Agent.status == models.AgentStatus.IDLE).count()
        online = total - offline
        
        print(f"✅ 统计数据:")
        print(f"  - 总数: {total}")
        print(f"  - 在线: {online}")
        print(f"  - 离线: {offline}")
        print(f"  - 忙碌: {busy}")
        print(f"  - 空闲: {idle}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ 统计查询失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n🏮 龙门客栈 - 数据库测试工具 🏮\n")
    
    all_passed = True
    
    if not test_db_connection():
        all_passed = False
    
    if not test_agents_query():
        all_passed = False
    
    if not test_statistics():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("=" * 60)
