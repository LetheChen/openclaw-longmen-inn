# 龙门客栈系统 - 代码审查报告 v2

**审查日期**：丙午年二月十二（2026-03-31）
**审查者**：账房先生
**本次审查范围**：今日改动（上午安全修复 + 晚间数据架构重构）
**基础评分**：82.5/100（上轮）→ 本轮目标：守住安全成果，修复架构问题

---

## 一、改动总览

### 上午：安全审计修复（9:13 - 9:24）

| 文件 | 改动内容 | 风险等级 |
|------|----------|----------|
| `main.py` | 启用安全中间件、速率限制60次/分钟、IP检测改进 | 🔴 高 |
| `tasks.py` | 全端点加认证、修复operator_agent_id | 🔴 高 |
| `projects.py` | 全端点加认证 | 🔴 高 |
| `agents.py` | 全端点加认证 | 🔴 高 |
| `longmenling.py` | 全端点加认证 | 🔴 高 |
| `audit_log.py` | 全端点加认证 | 🟠 中 |
| `security.py` | JTI黑名单、DB Session泄漏修复 | 🔴 高 |
| `auth.py` | logout撤销token、CSRF 修复 | 🔴 高 |
| `handler.py` | WebSocket token验证 | 🟠 中 |
| `config.py` | 生产拒绝弱密钥、CORS验证 | 🟠 中 |
| `openclaw.py` | API Key加密存储 | 🟠 中 |
| `files.py` | 路径遍历防护 | 🔴 高 |
| `validation.py` | body读取导致POST hang（回归bug）| 🔴 高 |

### 晚间：数据架构重构（21:26 - 21:32）

| 文件 | 改动内容 | 风险等级 |
|------|----------|----------|
| `app/cli/__init__.py` | 新建 inn CLI 工具 | 🟢 低 |
| `app/cli/__main__.py` | 新建 CLI 入口 | 🟢 低 |
| `app/cli/ledger_generator.py` | 新建 DB→LEDGER.md 导出器 | 🟡 低 |
| `files.py` | POST /files/ledger 改为 DB→MD 单向 | 🟡 低 |
| `init_db.py` | 移除启动时 LEDGER.md→DB 同步 | 🟢 低 |
| `Login.tsx` | 移除硬编码密码提示 | 🟡 低 |
| `Dashboard.tsx` | 清理未用图标导入 | 🟢 低 |
| `api.ts` | 修复类型安全 | 🟢 低 |
| `.gitignore` | 明确排除 backend/.env | 🟢 低 |

---

## 二、本轮新发现问题

### 🔴 L-01：Markdown Table Injection（LEDGER.md 生成器）

**文件**：`app/cli/ledger_generator.py`

**问题**：任务标题/描述中包含 `|` 字符会破坏 markdown 表格结构，导致账本渲染错乱。

```python
# 当前代码（有问题）
lines.append(f"| {task_no} | {title} | **{status_str}** | ...")
```

如果任务标题为 `"修复 | 重要bug"`，输出变为 6 列而非 5 列，表格错位。

**影响**：LEDGER.md 可读性受损，不影响 DB 数据安全
**概率**：低（任务标题通常不含 `|`）
**修复**：

```python
def _md_escape(text: str) -> str:
    """转义 Markdown 表格特殊字符"""
    if not text:
        return ""
    return str(text).replace("|", "\\|").replace("\n", " ").replace("\r", "")

# 使用
lines.append(f"| {task_no} | {_md_escape(title)} | ...")
```

---

### 🟡 L-02：`get_my_tasks` 筛选逻辑不对称

**文件**：`app/api/v1/endpoints/tasks.py`

**问题**：当前 `get_my_tasks` 只返回 `creator_agent_id = 我的agent` 的任务，但"我的任务"通常也包括"分配给我"的任务。

```python
# 当前（只查创建者）
if user_agent:
    query = query.filter(models.Task.creator_agent_id == user_agent.agent_id)
```

应同时包含"负责人是我"的任务。

**影响**：用户看不到被分配给自己的任务
**修复建议**：

```python
if user_agent:
    query = query.filter(
        (models.Task.creator_agent_id == user_agent.agent_id) |
        (models.Task.assignee_agent_id == user_agent.agent_id)
    )
```

---

### 🟡 L-03：CLI Windows UTF-8 输出截断

**文件**：`app/cli/__init__.py`

**问题**：Windows 控制台使用 `io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")` 会将无法编码的字符替换为 `?`，导致输出中任务状态 emoji 变成乱码 `�?`。

**当前状态**：已在代码中加入 UTF-8 模式，但 `errors="replace"` 会导致上述问题。

**更好的修复**：

```python
import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="strict")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="strict")
```

**注意**：`errors="strict"` 会在编码失败时抛异常，告知问题而非静默替换。开发环境可接受。

---

### 🟠 M-01：`_revoked_access_token_jtis` 进程内存 — 多实例不兼容

**文件**：`app/core/security.py`

**问题**：logout 时将 JTI 加入进程内 `Set`，单进程 FastAPI 没问题，但使用 `uvicorn --workers N`（N>1）或多 Pod 部署时，token 黑名单不共享。

**影响**：多实例部署时，登出后 token 在其他实例仍可用（最多 N-1/N 的概率）
**建议**：生产环境使用 Redis 存储黑名单（`SET revoked:jti:<jti> 1 EX <ttl>`）

**可接受理由**：目前 `main.py` 中 `uvicorn app.main:app` 以单进程运行，暂无多实例需求。

---

### 🟡 L-04：CLI `--status` 参数大小写敏感

**文件**：`app/cli/__init__.py`

**问题**：`--status=completed` 可用，但 `--status=Completed` 或 `--status=Completed` 报错，而 API 端点的 query 参数是大小写不敏感的。

```bash
# 报错
python -m app.cli task list --status=Completed

# 正常
python -m app.cli task list --status=completed
```

**修复**：在 `cmd_task_list` 中 `.upper()` 规范化：

```python
if args.status:
    status_val = args.status.upper()
    try:
        status_enum = getattr(models.TaskStatus, status_val)
        ...
```

---

### 🟡 L-05：干支纪年计算偏粗

**文件**：`app/cli/ledger_generator.py`

**问题**：`gregorian_to_chinese()` 的干支计算为简化实现，当前输出日期如 `丙午年壬辰?1`，有字符乱码和计算偏差。

**影响**：仅展示用，不影响数据正确性
**修复**：使用成熟的农历库（如 `chinese-calendar`）或接受简化版本

---

### 🟠 M-02：`export_ledger_to_file` 并发覆盖风险

**文件**：`app/cli/ledger_generator.py`

**问题**：两个进程同时执行 `export_ledger_to_file` 可能产生竞争（读-写-覆盖）。正常操作不会发生，除非：

1. 定时任务 + 手动同时执行
2. 多实例部署（见 M-01）

**建议**：使用写入临时文件 + `os.replace()` 原子操作：

```python
tmp_path = ledger_path.with_suffix(".tmp.md")
with open(tmp_path, "w", encoding="utf-8") as f:
    f.write(content)
os.replace(tmp_path, ledger_path)  # 原子替换
```

---

## 三、上轮问题回归检查

| 问题编号 | 问题描述 | 状态 |
|----------|----------|------|
| H-01 | 安全中间件禁用 | ✅ 已修复（但曾引入 regression，见下） |
| H-02 | 多端点无认证 | ✅ 已修复 |
| H-03 | 速率限制可绕过 | ✅ 已修复 |
| H-04 | 生产环境弱密钥 | ✅ 已修复 |
| H-05 | 路径遍历 | ✅ 已修复 |
| H-06 | 前端硬编码密码 | ✅ 已修复 |
| H-07 | logout不撤销token | ✅ 已修复 |
| H-08 | DB Session泄漏 | ✅ 已修复 |

### ⚠️ 回归问题：ValidationMiddleware body 读取导致 POST hang

**文件**：`middleware/validation.py`

**修复过程**：启用中间件后，`await request.body()` 消费了 stream，导致 FastAPI endpoint 拿不到 body，login 请求超时。后移除 body 读取逻辑解决。

**根因**：`request.body()` 返回 generator，调用后 stream 被消耗，且无缓存机制

**正确做法**：FastAPI 的 `Request.json()` 会缓存 body，但直接调用 `body()` 不会

**当前状态**：✅ 已修复（移除了 body 读取，JSON 验证由 Pydantic 接管）

---

## 四、安全改进肯定

本次重构在安全上有以下改进值得肯定：

1. **单一数据源**：LEDGER.md 不再作为写入目标，消除了"双写覆盖"风险
2. **JTI 黑名单**：logout 后 access_token 无法继续使用
3. **认证全覆盖**：tasks/projects/agents/longmenling/audit_log 全部端点加认证
4. **速率限制收紧**：1000次/分钟 → 60次/分钟
5. **IP 伪造防护**：优先使用 X-Real-IP
6. **API Key 简单加密**：非明文存储

---

## 五、评分

| 维度 | 上轮 | 本轮 |
|------|------|------|
| 安全 | 差→中 | 中→良 |
| 架构 | 良 | 良 |
| 代码质量 | 中 | 中 |
| 可维护性 | 中 | 良（CLI 解耦） |
| **综合** | **82.5** | **86** |

---

## 六、修复优先级建议

| 优先级 | 问题 | 预计工时 |
|--------|------|----------|
| 🔴 立即 | L-01 Markdown injection（LEDGER.md 可读性） | 15分钟 |
| 🟡 本周 | M-02 export 并发安全（原子写） | 10分钟 |
| 🟡 本周 | L-02 get_my_tasks 筛选逻辑 | 10分钟 |
| 🟡 本周 | L-04 status 参数大小写 | 5分钟 |
| 🟠 计划 | M-01 Redis 黑名单（多实例部署前） | 1小时 |
| 🟢 随意 | L-03 UTF-8 strict mode | 5分钟 |
| 🟢 随意 | L-05 干支纪年库 | 30分钟 |

---

**账房先生**  
丙午年二月十二（2026-03-31）酉时
