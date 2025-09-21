@echo off
echo ============================================================
echo FRONTEND-BACKEND CONNECTION FIX
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Step 1: Running connection diagnostic...
echo ----------------------------------------
python diagnose_connection.py
if errorlevel 1 (
    echo.
    echo Diagnostic found issues. Continuing with fix...
)

echo.
echo Step 2: Running quick connection test...
echo ----------------------------------------
python quick_connect_test.py
if errorlevel 1 (
    echo.
    echo ERROR: Server is not running!
    echo.
    echo Starting server now...
    start cmd /k "cd /d %~dp0 && python server.py"
    echo.
    echo Waiting 5 seconds for server to start...
    timeout /t 5 /nobreak >nul
    echo.
    echo Retrying connection test...
    python quick_connect_test.py
)

echo.
echo Step 3: Testing WebSocket with test script...
echo ----------------------------------------
python test_websocket_audio.py
if errorlevel 1 (
    echo.
    echo WebSocket test failed. Check the logs above.
)

echo.
echo ============================================================
echo FIX COMPLETE
echo ============================================================
echo.
echo Next steps:
echo 1. If server wasn't running, it has been started
echo 2. The server_port.txt file has been updated
echo 3. Refresh the Electron app (Ctrl+R)
echo 4. Check the browser console for connection status
echo.
echo If still having issues:
echo - Check Windows Firewall settings
echo - Try running as Administrator
echo - Check if another application is using the port
echo.
pause