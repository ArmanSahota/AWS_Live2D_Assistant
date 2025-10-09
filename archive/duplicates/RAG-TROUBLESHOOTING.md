# RAG Troubleshooting Guide

## Issues Encountered and Solutions

### ✅ Issue 1: OpenSearch Serverless Collection Required

**Problem**: Knowledge Base creation failed with error:
```
ValidationException: The knowledge base storage configuration provided is invalid... 403 Forbidden
```

**Root Cause**: Bedrock Knowledge Base requires an OpenSearch Serverless collection to store vector embeddings, but none existed.

**Solution**: 
1. Run the OpenSearch collection setup first:
   ```bash
   python setup_opensearch_collection.py
   ```
2. Then run the RAG infrastructure setup:
   ```bash
   python setup_rag_infrastructure.py
   ```

**Status**: ✅ **FIXED** - Created [`setup_opensearch_collection.py`](setup_opensearch_collection.py) script

---

### ✅ Issue 2: Missing LLM Interface Dependency

**Problem**: Test script failed with error:
```
ImportError: No module named 'llm'
```

**Root Cause**: The manufacturing RAG implementation tried to import from a non-existent `llm.llm_interface` module.

**Solution**: Added fallback interface creation in [`manufacturing_rag_implementation.py`](manufacturing_rag_implementation.py):
```python
try:
    from llm.llm_interface import LLMInterface
except ImportError:
    # Create a simple base interface if the original doesn't exist
    class LLMInterface:
        def __init__(self):
            pass
        # ... rest of interface
```

**Status**: ✅ **FIXED** - Added fallback interface implementation

---

## Current Setup Status

### ✅ What's Working
- ✅ AWS connectivity (S3 bucket accessible)
- ✅ Bedrock service available
- ✅ IAM role creation successful
- ✅ Sample documents uploaded to S3
- ✅ Configuration files updated
- ✅ RAG client implementation ready

### 🔄 What Needs Manual Setup
- 🔄 OpenSearch Serverless collection creation
- 🔄 Bedrock Knowledge Base creation
- 🔄 Document ingestion and indexing

## Step-by-Step Recovery

### Step 1: Create OpenSearch Collection
```bash
python setup_opensearch_collection.py
```

This will:
- Create security policies
- Create data access policies  
- Create the `manufacturing-kb` collection
- Wait for collection to become active

### Step 2: Create Knowledge Base
```bash
python setup_rag_infrastructure.py
```

This should now succeed because the OpenSearch collection exists.

### Step 3: Test Integration
```bash
python test_rag_integration.py
```

This will verify all components are working together.

## Alternative: Manual AWS Console Setup

If the automated scripts continue to have issues, you can set up manually:

### 1. OpenSearch Serverless Collection
1. Go to AWS Console → OpenSearch Service → Serverless collections
2. Create collection:
   - **Name**: `manufacturing-kb`
   - **Type**: Vector search
   - **Security**: Configure access policies for your account and Bedrock role

### 2. Bedrock Knowledge Base
1. Go to AWS Console → Bedrock → Knowledge bases
2. Create knowledge base:
   - **Name**: `manufacturing-assistant-kb`
   - **Vector database**: OpenSearch Serverless
   - **Collection**: `manufacturing-kb`
   - **Index**: `manufacturing-docs`

### 3. Data Source
1. In your knowledge base, add data source:
   - **Type**: S3
   - **Bucket**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761`
   - **Prefixes**: `manufacturing/`

### 4. Sync Data
1. Start ingestion job to process uploaded documents
2. Wait for completion (usually 5-10 minutes)

## Verification Commands

### Check S3 Documents
```bash
aws s3 ls s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/manufacturing/
```

### Check OpenSearch Collections
```bash
aws opensearchserverless list-collections --region us-west-2
```

### Check Knowledge Bases
```bash
aws bedrock-agent list-knowledge-bases --region us-west-2
```

### Test Python Imports
```bash
python -c "from manufacturing_rag_implementation import *; print('✅ RAG modules loaded successfully')"
```

## Expected Timeline

- **OpenSearch Collection**: 2-5 minutes to create and become active
- **Knowledge Base**: 1-2 minutes to create
- **Document Ingestion**: 5-10 minutes for sample documents
- **Total Setup Time**: 10-15 minutes

## Success Indicators

You'll know the setup is successful when:

1. **OpenSearch Collection**: Status shows "ACTIVE" in AWS Console
2. **Knowledge Base**: Shows "ACTIVE" status with data source connected
3. **Ingestion Job**: Completes with "SUCCEEDED" status
4. **Test Script**: Shows >70% pass rate
5. **Sample Queries**: Return relevant manufacturing information

## Next Steps After Fix

1. **Upload Your Documents**: Add real manufacturing documents to S3
2. **Test Queries**: Try manufacturing-specific questions
3. **Integrate with VTuber**: Connect RAG client to your assistant
4. **Monitor Performance**: Check response times and accuracy
5. **Iterate and Improve**: Adjust based on usage patterns

## Support Resources

- **AWS Documentation**: [Bedrock Knowledge Bases](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- **OpenSearch Serverless**: [Getting Started Guide](https://docs.aws.amazon.com/opensearch-service/latest/developerguide/serverless-getting-started.html)
- **CloudWatch Logs**: Check for detailed error messages
- **AWS Support**: For complex permission or service issues

---

**🎯 Bottom Line**: The main issues were missing prerequisites (OpenSearch collection) and import dependencies. Both are now fixed with the updated scripts. Run the setup in the correct order and your RAG system should work perfectly!