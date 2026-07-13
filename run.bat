@echo off
title PathForge Startup Service
echo ============================================================
echo                   STARTING PATHFORGE WEBSITE
echo ============================================================
python start.py
if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] There was an error starting PathForge.
    pause
)
