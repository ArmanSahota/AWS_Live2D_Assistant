@echo off
echo ===================================
echo   VTUBER APPLICATION STARTER
echo ===================================
echo.

REM Kill any existing processes
echo [1/5] Cleaning up existing processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM electron.exe 2>nul
timeout /t 2 >nul

REM Clean up port file
echo [2/5] Cleaning up port file...
del "LLM-Live2D-Desktop-Assitant-main\server_port.txt" 2>nul

REM Set the port to use consistently
echo [3/5] Setting consistent port (1018)...
echo SERVER_PORT=1018 > LLM-Live2D-Desktop-Assitant-main\.env
echo WEBSOCKET_PORT=1018 >> LLM-Live2D-Desktop-Assitant-main\.env

REM Start the backend server
echo [4/5] Starting backend server...
echo.
echo Starting Python server on port 1018...
start cmd /k "cd LLM-Live2D-Desktop-Assitant-main && python server.py"

REM Wait for server to start
echo Waiting for server to initialize (10 seconds)...
timeout /t 10 >nul

REM Start the frontend
echo [5/5] Starting frontend application...
echo.
echo Starting Electron frontend...
start cmd /k "cd LLM-Live2D-Desktop-Assitant-main && npm start"

echo.
echo ===================================
echo   APPLICATION STARTED
echo ===================================
echo.
echo If you encounter connection issues:
echo 1. Run: node test_connection_diagnostic.js
echo 2. Check the backend console for errors
echo 3. Verify the server is running on port 1018
echo.
echo To stop the application, close both terminal windows
echo or press Ctrl+C in each terminal.
echo.
pause
