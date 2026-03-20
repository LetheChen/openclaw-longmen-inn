# Stop all Longmen Inn services
# Run this in PowerShell: .\stop-services.ps1

Write-Host "Stopping Longmen Inn services..." -ForegroundColor Cyan
Write-Host ""

$backendPort = 8000
$frontendPort = 8080

# Kill backend process
$backendProcess = netstat -ano | Select-String ":$backendPort" | ForEach-Object { 
    ($_ -split '\s+')[-1] 
} | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1

if ($backendProcess) {
    Write-Host "Stopping backend (PID: $backendProcess)..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Backend stopped" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] Backend not running" -ForegroundColor Gray
}

# Kill frontend process
$frontendProcess = netstat -ano | Select-String ":$frontendPort" | ForEach-Object { 
    ($_ -split '\s+')[-1] 
} | Where-Object { $_ -match '^\d+$' } | Select-Object -First 1

if ($frontendProcess) {
    Write-Host "Stopping frontend (PID: $frontendProcess)..." -ForegroundColor Yellow
    Stop-Process -Id $frontendProcess -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Frontend stopped" -ForegroundColor Green
} else {
    Write-Host "  [SKIP] Frontend not running" -ForegroundColor Gray
}

# Clean up job files
$ScriptPath = $PSScriptRoot
if (-not $ScriptPath) {
    $ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
}

Remove-Item (Join-Path $ScriptPath ".backend_job") -ErrorAction SilentlyContinue
Remove-Item (Join-Path $ScriptPath ".frontend_job") -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "All services stopped." -ForegroundColor Green