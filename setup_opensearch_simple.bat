@echo off
echo ========================================
echo OpenSearch Serverless Collection Setup
echo ========================================
echo.

echo Checking AWS CLI...
aws --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: AWS CLI is not installed or not in PATH
    echo Please install AWS CLI and configure credentials
    pause
    exit /b 1
)

echo AWS CLI found. Setting up OpenSearch Serverless collection...
echo.

set COLLECTION_NAME=manufacturing-kb
set REGION=us-west-2

echo Creating network security policy...
aws opensearchserverless create-security-policy ^
    --name "%COLLECTION_NAME%-network-policy" ^
    --type network ^
    --policy "[{\"Rules\":[{\"Resource\":[\"collection/%COLLECTION_NAME%\"],\"ResourceType\":\"collection\"}],\"AllowFromPublic\":true}]" ^
    --region %REGION%

if errorlevel 1 (
    echo Network policy may already exist, continuing...
)

echo.
echo Creating encryption security policy...
aws opensearchserverless create-security-policy ^
    --name "%COLLECTION_NAME%-encryption-policy" ^
    --type encryption ^
    --policy "[{\"Rules\":[{\"Resource\":[\"collection/%COLLECTION_NAME%\"],\"ResourceType\":\"collection\"}],\"AWSOwnedKey\":true}]" ^
    --region %REGION%

if errorlevel 1 (
    echo Encryption policy may already exist, continuing...
)

echo.
echo Getting AWS account ID...
for /f "tokens=*" %%i in ('aws sts get-caller-identity --query Account --output text') do set ACCOUNT_ID=%%i
echo Account ID: %ACCOUNT_ID%

echo.
echo Creating data access policy...
aws opensearchserverless create-access-policy ^
    --name "%COLLECTION_NAME%-access-policy" ^
    --type data ^
    --policy "[{\"Rules\":[{\"Resource\":[\"collection/%COLLECTION_NAME%\"],\"Permission\":[\"aoss:CreateCollectionItems\",\"aoss:DeleteCollectionItems\",\"aoss:UpdateCollectionItems\",\"aoss:DescribeCollectionItems\"],\"ResourceType\":\"collection\"},{\"Resource\":[\"index/%COLLECTION_NAME%/*\"],\"Permission\":[\"aoss:CreateIndex\",\"aoss:DeleteIndex\",\"aoss:UpdateIndex\",\"aoss:DescribeIndex\",\"aoss:ReadDocument\",\"aoss:WriteDocument\"],\"ResourceType\":\"index\"}],\"Principal\":[\"arn:aws:iam::%ACCOUNT_ID%:root\",\"arn:aws:iam::%ACCOUNT_ID%:role/BedrockKnowledgeBaseRole\"]}]" ^
    --region %REGION%

if errorlevel 1 (
    echo Data access policy may already exist, continuing...
)

echo.
echo Creating OpenSearch Serverless collection...
aws opensearchserverless create-collection ^
    --name %COLLECTION_NAME% ^
    --type VECTORSEARCH ^
    --description "Manufacturing Knowledge Base vector collection" ^
    --region %REGION%

if errorlevel 1 (
    echo Collection may already exist, checking status...
)

echo.
echo Waiting for collection to become active...
:wait_loop
aws opensearchserverless batch-get-collection --names %COLLECTION_NAME% --region %REGION% --query "collectionDetails[0].status" --output text > temp_status.txt
set /p STATUS=<temp_status.txt
del temp_status.txt

echo Collection status: %STATUS%

if "%STATUS%"=="ACTIVE" (
    echo.
    echo ✅ Collection is now ACTIVE!
    goto collection_ready
)

if "%STATUS%"=="FAILED" (
    echo.
    echo ❌ Collection creation failed
    goto end
)

echo Waiting 30 seconds...
timeout /t 30 /nobreak >nul
goto wait_loop

:collection_ready
echo.
echo Getting collection endpoint...
for /f "tokens=*" %%i in ('aws opensearchserverless batch-get-collection --names %COLLECTION_NAME% --region %REGION% --query "collectionDetails[0].collectionEndpoint" --output text') do set ENDPOINT=%%i

echo.
echo ========================================
echo ✅ OpenSearch Collection Setup Complete!
echo ========================================
echo Collection Name: %COLLECTION_NAME%
echo Collection Endpoint: %ENDPOINT%
echo Collection ARN: arn:aws:aoss:%REGION%:%ACCOUNT_ID%:collection/%COLLECTION_NAME%
echo.
echo 📋 Next Steps:
echo 1. Run the RAG infrastructure setup:
echo    python setup_rag_infrastructure.py
echo 2. Test the integration:
echo    python test_rag_integration.py
echo.

:end
pause