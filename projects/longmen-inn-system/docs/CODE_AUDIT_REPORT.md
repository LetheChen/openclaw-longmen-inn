# 龙门客栈系统代码审查报告

> **版本**：v1.0.0-audit-001  
> **审查日期**：2026-03-31  
> **审查人**：账房先生（铁算盘老方）  
> **审查范围**：backend/app（Python/FastAPI） + frontend/src（React/TypeScript）

---

## 一、总评

| 维度 | 评分 | 说明 |
|------|------|------|
| **代码质量** | 72/100 | 整体结构清晰，文档完善，但存在大量重复代码和未完成功能 |
| **安全性** | 58/100 | 高危问题多，安全中间件全部禁用，多个端点缺少认证 |
| **规范遵守** | 70/100 | 有文档和类型标注，但部分规范（认证、错误处理）未落实 |
| **潜在Bug** | 65/100 | 硬编码时间戳、路径遍历风险、依赖注入不规范等问题存在 |
| **综合评分** | **64/100** | 项目整体处于"能跑但不够安全"的开发阶段 |

---

## 二、高危问题（High Severity）

### 🔴 H-01：安全中间件全部被禁用

**文件**：`backend/app/main.py`（第89-92行）

```python
# 安全中间件（暂时全部禁用，待修复）
# app.add_middleware(ErrorHandlerMiddleware)
# app.add_middleware(ValidationMiddleware)
# app.add_middleware(RateLimitMiddleware)
```

**风险**：
- `ErrorHandlerMiddleware` 被禁用意味着全局异常未统一处理，500错误直接暴露Python堆栈
- `ValidationMiddleware` 被禁用意味着请求参数校验完全依赖各端点自己处理
- `RateLimitMiddleware` 被禁用意味着接口完全无速率限制，容易遭受DDoS

**修复建议**：
- 立即启用 `ErrorHandlerMiddleware`，生产环境返回脱敏错误
- 启用 `RateLimitMiddleware`，对公开接口限流
- 评估 `ValidationMiddleware` 的必要性，若启用需全面测试

---

### 🔴 H-02：多个核心API端点完全无认证保护

**文件**：`backend/app/api/v1/endpoints/tasks.py`

```python
# get_tasks - 第15行：无需任何认证
@router.get("/")
async def get_tasks(
    db: Session = Depends(get_db),
    ...
):
```

**受影响端点**：

| 端点 | 文件 | 风险 |
|------|------|------|
| `GET /api/v1/tasks/` | tasks.py:15 | 无认证查看所有任务 |
| `POST /api/v1/tasks/` | tasks.py:129 | **无认证创建任务** |
| `GET /api/v1/tasks/{id}` | tasks.py:165 | 无认证查看任务详情 |
| `PUT /api/v1/tasks/{id}` | tasks.py:193 | **无认证修改任务** |
| `DELETE /api/v1/tasks/{id}` | tasks.py:254 | **无认证删除任务** |
| `GET /api/v1/projects/` | projects.py:17 | 无认证查看所有项目 |
| `POST /api/v1/projects/` | projects.py:92 | **无认证创建项目** |
| `GET /api/v1/agents/` | agents.py:18 | 无认证查看所有Agent |
| `POST /api/v1/agents/` | agents.py:183 | **无认证创建Agent** |
| `DELETE /api/v1/agents/{id}` | agents.py:233 | **无认证删除Agent** |
| `POST /api/v1/longmenling/` | longmenling.py:23 | **无认证发放积分** |
| `GET /api/v1/audit-logs` | audit_log.py (routers/) | 无认证查看审计日志 |

**修复建议**：
- 所有涉及数据修改的端点（POST/PUT/DELETE/PATCH）必须要求 `Depends(get_current_user_required)`
- 敏感数据读取端点至少要求 `Depends(get_current_user)` 或更高权限
- 建议在 API router 层统一加认证守卫，而不是逐端点添加

---

### 🔴 H-03：内存速率限制器可被轻易绕过

**文件**：`backend/app/main.py`（第47-75行）

```python
class RateLimiter:
    def is_allowed(self, client_id: str) -> Tuple[bool, int]:
        # 获取客户端标识（IP 或用户ID）
        client_id = request.client.host if request.client else "unknown"
```

**风险**：
1. `request.client.host` 可被 HTTP 头 `X-Forwarded-For` 或 `X-Real-IP` 伪造
2. 内存存储，重启即失效，多实例无法共享
3. 每分钟1000次限制过高，形同虚设

**修复建议**：
- 接入 Redis 实现分布式限流
- 使用可靠的IP获取方式（优先从 `X-Real-IP` 但需配置信任代理）
- 降低限制阈值至合理值（如每分钟60次）

---

### 🔴 H-04：开发环境默认密钥硬编码

**文件**：`backend/app/core/config.py`（第18行）

```python
_DEV_SECRET_KEY = "dev-secret-key-DO-NOT-USE-IN-PRODUCTION"
```

**文件**：`backend/app/core/config.py`（第65-79行）

```python
# 开发环境：允许使用默认开发密钥
if environment == "development":
    warnings.warn(...)
    return _DEV_SECRET_KEY  # ← 直接使用弱密钥
```

**风险**：
- 即使设置了 `ENVIRONMENT=production`，若未设置 `SECRET_KEY` 环境变量，staging 分支仍会使用弱密钥
- 攻击者可利用此密钥伪造任意用户的 JWT token

**修复建议**：
- 生产环境检测到未设置 `SECRET_KEY` 时应直接拒绝启动，而不是降级使用弱密钥
- 将 `_DEV_SECRET_KEY` 改为仅在 `ENVIRONMENT=development` 时使用
- 建议增加启动时强制检测：`if settings.is_production and settings.SECRET_KEY == _DEV_SECRET_KEY: raise RuntimeError(...)`

---

### 🔴 H-05：文件读取接口存在路径遍历风险

**文件**：`backend/app/api/v1/endpoints/files.py`（第101-105行）

```python
@router.get("/role/{agent_id}/file")
async def get_agent_role_file(agent_id: str, file_path: str = "IDENTITY.md"):
    ...
    if not str(file_full_path.resolve()).startswith(str(role_dir.resolve())):
        raise HTTPException(status_code=403, detail="无权访问此文件")
```

**风险**：
- 路径遍历检查 `startswith` 逻辑理论上可被符号链接（symlink）绕过
- `file_path` 参数用户可控，若处理不当可读取任意文件

**修复建议**：
- 使用 `Path.resolve()` 并对比规范化后的绝对路径
- 限制只能读取 `.md` 和 `.json` 文件（已在代码中部分实现）
- 考虑使用沙盒目录或 chroot 环境隔离

---

### 🔴 H-06：前端登录页硬编码暴露开发测试账号

**文件**：`frontend/src/pages/Login.tsx`（第119-122行）

```tsx
{import.meta.env.DEV && (
  <div className="dev-hint">
    <Text code>admin / Admin@123456</Text>
  </div>
)}
```

**风险**：
- 虽是 DEV 模式保护，但开发者可能误将 DEBUG 代码打包进生产
- 代码仓库若泄露，攻击者立即获得管理员账号

**修复建议**：
- 删除前端代码中的硬编码凭证提示
- 默认账户信息仅通过安全渠道（内部wiki）传达
- 可保留"开发环境提示"但不显示具体密码

---

### 🔴 H-07：refresh_token 不验证旧 token 即销毁（登出逻辑缺陷）

**文件**：`backend/app/api/v1/endpoints/auth.py`（第207-213行）

```python
@router.post("/logout")
async def logout(...):
    # 从Cookie获取refresh_token并撤销
    refresh_token_value = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if refresh_token_value:
        revoke_refresh_token(refresh_token_value, db)  # ← 只撤销了refresh_token
    # 清除所有Cookie
    clear_auth_cookies(response)
    # access_token 未被撤销！
```

**风险**：
- 攻击者拿到 valid 的 access_token（有效期24小时）后，即使受害者"登出"，攻击者仍可在24小时内以受害者身份操作
- Refresh token 被撤销但 access token 未被加入黑名单

**修复建议**：
- 引入 token 黑名单机制（如 Redis 存储已撤销的 access_token jti）
- 或者在 `logout` 时通过 `revoke_all_user_tokens` 撤销所有相关 refresh_tokens
- 参考方案：短期 access_token + 检查 Redis 黑名单

---

### 🔴 H-08：数据库会话依赖注入不规范，造成连接泄漏

**文件**：`backend/app/core/security.py`（第73、92行）

```python
async def get_current_user(..., db: Session = Depends(lambda: SessionLocal())):
    ...
    user = db.query(User).filter(User.id == user_id).first()
    return user  # ← 函数结束后 db 未关闭！
```

**受影响文件**：
- `backend/app/core/security.py` — `get_current_user` 和 `get_current_user_required`
- `backend/app/api/deps.py` — `get_current_user` 和 `get_current_user_required`

**问题**：
- 正确的 `get_db` 使用 `yield` 模式确保会话关闭
- 这里的 `db: Session = Depends(lambda: SessionLocal())` 不会触发 `finally: db.close()`
- 高并发场景下可能导致数据库连接耗尽

**修复建议**：
- 统一使用 `from app.api.deps import get_db` 作为依赖注入
- 不要在依赖项外自行实例化 `SessionLocal()`

---

## 三、中危问题（Medium Severity）

### 🟠 M-01：backend/.env 文件未被 .gitignore 忽略

**文件**：`backend/.env`

**风险**：
- `.env` 文件通常包含 `SECRET_KEY`、`DATABASE_URL` 等敏感信息
- 若提交到版本控制，攻击者可获取生产配置

**修复建议**：
- 立即从 git 历史中移除 `.env` 文件
- 在项目根目录和 backend 目录的 `.gitignore` 中添加 `*.env`（排除 `.env.example`）
- `.env` 应该是本地手动创建，不从版本库复制

---

### 🟠 M-02：Agent 管理端点完全无权限控制

**文件**：`backend/app/api/v1/endpoints/agents.py`

```python
@router.post("/")  # 无认证
async def create_agent(...)

@router.delete("/{agent_id}")  # 无认证
async def delete_agent(...)
```

**风险**：
- 任何人可以创建、修改、删除 Agent 记录
- 可能被用来伪造 Agent 数据以操纵积分排行榜

**修复建议**：
- 所有 Agent 管理端点要求 `Depends(get_admin_user)` 或 `Depends(get_current_user_required)`
- 创建/删除操作应记录审计日志

---

### 🟠 M-03：OpenClaw API Key 明文存储

**文件**：`backend/app/api/v1/endpoints/openclaw.py`（第122-148行）

```python
def _save_config(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ...)
```

**风险**：
- `OPENCLAW_API_KEY` 以明文形式写入 `~/.openclaw/workspace/.longmen_inn/openclaw_config.json`
- 文件权限若配置不当，本地其他用户可读取

**修复建议**：
- API Key 存储使用系统密钥加密（如 `python-keyring` 或 AWS Secrets Manager）
- 或仅从环境变量读取，不提供写入配置文件功能

---

### 🟠 M-04：审计日志端点无认证且记录到文件无加密

**文件**：`backend/app/routers/audit_log.py` + `audit_log.jsonl`

```python
AUDIT_LOG_PATH = os.path.expanduser("~/.openclaw/workspace/.longmen_inn/audit_log.jsonl")
```

**风险**：
- 审计日志记录用户操作，但 `/api/v1/audit-logs` 端点无认证
- 任何人可读取所有操作记录
- JSONL 文件明文存储，可被篡改

**修复建议**：
- 审计日志端点要求 `Depends(get_current_user_required)`
- 考虑使用 append-only 日志存储（如数据库表），防止文件被篡改

---

### 🟠 M-05：`health` 端点返回硬编码时间戳

**文件**：`backend/app/main.py`（第123-127行）

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2026-03-14T12:00:00Z"  # ← 硬编码！
    }
```

**风险**：
- 健康检查无法反映真实服务状态
- 监控告警系统基于此时间戳会误判

**修复建议**：
- 使用 `datetime.utcnow().isoformat()` 返回真实时间
- 增加数据库连接、Redis 等关键依赖的健康检查

---

### 🟠 M-06：前端 API 服务层直接暴露 `import.meta.env`

**文件**：`frontend/src/services/api.ts`

```typescript
const api: AxiosInstance = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_BASE_URL || '/api/v1',
});
```

**风险**：
- 使用 `(import.meta as any).env` 绕过 TypeScript 类型检查
- `VITE_` 前缀变量若配置不当可注入恶意值

**修复建议**：
- 定义正确的环境变量类型接口
- baseURL 应该有明确的类型和默认值校验

---

### 🟠 M-07：CSRF Token 验证接口未强制要求 Token

**文件**：`backend/app/api/v1/endpoints/auth.py`（第320-335行）

```python
@router.get("/csrf-token")
async def get_csrf_token(request: Request):
    csrf_token = request.cookies.get(CSRF_TOKEN_COOKIE_NAME)
    if not csrf_token:
        csrf_token = generate_csrf_token()  # ← 未设置到Cookie！
    return {"csrf_token": csrf_token}
```

**风险**：
- `generate_csrf_token()` 返回新 token 但未通过 `set_cookie` 写入响应
- 前端拿到的 token 与 Cookie 中的不一致，验证必然失败

**修复建议**：
- 若要实现 Double Submit Cookie 模式，应在返回 Response 对象时同时 set_cookie
- 或者改为纯 Cookie 模式（前端不读 token，只通过 Cookie 自动发送）

---

### 🟠 M-08：WebSocket 端点 Token 参数未验证

**文件**：`backend/app/websocket/handler.py`（第26行）

```python
@websocket_router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    token: Optional[str] = Query(None),  # ← 接收但未验证！
    groups: Optional[str] = Query(None)
):
```

**风险**：
- WebSocket 连接可被任意客户端建立
- `token` 参数被接收但未做任何校验

**修复建议**：
- 实现 WebSocket 握手时的 token 验证（参考 FastAPI WebSocket 认证最佳实践）
- 未验证前不向客户端发送任何业务数据

---

### 🟠 M-09：模块级循环依赖风险

**文件**：`backend/app/core/security.py` ↔ `backend/app/api/deps.py`

```
core/security.py imports app.db.base.SessionLocal
  → api/deps.py imports app.core.security.verify_token
    → 又 imports get_db from app.db.base (via SessionLocal)
```

**问题**：
- `security.py` 顶层的 `get_db` 依赖使用 `lambda: SessionLocal()` 而非 `Depends(get_db)`
- 两个文件互相 import，可能导致加载顺序问题

**修复建议**：
- 在 `api/deps.py` 中统一管理所有依赖注入
- `core/security.py` 中的认证函数应接收 `db` 作为参数而非依赖注入

---

### 🟠 M-10：跨域配置默认值在生产环境不当

**文件**：`backend/app/core/config.py`（第35行）

```python
CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8080"]
```

**风险**：
- 若生产环境未显式设置 `CORS_ORIGINS` 环境变量，会默认允许所有 localhost 端口
- 结合 `allow_credentials=True`，可能导致凭证泄露

**修复建议**：
- 生产环境必须有明确的 CORS_ORIGINS 配置
- 建议在 `validate_secret_key` 类似逻辑中强制检查 CORS_ORIGINS 配置

---

## 四、低危问题（Low Severity）

### 🟡 L-01：health 端点无鉴权可被探测

**文件**：`backend/app/main.py`（第121行）

**说明**：健康检查端点未认证，但这属于正常设计（给负载均衡器探测用），仅作记录。

---

### 🟡 L-02：代码中存在 TODO 注释未完成

**文件**：`backend/app/api/v1/endpoints/tasks.py`（第280行）

```python
operator_agent_id=None,  # TODO: 从当前用户获取
```

**说明**：任务状态变更日志的操作人 ID 为 None，未关联到真实用户。

---

### 🟡 L-03：登录表单 `min=8` 密码校验与后端 bcrypt 强度不匹配

**文件**：`frontend/src/pages/Login.tsx`（第90行）

```tsx
{ min: 8, message: '密码至少8个字符' }
```

**说明**：前端要求8位，后端 bcrypt 无此限制（可接受任意长度）。不一致可能导致用户困惑。

---

### 🟡 L-04：部分 Python 文件存在 `__pycache__` 和 `.pyc` 文件

**说明**：已构建的文件不应提交到版本库。虽然这是常见问题，但建议确认 `.gitignore` 配置正确。

---

### 🟡 L-05：Dashboard 页面导入了未使用的图标

**文件**：`frontend/src/pages/Dashboard.tsx`（第1-17行）

```tsx
import { ..., CoffeeOutlined, BookOutlined, EditOutlined, ... } from '@ant-design/icons'
```

**说明**：存在死代码，建议清理。

---

### 🟡 L-06：`get_my_tasks` 端点未实现用户绑定过滤

**文件**：`backend/app/api/v1/endpoints/tasks.py`（第110-127行）

```python
@router.get("/my")
async def get_my_tasks(...):
    """获取我的任务（未实现认证时返回所有任务）"""
    query = db.query(models.Task)
    ...
```

**说明**：注释已承认"未实现"，该端点实际返回所有任务而非当前用户任务。

---

### 🟡 L-07：项目 README.md 中暴露了开发环境默认账户信息

**文件**：`backend/README.md`（推测）

**说明**：文档不应包含生产或共享账户的明文凭据，应仅描述如何初始化账户。

---

### 🟡 L-08：SQLite 数据库文件存储在项目目录

**文件**：`backend/longmen_inn.db`

**风险**：
- 数据库文件与代码混在一起，不便于部署和备份
- 若误提交到 git 造成数据泄露

**修复建议**：
- 数据库文件放在项目外的独立目录
- 加入 `.gitignore`

---

## 五、整体改进建议

### 5.1 安全优先（最高优先级）

1. **立即启用安全中间件**：ErrorHandler、RateLimit 必须立即启用
2. **强制认证策略**：所有修改型 API 必须携带有效 JWT（除 `/auth/login`）
3. **密钥管理**：生产环境禁用默认密钥，启动时强制检测
4. **依赖注入规范化**：统一使用 `app/api/deps.py` 中的依赖，禁止直接实例化 `SessionLocal()`
5. **Token 撤销机制**：引入 Redis 黑名单，支持 access_token 的即时撤销

### 5.2 代码质量提升

1. **消除重复代码**：`core/security.py` 和 `api/deps.py` 中的认证逻辑高度重复，应合并为一个统一模块
2. **完善类型标注**：前端部分文件仍使用 `any`，应加强 TypeScript 类型安全
3. **清理 TODO**：代码中 TODO 注释应转化为 GitHub Issue 或立即实现
4. **统一错误处理**：所有端点应统一返回标准错误格式

### 5.3 测试覆盖

1. **增加认证相关单元测试**：JWT 生成/验证、token 刷新、登出等场景
2. **API 权限测试**：验证各角色对端点的访问控制
3. **前端组件测试**：关键页面（Login、Dashboard）的行为测试
4. **集成测试**：使用 `TestClient` 对 FastAPI 端点进行集成测试

### 5.4 配置与环境

1. **敏感文件隔离**：`.env` 文件彻底从版本控制排除
2. **数据库配置外置**：生产数据库连接信息不得写在代码或配置文件中
3. **日志规范化**：统一日志格式，增加请求ID追踪

### 5.5 架构优化

1. **Redis 集成**：速率限制、Token 黑名单、缓存等场景急需 Redis
2. **任务队列**：后台同步任务（openclaw_sync_service）应使用 Celery 或类似工具
3. **API 版本管理**：当前 v1 无版本隔离，建议平滑升级路径

---

## 六、问题汇总

| 编号 | 严重度 | 类别 | 位置 | 问题名称 |
|------|--------|------|------|----------|
| H-01 | 🔴高 | 安全 | main.py:89-92 | 安全中间件全部禁用 |
| H-02 | 🔴高 | 认证 | tasks.py等多文件 | 多个核心端点无认证 |
| H-03 | 🔴高 | 安全 | main.py:47-75 | 速率限制可被绕过 |
| H-04 | 🔴高 | 安全 | config.py:18,65-79 | 开发环境默认弱密钥 |
| H-05 | 🔴高 | 安全 | files.py:101-105 | 路径遍历风险 |
| H-06 | 🔴高 | 安全 | Login.tsx:119-122 | 前端硬编码测试账号 |
| H-07 | 🔴高 | 安全 | auth.py:207-213 | 登出后access_token未撤销 |
| H-08 | 🔴高 | 规范 | security.py:73,92 | 数据库会话未关闭 |
| M-01 | 🟠中 | 安全 | backend/.env | .env未加入gitignore |
| M-02 | 🟠中 | 认证 | agents.py | Agent端点无权限控制 |
| M-03 | 🟠中 | 安全 | openclaw.py:122 | API Key明文存储 |
| M-04 | 🟠中 | 安全 | audit_log.py | 审计日志无认证 |
| M-05 | 🟠中 | Bug | main.py:123 | health端点硬编码时间戳 |
| M-06 | 🟠中 | 规范 | api.ts | 环境变量类型不安全 |
| M-07 | 🟠中 | 安全 | auth.py:320 | CSRF token未写入Cookie |
| M-08 | 🟠中 | 认证 | handler.py:26 | WebSocket token未验证 |
| M-09 | 🟠中 | 规范 | security.py↔deps.py | 模块循环依赖 |
| M-10 | 🟠中 | 安全 | config.py:35 | CORS默认值生产不安全 |
| L-01 | 🟡低 | 规范 | main.py:121 | health端点说明（正常设计） |
| L-02 | 🟡低 | 规范 | tasks.py:280 | TODO未完成 |
| L-03 | 🟡低 | 规范 | Login.tsx:90 | 密码校验前后端不一致 |
| L-04 | 🟡低 | 规范 | backend/ | pycache文件 |
| L-05 | 🟡低 | 规范 | Dashboard.tsx | 未使用导入 |
| L-06 | 🟡低 | Bug | tasks.py:110 | get_my_tasks未实现 |
| L-07 | 🟡低 | 安全 | README.md | 文档暴露凭据 |
| L-08 | 🟡低 | 规范 | backend/ | SQLite数据库文件位置 |

**总计**：高危 8 项 · 中危 10 项 · 低危 8 项

---

*账房先生（铁算盘老方）审查完毕 · 2026-03-31*
