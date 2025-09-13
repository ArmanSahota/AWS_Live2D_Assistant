# Finding Your AWS Endpoint URL

This guide explains how to find or create the AWS API Gateway endpoint needed for the `.env` configuration.

## Option 1: Deploy the AWS Backend (Recommended)

The most direct way to get an AWS endpoint for Claude is to deploy our provided AWS serverless backend:

1. **Prerequisites**:
   - AWS account with [Bedrock access](https://docs.aws.amazon.com/bedrock/latest/userguide/model-access.html)
   - AWS CLI installed and configured with appropriate permissions
   - [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) installed

2. **Deploy the Backend**:
   ```bash
   # Navigate to the backend directory
   cd LLM-Live2D-Desktop-Assitant-main/backend
   
   # Build and deploy the SAM application
   sam build
   sam deploy --guided
   ```

3. **Collect the Endpoint URL**:
   - After successful deployment, SAM will output several values
   - Look for the `HttpApiUrl` value - this is your endpoint
   - The URL will look like: `https://a1b2c3d4e5.execute-api.us-west-2.amazonaws.com/dev`
   - If you miss it in the output, you can find it in the AWS Console under API Gateway > APIs

4. **Update Your `.env` File**:
   ```
   HTTP_BASE=https://a1b2c3d4e5.execute-api.us-west-2.amazonaws.com/dev
   ```

## Option 2: Find an Existing Endpoint

If you or your team have already deployed the backend:

1. **Check AWS Console**:
   - Log in to the [AWS Console](https://console.aws.amazon.com/)
   - Navigate to API Gateway > APIs
   - Find the API named something like "LLMVTuberClaudeAPI" or similar
   - Copy the "Invoke URL" from the details page
   
2. **Check CloudFormation**:
   - Navigate to CloudFormation in the AWS Console
   - Find the stack named like "llm-vtuber-claude" or similar
   - Go to the "Outputs" tab
   - Look for the key "HttpApiUrl" and copy its value

3. **Ask Your Team**:
   - If someone else deployed the backend, they may have noted the endpoint URL

## Option 3: Test Your Endpoint

To verify your endpoint is working correctly:

1. **Test the Health Endpoint**:
   ```bash
   curl https://your-api-endpoint.execute-api.us-west-2.amazonaws.com/dev/health
   ```
   
   Should return: `{"status":"ok"}`

2. **Test with Python Script**:
   ```bash
   # Run the test script
   python test_claude_aws.py
   ```

## Common Issues

- **403 Forbidden**: Check your AWS permissions and ensure you have access to Bedrock
- **404 Not Found**: Verify the endpoint URL is correct, including the stage (e.g., `/dev` or `/prod`)
- **500 Internal Server Error**: Check CloudWatch logs for the Lambda function
- **Timeout**: The Lambda function might be cold-starting; try again

## Endpoint Structure

The complete endpoint structure should be:

```
https://{api-id}.execute-api.{region}.amazonaws.com/{stage}
```

Where:
- `{api-id}` is the unique API Gateway identifier
- `{region}` is the AWS region (e.g., us-west-2)
- `{stage}` is the deployment stage (typically "dev" or "prod")

Make sure to include the full URL including the stage in your `.env` file.
