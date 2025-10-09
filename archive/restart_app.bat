@echo off
echo Restarting the application with a clean state...

echo Stopping any running instances of the application...
taskkill /f /im electron.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo Waiting for processes to terminate...
timeout /t 2 /nobreak >nul

echo Starting the server...
start cmd /k "python server.py"

echo Waiting for server to initialize...
timeout /t 5 /nobreak >nul

echo Starting the Electron app...
start cmd /k "npm start"

echo Application restart complete!
