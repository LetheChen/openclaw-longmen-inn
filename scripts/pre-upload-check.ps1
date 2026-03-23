# Longmen Inn - Pre-upload Audit Check Script
# Run: powershell -ExecutionPolicy Bypass -File scripts/pre-upload-check.ps1
# Enhanced: Add change log, task association, audit log features

$ErrorActionPreference = "Continue"
$WarningPreference = "SilentlyContinue"
$projectRoot = Split-Path -Parent $PSScriptRoot
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$auditLogPath = Join-Path $projectRoot "audit_log.jsonl"

Write-Host "=== Longmen Inn Git Upload Audit Check ===" -ForegroundColor Cyan
Write-Host "Timestamp: $timestamp" -ForegroundColor Gray
Write-Host ""

$checks = @()
$auditData = @{
    timestamp = $timestamp
    type = "git_audit"
    files_changed = @()
    lines_added = 0
    lines_deleted = 0
    tasks_found = @()
    summary = ""
    status = "passed"
    issues = @()
}

# Helper function to run git silently
function Invoke-GitCommand {
    param([string]$Command)
    $output = & git $Command 2>$null | Out-String
    return $output
}

# 1. Check sensitive files
Write-Host "[1/9] Checking sensitive files..." -ForegroundColor Yellow
$sensitiveFiles = @("*.db", "*.sqlite", "*.sqlite3", ".env", "*.env", "*.pem", "*.key")
$foundSensitive = @()
foreach ($pattern in $sensitiveFiles) {
    $files = Get-ChildItem -Path $projectRoot -Recurse -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        $foundSensitive += $files.FullName
    }
}

if ($foundSensitive.Count -gt 0) {
    Write-Host "  [W] Found sensitive files (may be cached by git):" -ForegroundColor Yellow
    $foundSensitive | Select-Object -First 5 | ForEach-Object { Write-Host "      $_" -ForegroundColor Yellow }
    if ($foundSensitive.Count -gt 5) {
        Write-Host "      ... and $($foundSensitive.Count - 5) more" -ForegroundColor Yellow
    }
    Write-Host "  Tip: Run 'git rm --cached <file>' to untrack" -ForegroundColor Gray
    $auditData.issues += "sensitive_files_cached"
} else {
    Write-Host "  [OK] No sensitive files" -ForegroundColor Green
}

# 2. Check node_modules
Write-Host "[2/9] Checking node_modules..." -ForegroundColor Yellow
$nodeModules = Get-ChildItem -Path $projectRoot -Recurse -Directory -Filter "node_modules" -ErrorAction SilentlyContinue
if ($nodeModules) {
    Write-Host "  [W] Found node_modules (excluded by .gitignore):" -ForegroundColor Yellow
    $nodeModules | Select-Object -First 3 | ForEach-Object { Write-Host "      $($_.FullName)" -ForegroundColor Yellow }
    if ($nodeModules.Count -gt 3) {
        Write-Host "      ... and $($nodeModules.Count - 3) more" -ForegroundColor Yellow
    }
    Write-Host "  Info: Already in .gitignore, safe to upload" -ForegroundColor Gray
    $auditData.issues += "node_modules_present_but_excluded"
} else {
    Write-Host "  [OK] No node_modules directory" -ForegroundColor Green
}

# 3. Check .gitignore
Write-Host "[3/9] Checking .gitignore..." -ForegroundColor Yellow
$gitignore = Join-Path $projectRoot ".gitignore"
if (Test-Path $gitignore) {
    Write-Host "  [OK] .gitignore exists" -ForegroundColor Green
} else {
    Write-Host "  [X] .gitignore not found" -ForegroundColor Red
    $checks += "gitignore_missing"
    $auditData.issues += "gitignore_missing"
    $auditData.status = "failed"
}

# 4. Check README
Write-Host "[4/9] Checking README..." -ForegroundColor Yellow
$readme = Join-Path $projectRoot "README.md"
if (Test-Path $readme) {
    Write-Host "  [OK] README.md exists" -ForegroundColor Green
} else {
    Write-Host "  [W] README.md not found (recommended)" -ForegroundColor Yellow
}

# 5. Check LICENSE
Write-Host "[5/9] Checking LICENSE..." -ForegroundColor Yellow
$license = Join-Path $projectRoot "LICENSE"
if (Test-Path $license) {
    Write-Host "  [OK] LICENSE exists" -ForegroundColor Green
} else {
    Write-Host "  [W] LICENSE not found (recommended)" -ForegroundColor Yellow
}

# 6. Check Python hardcoded secrets
Write-Host "[6/9] Checking Python hardcoded secrets..." -ForegroundColor Yellow
$pyFiles = Get-ChildItem -Path $projectRoot -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
$foundKeys = @()
foreach ($pyFile in $pyFiles) {
    $content = Get-Content $pyFile.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match "password\s*=\s*[`"'][^`"']+[`"']" -or $content -match "api_key\s*=\s*[`"'][^`"']+[`"']") {
        $foundKeys += $pyFile.Name
    }
}
if ($foundKeys.Count -gt 0) {
    Write-Host "  [W] Found potential secrets (may be OK if using env vars):" -ForegroundColor Yellow
    $foundKeys | ForEach-Object { Write-Host "      $_" -ForegroundColor Yellow }
    $auditData.issues += "potential_secrets_found"
} else {
    Write-Host "  [OK] No hardcoded secrets" -ForegroundColor Green
}

# 7. Generate change summary (NEW)
Write-Host "[7/9] Generating change summary..." -ForegroundColor Yellow
Push-Location $projectRoot
try {
    $hasGit = Test-Path ".git"
    if ($hasGit) {
        $gitStatus = Invoke-GitCommand "status --porcelain"
        if ($gitStatus -and $gitStatus.Trim()) {
            $changedFiles = @()
            $linesAdded = 0
            $linesDeleted = 0
            
            $lines = $gitStatus -split "`n" | Where-Object { $_.Trim() }
            foreach ($line in $lines) {
                if ($line -match "^\s*(\w+)\s+(.+)$") {
                    $changedFiles += $matches[2].Trim()
                }
            }
            
            $diffStat = Invoke-GitCommand "diff --numstat"
            $diffLines = $diffStat -split "`n" | Where-Object { $_.Trim() }
            foreach ($stat in $diffLines) {
                $parts = $stat -split "`t"
                if ($parts.Count -ge 2) {
                    $add = if ($parts[0] -match "^\d+$") { [int]$parts[0] } else { 0 }
                    $del = if ($parts[1] -match "^\d+$") { [int]$parts[1] } else { 0 }
                    $linesAdded += $add
                    $linesDeleted += $del
                }
            }
            
            $auditData.files_changed = $changedFiles
            $auditData.lines_added = $linesAdded
            $auditData.lines_deleted = $linesDeleted
            
            Write-Host "  [OK] Changed files: $($changedFiles.Count)" -ForegroundColor Green
            Write-Host "       Lines added: +$linesAdded" -ForegroundColor Green
            Write-Host "       Lines deleted: -$linesDeleted" -ForegroundColor Green
            
            if ($changedFiles.Count -gt 0) {
                Write-Host "       File list:" -ForegroundColor Gray
                $changedFiles | Select-Object -First 10 | ForEach-Object { 
                    Write-Host "         - $_" -ForegroundColor Gray 
                }
                if ($changedFiles.Count -gt 10) {
                    Write-Host "         ... and $($changedFiles.Count - 10) more files" -ForegroundColor Gray
                }
            }
        } else {
            Write-Host "  [OK] No uncommitted changes" -ForegroundColor Green
        }
    } else {
        Write-Host "  [W] Not a Git repo, skipping change stats" -ForegroundColor Yellow
    }
} finally {
    Pop-Location
}

# 8. Extract related tasks (NEW)
Write-Host "[8/9] Extracting related tasks..." -ForegroundColor Yellow
$ledgerPath = Join-Path $projectRoot "LEDGER.md"
if (Test-Path $ledgerPath) {
    $ledgerContent = Get-Content $ledgerPath -Raw -ErrorAction SilentlyContinue
    
    $taskIdPattern = "T-\d{8}-\d{3,}"
    $allTaskIds = [regex]::Matches($ledgerContent, $taskIdPattern) | ForEach-Object { $_.Value } | Sort-Object -Unique
    
    $relatedTasks = @()
    $taskKeywords = @{
        "T-20250322" = @("agent_workspace", "AgentWorkspace")
        "T-20250321" = @("security", "auth", "cors", "middleware")
        "T-20250329" = @("frontend", "Tasks", "Dashboard")
        "T-20250327" = @("backend", "api", "FastAPI")
    }
    
    foreach ($taskId in $allTaskIds) {
        $taskDate = $taskId.Substring(2, 8)
        if ($taskKeywords.ContainsKey($taskDate)) {
            $keywords = $taskKeywords[$taskDate]
            foreach ($file in $auditData.files_changed) {
                foreach ($kw in $keywords) {
                    if ($file -match $kw) {
                        $relatedTasks += $taskId
                        break
                    }
                }
            }
        }
    }
    
    foreach ($file in $auditData.files_changed) {
        $matched = [regex]::Matches($file, $taskIdPattern)
        foreach ($m in $matched) {
            if ($relatedTasks -notcontains $m.Value) {
                $relatedTasks += $m.Value
            }
        }
    }
    
    $auditData.tasks_found = $relatedTasks | Select-Object -Unique
    
    if ($relatedTasks.Count -gt 0) {
        Write-Host "  [OK] Related tasks found: $($relatedTasks.Count)" -ForegroundColor Green
        $relatedTasks | ForEach-Object { Write-Host "         - $_" -ForegroundColor Green }
    } else {
        Write-Host "  [OK] No related task IDs found" -ForegroundColor Green
    }
} else {
    Write-Host "  [W] LEDGER.md not found" -ForegroundColor Yellow
}

# 9. Write audit log (NEW)
Write-Host "[9/9] Writing audit log..." -ForegroundColor Yellow
try {
    $fileCount = $auditData.files_changed.Count
    $taskCount = $auditData.tasks_found.Count
    $auditData.summary = "Changed $fileCount files"
    if ($taskCount -gt 0) {
        $auditData.summary += ", related to $taskCount tasks"
    }
    if ($auditData.lines_added -gt 0) {
        $auditData.summary += ", +$($auditData.lines_added)/-$($auditData.lines_deleted) lines"
    }
    
    $auditEntry = $auditData | ConvertTo-Json -Compress
    Add-Content -Path $auditLogPath -Value $auditEntry -Encoding UTF8
    
    Write-Host "  [OK] Audit log written" -ForegroundColor Green
    Write-Host "       Path: audit_log.jsonl" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "  Audit Summary:" -ForegroundColor Cyan
    Write-Host "  ----------------------------------------" -ForegroundColor Cyan
    Write-Host "  Time: $($auditData.timestamp)"
    Write-Host "  Type: $($auditData.type)"
    Write-Host "  Status: $($auditData.status)"
    Write-Host "  Summary: $($auditData.summary)"
    if ($auditData.issues.Count -gt 0) {
        Write-Host "  Issues: $($auditData.issues -join ', ')" -ForegroundColor Yellow
    }
    Write-Host "  ----------------------------------------" -ForegroundColor Cyan
    
} catch {
    Write-Host "  [E] Failed to write audit log: $_" -ForegroundColor Red
    $checks += "audit_log_write_failed"
}

# Summary
Write-Host ""
Write-Host "=== Check Complete ===" -ForegroundColor Cyan
if ($checks.Count -eq 0) {
    Write-Host "[OK] All checks passed! Safe to upload." -ForegroundColor Green
} else {
    Write-Host "[X] Critical issues found:" -ForegroundColor Red
    $checks | ForEach-Object { Write-Host "      - $_" -ForegroundColor Red }
}

Write-Host ""
Write-Host "Recommended actions:" -ForegroundColor Yellow
Write-Host "  1. Backup: .\projects\longmen-inn-system\backup-local.ps1 backup"
Write-Host "  2. Add files: git add ."
Write-Host "  3. Commit: git commit -m 'update: description'"
Write-Host "  4. Push: git push origin main"
Write-Host ""
Write-Host "Audit log saved to: $auditLogPath" -ForegroundColor Gray
Write-Host "Used for inn-dynamics display and version tracking" -ForegroundColor Gray
