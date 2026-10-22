@echo off
cd /d "%~dp0"
start "" "http://127.0.0.1:8765"
"C:\Users\monker1624\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" -m http.server 8765 --bind 127.0.0.1 --directory dist
