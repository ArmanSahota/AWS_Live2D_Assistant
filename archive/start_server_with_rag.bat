@echo off
echo ========================================
echo Starting Live2D Server with Vision + RAG
echo ========================================
echo.

REM Set AWS Knowledge Base environment variables
set AWS_KNOWLEDGE_BASE_ID=HVTKAK0Q86
set AWS_REGION=us-west-2
set DOCUMENTS_BUCKET_NAME=live2d-aws-backend-documentsbucket-gvqh2hzqj761
set RAG_ENABLED=true
set RAG_MODE=hybrid
set PREFER_AWS_RAG=true
set RAG_SEARCH_TYPE=SEMANTIC

echo Environment configured:
echo - Knowledge Base ID: %AWS_KNOWLEDGE_BASE_ID%
echo - AWS Region: %AWS_REGION%
echo - RAG Enabled: %RAG_ENABLED%
echo - Search Type: %RAG_SEARCH_TYPE%
echo.

echo Starting original server with Vision + RAG enhancements...
echo Features enabled:
echo - STT/TTS: Working audio processing
echo - Vision Analysis: Claude Vision API
echo - RAG Integration: AWS Knowledge Base + local fallback
echo - Manufacturing Mode: Safety protocols and technical context
echo.

echo Server will start on: http://localhost:8000
echo WebSocket endpoint: ws://localhost:8000/client-ws
echo.

REM Start the original server (which now has Vision + RAG integration)
python server.py --port 8000

echo.
echo Server stopped.
pause