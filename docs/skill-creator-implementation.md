# Skill Creator 实现机制说明文档

> 本文档对 OpenClaw skill-creator 技能工具的实现原理进行完整解析。
> 适用对象：希望理解或二次开发 OpenClaw 技能系统的开发者。

---

## 一、整体架构概览

skill-creator 是 OpenClaw 技能生态中的"技能工厂"，负责创建、打包、验证技能。整个技能系统采用**渐进式披露（Progressive Disclosure）**的设计理念，将内容按需加载，避免一次性塞满上下文窗口。

### 核心模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **技能模板生成器** | `init_skill.py` | 从模板初始化一个完整的技能目录 |
| **技能打包器** | `package_skill.py` | 将技能目录压缩为可分发的 `.skill` 文件 |
| **技能验证器** | `quick_validate.py` | 验证 SKILL.md 的 frontmatter 格式与内容规范 |

### 技能标准结构

```
skill-name/
├── SKILL.md (必需)         ← 技能的核心描述与使用指南
├── scripts/  (可选)         ← 可执行脚本（Python/Bash等）
├── references/ (可选)       ← 参考文档（按需加载）
└── assets/ (可选)           ← 资源文件（模板、图片等）
```

---

## 二、SKILL.md 文件规范

SKILL.md 是每个技能的**唯一必需文件**，由两部分组成：

### 2.1 YAML Frontmatter（元数据）

位于文件顶部的 `---` 分隔符之间，必须包含两个字段：

```yaml
---
name: skill-name            # 技能名称：小写字母、数字、连字符
description: 描述文本...     # 触发说明：阐明何时该使用此技能
---
```

**description 的重要性**：Codex 是否触发某个技能，**完全取决于 description 的内容匹配**。因此描述必须具体、清晰，包含使用场景、文件类型、任务类型等关键信息。

**frontmatter 验证规则**（来源 `quick_validate.py`）：

- `name`：仅允许小写字母、数字、连字符（`^[a-z0-9-]+$`），长度 ≤ 64 字符，不能以连字符开头/结尾或包含连续连字符
- `description`：不能包含 `<` 或 `>` 字符，长度 ≤ 1024 字符
- 仅允许以下属性：`name`、`description`、`license`、`allowed-tools`、`metadata`

### 2.2 Markdown Body（使用指南）

位于 frontmatter 下方的 Markdown 内容，包含：
- 技能的详细使用说明
- 工作流程、决策树、代码示例
- 对 `scripts/`、`references/`、`assets/` 中资源的引用和调用指引

---

## 三、渐进式披露机制（Progressive Disclosure）

这是技能系统最核心的设计思想，将内容分为三个加载层级：

```
┌─────────────────────────────────────────────────────────┐
│  Level 1: Frontmatter (name + description)              │
│  → 始终加载 (~100 words)                                 │
│  → Codex 根据 description 决定是否触发该技能            │
├─────────────────────────────────────────────────────────┤
│  Level 2: SKILL.md Body                                 │
│  → 技能触发后才加载 (< 5k words)                        │
│  → 核心工作流程、指引、示例                               │
├─────────────────────────────────────────────────────────┤
│  Level 3: Bundled Resources (scripts/references/assets) │
│  → 按需加载（无上限）                                    │
│  → 脚本可直接执行而不加载进上下文                         │
└─────────────────────────────────────────────────────────┘
```

### 三种资源目录的定位

| 目录 | 何时使用 | 加载方式 | 典型用途 |
|------|---------|---------|---------|
| **scripts/** | 需要确定性执行或重复运行时 | 可直接执行，不加载进上下文 | PDF 旋转脚本、API 调用工具 |
| **references/** | 需要详细参考信息时 | 按需读取加载到上下文 | 数据库 Schema、API 文档、业务规则 |
| **assets/** | 需要在产出物中使用时 | 不加载进上下文，直接复制使用 | 品牌 Logo、PPT 模板、React  boilerplate |

---

## 四、init_skill.py 实现解析

**核心流程**：

```
1. 解析命令行参数
   ├── skill_name: 技能名称
   ├── --path: 输出目录
   ├── --resources: 要创建的资源目录（scripts,references,assets）
   └── --examples: 是否创建示例文件

2. 规范化技能名称
   normalize_skill_name()
   → 全小写，非法字符转为连字符
   → 连续连字符合并，单首尾连字符去除

3. 创建技能目录结构
   skill_dir = Path(path) / skill_name
   skill_dir.mkdir(parents=True)

4. 生成 SKILL.md 模板
   → 内置 SKILL_TEMPLATE，包含 TODO 占位符
   → 占位符包括：description、Overview、结构选择、Resources 说明

5. 创建资源目录（如有指定）
   scripts/     → 可选创建 example.py
   references/   → 可选创建 api_reference.md
   assets/       → 可选创建 example_asset.txt
```

**模板生成逻辑**：使用 Python `str.format()` 将技能名称和标题嵌入到预定义的模板字符串中。

---

## 五、package_skill.py 实现解析

**核心流程**：

```
1. 接收技能目录路径和可选输出目录

2. 前置验证（调用 quick_validate.py）
   → 验证不通过则终止打包

3. 确定输出文件路径
   output_path / {skill_name}.skill

4. 遍历技能目录 (rglob "*")
   → 排除目录：.git, .svn, .hg, __pycache__, node_modules
   → 安全检查：拒绝 symlink（防止路径穿越攻击）
   → 安全检查：文件不能逃离技能根目录
   → 避免将自己打包进去（检测输出文件是否在源目录内）

5. 写入 ZIP 压缩包（.skill 文件即 ZIP）
   → 使用 ZIP_DEFLATED 压缩算法
   → 内部路径结构：skill_name/文件相对路径
```

**关键安全设计**：
- symlink 拒绝：防止打包恶意指向系统文件的符号链接
- 路径穿越检查：`_is_within()` 确保所有文件都在技能根目录下
- 自包含检查：避免将输出文件打包进自身

---

## 六、quick_validate.py 实现解析

**验证检查项**：

| 检查项 | 规则 | 失败原因 |
|--------|------|---------|
| 文件存在性 | SKILL.md 必须存在 | `SKILL.md not found` |
| Frontmatter 格式 | 首尾 `---` 分隔符存在 | `Invalid frontmatter format` |
| YAML 解析 | PyYAML 可用时用标准解析，否则用简单解析器 | `Invalid YAML in frontmatter` |
| 字段完整性 | 必须包含 `name` 和 `description` | `Missing 'name/description' in frontmatter` |
| 字段类型 | name 和 description 必须为字符串 | type check 失败 |
| name 格式 | 小写字母+数字+连字符，不含首尾连字符或双连字符 | `Name should be hyphen-case` |
| name 长度 | ≤ 64 字符 | `Name is too long` |
| description 格式 | 不含 `<>` 字符，长度 ≤ 1024 | 格式检查失败 |
| 属性白名单 | 仅允许 5 个属性 | `Unexpected key(s)` |

**无 PyYAML 时的兜底解析器**：`_parse_simple_frontmatter()` 用纯 Python 实现简单 `key: value` 解析，支持多行值（通过缩进判断续行）。

---

## 七、技能创建完整流程

```
┌──────────────────────────────────────────────────────────────┐
│  Step 1: 理解需求                                             │
│  → 收集具体使用示例，明确技能功能范围                           │
├──────────────────────────────────────────────────────────────┤
│  Step 2: 规划资源                                              │
│  → 分析哪些需要 scripts / references / assets                  │
├──────────────────────────────────────────────────────────────┤
│  Step 3: 初始化技能                                            │
│  → python init_skill.py <name> --path <dir> [--resources]     │
├──────────────────────────────────────────────────────────────┤
│  Step 4: 编辑技能内容                                          │
│  → 编写 SKILL.md（description 是触发关键！）                    │
│  → 实现 scripts/ 中的脚本                                      │
│  → 编写 references/ 中的参考文档                               │
│  → 准备 assets/ 中的资源文件                                   │
├──────────────────────────────────────────────────────────────┤
│  Step 5: 打包技能                                              │
│  → python package_skill.py <skill-path> [output-dir]          │
│  → 验证通过后生成 .skill 文件                                  │
├──────────────────────────────────────────────────────────────┤
│  Step 6: 迭代优化                                              │
│  → 实际使用中收集反馈，持续改进                                 │
└──────────────────────────────────────────────────────────────┘
```

---

## 八、关键设计思想

### 1. 描述即触发器
Codex 决定是否使用某个技能，**完全依赖 frontmatter 中的 description**。因此 description 的编写质量直接决定技能的可用性。

### 2. 精简优先原则
SKILL.md body 建议控制在 500 行以内。详细信息应下沉到 `references/`，脚本逻辑应放入 `scripts/`。

### 3. 脚本即工具
scripts/ 中的脚本可以被**直接执行**而不必加载进上下文，这既节省了 token 消耗，又保证了确定性行为。

### 4. 安全第一
打包流程包含多层安全检查（symlink 拒绝、路径穿越检查、自包含检查），确保分发的 `.skill` 文件不包含任何恶意内容。

---

*文档版本：v1.0*
*生成时间：2026-03-26*
