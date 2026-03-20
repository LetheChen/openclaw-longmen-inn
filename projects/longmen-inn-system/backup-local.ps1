# 龙门客栈 - 本地数据备份脚本
# 在git操作前备份本地开发数据

param(
    [string]$Action = "backup"
)

$projectRoot = Split-Path -Parent $PSScriptRoot
$backupDir = Join-Path $projectRoot "..\..\backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

function Backup-LocalData {
    Write-Host "=== 备份本地开发数据 ===" -ForegroundColor Cyan
    
    # 创建备份目录
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir | Out-Null
        Write-Host "创建备份目录: $backupDir" -ForegroundColor Green
    }
    
    # 备份数据库
    $dbPath = Join-Path $projectRoot "backend\longmen_inn.db"
    if (Test-Path $dbPath) {
        $backupFile = Join-Path $backupDir "longmen_inn_$timestamp.db"
        Copy-Item $dbPath $backupFile
        Write-Host "[$([char]0x2713)] 数据库已备份: $backupFile" -ForegroundColor Green
    }
    
    # 备份LEDGER.md
    $ledgerPath = Join-Path $projectRoot "..\..\LEDGER.md"
    if (Test-Path $ledgerPath) {
        $backupFile = Join-Path $backupDir "LEDGER_$timestamp.md"
        Copy-Path $ledgerPath $backupFile
        Write-Host "[$([char]0x2713)] 任务看板已备份: $backupFile" -ForegroundColor Green
    }
    
    # 备份记忆文件
    $rolesDir = Join-Path $projectRoot "..\..\roles"
    if (Test-Path $rolesDir) {
        $memoryFiles = Get-ChildItem -Path $rolesDir -Recurse -Filter "MEMORY_LOG.md"
        foreach ($file in $memoryFiles) {
            $backupFile = Join-Path $backupDir "$($file.BaseName)_$timestamp.md"
            Copy-Item $file.FullName $backupFile
            Write-Host "[$([char]0x2713)] 记忆文件已备份: $backupFile" -ForegroundColor Green
        }
    }
    
    Write-Host "`n备份完成！位置: $backupDir" -ForegroundColor Green
}

function Restore-LocalData {
    Write-Host "=== 恢复本地开发数据 ===" -ForegroundColor Cyan
    
    # 列出可用备份
    $backups = Get-ChildItem -Path $backupDir -Filter "*.db" | Sort-Object Name -Descending
    
    if ($backups.Count -eq 0) {
        Write-Host "[X] 没有找到备份文件" -ForegroundColor Red
        return
    }
    
    Write-Host "可用的数据库备份:" -ForegroundColor Yellow
    for ($i = 0; $i -lt [Math]::Min(5, $backups.Count); $i++) {
        Write-Host "  [$i] $($backups[$i].Name)" -ForegroundColor White
    }
    
    $selection = Read-Host "选择要恢复的备份编号"
    if ($selection -match "^\d+$" -and [int]$selection -lt $backups.Count) {
        $selectedBackup = $backups[[int]$selection]
        $dbPath = Join-Path $projectRoot "backend\longmen_inn.db"
        
        Copy-Item $selectedBackup.FullName $dbPath -Force
        Write-Host "[$([char]0x2713)] 数据库已恢复: $($selectedBackup.Name)" -ForegroundColor Green
    } else {
        Write-Host "[X] 无效选择" -ForegroundColor Red
    }
}

function Clean-OldBackups {
    Write-Host "=== 清理旧备份 ===" -ForegroundColor Cyan
    
    $backups = Get-ChildItem -Path $backupDir
    $keepCount = 10  # 保留最近10个备份
    
    if ($backups.Count -gt $keepCount) {
        $toDelete = $backups | Sort-Object LastWriteTime | Select-Object -First ($backups.Count - $keepCount)
        foreach ($file in $toDelete) {
            Remove-Item $file.FullName -Force
            Write-Host "删除旧备份: $($file.Name)" -ForegroundColor Yellow
        }
        Write-Host "清理完成，保留最近 $keepCount 个备份" -ForegroundColor Green
    } else {
        Write-Host "备份数量正常，无需清理" -ForegroundColor Green
    }
}

# 主逻辑
switch ($Action.ToLower()) {
    "backup" { Backup-LocalData }
    "restore" { Restore-LocalData }
    "clean" { Clean-OldBackups }
    default {
        Write-Host "用法:" -ForegroundColor Yellow
        Write-Host "  .\backup-local.ps1 backup   # 创建备份"
        Write-Host "  .\backup-local.ps1 restore  # 恢复数据"
        Write-Host "  .\backup-local.ps1 clean    # 清理旧备份"
    }
}