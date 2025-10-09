@echo off
echo ========================================
echo RAG Document Ingestion for Manufacturing
echo ========================================
echo.
echo This script will add manufacturing error documentation
echo to your RAG system for enhanced AI analysis.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking required packages...
python -c "import yaml, boto3" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install pyyaml boto3 opensearch-py requests-aws4auth
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo.
echo Starting RAG document ingestion...
echo.

REM Run the ingestion script
python add_rag_documents.py

if errorlevel 1 (
    echo.
    echo ERROR: Document ingestion failed
    echo Check the error messages above for details
) else (
    echo.
    echo SUCCESS: RAG documents have been processed!
    echo.
    echo Your manufacturing error documentation is now available
    echo for AI-powered analysis and troubleshooting.
    echo.
    echo Next steps:
    echo 1. Test the image upload feature with your heater error image
    echo 2. The AI should now provide more detailed analysis
    echo 3. Check the rag_documents_index.json file for local storage
)

echo.
echo Press any key to continue...
pause >nul