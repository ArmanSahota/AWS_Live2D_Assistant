# RAG Setup - Next Steps

## ✅ Current Status
Your AWS infrastructure is now deployed successfully!

**Deployed Resources:**
- ✅ **S3 Bucket**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761`
- ✅ **HTTP API**: `https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev`
- ✅ **WebSocket**: `wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev`
- ❌ **RAG Infrastructure**: Not yet enabled (`RagEnabled: false`)

## 🚀 Step 1: Test Basic Functionality

First, let's verify the basic Claude integration works:

```bash
curl -X POST "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev/claude" \
    -H "Content-Type: application/json" \
    -d '{"text": "Hello, can you help me with manufacturing questions?"}'
```

## 📄 Step 2: Upload Sample Documents

Upload the sample manufacturing documents to your S3 bucket:

```bash
# Upload sample documents
aws s3 cp sample-docs/ s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/ --recursive

# Verify upload
aws s3 ls s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/ --recursive
```

## 🏗️ Step 3: Enable RAG Infrastructure

Now enable the RAG infrastructure (OpenSearch, IAM roles):

```bash
sam deploy --parameter-overrides EnableRagInfra=true
```

This will add:
- ✅ **OpenSearch Domain** for vector storage
- ✅ **IAM Roles** for Bedrock Knowledge Base
- ✅ **Enhanced Lambda** with RAG capabilities

## 🧠 Step 4: Create Bedrock Knowledge Base (Manual)

**Important**: Knowledge Bases cannot be created via CloudFormation, so this must be done manually.

### Option A: AWS Console (Recommended)
1. Go to [AWS Bedrock Console → Knowledge bases](https://console.aws.amazon.com/bedrock/home#/knowledge-bases)
2. Click **"Create knowledge base"**
3. **Name**: `VTuberManufacturingKB`
4. **Description**: `Manufacturing documentation for VTuber assistant`
5. **IAM Role**: Select the role created by CloudFormation (look for `BedrockKBRole`)
6. **Vector Database**: Choose OpenSearch Serverless
7. **S3 Data Source**: Point to `s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/`
8. **Chunking**: Fixed size, 300 tokens, 20% overlap
9. **Embedding Model**: `amazon.titan-embed-text-v1`

### Option B: AWS CLI
```bash
# Get the IAM role ARN from CloudFormation outputs
ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name live2d-aws-backend \
    --query 'Stacks[0].Outputs[?OutputKey==`BedrockKBRoleArn`].OutputValue' \
    --output text)

# Create Knowledge Base (after RAG infrastructure is enabled)
aws bedrock-agent create-knowledge-base \
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
            "collectionArn": "arn:aws:aoss:us-west-2:615299772411:collection/vtuber-vectors",
            "vectorIndexName": "manufacturing-index",
            "fieldMapping": {
                "vectorField": "vector",
                "textField": "text",
                "metadataField": "metadata"
            }
        }
    }'
```

## 📊 Step 5: Create Data Source and Start Ingestion

After creating the Knowledge Base:

```bash
# Get Knowledge Base ID
KB_ID=$(aws bedrock-agent list-knowledge-bases \
    --query 'knowledgeBaseSummaries[?name==`VTuberManufacturingKB`].knowledgeBaseId' \
    --output text)

# Create data source
aws bedrock-agent create-data-source \
    --knowledge-base-id $KB_ID \
    --name "ManufacturingDocuments" \
    --data-source-configuration '{
        "type": "S3",
        "s3Configuration": {
            "bucketArn": "arn:aws:s3:::live2d-aws-backend-documentsbucket-gvqh2hzqj761"
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
    }'

# Get data source ID
DS_ID=$(aws bedrock-agent list-data-sources \
    --knowledge-base-id $KB_ID \
    --query 'dataSourceSummaries[0].dataSourceId' \
    --output text)

# Start ingestion job
aws bedrock-agent start-ingestion-job \
    --knowledge-base-id $KB_ID \
    --data-source-id $DS_ID
```

## 🔧 Step 6: Update Lambda Environment

Once you have the Knowledge Base ID, update the Lambda function:

```bash
# Update Lambda with Knowledge Base ID
aws lambda update-function-configuration \
    --function-name $(aws lambda list-functions --query 'Functions[?contains(FunctionName, `ClaudeHttpFn`)].FunctionName' --output text) \
    --environment Variables="{
        MODEL_ID=arn:aws:bedrock:us-west-2:615299772411:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0,
        BEDROCK_REGION=us-west-2,
        MAX_TOKENS=2048,
        KNOWLEDGE_BASE_ID=$KB_ID,
        DOCUMENTS_BUCKET=live2d-aws-backend-documentsbucket-gvqh2hzqj761
    }"
```

## 🧪 Step 7: Test RAG Functionality

Test manufacturing-specific queries:

```bash
# Test safety protocol query
curl -X POST "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev/claude" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "What is the lockout tagout procedure?",
        "enable_rag": true
    }'

# Test troubleshooting query
curl -X POST "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev/claude" \
    -H "Content-Type: application/json" \
    -d '{
        "text": "How do I troubleshoot CNC error code E456?",
        "enable_rag": true
    }'
```

## 🎮 Step 8: Update VTuber Client Configuration

Update your `conf.yaml` to use the new RAG endpoint:

```yaml
# Update LLM configuration
LLM_PROVIDER: claude
claude:
  BASE_URL: "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev"
  MODEL: "anthropic.claude-3-7-sonnet-20250219-v1:0"

# Add RAG configuration
MANUFACTURING_RAG:
  ENABLED: true
  HTTP_BASE_URL: "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev"
  AWS_REGION: "us-west-2"
```

## 📋 Summary Checklist

- [ ] **Step 1**: Test basic Claude functionality
- [ ] **Step 2**: Upload sample documents to S3
- [ ] **Step 3**: Enable RAG infrastructure (`EnableRagInfra=true`)
- [ ] **Step 4**: Create Bedrock Knowledge Base manually
- [ ] **Step 5**: Create data source and start ingestion
- [ ] **Step 6**: Update Lambda environment with KB ID
- [ ] **Step 7**: Test RAG queries
- [ ] **Step 8**: Update VTuber client configuration

## 🎯 Expected Results

After completing these steps, your VTuber assistant will be able to:
- ✅ Answer manufacturing safety questions with specific protocols
- ✅ Provide troubleshooting steps for equipment errors
- ✅ Reference maintenance schedules and procedures
- ✅ Include source document citations in responses
- ✅ Prioritize safety-critical information

---

**Current Status**: Basic infrastructure deployed ✅  
**Next**: Follow steps 1-8 above to enable full RAG capabilities