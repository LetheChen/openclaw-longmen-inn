"""
龙门客栈业务管理系统 - 初始化管理员账户
===============================
作者: 厨子 (神厨小福贵)

创建默认管理员账户，用于首次登录系统
"""

import sys
import os

# 确保能找到app模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.base import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import hash_password


def init_admin_user(db: Session) -> User:
    """
    初始化管理员账户
    
    默认账户:
    - 用户名: admin
    - 邮箱: admin@longmen-inn.local
    - 密码: Admin@123456（首次登录后请修改）
    
    操作: 在控制台输出密码，便于管理员查看
    """
    # 检查是否已存在管理员
    admin = db.query(User).filter(User.username == "admin").first()
    
    if admin:
        print(f"管理员账户已存在: {admin.username}")
        return admin
    
    # 创建管理员账户
    default_password = "Admin@123456"  # 首次登录后请修改
    
    admin = User(
        username="admin",
        email="admin@longmen-inn.local",
        hashed_password=hash_password(default_password),
        full_name="龙门客栈掌柜",
        role=UserRole.ADMIN.value,
        is_active=True,
        is_superuser=True
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print("=" * 60)
    print("默认管理员账户已创建")
    print("=" * 60)
    print(f"用户名: admin")
    print(f"密码: {default_password}")
    print("⚠️  请在首次登录后立即修改密码！")
    print("=" * 60)
    
    return admin


def init_test_users(db: Session):
    """
    初始化测试账户（仅开发环境）
    
    创建几个测试用户，方便开发测试
    """
    test_users = [
        {
            "username": "zhangsan",
            "email": "zhangsan@longmen-inn.local",
            "full_name": "张三",
            "role": UserRole.WORKER.value,
            "password": "Zhangsan@123"
        },
        {
            "username": "lisi",
            "email": "lisi@longmen-inn.local",
            "full_name": "李四",
            "role": UserRole.WORKER.value,
            "password": "Lisi@123"
        },
        {
            "username": "manager",
            "email": "manager@longmen-inn.local",
            "full_name": "王掌柜",
            "role": UserRole.MANAGER.value,
            "password": "Manager@123"
        }
    ]
    
    for user_data in test_users:
        # 检查用户是否已存在
        if db.query(User).filter(User.username == user_data["username"]).first():
            continue
        
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hash_password(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            is_active=True
        )
        db.add(user)
        print(f"创建测试用户: {user_data['username']}")
    
    db.commit()


def main():
    """主函数"""
    print("初始化数据库表结构...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表结构创建完成")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 初始化管理员账户
        init_admin_user(db)
        
        # 开发环境：创建测试用户
        from app.core.config import settings
        if settings.is_development:
            print("\n开发环境：创建测试用户...")
            init_test_users(db)
        
        print("\n初始化完成！")
        
    except Exception as e:
        print(f"初始化失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()