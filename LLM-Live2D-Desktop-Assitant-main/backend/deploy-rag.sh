#!/bin/bash

# RAG Infrastructure Deployment Script
# This script deploys the enhanced SAM template with RAG capabilities

set -e

echo "🚀 Starting RAG Infrastructure Deployment..."

# Check if AWS CLI is configured
if ! aws sts get-caller-identity > /dev/null 2>&1; then
    echo "❌ AWS CLI not configured. Please run 'aws configure' first."
    exit 1
fi

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "📋 AWS Account ID: $ACCOUNT_ID"

# Set deployment parameters
STACK_NAME="live2d-aws-backend"
REGION="us-west-2"
ENV="dev"

echo "📦 Building SAM application..."
sam build

echo "🚀 Deploying SAM stack..."
sam deploy \
    --stack-name $STACK_NAME \
    --region $REGION \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --parameter-overrides \
        Env=$ENV \
        DocumentBucketName="vtuber-manufacturing-docs-$ACCOUNT_ID" \
        KnowledgeBaseName="VTuberManufacturingKB" \
        OpenSearchDomainName="vtuber-vectors-$ENV" \
    --confirm-changeset

echo "✅ Infrastructure deployment complete!"

# Get stack outputs
echo "📋 Stack Outputs:"
aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
    --output table

echo ""
echo "🔧 Next Steps:"
echo "1. Create Bedrock Knowledge Base (manual step required)"
echo "2. Upload sample manufacturing documents to S3"
echo "3. Configure Knowledge Base data source"
echo "4. Start ingestion job"
echo "5. Update Lambda environment variable with Knowledge Base ID"
echo ""
echo "📖 See aws-rag-implementation-todo.md for detailed next steps"