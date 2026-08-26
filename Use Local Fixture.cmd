@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\use_local_fixture.ps1" %*
set "exitCode=%ERRORLEVEL%"
if not "%exitCode%"=="0" pause
endlocal & exit /b %exitCode%
