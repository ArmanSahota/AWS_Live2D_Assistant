@echo off
echo ===================================================
echo Testing WebSocket Connection Between Frontend and Backend
echo ===================================================
echo.

echo Starting the test script...
echo.

cd /d "%~dp0"
call LLM-Live2D-Desktop-Assitant-main\test_websocket_connection.bat
