#!/bin/bash

# Upload Sample Manufacturing Documents Script
# This script uploads sample documents to the S3 bucket for RAG testing

set -e

echo "📄 Uploading sample manufacturing documents..."

# Configuration
STACK_NAME="live2d-aws-backend"
REGION="us-west-2"

# Get S3 bucket name from stack outputs
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name $STACK_NAME \
    --region $REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
    --output text)

echo "📦 S3 Bucket: $BUCKET_NAME"

# Check if sample docs directory exists
if [ ! -d "sample-docs" ]; then
    echo "❌ Sample docs directory not found. Please run this script from the backend directory."
    exit 1
fi

# Upload safety protocols
echo "🔒 Uploading safety protocols..."
aws s3 cp sample-docs/safety-protocols/ s3://$BUCKET_NAME/safety-protocols/ \
    --recursive \
    --region $REGION

# Upload troubleshooting guides
echo "🔧 Uploading troubleshooting guides..."
aws s3 cp sample-docs/troubleshooting/ s3://$BUCKET_NAME/troubleshooting/ \
    --recursive \
    --region $REGION

# Upload manuals
echo "📖 Uploading manuals..."
aws s3 cp sample-docs/manuals/ s3://$BUCKET_NAME/manuals/ \
    --recursive \
    --region $REGION

# List uploaded files
echo "✅ Upload complete! Files in S3:"
aws s3 ls s3://$BUCKET_NAME/ --recursive --region $REGION

echo ""
echo "📋 Next Steps:"
echo "1. Run setup-knowledge-base.sh to create the Knowledge Base"
echo "2. Start ingestion job to process these documents"
echo "3. Test RAG queries once ingestion is complete"
echo ""
echo "Sample test queries:"
echo "- 'What is the lockout tagout procedure?'"
echo "- 'How do I troubleshoot CNC error code E456?'"
echo "- 'What is the maintenance schedule for the conveyor belt?'"