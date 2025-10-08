@echo off
echo Fixing failed CloudFormation deployment...

echo.
echo Step 1: Manually delete the failed S3 bucket from AWS Console
echo Go to: https://s3.console.aws.amazon.com/s3/buckets
echo Look for any bucket with "live2d" or "vtuber" in the name
echo Delete it manually if it exists
echo.
pause

echo.
echo Step 2: Rolling back the CloudFormation stack...
aws cloudformation rollback-stack --stack-name live2d-aws-backend
echo Waiting for rollback to complete...

:wait_rollback
timeout /t 10 /nobreak >nul
aws cloudformation describe-stacks --stack-name live2d-aws-backend --query "Stacks[0].StackStatus" --output text > temp_status.txt
set /p STACK_STATUS=<temp_status.txt
del temp_status.txt

echo Current status: %STACK_STATUS%

if "%STACK_STATUS%"=="UPDATE_ROLLBACK_COMPLETE" goto rollback_complete
if "%STACK_STATUS%"=="ROLLBACK_COMPLETE" goto rollback_complete
if "%STACK_STATUS%"=="UPDATE_ROLLBACK_FAILED" goto rollback_failed

goto wait_rollback

:rollback_failed
echo.
echo Rollback failed. Let's try deleting and recreating the stack...
echo.
aws cloudformation delete-stack --stack-name live2d-aws-backend
echo Waiting for stack deletion...

:wait_delete
timeout /t 10 /nobreak >nul
aws cloudformation describe-stacks --stack-name live2d-aws-backend 2>nul
if errorlevel 1 goto stack_deleted
echo Stack still exists, waiting...
goto wait_delete

:stack_deleted
echo Stack deleted successfully!
goto deploy_fresh

:rollback_complete
echo Rollback completed successfully!

echo.
echo Step 3: Deploying fresh stack...
:deploy_fresh
echo Building SAM application...
sam build

echo Deploying without RAG infrastructure first...
sam deploy --parameter-overrides EnableRagInfra=false

echo.
echo Deployment complete! 
echo.
echo To enable RAG later, run:
echo sam deploy --parameter-overrides EnableRagInfra=true
echo.
pause