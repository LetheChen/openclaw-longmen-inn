# Start both backend and frontend services for Longmen Inn System
# Run this in PowerShell: .\start-services.ps1

$ScriptPath = $PSScriptRoot
if (-not $ScriptPath) {
    $ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  龙门客栈 - Longmen Inn System" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  Found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Node.js not found! Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if ports are in use
$backendPort = 8000
$frontendPort = 8080

Write-Host "Checking port availability..." -ForegroundColor Gray

$backendInUse = netstat -ano | Select-String ":$backendPort" 2>$null
$frontendInUse = netstat -ano | Select-String ":$frontendPort" 2>$null

if ($backendInUse) {
    Write-Host "Backend port $backendPort is in use" -ForegroundColor Yellow
    Write-Host "  Run: Stop-Services.ps1 to stop existing services" -ForegroundColor Gray
}

if ($frontendInUse) {
    Write-Host "Frontend port $frontendPort is in use" -ForegroundColor Yellow
    Write-Host "  Run: Stop-Services.ps1 to stop existing services" -ForegroundColor Gray
}

Write-Host ""

# Check database
$dbPath = Join-Path $ScriptPath "backend\data\longmen_inn.db"
$dbDir = Join-Path $ScriptPath "backend\data"

if (-not (Test-Path $dbPath)) {
    Write-Host "Database not found, initializing..." -ForegroundColor Yellow
    if (-not (Test-Path $dbDir)) {
        New-Item -ItemType Directory -Path $dbDir -Force | Out-Null
    }
    Push-Location (Join-Path $ScriptPath "backend")
    python init_db.py --seed
    Pop-Location
    Write-Host "Database initialized with sample data!" -ForegroundColor Green
}

Write-Host ""

# Start backend service
Write-Host "Starting backend service..." -ForegroundColor Cyan
$backendPath = Join-Path $ScriptPath "backend"
Write-Host "  Path: $backendPath" -ForegroundColor Gray
Write-Host "  URL: http://localhost:$backendPort" -ForegroundColor Gray
Write-Host "  API Docs: http://localhost:$backendPort/docs" -ForegroundColor Gray

$backendJob = Start-Job -ScriptBlock {
    param($path, $port)
    Set-Location $path
    python -m uvicorn app.main:app --host 0.0.0.0 --port $port --reload
} -ArgumentList $backendPath, $backendPort

# Start frontend service
Write-Host ""
Write-Host "Starting frontend service..." -ForegroundColor Cyan
$frontendPath = Join-Path $ScriptPath "frontend"
Write-Host "  Path: $frontendPath" -ForegroundColor Gray
Write-Host "  URL: http://localhost:$frontendPort" -ForegroundColor Gray

# Check if node_modules exists
$nodeModulesPath = Join-Path $frontendPath "node_modules"
if (-not (Test-Path $nodeModulesPath)) {
    Write-Host "  node_modules not found, running npm install..." -ForegroundColor Yellow
    Push-Location $frontendPath
    npm install
    Pop-Location
}

$frontendJob = Start-Job -ScriptBlock {
    param($path)
    Set-Location $path
    npm run dev
} -ArgumentList $frontendPath

# Wait for services to start
Write-Host ""
Write-Host "Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Check if services are running
Write-Host ""
Write-Host "Status:" -ForegroundColor Cyan

$backendRunning = $false
$frontendRunning = $false

try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:$backendPort/docs" -UseBasicParsing -TimeoutSec 3
    if ($backendResponse.StatusCode -eq 200) {
        $backendRunning = $true
    }
} catch { }

try {
    $frontendConnection = Test-NetConnection -ComputerName localhost -Port $frontendPort -WarningAction SilentlyContinue
    if ($frontendConnection.TcpTestSucceeded) {
        $frontendRunning = $true
    }
} catch { }

if ($backendRunning) {
    Write-Host "  [OK] Backend: http://localhost:$backendPort" -ForegroundColor Green
    Write-Host "       API Docs: http://localhost:$backendPort/docs" -ForegroundColor Gray
} else {
    Write-Host "  [WAIT] Backend starting..." -ForegroundColor Yellow
}

if ($frontendRunning) {
    Write-Host "  [OK] Frontend: http://localhost:$frontendPort" -ForegroundColor Green
} else {
    Write-Host "  [WAIT] Frontend starting..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Save job IDs for cleanup
$backendJob.Id | Out-File -FilePath (Join-Path $ScriptPath ".backend_job") -Force
$frontendJob.Id | Out-File -FilePath (Join-Path $ScriptPath ".frontend_job") -Force

# Keep window open and monitor
try {
    while ($true) {
        Start-Sleep -Seconds 10
    }
} finally {
    # Cleanup on exit
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $ScriptPath ".backend_job") -ErrorAction SilentlyContinue
    Remove-Item (Join-Path $ScriptPath ".frontend_job") -ErrorAction SilentlyContinue
    Write-Host "Services stopped." -ForegroundColor Green
}