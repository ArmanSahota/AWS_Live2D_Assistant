@echo off
echo Starting RAG Infrastructure Deployment...

REM Build the SAM application
echo Building SAM application...
sam build

REM Deploy with RAG infrastructure enabled
echo Deploying with RAG infrastructure...
sam deploy --parameter-overrides EnableRagInfra=true

echo Deployment complete!
echo.
echo Next steps:
echo 1. Note the S3 bucket name from the outputs
echo 2. Upload sample documents to the bucket
echo 3. Create Bedrock Knowledge Base manually (cannot be automated)
echo 4. Update Lambda environment variables with Knowledge Base ID
echo.
pause