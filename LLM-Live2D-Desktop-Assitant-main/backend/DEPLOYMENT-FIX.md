# S3 Bucket Deployment Fix

## Issue
The S3 bucket creation is failing with a null pointer exception: `"Cannot invoke "String.hashCode()" because "<local4>" is null"`

## Root Cause
This error typically occurs when there's an issue with the S3 bucket configuration, often related to:
1. CloudWatch notifications (already removed)
2. Explicit bucket naming conflicts
3. AWS service internal issues

## Fix Applied
✅ **Removed explicit bucket naming** - Let AWS auto-generate the bucket name to avoid conflicts
✅ **Added tags instead** - The bucket will be tagged with the intended name for identification
✅ **Simplified bucket configuration** - Removed problematic configurations

## Deployment Steps

### Option 1: Deploy with RAG Infrastructure (Recommended)
```bash
cd LLM-Live2D-Desktop-Assitant-main/backend
sam build
sam deploy --parameter-overrides EnableRagInfra=true
```

### Option 2: Deploy Basic Infrastructure First
```bash
cd LLM-Live2D-Desktop-Assitant-main/backend
sam build
sam deploy --parameter-overrides EnableRagInfra=false
```

### Option 3: Use the Batch Script (Windows)
```bash
cd LLM-Live2D-Desktop-Assitant-main/backend
deploy-with-rag.bat
```

## If Deployment Still Fails

### 1. Check AWS Permissions
Ensure your AWS credentials have permissions for:
- S3 bucket creation
- IAM role creation
- Lambda function creation
- API Gateway creation
- OpenSearch domain creation (if EnableRagInfra=true)

### 2. Try Different Region
The error might be region-specific. Try deploying to a different region:
```bash
sam deploy --parameter-overrides EnableRagInfra=true --region us-east-1
```

### 3. Manual Rollback and Retry
```bash
aws cloudformation rollback-stack --stack-name live2d-aws-backend
# Wait for rollback to complete, then retry deployment
```

### 4. Delete and Recreate Stack
```bash
aws cloudformation delete-stack --stack-name live2d-aws-backend
# Wait for deletion to complete, then deploy fresh
sam deploy --guided
```

## After Successful Deployment

### 1. Get the S3 Bucket Name
```bash
aws cloudformation describe-stacks \
    --stack-name live2d-aws-backend \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
    --output text
```

### 2. Upload Sample Documents
```bash
# Get bucket name from outputs first
BUCKET_NAME=$(aws cloudformation describe-stacks --stack-name live2d-aws-backend --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' --output text)

# Upload sample documents
aws s3 cp sample-docs/ s3://$BUCKET_NAME/ --recursive
```

### 3. Create Bedrock Knowledge Base
This must be done manually as CloudFormation doesn't support Knowledge Bases yet:

1. Go to AWS Bedrock Console → Knowledge bases
2. Click "Create knowledge base"
3. Use the IAM role created by the stack
4. Point to the S3 bucket created by the stack
5. Configure OpenSearch as the vector database

### 4. Update Lambda Environment
```bash
# Get the Knowledge Base ID from Bedrock console, then:
aws lambda update-function-configuration \
    --function-name $(aws lambda list-functions --query 'Functions[?contains(FunctionName, `ClaudeHttpFn`)].FunctionName' --output text) \
    --environment Variables="{
        MODEL_ID=arn:aws:bedrock:us-west-2:615299772411:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0,
        BEDROCK_REGION=us-west-2,
        MAX_TOKENS=2048,
        KNOWLEDGE_BASE_ID=YOUR_KB_ID_HERE,
        DOCUMENTS_BUCKET=$BUCKET_NAME
    }"
```

## Verification

Test the deployment:
```bash
# Get API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks --stack-name live2d-aws-backend --query 'Stacks[0].Outputs[?OutputKey==`HttpBase`].OutputValue' --output text)

# Test basic functionality
curl -X POST "$API_ENDPOINT/claude" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello, test message"}'
```

## Support

If you continue to experience issues:
1. Check CloudWatch logs for the Lambda functions
2. Verify all AWS services are in the same region
3. Ensure proper IAM permissions
4. Contact AWS support if the S3 service error persists

The S3 bucket naming issue has been resolved by letting AWS auto-generate the bucket name, which should eliminate the null pointer exception.