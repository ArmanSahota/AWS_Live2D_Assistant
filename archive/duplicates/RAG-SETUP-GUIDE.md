# RAG Setup Guide for Manufacturing VTuber Assistant

This guide will help you set up the RAG (Retrieval-Augmented Generation) system for your Manufacturing VTuber Assistant using your existing AWS infrastructure.

## 🏗️ Current AWS Infrastructure

Your deployment includes:
- **WebSocket URL**: `wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev`
- **HTTP Base URL**: `https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev`
- **Documents S3 Bucket**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761`
- **AWS Region**: `us-west-2`
- **RAG Status**: Currently disabled (RagEnabled: false)

## 📋 Prerequisites

Before setting up RAG, ensure you have:

1. **AWS CLI configured** with appropriate permissions
2. **Python 3.8+** installed
3. **Required Python packages**:
   ```bash
   pip install boto3 requests asyncio
   ```
4. **AWS permissions** for:
   - S3 (read/write to your documents bucket)
   - Bedrock (create knowledge bases, invoke models)
   - IAM (create roles for Bedrock)
   - OpenSearch Serverless (for vector storage)

## 🚀 Quick Setup (Automated)

### Step 1: Run the Setup Script

```bash
python setup_rag_infrastructure.py
```

This script will:
- ✅ Check your existing AWS resources
- ✅ Upload sample manufacturing documents to S3
- ✅ Create IAM roles for Bedrock
- ✅ Set up Bedrock Knowledge Base (if possible)
- ✅ Configure data sources and ingestion
- ✅ Update configuration files

### Step 2: Test the Integration

```bash
python test_rag_integration.py
```

This will verify:
- AWS connectivity
- Knowledge base functionality
- RAG query processing
- HTTP endpoint availability

## 🔧 Manual Setup (If Automated Setup Fails)

### Step 1: Create OpenSearch Serverless Collection

1. Go to AWS Console → OpenSearch Service → Serverless collections
2. Create a new collection:
   - **Name**: `manufacturing-kb`
   - **Type**: Vector search
   - **Security**: Configure appropriate access policies

### Step 2: Create Bedrock Knowledge Base

1. Go to AWS Console → Bedrock → Knowledge bases
2. Create knowledge base:
   - **Name**: `manufacturing-assistant-kb`
   - **Description**: Manufacturing technical documentation
   - **Vector database**: OpenSearch Serverless
   - **Collection**: `manufacturing-kb`

### Step 3: Configure Data Source

1. In your knowledge base, add a data source:
   - **Type**: S3
   - **Bucket**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761`
   - **Prefixes**: `manufacturing/`, `docs/`, `manuals/`

### Step 4: Upload Documents

Upload your manufacturing documents to S3:

```bash
aws s3 cp your-manual.pdf s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/manufacturing/
aws s3 cp safety-protocols.txt s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/manufacturing/
```

### Step 5: Sync Knowledge Base

1. Go to your knowledge base in AWS Console
2. Select your data source
3. Click "Sync" to ingest documents

## ⚙️ Configuration Files Updated

The setup process updates these configuration files:

### 1. `manufacturing-assistant-config.yaml`
```yaml
MANUFACTURING_RAG:
  ENABLED: true
  HTTP_BASE_URL: "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev"
  KNOWLEDGE_BASE_ID: "your-kb-id"
  AWS_REGION: "us-west-2"
```

### 2. `LLM-Live2D-Desktop-Assitant-main/config/app_config.json`
```json
{
  "rag_config": {
    "enabled": true,
    "documents_bucket_name": "live2d-aws-backend-documentsbucket-gvqh2hzqj761",
    "knowledge_base_id": "your-kb-id",
    "aws_region": "us-west-2"
  }
}
```

### 3. Environment Variables (`.env.rag`)
```bash
RAG_ENABLED=true
KNOWLEDGE_BASE_ID=your-kb-id
DOCUMENTS_BUCKET_NAME=live2d-aws-backend-documentsbucket-gvqh2hzqj761
AWS_REGION=us-west-2
HTTP_BASE=https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev
```

## 🧪 Testing RAG Functionality

### Test Queries

Try these sample queries to test your RAG system:

1. **Safety Protocols**:
   - "What is the lockout tagout procedure?"
   - "Show me emergency shutdown steps"
   - "What PPE is required in the welding area?"

2. **Troubleshooting**:
   - "Machine error code E001 troubleshooting"
   - "Conveyor belt making unusual noise"
   - "Robot arm not responding"

3. **Maintenance**:
   - "Conveyor belt maintenance schedule"
   - "Lubrication requirements for spindle"
   - "Part number for drive belt"

### Expected Behavior

With RAG enabled, your assistant should:
- ✅ Retrieve relevant documents from S3
- ✅ Provide specific part numbers and procedures
- ✅ Include safety warnings when appropriate
- ✅ Reference source documents
- ✅ Give step-by-step instructions

## 📁 Document Organization

Organize your manufacturing documents in S3:

```
live2d-aws-backend-documentsbucket-gvqh2hzqj761/
├── manufacturing/
│   ├── safety-protocols.txt
│   ├── machine-maintenance.txt
│   └── parts-catalog.txt
├── manuals/
│   ├── cnc-machine-manual.pdf
│   ├── conveyor-system-guide.pdf
│   └── robot-arm-manual.pdf
└── docs/
    ├── troubleshooting-guide.txt
    ├── emergency-procedures.txt
    └── quality-standards.txt
```

## 🔍 Monitoring and Maintenance

### Check Knowledge Base Status

```python
import boto3

bedrock = boto3.client('bedrock-agent', region_name='us-west-2')
response = bedrock.list_knowledge_bases()
print(response)
```

### Monitor Ingestion Jobs

```python
jobs = bedrock.list_ingestion_jobs(
    knowledgeBaseId='your-kb-id',
    dataSourceId='your-ds-id'
)
print(jobs)
```

### Update Documents

When you add new documents:
1. Upload to S3
2. Trigger sync in AWS Console or via API
3. Wait for ingestion to complete

## 🚨 Troubleshooting

### Common Issues

#### 1. "Knowledge Base not found"
- Verify the Knowledge Base ID in configuration
- Check AWS region settings
- Ensure proper IAM permissions

#### 2. "No documents retrieved"
- Check if documents are uploaded to S3
- Verify data source configuration
- Ensure ingestion job completed successfully

#### 3. "Permission denied"
- Check IAM roles and policies
- Verify Bedrock service permissions
- Ensure S3 bucket access

#### 4. "Empty responses"
- Check document content and format
- Verify chunking configuration
- Review embedding model settings

### Debug Commands

```bash
# Test AWS connectivity
aws s3 ls s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/

# Check Bedrock models
aws bedrock list-foundation-models --region us-west-2

# List knowledge bases
aws bedrock-agent list-knowledge-bases --region us-west-2
```

## 📊 Performance Optimization

### Document Chunking

Optimize for your content:
- **Technical manuals**: 500-800 tokens per chunk
- **Safety procedures**: 200-400 tokens per chunk
- **Parts catalogs**: 300-500 tokens per chunk

### Caching

The system includes response caching:
- Common queries cached for 1 hour
- Machine-specific responses cached separately
- Safety-critical information always fresh

### Query Enhancement

The system automatically enhances queries with:
- Machine IDs extracted from speech
- Error codes and context
- Department and safety level information

## 🔄 Integration with Existing System

### Using RAG in Your VTuber

```python
from manufacturing_rag_implementation import ManufacturingRAGClient, ManufacturingContext

# Create RAG client
client = ManufacturingRAGClient(
    base_url='https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
    knowledge_base_id='your-kb-id',
    aws_region='us-west-2',
    verbose=True
)

# Create manufacturing context
context = ManufacturingContext(
    machine_id='CNC-001',
    error_code='E456',
    department='production',
    safety_level='high'
)

# Query with RAG
async for response_part in client.chat_iter_with_rag(
    "What should I do about this error?",
    context=context
):
    print(response_part, end='')
```

## 📈 Next Steps

1. **Upload Your Documents**: Add your actual manufacturing documents to S3
2. **Customize Prompts**: Modify system prompts for your specific use case
3. **Train on Your Data**: Fine-tune responses based on your feedback
4. **Monitor Usage**: Track query patterns and response quality
5. **Scale Up**: Add more document types and knowledge domains

## 📞 Support

If you encounter issues:

1. **Check CloudWatch Logs**: Look for detailed error messages
2. **Review IAM Permissions**: Ensure all required permissions are granted
3. **Test Components**: Use the test script to isolate issues
4. **AWS Documentation**: Refer to Bedrock and OpenSearch documentation

## 🎯 Success Metrics

Your RAG system is working well when:
- ✅ Query response time < 5 seconds
- ✅ Relevant documents retrieved > 80% of time
- ✅ Safety warnings properly highlighted
- ✅ Specific part numbers and procedures provided
- ✅ Source documents properly referenced

---

**🎉 Congratulations!** Your Manufacturing VTuber Assistant now has RAG capabilities powered by your AWS infrastructure. The assistant can now provide specific, document-backed answers to manufacturing questions while maintaining safety as the top priority.