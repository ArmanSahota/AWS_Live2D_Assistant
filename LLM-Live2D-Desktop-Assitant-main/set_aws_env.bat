@echo off
REM Set AWS environment variables for the Live2D Desktop Assistant

REM WebSocket URL
set VITE_WS_URL=wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev

REM HTTP Base URL
set VITE_HTTP_BASE=https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev

REM AWS Region
set VITE_AWS_REGION=us-west-2

REM Feature flags (defaults)
set VITE_FEATURE_USE_LOCAL_TTS=true
set VITE_FEATURE_USE_LOCAL_STT=true
set VITE_FEATURE_USE_CLOUD_FALLBACKS=true

echo AWS environment variables set successfully:
echo WS_URL: %VITE_WS_URL%
echo HTTP_BASE: %VITE_HTTP_BASE%
echo REGION: %VITE_AWS_REGION%
echo.
echo To use these variables in your current terminal session, run:
echo     call set_aws_env.bat
