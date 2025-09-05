#!/bin/bash
# Set AWS environment variables for the Live2D Desktop Assistant

# WebSocket URL
export VITE_WS_URL="wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev"

# HTTP Base URL
export VITE_HTTP_BASE="https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev"

# AWS Region
export VITE_AWS_REGION="us-west-2"

# Feature flags (defaults)
export VITE_FEATURE_USE_LOCAL_TTS="true"
export VITE_FEATURE_USE_LOCAL_STT="true"
export VITE_FEATURE_USE_CLOUD_FALLBACKS="true"

echo "AWS environment variables set successfully:"
echo "WS_URL: $VITE_WS_URL"
echo "HTTP_BASE: $VITE_HTTP_BASE"
echo "REGION: $VITE_AWS_REGION"
echo ""
echo "To use these variables in your current terminal session, run:"
echo "    source set_aws_env.sh"
