@echo off
echo ==================================================
echo Starting VTuber Assistant (No Security Mode)
echo ==================================================
echo.

REM Kill any existing processes
echo Cleaning up old processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM electron.exe 2>nul
timeout /t 2 /nobreak >nul

REM Start Python server in background
echo Starting Python server...
cd /d "%~dp0LLM-Live2D-Desktop-Assitant-main"
start /B python server.py
echo Python server starting...

REM Wait for server to initialize
echo Waiting for server to start (5 seconds)...
timeout /t 5 /nobreak >nul

REM Start Electron app
echo Starting Electron app...
npm start

echo.
echo ==================================================
echo App should be running now!
echo ==================================================
echo.
echo If you see errors:
echo 1. Check Python is installed: python --version
echo 2. Check Node is installed: node --version
echo 3. Install dependencies:
echo    pip install -r requirements.txt
echo    npm install
echo.
pause