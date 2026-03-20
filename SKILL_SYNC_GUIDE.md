# 龙门客栈 Skill 同步指南

**最后更新**：2026-03-17  
**版本**：v1.0

---

## 📁 目录结构

### 双层架构

```
龙门客栈业务目录（配置源码）
    ~/.openclaw/workspace/.longmen_inn/roles/{agent}/skills/{skill-name}/
                        ↓  同步/部署
OpenClaw 运行时目录（运行时）
    ~/.openclaw/agents/{agent}/skills/{skill-name}/
```

---

## 🔄 同步命令

### 手动同步（推荐）

```powershell
# 同步厨子的 ci-cd-pipeline skill
Copy-Item -Path "$env:USERPROFILE\.openclaw\workspace\.longmen_inn\roles\chef\skills\ci-cd-pipeline\SKILL.md" `
    -Destination "$env:USERPROFILE\.openclaw\agents\chef\skills\ci-cd-pipeline\SKILL.md" -Force

# 同步账房先生的 quality-assurance skill
Copy-Item -Path "$env:USERPROFILE\.openclaw\workspace\.longmen_inn\roles\accountant\skills\quality-assurance\SKILL.md" `
    -Destination "$env:USERPROFILE\.openclaw\agents\accountant\skills\quality-assurance\SKILL.md" -Force
```

### 使用同步脚本

```powershell
# 进入脚本目录
cd ~/.openclaw/workspace/.longmen_inn/scripts

# 查看帮助
.\sync-skills.ps1

# 同步所有 skills
.\sync-skills.ps1 -All

# 同步单个 skill
.\sync-skills.ps1 -Agent chef -SkillName ci-cd-pipeline
```

---

## ✅ 同步状态检查

### 检查厨子的 CI/CD Skill

```powershell
# 检查文件是否存在
Test-Path "$env:USERPROFILE\.openclaw\agents\chef\skills\ci-cd-pipeline\SKILL.md"

# 查看文件内容（前 30 行）
Get-Content "$env:USERPROFILE\.openclaw\agents\chef\skills\ci-cd-pipeline\SKILL.md" -TotalCount 30
```

### 检查账房先生的 QA Skill

```powershell
# 检查文件是否存在
Test-Path "$env:USERPROFILE\.openclaw\agents\accountant\skills\quality-assurance\SKILL.md"

# 查看文件内容（前 30 行）
Get-Content "$env:USERPROFILE\.openclaw\agents\accountant\skills\quality-assurance\SKILL.md" -TotalCount 30
```

---

## 📊 当前同步状态

| Agent | Skill | 龙门客栈目录 | OpenClaw 目录 | 状态 |
|-------|-------|-------------|--------------|------|
| chef | ci-cd-pipeline | ✅ 存在 | ✅ 存在 | ✅ 已同步 |
| accountant | quality-assurance | ✅ 存在 | ✅ 存在 | ✅ 已同步 |

---

## 🚀 使用流程

### 1. 开发新 Skill

1. 在龙门客栈目录创建/编辑 `SKILL.md`：
   ```
   ~/.openclaw/workspace/.longmen_inn/roles/{agent}/skills/{skill-name}/SKILL.md
   ```

2. 验证 Skill 内容符合规范

### 2. 同步到 OpenClaw

```powershell
# 方法 1: 手动复制
Copy-Item -Path "源路径" -Destination "目标路径" -Force

# 方法 2: 使用同步脚本
cd ~/.openclaw/workspace/.longmen_inn/scripts
.\sync-skills.ps1 -Agent {agent} -SkillName {skill-name}
```

### 3. 验证同步结果

```powershell
# 检查文件是否存在
Test-Path "~/.openclaw/agents/{agent}/skills/{skill-name}/SKILL.md"

# 查看文件大小
Get-Item "~/.openclaw/agents/{agent}/skills/{skill-name}/SKILL.md" | Select-Object Length
```

---

## ⚠️ 注意事项

1. **必须同步后才能使用** - OpenClaw 只读取运行时目录的 Skill
2. **修改后重新同步** - 修改龙门客栈目录后需要重新同步
3. **保留备份** - 同步前建议备份重要的 Skill 文件

---

## 📞 支持

如有问题，请联系 **老板娘** 协助处理。

**更新日志**：
- v1.0 (2026-03-17): 初始版本，完成 ci-cd-pipeline 和 quality-assurance Skill 同步
