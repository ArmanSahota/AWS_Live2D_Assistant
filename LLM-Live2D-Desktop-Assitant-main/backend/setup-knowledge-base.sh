#!/bin/bash

# Bedrock Knowledge Base Setup Script
# This script creates the Knowledge Base and data source after infrastructure deployment

set -e

echo "🧠 Setting up Bedrock Knowledge Base..."

# Configuration
STACK_NAME="live2d-aws-backend"
REGION="us-west-2"
KB_NAME="VTuberManufacturingKB"

# Get stack outputs
echo "📋 Getting stack outputs..."
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
    --output text)

OPENSEARCH_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`OpenSearchDomainEndpoint`].OutputValue' \
    --output text)

ROLE_ARN=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`BedrockKBRoleArn`].OutputValue' \
    --output text)

echo "📦 S3 Bucket: $BUCKET_NAME"
echo "🔍 OpenSearch Endpoint: $OPENSEARCH_ENDPOINT"
echo "🔐 IAM Role ARN: $ROLE_ARN"

# Check if Knowledge Base already exists
echo "🔍 Checking if Knowledge Base exists..."
KB_ID=$(aws bedrock-agent list-knowledge-bases \
    --region $REGION \
    --query "knowledgeBaseSummaries[?name=='$KB_NAME'].knowledgeBaseId" \
    --output text 2>/dev/null || echo "")

if [ -n "$KB_ID" ] && [ "$KB_ID" != "None" ]; then
    echo "✅ Knowledge Base already exists with ID: $KB_ID"
else
    echo "🚀 Creating Bedrock Knowledge Base..."
    
    # Create Knowledge Base
    KB_RESPONSE=$(aws bedrock-agent create-knowledge-base \
        --region $REGION \
        --name "$KB_NAME" \
        --description "Manufacturing documentation knowledge base for VTuber assistant" \
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
                "collectionArn": "arn:aws:aoss:'$REGION':123456789012:collection/manufacturing-vectors",
                "vectorIndexName": "manufacturing-index",
                "fieldMapping": {
                    "vectorField": "vector",
                    "textField": "text",
                    "metadataField": "metadata"
                }
            }
        }')
    
    KB_ID=$(echo $KB_RESPONSE | jq -r '.knowledgeBase.knowledgeBaseId')
    echo "✅ Knowledge Base created with ID: $KB_ID"
fi

# Create S3 folder structure
echo "📁 Creating S3 folder structure..."
aws s3api put-object --bucket $BUCKET_NAME --key manuals/ --region $REGION
aws s3api put-object --bucket $BUCKET_NAME --key safety-protocols/ --region $REGION
aws s3api put-object --bucket $BUCKET_NAME --key troubleshooting/ --region $REGION
aws s3api put-object --bucket $BUCKET_NAME --key parts-catalogs/ --region $REGION

echo "✅ S3 folder structure created"

# Check if data source exists
echo "🔍 Checking if data source exists..."
DS_ID=$(aws bedrock-agent list-data-sources \
    --knowledge-base-id $KB_ID \
    --region $REGION \
    --query "dataSourceSummaries[?name=='ManufacturingDocuments'].dataSourceId" \
    --output text 2>/dev/null || echo "")

if [ -n "$DS_ID" ] && [ "$DS_ID" != "None" ]; then
    echo "✅ Data source already exists with ID: $DS_ID"
else
    echo "🚀 Creating data source..."
    
    # Create data source
    DS_RESPONSE=$(aws bedrock-agent create-data-source \
        --region $REGION \
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
    echo "✅ Data source created with ID: $DS_ID"
fi

# Update Lambda environment variable
echo "🔧 Updating Lambda environment variable..."
aws lambda update-function-configuration \
    --region $REGION \
    --function-name live2d-aws-backend-ClaudeHttpFn-* \
    --environment Variables="{MODEL_ID=arn:aws:bedrock:us-west-2:615299772411:inference-profile/us.anthropic.claude-3-7-sonnet-20250219-v1:0,BEDROCK_REGION=us-west-2,MAX_TOKENS=2048,KNOWLEDGE_BASE_ID=$KB_ID,DOCUMENTS_BUCKET=$BUCKET_NAME}" \
    2>/dev/null || echo "⚠️  Could not update Lambda environment - please update manually"

echo ""
echo "✅ Knowledge Base setup complete!"
echo ""
echo "📋 Summary:"
echo "  Knowledge Base ID: $KB_ID"
echo "  Data Source ID: $DS_ID"
echo "  S3 Bucket: $BUCKET_NAME"
echo ""
echo "🔧 Next Steps:"
echo "1. Upload sample manufacturing documents to S3 bucket folders"
echo "2. Start ingestion job: aws bedrock-agent start-ingestion-job --knowledge-base-id $KB_ID --data-source-id $DS_ID --region $REGION"
echo "3. Monitor ingestion: aws bedrock-agent list-ingestion-jobs --knowledge-base-id $KB_ID --data-source-id $DS_ID --region $REGION"
echo "4. Test RAG queries once ingestion is complete"