@echo off
echo ========================================
echo Testing RAG-Enhanced Claude Integration
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Checking required Python packages...
python -c "import boto3, requests; print('✅ Required packages available')" 2>nul
if errorlevel 1 (
    echo WARNING: Some required packages may be missing
    echo Installing required packages...
    pip install boto3 requests
)

echo.
echo Running RAG integration test...
python test_rag_claude_integration.py

echo.
echo Test completed. Press any key to exit...
pause >nul