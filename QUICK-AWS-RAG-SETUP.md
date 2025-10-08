# Quick AWS RAG Setup Guide

## Current Status
✅ **S3 Bucket Ready**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761`
✅ **Documents Uploaded**: Sample manufacturing documents in S3
✅ **IAM Role Created**: BedrockKnowledgeBaseRole exists
🔄 **OpenSearch Collection**: Currently being created
❌ **Bedrock Knowledge Base**: Needs OpenSearch collection first

## What's Already Working
Your system already has **Demo RAG** working with pre-loaded manufacturing knowledge:
- Error codes E001, E002 with troubleshooting steps
- Safety protocols (lockout/tagout, emergency procedures)
- Maintenance schedules for CNC machines and conveyors
- Parts catalog with specific part numbers

## Quick Manual AWS Console Setup

### Step 1: Create OpenSearch Serverless Collection
1. Go to [OpenSearch Console](https://us-west-2.console.aws.amazon.com/aos/home?region=us-west-2#opensearch/collections)
2. Click "Create collection"
3. **Collection name**: `manufacturing-kb`
4. **Collection type**: Vector search
5. **Security settings**: 
   - Network access: Public
   - Encryption: AWS owned key
6. Click "Create"

### Step 2: Create Bedrock Knowledge Base
1. Go to [Bedrock Console](https://us-west-2.console.aws.amazon.com/bedrock/home?region=us-west-2#/knowledge-bases)
2. Click "Create knowledge base"
3. **Knowledge base details**:
   - Name: `manufacturing-assistant-kb`
   - Description: `Manufacturing technical documentation`
   - IAM role: Select existing `BedrockKnowledgeBaseRole`
4. **Data source**:
   - Data source name: `manufacturing-docs`
   - S3 URI: `s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/manufacturing/`
5. **Vector database**:
   - Vector database: Amazon OpenSearch Serverless
   - Collection: `manufacturing-kb` (created in Step 1)
   - Vector index name: `manufacturing-index`
6. **Embeddings model**: `amazon.titan-embed-text-v1`
7. Click "Create knowledge base"

### Step 3: Sync Data Source
1. In your new knowledge base, go to "Data sources"
2. Select `manufacturing-docs`
3. Click "Sync" to ingest the documents

### Step 4: Get Knowledge Base ID
1. In the knowledge base details, copy the **Knowledge base ID**
2. It will look like: `ABCDEFGHIJ`

### Step 5: Update Configuration
Update [`app_config.json`](LLM-Live2D-Desktop-Assitant-main/config/app_config.json):
```json
{
  "rag_config": {
    "enabled": true,
    "documents_bucket_name": "live2d-aws-backend-documentsbucket-gvqh2hzqj761",
    "knowledge_base_id": "YOUR_KB_ID_HERE",
    "aws_region": "us-west-2"
  }
}
```

## Alternative: Use Demo RAG (Recommended for POC)

The Demo RAG is perfect for proof-of-concept because:
- ✅ Works immediately without complex AWS setup
- ✅ Has realistic manufacturing scenarios
- ✅ Demonstrates all RAG capabilities
- ✅ No additional AWS costs (~$50/month for OpenSearch)

## Test Your Setup

### With Demo RAG (Current)
```bash
cd "D:\AWS_Vtuber_LLM - Copy\LLM-Live2D-Desktop-Assitant-main"
python switch_to_manufacturing_mode.py
# Choose option 1 for Manufacturing RAG mode
python server.py --web
```

### With AWS RAG (After setup)
Same commands, but responses will come from your actual S3 documents instead of pre-loaded knowledge.

## Sample Documents Already Uploaded

The setup script uploaded these to your S3 bucket:

### `manufacturing/safety-protocols.txt`
- Lockout/tagout procedures
- Emergency shutdown steps
- PPE requirements

### `manufacturing/machine-maintenance.txt`
- CNC machine maintenance schedules
- Conveyor system maintenance
- Preventive maintenance checklists

### `manufacturing/parts-catalog.txt`
- Part numbers and specifications
- Replacement intervals
- Compatibility information

## Cost Estimate

**Demo RAG**: Free (uses pre-loaded knowledge)
**AWS RAG**: ~$50-60/month
- OpenSearch Serverless: ~$50/month
- S3 Storage: ~$0.25/month
- Bedrock queries: ~$0.10 per 1K queries

## Troubleshooting

If you encounter issues:
1. Check CloudWatch logs for detailed error messages
2. Verify IAM permissions for Bedrock and OpenSearch
3. Ensure OpenSearch collection is in "Active" status
4. Test with simple queries first

## Next Steps

1. **For POC**: Use Demo RAG (already working)
2. **For Production**: Complete manual AWS setup above
3. **Add Your Documents**: Upload your actual manuals to S3
4. **Monitor Performance**: Track query response times and accuracy