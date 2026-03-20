---
name: ci-cd-pipeline
description: CI/CD流水线管理、自动化测试、构建部署
version: 1.0.0
author: 龙门客栈大厨
created: 2026-03-17
---

# CI/CD 流水线管理

## 能力范围

### 1. 持续集成 (CI)
- 配置 GitHub Actions / GitLab CI / Jenkins 流水线
- 编写自动化构建脚本（npm build / docker build / maven package）
- 管理构建产物和缓存策略
- 处理构建失败的重试和报警

### 2. 自动化测试
- 单元测试（pytest / jest / junit）
- 集成测试（API测试、数据库测试）
- 端到端测试（Playwright / Cypress）
- 测试覆盖率报告（codecov / sonarqube）

### 3. 持续部署 (CD)
- Docker 镜像构建与推送（DockerHub / 私有仓库）
- 蓝绿部署、滚动更新策略
- Kubernetes 配置管理（Helm / Kustomize）
- 部署回滚机制

### 4. 监控与告警
- Prometheus 指标采集
- Grafana 监控面板配置
- PagerDuty / 钉钉 / 飞书告警集成
- 日志聚合（ELK / Loki）

## 输入

### 必需输入
- 代码仓库地址（GitHub / GitLab URL）
- 部署目标环境（dev / staging / prod）
- 技术栈信息（Node.js / Python / Java / Go）

### 可选输入
- 测试覆盖率要求（默认：80%）
- 构建超时时间（默认：30分钟）
- 部署策略（蓝绿 / 滚动 / 金丝雀）

## 输出

### 产出物
1. **CI配置文件**
   - `.github/workflows/ci.yml` 或 `.gitlab-ci.yml`
   - Jenkinsfile

2. **Docker相关**
   - `Dockerfile`
   - `docker-compose.yml`
   - `.dockerignore`

3. **部署配置**
   - Kubernetes manifests / Helm charts
   - 部署脚本（deploy.sh）

4. **测试配置**
   - 测试框架配置（pytest.ini / jest.config.js）
   - 覆盖率配置（.coveragerc）

5. **监控配置**
   - Prometheus rules
   - Grafana dashboards (JSON)

### 报告
- 构建状态报告（成功/失败、耗时、日志）
- 测试报告（通过率、覆盖率趋势）
- 部署报告（版本、环境、回滚点）

## 注意事项

### 必须遵守
1. **Pipeline as Code**: 所有流水线配置必须版本化，禁止手工配置UI
2. **Fail Fast**: 快速失败的阶段放在前面（lint -> unit test -> build）
3. **Security First**: 
   - 密钥绝不硬编码，使用CI内置的secrets管理
   - Docker镜像扫描（Trivy / Snyk）
   - 依赖漏洞检查
4. **Immutable Artifacts**: 构建产物一旦生成不可修改，部署时只选择版本

### 推荐实践
1. **并行化**: 无依赖的阶段并行执行（单元测试 vs 代码扫描）
2. **缓存策略**: 
   - 依赖缓存（npm_modules / pip cache）
   - Docker layer caching
3. **自文档化**: Pipeline中每个stage添加注释说明目的
4. **可观测性**: 关键步骤输出结构化日志（JSON格式）

### 常见陷阱
- ❌ 在CI中直接修改生产数据库
- ❌ 使用latest标签部署Docker镜像
- ❌ 忽略测试失败强行部署
- ❌ 将私有密钥提交到代码仓库
- ❌ 没有回滚策略直接全量部署

## 执行指令模板

当被要求"配置CI/CD流水线"时，按以下流程执行：

```
1. 确认输入信息
   - 代码仓库URL: {repo_url}
   - 技术栈: {stack}
   - CI平台: {github_actions/gitlab_ci/jenkins}
   - 部署环境: {dev/staging/prod}

2. 创建分支进行配置
   git checkout -b feature/setup-ci-cd

3. 创建配置文件
   - 根据技术栈选择基础模板
   - 配置build/test/deploy stages
   - 添加secrets引用

4. 本地验证（如可能）
   - act 工具本地运行 GitHub Actions
   - 或提交到测试分支验证

5. 创建PR并关联Issue
   - 详细描述配置说明
   - 提供回滚方案

6. 合并后观察首次运行
   - 检查各stage执行时间
   - 验证artifacts生成
   - 确认部署成功
```

---

**备案信息**
- 创建者：龙门客栈大厨
- 备案编号：SKILL-CI-CD-001
- 生效日期：2026-03-17
- 适用范围：龙门客栈所有工程项目
