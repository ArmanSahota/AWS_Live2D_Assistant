@echo off
echo Starting VTuber in debug mode with enhanced logging...

:: Set the log level to debug
set LOGURU_LEVEL=DEBUG

:: Start the server with debug logging
start cmd /k "python server.py"

:: Wait for server to initialize
timeout /t 5 /nobreak >nul

:: Start the Electron app
start cmd /k "npm start"

echo VTuber started in debug mode!
echo Check the terminal windows for detailed logs including speech recognition output.
