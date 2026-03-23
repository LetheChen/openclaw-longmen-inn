"""
龙门客栈业务管理系统 - 依赖注入
===============================
作者: 厨子 (神厨小福贵)

顶层依赖导出，便于导入
"""

# 从API依赖导入
from app.api.deps import (
    get_db,
    get_current_user,
    get_current_user_required,
    get_admin_user,
)

# 从安全模块导入
from app.core.security import (
    verify_token,
    create_access_token,
    create_refresh_token,
    generate_csrf_token,
    validate_csrf_token,
)

__all__ = [
    # 数据库
    "get_db",
    # 用户认证
    "get_current_user",
    "get_current_user_required",
    "get_admin_user",
    # Token操作
    "verify_token",
    "create_access_token",
    "create_refresh_token",
    # CSRF保护
    "generate_csrf_token",
    "validate_csrf_token",
]