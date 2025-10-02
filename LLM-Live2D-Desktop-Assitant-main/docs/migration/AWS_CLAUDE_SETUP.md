# AWS Claude Integration Setup

This document explains how to set up and use the AWS Claude integration for the LLM-Live2D-Desktop-Assistant project.

## Overview

The AWS Claude integration allows you to use Claude via AWS Bedrock instead of directly using the Anthropic API. This has several advantages:

1. **Security**: API keys are managed by AWS, not stored in client code
2. **Cost Control**: AWS Bedrock usage can be monitored and controlled
3. **Scalability**: AWS infrastructure handles scaling
4. **Customization**: The Lambda function can be enhanced with additional logic

## Prerequisites

1. An AWS account with access to AWS Bedrock
2. AWS CLI installed and configured
3. AWS SAM CLI installed
4. Access to Claude models in AWS Bedrock (you may need to request access)

## Deployment Steps

### 1. Deploy the AWS SAM Template

The `backend/template.yml` file contains the AWS SAM template that defines the serverless backend. To deploy it:

```bash
cd LLM-Live2D-Desktop-Assitant-main/backend
sam build
sam deploy --guided
```

Follow the prompts to complete the deployment. When asked for parameters:
- `Env`: Use `dev` for development or `prod` for production

After deployment, SAM will output the WebSocket URL and HTTP Base URL. Make note of these URLs.

### 2. Configure Environment Variables

Update your environment variables to use the AWS HTTP endpoint:

#### Windows
Edit `set_aws_env.bat` to include the HTTP Base URL from the SAM deployment:

```batch
set VITE_HTTP_BASE=https://your-api-gateway-url.execute-api.us-west-2.amazonaws.com/dev
```

Then run:
```batch
call set_aws_env.bat
```

#### macOS/Linux
Edit `set_aws_env.sh` to include the HTTP Base URL from the SAM deployment:

```bash
export VITE_HTTP_BASE="https://your-api-gateway-url.execute-api.us-west-2.amazonaws.com/dev"
```

Then run:
```bash
source set_aws_env.sh
```

### 3. Update Configuration

Ensure your `conf.yaml` file is configured to use the AWS HTTP endpoint:

```yaml
LLM_PROVIDER: "claude"
claude:
  BASE_URL: "https://your-api-gateway-url.execute-api.us-west-2.amazonaws.com/dev"
  # No API key needed when using the AWS HTTP endpoint
  LLM_API_KEY: ""
  MODEL: "claude-3-haiku-20240307"
  VERBOSE: False
```

## Testing the Connection

You can test the AWS Claude integration using the provided test script:

```bash
python test_claude_aws.py
```

This script will:
1. Test the health endpoint
2. Test the Claude endpoint with a simple prompt
3. Test the Claude endpoint with a system prompt

## How It Works

### AWS Backend

The AWS backend consists of:

1. **API Gateway HTTP API**: Provides HTTP endpoints for Claude and health checks
2. **Lambda Functions**:
   - `ClaudeHttpFn`: Handles Claude API requests by proxying them to Amazon Bedrock
   - `HealthFunction`: Simple health check endpoint
3. **DynamoDB Tables**: For storing WebSocket connections and session data

### Python Client

The `claude.py` file has been modified to use HTTP requests to the AWS endpoint instead of the Anthropic SDK. It:

1. Sends requests to the `/claude` endpoint
2. Includes the system prompt and conversation history
3. Simulates streaming by yielding characters one by one

### Enhanced Features

The AWS Lambda function supports:

1. **System Prompts**: Set the system prompt for Claude
2. **Conversation History**: Send the full conversation history
3. **Configurable Parameters**: Set max tokens and other parameters

## Troubleshooting

### Common Issues

1. **HTTP 403 Forbidden**: Check your AWS permissions and ensure you have access to Bedrock
2. **HTTP 500 Internal Server Error**: Check the Lambda logs in CloudWatch
3. **Connection Timeout**: Check your network connection and AWS region

### Viewing Logs

To view the Lambda function logs:

```bash
cd backend
sam logs -n ClaudeHttpFn --tail
```

## Future Enhancements

1. **Streaming Responses**: Implement streaming using WebSockets
2. **Authentication**: Add Cognito authentication
3. **Additional Endpoints**: Add endpoints for TTS and other features
