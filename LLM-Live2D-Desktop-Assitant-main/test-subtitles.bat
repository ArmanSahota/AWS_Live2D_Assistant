@echo off
echo ========================================
echo SUBTITLE DIAGNOSTIC TEST
echo ========================================
echo.
echo This script will help diagnose subtitle display issues.
echo Please follow these steps:
echo.
echo 1. Start the application with this script
echo 2. Open Developer Tools (F12 or Ctrl+Shift+I)
echo 3. Go to Console tab
echo 4. Look for [SUBTITLE DEBUG] messages
echo 5. Click "Test TTS" button in the test panel
echo 6. Check if subtitles appear
echo.
echo Starting application...
echo.

cd /d "%~dp0\LLM-Live2D-Desktop-Assitant-main"
npm start

pause