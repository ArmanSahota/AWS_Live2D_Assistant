# AWS Knowledge Base Setup - Quick Start Guide

This guide walks you through setting up AWS Knowledge Base for your Live2D VTuber Assistant step-by-step.

## 📋 Prerequisites Checklist

### 1. AWS Account Setup
- [ ] AWS Account created
- [ ] AWS CLI installed
- [ ] SAM CLI installed
- [ ] Python 3.11+ installed

### 2. Required Permissions
Your AWS user needs these permissions:
- [ ] CloudFormation (create/update stacks)
- [ ] Lambda (create/manage functions)
- [ ] S3 (create buckets, upload files)
- [ ] OpenSearch (create domains)
- [ ] Bedrock (create knowledge bases)
- [ ] IAM (create roles and policies)

## 🚀 Step-by-Step Setup

### Step 1: Install AWS Tools

#### Windows:
```powershell
# Install AWS CLI
winget install Amazon.AWSCLI

# Install SAM CLI
winget install Amazon.SAM-CLI

# Or use pip
pip install aws-sam-cli
```

#### macOS/Linux:
```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install SAM CLI
pip install aws-sam-cli
```

### Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI with your credentials
aws configure

# You'll be prompted for:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-west-2
# Default output format: json
```

**Alternative: Use AWS SSO or Environment Variables**
```bash
# Environment variables method
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

### Step 3: Verify AWS Setup

```bash
# Test AWS CLI
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDACKCEVSQ6C2EXAMPLE",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/YourUsername"
# }
```

### Step 4: Install Python Dependencies

```bash
cd LLM-Live2D-Desktop-Assitant-main
pip install boto3 pyyaml
```

### Step 5: Deploy AWS Infrastructure

#### Option A: Automated Deployment (Recommended)
```bash
# Run the automated deployment script
python deploy_aws_rag.py --region us-west-2 --stack-name live2d-aws-backend

# This will:
# ✅ Deploy CloudFormation stack
# ✅ Create OpenSearch domain
# ✅ Set up S3 bucket
# ✅ Create Knowledge Base
# ✅ Upload sample documents
# ✅ Configure Lambda functions
# ✅ Generate .env file
```

#### Option B: Manual Step-by-Step
```bash
# 1. Deploy infrastructure only
python deploy_aws_rag.py --skip-kb --skip-docs

# 2. Create Knowledge Base manually (see Manual Setup section)

# 3. Upload documents
python deploy_aws_rag.py --skip-deploy --skip-kb

# 4. Test the setup
python test_aws_kb_integration.py --test all
```

### Step 6: Verify Deployment

```bash
# Check CloudFormation stack
aws cloudformation describe-stacks --stack-name live2d-aws-backend

# Test Knowledge Base
python test_aws_kb_integration.py --test aws-kb

# Test enhanced server
python run_enhanced_server.py
```

## 🔧 Manual Knowledge Base Setup (If Automated Fails)

### 1. Go to AWS Bedrock Console
1. Open [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to **Knowledge Bases** → **Create Knowledge Base**

### 2. Configure Knowledge Base
```yaml
Name: live2d-manufacturing-kb
Description: Manufacturing documentation for Live2D VTuber Assistant
```

### 3. Set Up Data Source
```yaml
Data Source Type: S3
S3 URI: s3://your-bucket-name/manufacturing/
Chunking Strategy: Fixed Size
Chunk Size: 300 tokens
Overlap: 20%
```

### 4. Configure Vector Store
```yaml
Vector Database: OpenSearch Serverless
Collection Name: Use the one from CloudFormation
Index Name: manufacturing-docs-index
```

### 5. Set Embedding Model
```yaml
Embedding Model: amazon.titan-embed-text-v1
```

## 📁 Document Upload

### Automated Upload
```bash
# Upload sample manufacturing documents
python deploy_aws_rag.py --skip-deploy --skip-kb --skip-test
```

### Manual Upload
```bash
# Upload to S3
aws s3 cp rag_documents/ s3://your-bucket-name/manufacturing/ --recursive

# Trigger ingestion job (replace with your IDs)
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id your-kb-id \
  --data-source-id your-data-source-id
```

## 🧪 Testing Your Setup

### 1. Test AWS Knowledge Base Directly
```bash
python test_aws_kb_integration.py --test aws-kb
```

### 2. Test Enhanced Server Integration
```bash
# Start the server
python run_enhanced_server.py

# In another terminal, test the endpoint
curl -X POST http://localhost:8000/claude \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What should I do for heater error 103?",
    "enable_rag": true
  }'
```

### 3. Test Health Endpoints
```bash
# Server health
curl http://localhost:8000/health

# RAG system health
curl http://localhost:8000/rag/health
```

## 🔍 Troubleshooting Common Issues

### Issue 1: AWS Permissions Error
```bash
# Error: User is not authorized to perform: bedrock:CreateKnowledgeBase
# Solution: Add Bedrock permissions to your IAM user
```

**Fix:**
1. Go to IAM Console → Users → Your User → Permissions
2. Add policy: `AmazonBedrockFullAccess`
3. Or create custom policy with required permissions

### Issue 2: SAM Deploy Fails
```bash
# Error: Unable to upload artifact... Access Denied
# Solution: Create S3 bucket for SAM deployments
```

**Fix:**
```bash
# Create SAM deployment bucket
aws s3 mb s3://your-sam-deployment-bucket-name

# Deploy with bucket specified
sam deploy --s3-bucket your-sam-deployment-bucket-name
```

### Issue 3: Knowledge Base Creation Fails
```bash
# Error: OpenSearch domain not found
# Solution: Wait for OpenSearch domain to be ready
```

**Fix:**
```bash
# Check OpenSearch domain status
aws opensearch describe-domain --domain-name vtuber-vectors-dev

# Wait until Status shows "Active"
```

### Issue 4: No Documents Retrieved
```bash
# Error: Knowledge Base returns no results
# Solution: Check ingestion job status
```

**Fix:**
```bash
# Check ingestion job
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id your-kb-id \
  --data-source-id your-data-source-id

# If failed, restart ingestion
aws bedrock-agent start-ingestion-job \
  --knowledge-base-id your-kb-id \
  --data-source-id your-data-source-id
```

## 💰 Cost Estimation

### Expected Monthly Costs (Light Usage):
- **OpenSearch t3.small**: ~$25/month
- **Lambda executions**: ~$1-5/month
- **S3 storage**: ~$1/month
- **Bedrock Knowledge Base**: ~$5-10/month
- **Total**: ~$30-40/month

### Cost Optimization Tips:
1. Use smallest OpenSearch instance (t3.small.search)
2. Set up billing alerts
3. Delete test resources when not needed
4. Use reserved instances for production

## 🎯 Next Steps After Setup

### 1. Configure Your Application
```bash
# Copy generated environment file
cp .env.aws-rag .env

# Update your configuration
# AWS_KNOWLEDGE_BASE_ID=your-kb-id-here
# DOCUMENTS_BUCKET_NAME=your-bucket-name
```

### 2. Upload Your Documents
```bash
# Upload your manufacturing documents
aws s3 cp your-documents/ s3://your-bucket-name/manufacturing/ --recursive
```

### 3. Test RAG Integration
```bash
# Test with your specific questions
python test_aws_kb_integration.py --test accuracy
```

### 4. Monitor Performance
- Check CloudWatch metrics
- Monitor costs in AWS Billing
- Review retrieval accuracy

## 📞 Getting Help

### If You Get Stuck:

1. **Check the logs**: Look for specific error messages
2. **Verify permissions**: Ensure your AWS user has required permissions
3. **Check AWS service status**: Visit AWS Service Health Dashboard
4. **Use the troubleshooting guide**: See [`SERVER_TROUBLESHOOTING.md`](SERVER_TROUBLESHOOTING.md)
5. **Test components individually**: Use the testing scripts

### Useful AWS CLI Commands:
```bash
# Check your identity
aws sts get-caller-identity

# List CloudFormation stacks
aws cloudformation list-stacks

# Check Bedrock model access
aws bedrock list-foundation-models

# List Knowledge Bases
aws bedrock-agent list-knowledge-bases
```

## 🎉 Success Indicators

You'll know the setup is working when:

✅ **CloudFormation stack** shows `CREATE_COMPLETE`
✅ **Knowledge Base** shows `ACTIVE` status
✅ **Document ingestion** completes successfully
✅ **Test queries** return relevant results
✅ **Enhanced server** starts without errors
✅ **Health endpoints** return success responses

Once you see these indicators, your AWS Knowledge Base RAG integration is ready for production use!