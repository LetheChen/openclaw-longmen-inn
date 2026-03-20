# 龙门客栈多Agent协作系统 - 目录结构创建脚本
# 运行此脚本创建完整的目录和文件结构

$BaseDir = $PSScriptRoot
$LongmenInnDir = Join-Path $BaseDir ".longmen_inn"

Write-Host "🏯 开始创建龙门客栈多Agent协作系统目录结构..." -ForegroundColor Cyan

# 1. 创建核心目录
Write-Host "📁 创建核心目录..." -ForegroundColor Yellow
$Dirs = @(
    ".longmen_inn",
    ".longmen_inn\roles",
    ".longmen_inn\roles\innkeeper",
    ".longmen_inn\roles\waiter",
    ".longmen_inn\roles\chef",
    ".longmen_inn\roles\accountant",
    ".longmen_inn\roles\storyteller",
    ".longmen_inn\roles\main",
    "deliverables",
    "deliverables\prd",
    "deliverables\design",
    "deliverables\docs",
    "deliverables\src",
    "archive"
)

foreach ($Dir in $Dirs) {
    $Path = Join-Path $BaseDir $Dir
    if (!(Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "  ✓ $Dir" -ForegroundColor Green
    } else {
        Write-Host "  → $Dir (已存在)" -ForegroundColor Gray
    }
}

Write-Host "`n✅ 目录结构创建完成！" -ForegroundColor Cyan
Write-Host "`n下一步：请手动复制模板文件到对应位置" -ForegroundColor Yellow
