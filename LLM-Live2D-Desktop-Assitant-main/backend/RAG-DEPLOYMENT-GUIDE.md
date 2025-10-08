# RAG System Deployment Guide

## 🚀 Quick Start Deployment

This guide will walk you through deploying the RAG-enhanced VTuber assistant with manufacturing knowledge base capabilities.

## Prerequisites

- ✅ AWS CLI configured with appropriate permissions
- ✅ SAM CLI installed (`pip install aws-sam-cli`)
- ✅ Python 3.11+ installed
- ✅ Access to AWS Bedrock (request access if needed)
- ✅ Bash shell (Git Bash on Windows, Terminal on Mac/Linux)

## Step 1: Deploy Infrastructure

Navigate to the backend directory and deploy the SAM stack:

```bash
cd LLM-Live2D-Desktop-Assitant-main/backend

# Build the SAM application
sam build

# Deploy with guided setup (first time)
sam deploy --guided

# Or deploy with parameters
sam deploy \
    --stack-name live2d-aws-backend \
    --region us-west-2 \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --parameter-overrides \
        Env=dev \
        DocumentBucketName="vtuber-manufacturing-docs-$(aws sts get-caller-identity --query Account --output text)" \
        KnowledgeBaseName="VTuberManufacturingKB" \
        OpenSearchDomainName="vtuber-vectors-dev"
```

## Step 2: Upload Sample Documents

Upload the sample manufacturing documents to S3:

```bash
# Get the bucket name from stack outputs
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name live2d-aws-backend \
    --region us-west-2 \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
    --output text)

# Upload sample documents
aws s3 cp sample-docs/ s3://$BUCKET_NAME/ --recursive --region us-west-2

# Verify upload
aws s3 ls s3://$BUCKET_NAME/ --recursive --region us-west-2
```

## Step 3: Create Bedrock Knowledge Base

**Note:** Knowledge Bases cannot be created via CloudFormation, so this must be done manually.

### Option A: Using AWS CLI

```bash
# Get stack outputs
ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name live2d-aws-backend \
    --region us-west-2 \
    --query 'Stacks[0].Outputs[?OutputKey==`BedrockKBRoleArn`].OutputValue' \
    --output text)

# Create Knowledge Base
KB_RESPONSE=$(aws bedrock-agent create-knowledge-base \
    --region us-west-2 \
    --name "VTuberManufacturingKB" \
    --description "Manufacturing documentation knowledge base" \
    --role-arn "$ROLE_ARN" \
    --knowledge-base-configuration '{
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": "arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v1"
        }
    }' \
    --storage-configuration '{
        "type": "OPENSEARCH_SERVERLESS",
        "opensearchServerlessConfiguration": {
            "collectionArn": "arn:aws:aoss:us-west-2:123456789012:collection/manufacturing-vectors",
            "vectorIndexName": "manufacturing-index",
            "fieldMapping": {
                "vectorField": "vector",
                "textField": "text",
                "metadataField": "metadata"
            }
        }
    }')

# Extract Knowledge Base ID
KB_ID=$(echo $KB_RESPONSE | jq -r '.knowledgeBase.knowledgeBaseId')
echo "Knowledge Base ID: $KB_ID"
```

### Option B: Using AWS Console

1. Go to AWS Bedrock Console → Knowledge bases
2. Click "Create knowledge base"
3. Name: `VTuberManufacturingKB`
4. Description: `Manufacturing documentation knowledge base`
5. Select the IAM role created by the stack
6. Choose OpenSearch Serverless as vector database
7. Configure embedding model: `amazon.titan-embed-text-v1`

## Step 4: Create Data Source

```bash
# Create data source for S3 bucket
DS_RESPONSE=$(aws bedrock-agent create-data-source \
    --region us-west-2 \
    --knowledge-base-id $KB_ID \
    --name "ManufacturingDocuments" \
    --description "Manufacturing documents from S3" \
    --data-source-configuration '{
        "type": "S3",
        "s3Configuration": {
            "bucketArn": "arn:aws:s3:::'$BUCKET_NAME'",
            "inclusionPrefixes": ["manuals/", "safety-protocols/", "troubleshooting/", "parts-catalogs/"]
        }
    }' \
    --vector-ingestion-configuration '{
        "chunkingConfiguration": {
            "chunkingStrategy": "FIXED_SIZE",
            "fixedSizeChunkingConfiguration": {
                "maxTokens": 300,
                "overlapPercentage": 20
            }
        }
    }')

DS_ID=$(echo $DS_RESPONSE | jq -r '.dataSource.dataSourceId')
echo "Data Source ID: $DS_ID"
```

## Step 5: Start Ingestion Job

```bash
# Start ingestion job
aws bedrock-agent start-ingestion-job \
    --knowledge-base-id $KB_ID \
    --data-source-id $DS_ID \
    --region us-west-2

# Monitor ingestion progress
aws bedrock-agent list-ingestion-jobs \
    --knowledge-base-id $KB_ID \
    --data-source-id $DS_ID \
    --region us-west-2
```

## Step 6: Update Lambda Environment

```bash
# Update Lambda function with Knowledge Base ID
aws lambda update-function-configuration \
    --region us-west-2 \
    --function-name $(aws lambda list-functions --region us-west-2 --query 'Functions[?contains(FunctionName, `ClaudeHttpFn`)].FunctionName' --output text) \
    --environment Variables="{
        MODEL_ID=arn:aws:bedrock:us-west-2:615299772411:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0,
        BEDROCK_REGION=us-west-2,
        MAX_TOKENS=2048,
        KNOWLEDGE_BASE_ID=$KB_ID,
        DOCUMENTS_BUCKET=$BUCKET_NAME
    }"
```

## Step 7: Test RAG System

Get your API endpoint:

```bash
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name live2d-aws-backend \
    --region us-west-2 \
    --query 'Stacks[0].Outputs[?OutputKey==`HttpBase`].OutputValue' \
    --output text)

echo "API Endpoint: $API_ENDPOINT"
```

Test with curl:

```bash
# Test basic functionality
curl -X POST "$API_ENDPOINT/claude" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "What is the lockout tagout procedure?",
        "enable_rag": true
    }'

# Test troubleshooting query
curl -X POST "$API_ENDPOINT/claude" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "How do I troubleshoot CNC error code E456?",
        "enable_rag": true
    }'
```

## Step 8: Update VTuber Client Configuration

Update your `conf.yaml` to use the new RAG endpoint:

```yaml
# Update LLM configuration
LLM_PROVIDER: claude
claude:
  BASE_URL: "https://your-api-id.execute-api.us-west-2.amazonaws.com/dev"
  MODEL: "anthropic.claude-3-7-sonnet-20250219-v1:0"

# Add RAG configuration
MANUFACTURING_RAG:
  ENABLED: true
  HTTP_BASE_URL: "https://your-api-id.execute-api.us-west-2.amazonaws.com/dev"
  KNOWLEDGE_BASE_ID: "your-knowledge-base-id"
  AWS_REGION: "us-west-2"
```

## Verification Checklist

- [ ] Infrastructure deployed successfully
- [ ] S3 bucket created with sample documents
- [ ] OpenSearch domain running
- [ ] Knowledge Base created
- [ ] Data source configured
- [ ] Ingestion job completed successfully
- [ ] Lambda function updated with KB ID
- [ ] RAG queries return enhanced responses
- [ ] VTuber client connects to new endpoint

## Sample Test Queries

Once deployed, test these manufacturing-specific queries:

1. **Safety Protocols:**
   - "What is the lockout tagout procedure?"
   - "What safety equipment is required for CNC operation?"

2. **Troubleshooting:**
   - "How do I fix CNC error code E456?"
   - "What causes conveyor belt slipping?"

3. **Maintenance:**
   - "What is the maintenance schedule for the conveyor?"
   - "How do I adjust belt tension?"

4. **Parts Information:**
   - "What is the part number for the drive belt?"
   - "What type of coolant should I use?"

## Monitoring and Maintenance

### CloudWatch Metrics
- Monitor Lambda execution times
- Track Bedrock API calls
- Watch for error rates

### Cost Monitoring
- Set up billing alerts
- Monitor OpenSearch usage
- Track Bedrock token consumption

### Regular Maintenance
- Update documents in S3 as needed
- Re-run ingestion jobs for new content
- Monitor Knowledge Base performance

## Troubleshooting

### Common Issues

**Knowledge Base creation fails:**
- Verify IAM role permissions
- Check Bedrock service access
- Ensure OpenSearch domain is running

**Ingestion job fails:**
- Check S3 bucket permissions
- Verify document formats are supported
- Review CloudWatch logs

**RAG queries return no context:**
- Verify ingestion job completed
- Check document chunking settings
- Test with simpler queries

**Lambda timeouts:**
- Increase timeout settings
- Optimize retrieval queries
- Check network connectivity

## Support

For issues with deployment:
1. Check CloudWatch logs for Lambda functions
2. Verify all AWS services are in the same region
3. Ensure proper IAM permissions
4. Review the troubleshooting section in aws-rag-implementation-todo.md

## Next Steps

After successful deployment:
1. Add more manufacturing documents
2. Fine-tune chunking parameters
3. Implement user feedback collection
4. Set up automated document updates
5. Consider adding more specialized knowledge bases

---

**Estimated Deployment Time:** 30-45 minutes
**Monthly AWS Cost:** ~$55-60 (depending on usage)