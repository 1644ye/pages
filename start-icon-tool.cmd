@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 icon-server.py
) else (
  python icon-server.py
)
if errorlevel 1 (
  echo.
  echo This feature requires Python 3.10 or newer: https://www.python.org/downloads/
  pause
)
