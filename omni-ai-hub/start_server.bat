@echo off
title Puter.js Local Server
echo ===================================================
echo Starting local server for Puter.js AI functionalities
echo ===================================================
echo.
echo The browser will open automatically.
echo Please do not close this window while using the app.
echo.

:: 在默认浏览器中打开 localhost:8001
start http://localhost:8001

:: 启动 Python HTTP 服务器
python -m http.server 8001
