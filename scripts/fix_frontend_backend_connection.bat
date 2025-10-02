@echo off
echo === Fixing Frontend-Backend Connection ===
echo.

REM Kill all Python processes to stop multiple backend instances
echo 1. Stopping all backend instances...
taskkill /F /IM python.exe 2>nul
timeout /t 2 >nul

REM Clean up port file
echo 2. Cleaning up port file...
del "LLM-Live2D-Desktop-Assitant-main\server_port.txt" 2>nul

REM Kill any Electron processes
echo 3. Stopping any running Electron apps...
taskkill /F /IM electron.exe 2>nul
timeout /t 2 >nul

REM Set the port to use consistently
echo 4. Setting consistent port (1018)...
echo SERVER_PORT=1018 > LLM-Live2D-Desktop-Assitant-main\.env
echo WEBSOCKET_PORT=1018 >> LLM-Live2D-Desktop-Assitant-main\.env

echo.
echo 5. Now start the backend and frontend in the correct order:
echo.
echo    Step 1: Start the backend FIRST
echo    - Open a new terminal
echo    - Navigate to: cd LLM-Live2D-Desktop-Assitant-main
echo    - Run: python server.py
echo    - Wait for it to show the port number (e.g., "Server is running: http://0.0.0.0:1018")
echo.
echo    Step 2: Start the frontend AFTER backend is running
echo    - Open another terminal
echo    - Navigate to: cd LLM-Live2D-Desktop-Assitant-main
echo    - Run: npm start
echo.
echo    The frontend will automatically find the backend port!
echo.
pause
