# Manual Fix for Failed S3 Bucket Deployment

## Current Issue
The S3 bucket `DocumentsBucket` is in a `DELETE_FAILED` state with error: "The specified bucket is not valid"

## Quick Fix Steps

### Step 1: Manual S3 Bucket Cleanup
1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/s3/buckets)
2. Look for any bucket with names containing:
   - `live2d`
   - `vtuber`
   - `manufacturing`
   - Or any bucket created today
3. **Delete any such buckets manually**
4. **Empty the bucket first if it contains objects, then delete**

### Step 2: Fix CloudFormation Stack

**Option A: Rollback and Retry**
```bash
# Rollback the stack
aws cloudformation rollback-stack --stack-name live2d-aws-backend

# Wait for rollback to complete (check in AWS Console)
# Then retry deployment
sam deploy --parameter-overrides EnableRagInfra=false
```

**Option B: Delete and Recreate (Recommended)**
```bash
# Delete the entire stack
aws cloudformation delete-stack --stack-name live2d-aws-backend

# Wait for deletion to complete (5-10 minutes)
# Check status with:
aws cloudformation describe-stacks --stack-name live2d-aws-backend
# Should return "Stack does not exist" error when fully deleted

# Deploy fresh
sam build
sam deploy --guided
```

### Step 3: Deploy Without RAG First
To avoid complications, deploy the basic infrastructure first:

```bash
sam deploy --parameter-overrides EnableRagInfra=false
```

This will create:
- ✅ Basic Lambda functions
- ✅ API Gateway
- ✅ S3 bucket (auto-named)
- ❌ No OpenSearch or RAG infrastructure

### Step 4: Enable RAG Later
Once the basic deployment works:

```bash
sam deploy --parameter-overrides EnableRagInfra=true
```

## Alternative: Use the Automated Script

Run the automated fix script:
```bash
cd LLM-Live2D-Desktop-Assitant-main/backend
fix-failed-deployment.bat
```

This script will:
1. Guide you through manual S3 cleanup
2. Automatically rollback the CloudFormation stack
3. Deploy a fresh stack

## Verification

After successful deployment:

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name live2d-aws-backend --query 'Stacks[0].StackStatus'

# Get API endpoint
aws cloudformation describe-stacks --stack-name live2d-aws-backend --query 'Stacks[0].Outputs[?OutputKey==`HttpBase`].OutputValue' --output text

# Test the endpoint
curl -X POST "YOUR_API_ENDPOINT/claude" -H "Content-Type: application/json" -d '{"text": "Hello test"}'
```

## Why This Happened

The S3 bucket got into an invalid state due to:
1. **Naming conflicts** - Explicit bucket names can conflict
2. **CloudFormation race conditions** - S3 service internal issues
3. **Previous failed deployments** - Leftover resources

## Prevention

The template has been updated to:
- ✅ Use auto-generated bucket names
- ✅ Simplified S3 configuration
- ✅ Conditional RAG infrastructure
- ✅ Better error handling

## Next Steps After Fix

1. **Basic deployment working** ✅
2. **Upload sample documents** to the S3 bucket
3. **Create Bedrock Knowledge Base** manually
4. **Enable RAG infrastructure** with `EnableRagInfra=true`
5. **Test manufacturing queries**

---

**TL;DR:** Delete any failed S3 buckets manually in AWS Console, then run `fix-failed-deployment.bat` or delete/recreate the CloudFormation stack.