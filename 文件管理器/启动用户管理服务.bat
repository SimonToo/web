@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动HTTP服务器...
echo 访问地址: http://localhost:8080/文件管理器.html
echo.
echo 按 Ctrl+C 停止服务器
python server.py
pause