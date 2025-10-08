@echo off
echo Testing Basic AWS Infrastructure...

set API_ENDPOINT=https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev
set S3_BUCKET=live2d-aws-backend-documentsbucket-gvqh2hzqj761

echo.
echo ========================================
echo Step 1: Testing Basic Claude Endpoint
echo ========================================
echo.

curl -X POST "%API_ENDPOINT%/claude" ^
    -H "Content-Type: application/json" ^
    -d "{\"text\": \"Hello, can you help me with manufacturing questions?\"}"

echo.
echo.
echo ========================================
echo Step 2: Uploading Sample Documents
echo ========================================
echo.

echo Uploading sample manufacturing documents...
aws s3 cp sample-docs/ s3://%S3_BUCKET%/ --recursive

echo.
echo Verifying upload...
aws s3 ls s3://%S3_BUCKET%/ --recursive

echo.
echo ========================================
echo Step 3: Ready for RAG Infrastructure
echo ========================================
echo.
echo Basic infrastructure is working!
echo.
echo Next steps:
echo 1. Enable RAG infrastructure: sam deploy --parameter-overrides EnableRagInfra=true
echo 2. Create Bedrock Knowledge Base manually
echo 3. Test RAG queries
echo.
echo See NEXT-STEPS.md for detailed instructions.
echo.
pause