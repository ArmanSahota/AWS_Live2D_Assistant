# Environment Configuration Guide

## Configuring AWS Endpoints

The `.env` file contains placeholder values that need to be updated with real endpoint information before the application will work with AWS Bedrock Claude.

### HTTP_BASE URL

The HTTP_BASE value `https://your-aws-api-endpoint.execute-api.us-west-2.amazonaws.com/prod` is a placeholder that needs to be replaced with your actual AWS API Gateway endpoint.

### Why Use Placeholders?

1. **Security**: Real AWS endpoints contain account-specific identifiers that shouldn't be committed to source control
2. **Configuration flexibility**: The actual endpoint will be specific to your AWS deployment
3. **Environment separation**: Different environments (dev/staging/prod) would use different endpoints
4. **Best practices**: Environment variables with sensitive or deployment-specific values should use placeholders in template files

### How to Get Your Actual Endpoint

1. Deploy the AWS backend using the CloudFormation template in the `backend` directory
2. After deployment completes, find the API Gateway endpoint URL in the CloudFormation outputs
3. Copy this URL and paste it as the HTTP_BASE value in your `.env` file
4. Restart the application for the changes to take effect

### Example with Real Values

```
# AWS Bedrock Claude Configuration
HTTP_BASE=https://a1b2c3d4e5.execute-api.us-west-2.amazonaws.com/prod
AUTH_TOKEN=your_optional_auth_token_if_configured

# Feature Flags
USE_LOCAL_TTS=true
USE_LOCAL_STT=true
USE_CLOUD_FALLBACKS=false

# Server Configuration 
PORT=1025
```

## Port Configuration

The `PORT=1025` value specifies which port the local server will attempt to use. If this port is already in use, the application will automatically try the next available port (1026, 1027, etc.) thanks to the port conflict resolution we've implemented.
