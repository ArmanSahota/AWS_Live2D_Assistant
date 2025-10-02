@echo off
echo ===================================================
echo Testing WebSocket Connection Between Frontend and Backend
echo ===================================================
echo.

echo Starting the application...
echo This will launch both the backend server and the Electron frontend.
echo The application will automatically detect the backend port and connect.
echo.

cd /d "%~dp0LLM-Live2D-Desktop-Assitant-main"

echo Starting application...
start /b cmd /c "node main.js"

echo.
echo Application started!
echo.
echo Check the console output for:
echo 1. "[Backend] Detected server running on port: XXXX" - This shows the backend port was detected
echo 2. "[WEBSOCKET PORT FIX] Using port from main process: XXXX" - This shows the frontend is using the correct port
echo 3. "WebSocket connected successfully" - This confirms the connection was established
echo.
echo Press any key to exit...
pause > nul
