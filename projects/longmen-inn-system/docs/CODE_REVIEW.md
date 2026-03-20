// ❌ 不良示例：重复计算、内联函数定义
function RoomList({ rooms, filters, onSelect }) {
  const filtered = rooms.filter(room => {
    if (filters.minPrice && room.price < filters.minPrice) return false;
    if (filters.maxPrice && room.price > filters.maxPrice) return false;
    return true;
  });

  return (
    <div>
      {filtered.map(room => (
        <div key={room.id} onClick={() => onSelect(room.id)}>
          {room.name}
        </div>
      ))}
    </div>
  );
}
```

---

## 安全审查要点

### 1. 输入验证

- [ ] **边界检查**：所有输入都进行长度、范围、格式验证
- [ ] **类型转换**：使用安全的类型转换函数
- [ ] **白名单**：使用白名单而非黑名单进行验证
- [ ] **SQL注入**：使用参数化查询，禁止字符串拼接SQL

```python
# ✅ 良好示例
from pydantic import BaseModel, Field, validator

class CreateBookingRequest(BaseModel):
    room_id: str = Field(..., min_length=1, max_length=50)
    customer_name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., regex=r'^[1-9]\d{10}$')  # 手机号格式
    check_in: str
    check_out: str
    
    @validator('check_out')
    def check_out_after_check_in(cls, v, values):
        if 'check_in' in values and v <= values['check_in']:
            raise ValueError('退房日期必须晚于入住日期')
        return v

# 使用
@app.post("/api/bookings")
async def create_booking(request: CreateBookingRequest):
    # request 已经过验证
    booking = await booking_service.create(request)
    return booking

# ✅ SQL参数化查询
@app.get("/api/rooms/{room_id}")
async def get_room(room_id: str):
    # 参数化查询，防止SQL注入
    result = await db.fetch_one(
        "SELECT * FROM rooms WHERE id = :room_id",
        {"room_id": room_id}
    )
    if not result:
        raise HTTPException(status_code=404, detail="房间不存在")
    return result

# ❌ 不良示例：字符串拼接SQL（危险！）
@app.get("/api/rooms/search")
async def search_rooms(room_type: str):
    # SQL注入漏洞！
    query = f"SELECT * FROM rooms WHERE type = '{room_type}'"
    return await db.fetch_all(query)
```

### 2. 认证与授权

- [ ] **身份验证**：敏感操作需要身份验证
- [ ] **权限检查**：操作前检查用户权限
- [ ] **令牌安全**：JWT令牌设置合理的过期时间
- [ ] **密码安全**：密码使用bcrypt等安全算法存储

```python
# ✅ 良好示例
from functools import wraps
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """获取当前登录用户。"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="无效的令牌")
        
        user = await get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="无效的令牌")

def require_permission(permission: str):
    """权限检查装饰器。"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if not current_user.has_permission(permission):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"需要权限: {permission}"
                )
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# 使用示例
@app.post("/api/admin/rooms")
@require_permission("rooms:create")
async def create_room(
    room_data: RoomCreateRequest,
    current_user: User = Depends(get_current_user)
):
    """创建房间（需要 rooms:create 权限）。"""
    room = await room_service.create(room_data, created_by=current_user.id)
    return room
```

### 3. 敏感信息保护

- [ ] **密钥管理**：密钥不硬编码，使用环境变量或密钥管理服务
- [ ] **日志脱敏**：日志中不记录敏感信息（密码、身份证号等）
- [ ] **响应过滤**：API响应中不返回敏感字段
- [ ] **HTTPS**：所有通信使用HTTPS

```python
# ✅ 良好示例
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """应用配置，从环境变量读取。"""
    database_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# 脱敏日志
def log_user_action(user_id: str, action: str, details: dict):
    """记录用户操作日志，自动脱敏敏感字段。"""
    SENSITIVE_FIELDS = {'password', 'token', 'credit_card', 'id_card', 'phone'}
    
    sanitized_details = {
        k: '***' if k in SENSITIVE_FIELDS else v
        for k, v in details.items()
    }
    
    logger.info(f"User {user_id} {action}: {sanitized_details}")

# API响应模型，排除敏感字段
from pydantic import BaseModel, Field

class UserResponse(BaseModel):
    """用户API响应模型（不包含敏感信息）。"""
    id: str
    username: str
    email: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class UserInDB(UserResponse):
    """数据库用户模型（包含密码哈希，不用于API响应）。"""
    hashed_password: str
```

---

## 性能审查要点

### 1. Python后端性能

- [ ] **数据库查询**：使用索引，避免N+1查询问题
- [ ] **缓存使用**：频繁访问的数据使用缓存
- [ ] **异步处理**：IO密集型操作使用异步
- [ ] **资源释放**：及时关闭数据库连接、文件句柄

```python
# ✅ 良好示例：避免N+1查询
from sqlalchemy.orm import selectinload

# 一次性加载关联数据
@app.get("/api/bookings/with-details")
async def get_bookings_with_details():
    """获取预订列表（包含关联的客户和房间信息）。"""
    async with db.session() as session:
        result = await session.execute(
            select(Booking)
            .options(
                selectinload(Booking.customer),
                selectinload(Booking.room)
            )
            .limit(100)
        )
        bookings = result.scalars().all()
        return [booking.to_dict() for booking in bookings]

# ❌ 不良示例：N+1查询问题
@app.get("/api/bookings/slow")
async def get_bookings_slow():
    """获取预订列表（会产生N+1查询）。"""
    bookings = await db.fetch_all("SELECT * FROM bookings LIMIT 100")
    
    # 对每个预订都查询关联数据！N+1查询问题
    for booking in bookings:
        customer = await db.fetch_one(
            "SELECT * FROM customers WHERE id = ?", 
            booking.customer_id
        )
        room = await db.fetch_one(
            "SELECT * FROM rooms WHERE id = ?", 
            booking.room_id
        )
        booking.customer = customer
        booking.room = room
    
    return bookings

# ✅ 缓存示例
from functools import lru_cache
import aiocache

# 使用Redis缓存
room_cache = aiocache.Cache(aiocache.RedisCache, endpoint="localhost", port=6379)

@app.get("/api/rooms/{room_id}")
async def get_room(room_id: str):
    """获取房间信息（带缓存）。"""
    # 尝试从缓存获取
    cached = await room_cache.get(f"room:{room_id}")
    if cached:
        return cached
    
    # 从数据库获取
    room = await room_service.get_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="房间不存在")
    
    # 写入缓存（5分钟过期）
    await room_cache.set(f"room:{room_id}", room, ttl=300)
    
    return room
```

### 2. React前端性能

- [ ] **组件拆分**：合理拆分组件，避免过度渲染
- [ ] **Memoization**：使用React.memo、useMemo、useCallback
- [ ] **列表优化**：大列表使用虚拟滚动
- [ ] **图片优化**：使用懒加载、适当压缩图片
- [ ] **代码分割**：路由和组件使用懒加载

```typescript
// ✅ 良好示例：性能优化
import React, { memo, useMemo, useCallback, Suspense, lazy } from 'react';

// 懒加载大组件
const BookingChart = lazy(() => import('./BookingChart'));
const RoomMap = lazy(() => import('./RoomMap'));

// 使用memo避免不必要的重渲染
const RoomCard = memo(function RoomCard({
  room,
  isSelected,
  onSelect
}: {
  room: Room;
  isSelected: boolean;
  onSelect: (roomId: string) => void;
}) {
  const handleClick = useCallback(() => {
    onSelect(room.id);
  }, [room.id, onSelect]);

  return (
    <div 
      className={`room-card ${isSelected ? 'selected' : ''}`}
      onClick={handleClick}
    >
      <img src={room.imageUrl} alt={room.name} loading="lazy" />
      <h4>{room.name}</h4>
      <p>¥{room.price}/晚</p>
    </div>
  );
});

// 主组件
export default function RoomSelector({ rooms }: { rooms: Room[] }) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string>('all');

  // 使用useMemo缓存筛选结果
  const filteredRooms = useMemo(() => {
    if (filterType === 'all') return rooms;
    return rooms.filter(room => room.type === filterType);
  }, [rooms, filterType]);

  // 使用useCallback缓存回调函数
  const handleSelect = useCallback((roomId: string) => {
    setSelectedId(roomId);
  }, []);

  return (
    <div className="room-selector">
      <div className="filters">
        <select value={filterType} onChange={e => setFilterType(e.target.value)}>
          <option value="all">全部</option>
          <option value="standard">标准间</option>
          <option value="deluxe">豪华间</option>
          <option value="suite">套房</option>
        </select>
      </div>
      
      <div className="room-grid">
        {filteredRooms.map(room => (
          <RoomCard
            key={room.id}
            room={room}
            isSelected={room.id === selectedId}
            onSelect={handleSelect}
          />
        ))}
      </div>

      {/* 懒加载大型组件 */}
      <Suspense fallback={<div>加载中...</div>}>
        {selectedId && <RoomMap roomId={selectedId} />}
      </Suspense>
    </div>
  );
}

// ❌ 不良示例：性能问题
function RoomList({ rooms }) {
  const [filter, setFilter] = useState('');
  
  // 每次渲染都重新计算
  const filtered = rooms.filter(r => r.type.includes(filter));
  
  // 每次渲染都创建新函数
  const handleSelect = (id) => {
    console.log('Selected:', id);
  };
  
  return (
    <div>
      {filtered.map(room => (
        // 子组件每次都会重新渲染
        <RoomCard room={room} onSelect={handleSelect} />
      ))}
    </div>
  );
}
```

---

## 代码风格检查

### 1. Python代码风格

**使用工具链**：`black` + `isort` + `flake8` + `mypy`

```bash
# 格式化代码
black backend/

# 整理导入
isort backend/

# 代码风格检查
flake8 backend/

# 类型检查
mypy backend/
```

**关键规则**：

| 规则 | 说明 | 示例 |
|------|------|------|
| 行长度 | 最大88字符 | `black`默认 |
| 引号 | 双引号优先 | `"hello"` |
| 空行 | 类2行，函数1行 | PEP 8 |
| 导入 | 按stdlib、third-party、local分组 | `isort` |

### 2. TypeScript/React代码风格

**使用工具链**：`ESLint` + `Prettier` + `TypeScript`

```bash
# 检查代码
eslint src/

# 格式化
prettier --write src/

# 类型检查
tsc --noEmit
```

**关键规则**：

| 规则 | 说明 |
|------|------|
| 缩进 | 2空格 |
| 引号 | 单引号 |
| 分号 | 不使用 |
| 行长度 | 100字符 |

---

## 审查流程和记录模板

### 审查流程图

```
┌─────────────────┐
│   提交PR        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  自动化检查      │ ◄── CI运行测试、代码风格检查
│  (CI Pipeline)  │
└────────┬────────┘
         │
    ┌────┴────┐
    │ 通过?   │
    └────┬────┘
       │     │
      否     是
       │     │
       ▼     ▼
┌──────────┐  ┌─────────────────┐
│  修复问题  │  │  人工代码审查   │ ◄── 至少1人审查
│  重新提交  │  └────────┬────────┘
└──────────┘           │
                       ▼
              ┌─────────────────┐
              │   审查通过?     │
              └────────┬────────┘
                 │     │
                否     是
                 │     │
                 ▼     ▼
        ┌──────────┐  ┌─────────────────┐
        │ 修复反馈  │  │   合并到主干    │
        │ 重新审查  │  │   部署测试环境  │
        └──────────┘  └─────────────────┘
```

### 审查检查清单模板

**提交前自查清单**（提交者填写）：

```markdown
## PR自查清单

- [ ] 代码已通过本地测试
- [ ] 新增功能有对应的单元测试
- [ ] 代码风格检查通过 (black/isort/flake8 或 eslint/prettier)
- [ ] 类型检查通过 (mypy 或 tsc)
- [ ] 文档已更新（如果有API变更）
- [ ] 无敏感信息提交（密码、密钥等）

### PR描述
- 变更内容：
- 相关Issue：
- 测试方式：
```

**审查者检查清单**（审查者填写）：

```markdown
## 代码审查清单

### 基础检查
- [ ] 代码逻辑清晰，易于理解
- [ ] 命名规范，见名知意
- [ ] 没有明显的代码重复
- [ ] 错误处理完善

### 安全审查
- [ ] 输入验证