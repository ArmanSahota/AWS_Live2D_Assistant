@echo off
set HTTP_BASE=https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev
echo Testing AWS Claude Opus endpoint...
echo Endpoint: %HTTP_BASE%
python test_claude_opus.py