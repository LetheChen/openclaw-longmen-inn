# LEDGER - 龙门客栈业务管理系统

> 📅 最后更新：2026-03-15
> 🏷️ 状态：代码审查规范建立中

---

## 📋 项目概览

**项目名称**：龙门客栈业务管理系统  
**项目代号**：longmen-inn-system  
**业务领域**：客栈业务管理（订单、客房、库存、财务等）  
**技术栈**：Python + TypeScript/React

---

## 🎯 当前任务

### 账房先生（质量保证工程师）

**任务描述**：建立完整的代码审查规范和质量保障体系

**交付物清单**：
- [ ] **代码审查规范文档** (docs/CODE_REVIEW.md)
- [ ] **代码质量配置文件** (.flake8, .pylintrc, pyproject.toml, .eslintrc.json, .prettierrc, .pre-commit-config.yaml)
- [ ] **CI/CD配置** (.github/workflows/ci.yml)
- [ ] **测试规范文档** (docs/TESTING.md)
- [ ] **安全检查清单** (docs/SECURITY.md)
- [ ] **质量指标定义**

---

## 📝 进度日志

### 2026-03-15

**开始任务**：账房先生-代码审查规范建立  
**状态**：进行中  
**备注**：
- 创建项目基础文档结构
- 开始编写代码审查规范文档
- 准备质量配置文件

---

## 📁 目录结构

```
longmen-inn-system/
├── docs/                    # 项目文档
│   ├── CODE_REVIEW.md      # 代码审查规范
│   ├── TESTING.md          # 测试规范
│   └── SECURITY.md         # 安全检查清单
├── .github/
│   └── workflows/
│       └── ci.yml            # CI/CD配置
├── .flake8                  # Python风格检查
├── .pylintrc                # Python代码分析
├── pyproject.toml           # Python项目配置
├── .eslintrc.json           # JS/TS代码检查
├── .prettierrc              # 代码格式化
├── .pre-commit-config.yaml  # 提交前钩子
├── tsconfig.json            # TypeScript配置
└── LEDGER.md                # 项目账本（本文件）
```

---

## 🔗 相关资源

- 项目路径：`./longmen-inn-system`（相对于仓库根目录）
- 全局规则：`.longmen_inn/INN_RULES.md`
- 角色配置：`.longmen_inn/roles/main/`

---

*"账房先生记账，一笔一笔，清清楚楚。"* 📚
