@echo off
chcp 65001 >nul
echo === 龙门客栈 Skill 同步工具 ===
echo.

set SOURCE=%USERPROFILE%\.openclaw\workspace\.longmen_inn\roles
set TARGET=%USERPROFILE%\.openclaw\agents

echo Source: %SOURCE%
echo Target: %TARGET%
echo.

REM 同步厨子的 ci-cd-pipeline skill
if exist "%SOURCE%\chef\skills\ci-cd-pipeline" (
    echo Syncing: chef/ci-cd-pipeline
    if not exist "%TARGET%\chef\skills\ci-cd-pipeline" mkdir "%TARGET%\chef\skills\ci-cd-pipeline"
    copy /Y "%SOURCE%\chef\skills\ci-cd-pipeline\*" "%TARGET%\chef\skills\ci-cd-pipeline\"
    echo   OK
)

REM 同步账房先生的 quality-assurance skill
if exist "%SOURCE%\accountant\skills\quality-assurance" (
    echo Syncing: accountant/quality-assurance
    if not exist "%TARGET%\accountant\skills\quality-assurance" mkdir "%TARGET%\accountant\skills\quality-assurance"
    copy /Y "%SOURCE%\accountant\skills\quality-assurance\*" "%TARGET%\accountant\skills\quality-assurance\"
    echo   OK
)

echo.
echo === 同步完成 ===
pause
