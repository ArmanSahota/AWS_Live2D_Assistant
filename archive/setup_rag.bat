@echo off
echo ========================================
echo Manufacturing VTuber RAG Setup
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Checking required packages...
python -c "import boto3, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install boto3 requests
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Step 1: Setting up OpenSearch Collection
echo ========================================
echo.
echo First, we need to create an OpenSearch Serverless collection
echo for the Bedrock Knowledge Base.
echo.
set /p opensearch="Create OpenSearch collection? (y/n): "
if /i "%opensearch%"=="y" (
    echo.
    echo Creating OpenSearch Serverless collection using AWS CLI...
    call setup_opensearch_simple.bat
    if errorlevel 1 (
        echo.
        echo WARNING: OpenSearch setup had issues.
        echo Trying Python approach as fallback...
        python setup_opensearch_collection.py
        if errorlevel 1 (
            echo.
            echo WARNING: Both approaches failed.
            echo You may need to create the collection manually in AWS Console.
            echo.
        )
    ) else (
        echo.
        echo SUCCESS: OpenSearch collection created!
        echo.
    )
)

echo.
echo ========================================
echo Step 2: Setting up RAG Infrastructure
echo ========================================
echo.
echo This will:
echo - Check your AWS resources
echo - Upload sample documents
echo - Create Bedrock Knowledge Base
echo - Configure RAG settings
echo.
set /p confirm="Continue with RAG setup? (y/n): "
if /i not "%confirm%"=="y" (
    echo Setup cancelled.
    pause
    exit /b 0
)

echo.
echo Running RAG infrastructure setup...
python setup_rag_infrastructure.py
if errorlevel 1 (
    echo.
    echo WARNING: Setup encountered issues.
    echo Check the output above for details.
    echo You may need to complete some steps manually.
    echo.
) else (
    echo.
    echo SUCCESS: RAG infrastructure setup completed!
    echo.
)

echo.
echo ========================================
echo Step 3: Testing RAG Integration
echo ========================================
echo.
set /p test="Run integration tests? (y/n): "
if /i "%test%"=="y" (
    echo.
    echo Running RAG integration tests...
    python test_rag_integration.py
    if errorlevel 1 (
        echo.
        echo Some tests failed. Check the report above.
        echo.
    ) else (
        echo.
        echo All tests passed! RAG system is ready.
        echo.
    )
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Upload your manufacturing documents to S3
echo 2. Test the RAG functionality with sample queries
echo 3. Integrate with your VTuber assistant
echo.
echo Documentation:
echo - RAG-SETUP-GUIDE.md - Complete setup guide
echo - setup_opensearch_collection.py - OpenSearch collection setup
echo - setup_rag_infrastructure.py - RAG infrastructure setup
echo - manufacturing_rag_implementation.py - RAG client code
echo - test_rag_integration.py - Test and validation script
echo.
echo Your AWS Infrastructure:
echo - HTTP Base: https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev
echo - WebSocket: wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev
echo - S3 Bucket: live2d-aws-backend-documentsbucket-gvqh2hzqj761
echo - Region: us-west-2
echo.
pause