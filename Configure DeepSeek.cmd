@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\configure_deepseek.ps1" %*
set "exitCode=%ERRORLEVEL%"
if not "%exitCode%"=="0" pause
endlocal & exit /b %exitCode%
