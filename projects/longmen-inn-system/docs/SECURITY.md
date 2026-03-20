# 安全检查清单 (Security Checklist)

> 🔒 本清单用于龙门客栈业务管理系统的代码安全审查  
> 📅 版本：v1.0  
> 👤 维护者：账房先生（质量保证工程师）

---

## 目录

1. [代码安全审查要点](#代码安全审查要点)
2. [依赖安全检查](#依赖安全检查)
3. [敏感信息处理](#敏感信息处理)
4. [API安全规范](#api安全规范)
5. [常见漏洞检查](#常见漏洞检查)

---

## 代码安全审查要点

### Python安全编码规范

#### ✅ 必须遵守的安全规则

| 规则编号 | 规则描述 | 风险等级 | 检查方式 |
|----------|----------|----------|----------|
| SEC-001 | 禁止直接拼接SQL字符串 | 🔴 高危 | 代码审查/SAST |
| SEC-002 | 禁止硬编码密钥或密码 | 🔴 高危 | 代码审查/密钥扫描 |
| SEC-003 | 必须验证所有用户输入 | 🔴 高危 | 代码审查/渗透测试 |
| SEC-004 | 禁止eval()和exec()执行动态代码 | 🟡 中危 | 代码审查 |
| SEC-005 | 必须设置安全的会话Cookie属性 | 🟡 中危 | 配置审查 |
| SEC-006 | 必须记录安全相关日志 | 🟢 低危 | 日志审查 |

---

## 依赖安全检查

### Python依赖安全检查

**使用工具**：`safety`、`pip-audit`、`bandit`

```bash
# 安装安全扫描工具
pip install safety pip-audit bandit

# 检查已知漏洞
safety check

# 详细报告
safety check --json > safety-report.json

# pip-audit检查
pip-audit

# 代码安全扫描
bandit -r backend/ -f json -o bandit-report.json
```

**CI集成**：

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 2 * * 1'  # 每周一早2点

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install safety pip-audit
      
      - name: Run safety check
        run: safety check --full-report
        continue-on-error: true
      
      - name: Run pip-audit
        run: pip-audit --desc --format=json | tee audit-report.json
        continue-on-error: true
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            audit-report.json
  
  code-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install bandit
        run: pip install bandit
      
      - name: Run bandit
        run: bandit -r backend/ -f json -o bandit-report.json || true
      
      - name: Upload bandit report
        uses: actions/upload-artifact@v3
        with:
          name: bandit-report
          path: bandit-report.json
```

### JavaScript依赖安全检查

**使用工具**：`npm audit`、`snyk`、`dependabot`

```bash
# npm audit检查
npm audit

# 修复漏洞
npm audit fix

# 详细报告
npm audit --json
```

---

## 敏感信息处理

### 敏感信息清单

| 信息类型 | 示例 | 存储要求 | 传输要求 |
|----------|------|----------|----------|
| 密码 | 用户登录密码 | bcrypt哈希，加盐 | 禁止明文传输 |
| API密钥 | 支付宝/微信支付密钥 | 密钥管理系统 | HTTPS |
| 数据库密码 | 数据库连接密码 | 环境变量/KMS | TLS加密 |
| JWT密钥 | 签名密钥 | 密钥管理系统 | 禁止传输 |
| 身份证号 | 客户身份证 | 加密存储(AES-256) | 脱敏显示 |
| 手机号 | 客户联系方式 | 加密存储 | 脱敏显示 |
| 信用卡号 | 支付信息 | 符合PCI DSS | 禁止存储 |

### 敏感信息处理规范

```python
# ✅ 密码哈希
import bcrypt

def hash_password(password: str) -> str:
    """对密码进行bcrypt哈希。"""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码。"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ✅ 敏感数据加密
from cryptography.fernet import Fernet
import os

# 加密密钥应该从密钥管理服务获取
ENCRYPTION_KEY = os.getenv('DATA_ENCRYPTION_KEY')
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_sensitive_data(data: str) -> str:
    """加密敏感数据。"""
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted: str) -> str:
    """解密敏感数据。"""
    return cipher_suite.decrypt(encrypted.encode()).decode()

# ✅ 数据脱敏
def mask_id_card(id_card: str) -> str:
    """身份证号脱敏显示。"""
    if len(id_card) != 18:
        return id_card
    return f"{id_card[:6]}********{id_card[-4:]}"

def mask_phone(phone: str) -> str:
    """手机号脱敏显示。"""
    if len(phone) != 11:
        return phone
    return f"{phone[:3]}****{phone[-4:]}"

def mask_name(name: str) -> str:
    """姓名脱敏显示。"""
    if len(name) <= 1:
        return name
    return f"{name[0]}*{'*' * (len(name) - 2)}"

# 使用示例
class UserResponse(BaseModel):
    """用户响应模型，自动脱敏。"""
    id: str
    username: str
    email: str
    phone_masked: str  # 脱敏后的手机号
    id_card_masked: Optional[str] = None  # 脱敏后的身份证号
    
    @staticmethod
    def from_user(user: User) -> 'UserResponse':
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone_masked=mask_phone(user.phone),
            id_card_masked=mask_id_card(user.id_card) if user.id_card else None
        )
```

---

## API安全规范

### 1. 认证规范

```python
# ✅ JWT认证示例
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 从环境变量获取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    """创建访问令牌。"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    """创建刷新令牌。"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """获取当前用户（依赖注入）。"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    
    return user

# 使用示例
@app.post("/api/auth/login")
async def login(credentials: LoginRequest):
    """用户登录。"""
    user = await authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误"
        )
    
    access_token = create_access_token({"sub": user.id})
    refresh_token = create_refresh_token({"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.get("/api/user/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    """获取当前用户信息（需要认证）。"""
    return UserResponse.from_user(current_user)

@app.post("/api/admin/rooms")
async def create_room(
    room_data: RoomCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """创建房间（需要管理员权限）。"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    
    room = await room_service.create(room_data)
    return room
```

### 2. 授权规范

```python
# ✅ 基于角色的访问控制（RBAC）
from enum import Enum
from functools import wraps

class Role(str, Enum):
    """用户角色。"""
    ADMIN = "admin"           # 管理员
    MANAGER = "manager"       # 经理
    RECEPTIONIST = "receptionist"  # 前台
    ACCOUNTANT = "accountant" # 财务
    VIEWER = "viewer"         # 只读

class Permission(str, Enum):
    """权限列表。"""
    # 预订管理
    BOOKING_CREATE = "booking:create"
    BOOKING_READ = "booking:read"
    BOOKING_UPDATE = "booking:update"
    BOOKING_DELETE = "booking:delete"
    BOOKING_CANCEL = "booking:cancel"
    
    # 房间管理
    ROOM_CREATE = "room:create"
    ROOM_READ = "room:read"
    ROOM_UPDATE = "room:update"
    ROOM_DELETE = "room:delete"
    
    # 客户管理
    CUSTOMER_CREATE = "customer:create"
    CUSTOMER_READ = "customer:read"
    CUSTOMER_UPDATE = "customer:update"
    
    # 财务管理
    FINANCE_READ = "finance:read"
    FINANCE_REPORT = "finance:report"
    
    # 系统管理
    USER_MANAGE = "user:manage"
    SETTINGS_MANAGE = "settings:manage"

# 角色-权限映射
ROLE_PERMISSIONS = {
    Role.ADMIN: [p for p in Permission],  # 管理员拥有所有权限
    
    Role.MANAGER: [
        # 预订管理
        Permission.BOOKING_CREATE,
        Permission.BOOKING_READ,
        Permission.BOOKING_UPDATE,
        Permission.BOOKING_CANCEL,
        # 房间管理
        Permission.ROOM_READ,
        Permission.ROOM_UPDATE,
        # 客户管理
        Permission.CUSTOMER_CREATE,
        Permission.CUSTOMER_READ,
        Permission.CUSTOMER_UPDATE,
        # 财务
        Permission.FINANCE_READ,
        Permission.FINANCE_REPORT,
    ],
    
    Role.RECEPTIONIST: [
        # 预订管理
        Permission.BOOKING_CREATE,
        Permission.BOOKING_READ,
        Permission.BOOKING_UPDATE,
        Permission.BOOKING_CANCEL,
        # 房间管理
        Permission.ROOM_READ,
        # 客户管理
        Permission.CUSTOMER_CREATE,
        Permission.CUSTOMER_READ,
    ],
    
    Role.ACCOUNTANT: [
        # 预订管理（只读）
        Permission.BOOKING_READ,
        # 客户管理（只读）
        Permission.CUSTOMER_READ,
        # 财务
        Permission.FINANCE_READ,
        Permission.FINANCE_REPORT,
    ],
    
    Role.VIEWER: [
        # 所有只读权限
        Permission.BOOKING_READ,
        Permission.ROOM_READ,
        Permission.CUSTOMER_READ,
    ],
}

# 权限检查装饰器
def require_permission(permission: Permission):
    """检查用户是否拥有指定权限。"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要权限: {permission.value}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 使用示例
@app.post("/api/bookings")
@require_permission(Permission.BOOKING_CREATE)
async def create_booking(
    booking_data: CreateBookingRequest,
    current_user: User = Depends(get_current_user)
):
    """创建预订（需要 booking:create 权限）。"""
    booking = await booking_service.create(booking_data, created_by=current_user.id)
    return booking

@app.get("/api/finance/report")
@require_permission(Permission.FINANCE_REPORT)
async def get_finance_report(
    start_date: date,
    end_date: date,
    current_user: User = Depends(get_current_user)
):
    """获取财务报表（需要 finance:report 权限）。"""
    report = await finance_service.generate_report(start_date, end_date)
    return report
```

---

## 常见漏洞检查

### OWASP Top 10 检查清单

| 排名 | 漏洞类型 | 检查点 | 防护措施 |
|------|----------|--------|----------|
| A01 | 失效的访问控制 | 权限检查、IDOR漏洞 | RBAC、资源级授权 |
| A02 | 加密失败 | 敏感数据存储、传输 | HTTPS、AES加密 |
| A03 | 注入攻击 | SQL注入、命令注入 | 参数化查询、输入验证 |
| A04 | 不安全设计 | 业务逻辑漏洞 | 安全设计评审 |
| A05 | 安全配置错误 | 默认配置、错误信息 | 安全配置基线 |
| A06 | 易受攻击的组件 | 依赖组件漏洞 | 依赖扫描、及时更新 |
| A07 | 身份识别失败 | 弱密码、会话管理 | 强密码策略、MFA |
| A08 | 软件和数据完整性 | 供应链攻击 | 签名验证、依赖锁定 |
| A09 | 安全日志和监控 | 日志缺失、监控不足 | 完整日志、实时监控 |
| A10 | 服务端请求伪造 | SSRF漏洞 | URL白名单、内网限制 |

---

## 安全测试工具推荐

### SAST（静态应用安全测试）

| 工具 | 语言 | 用途 | 集成方式 |
|------|------|------|----------|
| Bandit | Python | 安全漏洞扫描 | CI/CD |
| Semgrep | 多语言 | 自定义规则扫描 | CI/CD |
| SonarQube | 多语言 | 代码质量和安全 | 独立服务 |
| CodeQL | 多语言 | GitHub原生安全扫描 | GitHub Actions |
