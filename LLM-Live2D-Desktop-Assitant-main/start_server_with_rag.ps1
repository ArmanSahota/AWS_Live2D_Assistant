# PowerShell script to start Live2D server with AWS Knowledge Base RAG
# This properly sets environment variables and starts the server

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Live2D Server with Vision + RAG" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set AWS Knowledge Base environment variables
$env:AWS_KNOWLEDGE_BASE_ID = "HVTKAK0Q86"
$env:AWS_REGION = "us-west-2"
$env:DOCUMENTS_BUCKET_NAME = "live2d-aws-backend-documentsbucket-gvqh2hzqj761"
$env:RAG_ENABLED = "true"
$env:RAG_MODE = "hybrid"
$env:PREFER_AWS_RAG = "true"
$env:RAG_SEARCH_TYPE = "SEMANTIC"

Write-Host "Environment configured:" -ForegroundColor Yellow
Write-Host "- Knowledge Base ID: $env:AWS_KNOWLEDGE_BASE_ID" -ForegroundColor White
Write-Host "- AWS Region: $env:AWS_REGION" -ForegroundColor White
Write-Host "- RAG Enabled: $env:RAG_ENABLED" -ForegroundColor White
Write-Host "- Search Type: $env:RAG_SEARCH_TYPE" -ForegroundColor White
Write-Host ""

Write-Host "Starting original server with Vision + RAG enhancements..." -ForegroundColor Yellow
Write-Host "Features enabled:" -ForegroundColor Cyan
Write-Host "- STT/TTS: Working audio processing" -ForegroundColor Green
Write-Host "- Vision Analysis: Claude Vision API" -ForegroundColor Green
Write-Host "- RAG Integration: AWS Knowledge Base + local fallback" -ForegroundColor Green
Write-Host "- Manufacturing Mode: Safety protocols and technical context" -ForegroundColor Green
Write-Host ""

Write-Host "Server will start on: http://localhost:8000" -ForegroundColor Cyan
Write-Host "WebSocket endpoint: ws://localhost:8000/client-ws" -ForegroundColor Cyan
Write-Host ""

Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

# Start the original server (which now has Vision + RAG integration)
try {
    python server.py --port 8000
} catch {
    Write-Host "Error starting server: $_" -ForegroundColor Red
} finally {
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}