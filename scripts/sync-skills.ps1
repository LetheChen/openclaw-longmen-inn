#!/usr/bin/env pwsh
<#
.SYNOPSIS
    同步龙门客栈 Skill 到 OpenClaw Agent 运行时目录

.DESCRIPTION
    将 .longmen_inn/roles/{agent}/skills/ 下的 Skill 文件
    同步到 ~/.openclaw/agents/{agent}/skills/ 目录

.PARAMETER Agent
    要同步的 Agent ID，如 chef, accountant

.PARAMETER SkillName
    要同步的 Skill 名称，如 ci-cd-pipeline, quality-assurance

.PARAMETER All
    同步所有 Agents 的所有 Skills

.EXAMPLE
    .\sync-skills.ps1 -Agent chef -SkillName ci-cd-pipeline
    同步厨子的 ci-cd-pipeline skill

.EXAMPLE
    .\sync-skills.ps1 -All
    同步所有 skills
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$Agent,
    
    [Parameter(Mandatory=$false)]
    [string]$SkillName,
    
    [Parameter(Mandatory=$false)]
    [switch]$All
)

# 路径配置
$LONGMEN_ROLES = "$env:USERPROFILE\.openclaw\workspace\.longmen_inn\roles"
$OPENCLAW_AGENTS = "$env:USERPROFILE\.openclaw\agents"

# 检查路径是否存在
if (-not (Test-Path $LONGMEN_ROLES)) {
    Write-Host "❌ 龙门客栈角色目录不存在: $LONGMEN_ROLES" -ForegroundColor Red
    exit 1
}

# 同步单个 skill
function Sync-Skill($agent, $skill) {
    $sourceDir = "$LONGMEN_ROLES\$agent\skills\$skill"
    $targetDir = "$OPENCLAW_AGENTS\$agent\skills\$skill"
    
    if (-not (Test-Path $sourceDir)) {
        Write-Host "⚠️ Source skill not found: $sourceDir" -ForegroundColor Yellow
        return $false
    }
    
    # 创建目标目录
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        Write-Host "📁 Created: $targetDir" -ForegroundColor DarkGray
    }
    
    # 复制文件
    $files = Get-ChildItem -Path $sourceDir -File
    foreach ($file in $files) {
        $targetPath = Join-Path $targetDir $file.Name
        Copy-Item -Path $file.FullName -Destination $targetPath -Force
        Write-Host "  📄 $($file.Name)" -ForegroundColor Gray
    }
    
    Write-Host "✅ Synced: $agent/$skill" -ForegroundColor Green
    return $true
}

# 获取所有 agents 的 skills
function Get-AllSkills() {
    $skills = @()
    $agents = Get-ChildItem -Path $LONGMEN_ROLES -Directory
    
    foreach ($agent in $agents) {
        $skillsDir = "$($agent.FullName)\skills"
        if (Test-Path $skillsDir) {
            $agentSkills = Get-ChildItem -Path $skillsDir -Directory
            foreach ($skill in $agentSkills) {
                $skills += [PSCustomObject]@{
                    Agent = $agent.Name
                    Skill = $skill.Name
                }
            }
        }
    }
    
    return $skills
}

# 主逻辑
Write-Host "=== 龙门客栈 Skill 同步工具 ===" -ForegroundColor Cyan
Write-Host "Source: $LONGMEN_ROLES" -ForegroundColor DarkGray
Write-Host "Target: $OPENCLAW_AGENTS`n" -ForegroundColor DarkGray

if ($All) {
    Write-Host "🔄 Syncing all skills..." -ForegroundColor Yellow
    $allSkills = Get-AllSkills
    
    if ($allSkills.Count -eq 0) {
        Write-Host "⚠️ No skills found!" -ForegroundColor Yellow
        exit 0
    }
    
    $success = 0
    foreach ($item in $allSkills) {
        if (Sync-Skill -agent $item.Agent -skill $item.Skill) {
            $success++
        }
    }
    
    Write-Host "`n✅ Synced $success/$($allSkills.Count) skills" -ForegroundColor Green
}
elseif ($Agent -and $SkillName) {
    Write-Host "🔄 Syncing: $Agent/$SkillName" -ForegroundColor Yellow
    Sync-Skill -agent $Agent -skill $SkillName
}
else {
    Write-Host "Usage:" -ForegroundColor Cyan
    Write-Host "  .\sync-skills.ps1 -Agent <agent> -SkillName <skill>" -ForegroundColor Gray
    Write-Host "  .\sync-skills.ps1 -All" -ForegroundColor Gray
    Write-Host "`nAvailable skills:" -ForegroundColor Cyan
    
    $allSkills = Get-AllSkills
    foreach ($item in $allSkills | Sort-Object Agent, Skill) {
        Write-Host "  $($item.Agent)/$($item.Skill)" -ForegroundColor Gray
    }
}
