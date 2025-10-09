@echo off
echo Restarting the application with all fixes applied...

echo Stopping any running instances of the application...
taskkill /f /im electron.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo Waiting for processes to terminate...
timeout /t 3 /nobreak >nul

echo Clearing cache...
if exist ".\LLM-Live2D-Desktop-Assitant-main\cache" (
    rmdir /s /q ".\LLM-Live2D-Desktop-Assitant-main\cache"
    mkdir ".\LLM-Live2D-Desktop-Assitant-main\cache"
)

echo Setting debug log level...
set LOGURU_LEVEL=DEBUG

echo Starting the server...
cd LLM-Live2D-Desktop-Assitant-main
start cmd /k "python server.py"

echo Waiting for server to initialize...
timeout /t 7 /nobreak >nul

echo Starting the Electron app...
start cmd /k "npm start"

echo Application restart complete!
echo.
echo If you still experience issues:
echo 1. Check the browser console (F12) for any errors
echo 2. Look for "model2 is not available" or "Using fallback audio playback" messages
echo 3. Make sure your system's audio output is working and not muted
echo.
echo See DEBUG_README.md and AUDIO_FIX_README.md for more troubleshooting tips.
