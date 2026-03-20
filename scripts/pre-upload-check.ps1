# Longmen Inn - Pre-upload Privacy Check Script
# Run: powershell -ExecutionPolicy Bypass -File scripts/pre-upload-check.ps1

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== Longmen Inn GitHub Upload Check ===" -ForegroundColor Cyan
Write-Host ""

$checks = @()

# 1. Check sensitive files
Write-Host "[1/6] Checking sensitive files..." -ForegroundColor Yellow
$sensitiveFiles = @("*.db", "*.sqlite", "*.sqlite3", ".env", "*.env", "*.pem", "*.key")
$foundSensitive = @()
foreach ($pattern in $sensitiveFiles) {
    $files = Get-ChildItem -Path $projectRoot -Recurse -Filter $pattern -ErrorAction SilentlyContinue
    if ($files) {
        $foundSensitive += $files.FullName
    }
}

if ($foundSensitive.Count -gt 0) {
    Write-Host "  [X] Found sensitive files:" -ForegroundColor Red
    $foundSensitive | ForEach-Object { Write-Host "      $_" -ForegroundColor Red }
    $checks += "Sensitive files not cleaned"
} else {
    Write-Host "  [OK] No sensitive files" -ForegroundColor Green
}

# 2. Check node_modules
Write-Host "[2/6] Checking node_modules..." -ForegroundColor Yellow
$nodeModules = Get-ChildItem -Path $projectRoot -Recurse -Directory -Filter "node_modules" -ErrorAction SilentlyContinue
if ($nodeModules) {
    Write-Host "  [X] Found node_modules directories:" -ForegroundColor Red
    $nodeModules | ForEach-Object { Write-Host "      $($_.FullName)" -ForegroundColor Red }
    $checks += "node_modules not excluded"
} else {
    Write-Host "  [OK] No node_modules directory" -ForegroundColor Green
}

# 3. Check .gitignore
Write-Host "[3/6] Checking .gitignore..." -ForegroundColor Yellow
$gitignore = Join-Path $projectRoot ".gitignore"
if (Test-Path $gitignore) {
    Write-Host "  [OK] .gitignore exists" -ForegroundColor Green
} else {
    Write-Host "  [X] .gitignore not found" -ForegroundColor Red
    $checks += ".gitignore does not exist"
}

# 4. Check README
Write-Host "[4/6] Checking README..." -ForegroundColor Yellow
$readme = Join-Path $projectRoot "README.md"
if (Test-Path $readme) {
    Write-Host "  [OK] README.md exists" -ForegroundColor Green
} else {
    Write-Host "  [X] README.md not found" -ForegroundColor Yellow
}

# 5. Check LICENSE
Write-Host "[5/6] Checking LICENSE..." -ForegroundColor Yellow
$license = Join-Path $projectRoot "LICENSE"
if (Test-Path $license) {
    Write-Host "  [OK] LICENSE exists" -ForegroundColor Green
} else {
    Write-Host "  [X] LICENSE not found (recommended)" -ForegroundColor Yellow
}

# 6. Check Python files for hardcoded secrets
Write-Host "[6/6] Checking Python files for hardcoded secrets..." -ForegroundColor Yellow
$pyFiles = Get-ChildItem -Path $projectRoot -Recurse -Filter "*.py" -ErrorAction SilentlyContinue
$foundKeys = @()
foreach ($pyFile in $pyFiles) {
    $content = Get-Content $pyFile.FullName -Raw -ErrorAction SilentlyContinue
    if ($content -match "password\s*=\s*[`"'][^`"']+[`"']" -or $content -match "api_key\s*=\s*[`"'][^`"']+[`"']") {
        $foundKeys += $pyFile.Name
    }
}
if ($foundKeys.Count -gt 0) {
    Write-Host "  [X] Found potential hardcoded secrets in:" -ForegroundColor Red
    $foundKeys | ForEach-Object { Write-Host "      $_" -ForegroundColor Red }
    $checks += "Hardcoded secrets found"
} else {
    Write-Host "  [OK] No hardcoded secrets" -ForegroundColor Green
}

# Summary
Write-Host ""
Write-Host "=== Check Complete ===" -ForegroundColor Cyan
if ($checks.Count -eq 0) {
    Write-Host "[OK] All checks passed! Safe to upload." -ForegroundColor Green
} else {
    Write-Host "[X] Issues found, please fix before upload:" -ForegroundColor Red
    $checks | ForEach-Object { Write-Host "      - $_" -ForegroundColor Red }
}

Write-Host ""
Write-Host "Recommended actions:"
Write-Host "  1. Remove database files: Remove-Item -Recurse *.db"
Write-Host "  2. Remove node_modules: Get-ChildItem -Recurse -Directory -Filter node_modules | Remove-Item -Recurse"
Write-Host "  3. git init"
Write-Host "  4. git add ."
Write-Host "  5. git commit -m 'Initial commit'"
Write-Host "  6. git remote add origin https://github.com/username/longmen-inn.git"
Write-Host "  7. git push -u origin main"