# AWS Knowledge Base Integration with Live2D VTuber Assistant

## Overview
This guide shows how to integrate AWS Knowledge Base (Bedrock) with your existing Claude setup for enhanced RAG capabilities.

## Current Architecture
- **Local Server**: `server.py` with existing RAG functionality
- **AWS Backend**: SAM template with Claude HTTP endpoint
- **S3 Storage**: DocumentsBucket for document storage
- **Optional RAG Infra**: OpenSearch domain and Bedrock KB role

## Integration Strategy

### Phase 1: Enable AWS Knowledge Base Infrastructure

1. **Deploy RAG Infrastructure**
   ```bash
   cd LLM-Live2D-Desktop-Assitant-main/backend
   sam deploy --parameter-overrides EnableRagInfra=true
   ```

2. **Create Knowledge Base** (Manual step via AWS Console)
   - Go to AWS Bedrock Console → Knowledge Bases
   - Create new Knowledge Base
   - Use the deployed OpenSearch domain
   - Connect to your S3 DocumentsBucket
   - Use the BedrockKBRole for permissions

### Phase 2: Update Backend Template

The current template already has RAG support built-in. We need to:

1. **Update KNOWLEDGE_BASE_ID** in the Lambda environment
2. **Add bedrock-agent-runtime permissions**
3. **Enhance the Claude function for better RAG integration**

### Phase 3: Integrate with Local Server

Update `server.py` to use AWS Knowledge Base alongside local RAG:

```python
# Enhanced RAG integration
class AWSKnowledgeBaseRAG:
    def __init__(self, knowledge_base_id: str, region: str = "us-west-2"):
        self.knowledge_base_id = knowledge_base_id
        self.bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=region)
    
    def retrieve_documents(self, query: str, max_results: int = 5):
        try:
            response = self.bedrock_agent.retrieve(
                knowledgeBaseId=self.knowledge_base_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {
                        "numberOfResults": max_results,
                        "overrideSearchType": "HYBRID"
                    }
                }
            )
            return self._format_results(response.get("retrievalResults", []))
        except Exception as e:
            print(f"[AWS KB] Error retrieving documents: {e}")
            return []
    
    def _format_results(self, results):
        formatted = []
        for result in results:
            formatted.append({
                "content": result["content"]["text"],
                "source": result["metadata"].get("source", "Unknown"),
                "score": result["score"],
                "location": result["location"]
            })
        return formatted
```

## Implementation Steps

### Step 1: Enhanced Backend Template

Update the ClaudeHttpFn to better support Knowledge Base integration:

```yaml
ClaudeHttpFn:
  Environment:
    Variables:
      MODEL_ID: !Ref ModelId
      BEDROCK_REGION: !Ref AWS::Region
      MAX_TOKENS: "2048"
      KNOWLEDGE_BASE_ID: ""  # Will be set after KB creation
      DOCUMENTS_BUCKET: !Ref DocumentsBucket
      RAG_ENABLED: "true"
  Policies:
    - AWSLambdaBasicExecutionRole
    - Statement:
        - Effect: Allow
          Action:
            - bedrock:InvokeModel
            - bedrock-agent:Retrieve
          Resource: "*"
        - Effect: Allow
          Action:
            - s3:GetObject
            - s3:ListBucket
          Resource:
            - !GetAtt DocumentsBucket.Arn
            - !Sub "${DocumentsBucket.Arn}/*"
```

### Step 2: Local Server Integration

Update `server.py` to use both local and AWS RAG:

```python
# In server.py, enhance the Claude endpoint
@self.app.post("/claude")
async def claude_endpoint(request: ClaudeRequest):
    try:
        # Get user input
        user_message = request.text
        
        # Try AWS Knowledge Base first
        aws_rag_context = ""
        if AWS_KB_AVAILABLE:
            try:
                aws_kb = AWSKnowledgeBaseRAG(KNOWLEDGE_BASE_ID)
                aws_docs = aws_kb.retrieve_documents(user_message)
                if aws_docs:
                    aws_rag_context = format_aws_kb_context(aws_docs)
            except Exception as e:
                print(f"[AWS KB] Fallback to local RAG: {e}")
        
        # Fallback to local RAG if AWS KB fails
        local_rag_context = ""
        if not aws_rag_context and S3_RAG_AVAILABLE:
            try:
                s3_rag = SimpleS3RAG()
                local_docs = s3_rag.search_documents(user_message)
                if local_docs:
                    local_rag_context = format_local_rag_context(local_docs)
            except Exception as e:
                print(f"[Local RAG] Error: {e}")
        
        # Combine contexts
        rag_context = aws_rag_context or local_rag_context
        
        # Enhanced prompt with RAG context
        enhanced_prompt = user_message
        if rag_context:
            enhanced_prompt = f"{rag_context}\n\nUser Question: {user_message}"
        
        # Call Claude with enhanced prompt
        # ... existing Claude API call logic
        
    except Exception as e:
        # ... error handling
```

### Step 3: Configuration Updates

Update your environment variables:

```bash
# .env additions
AWS_KNOWLEDGE_BASE_ID=your-kb-id-here
AWS_BEDROCK_REGION=us-west-2
RAG_MODE=hybrid  # aws, local, or hybrid
DOCUMENTS_BUCKET_NAME=your-bucket-name
```

### Step 4: Document Management

Create a document upload system:

```python
# document_manager.py
class DocumentManager:
    def __init__(self, bucket_name: str, knowledge_base_id: str):
        self.bucket_name = bucket_name
        self.knowledge_base_id = knowledge_base_id
        self.s3 = boto3.client('s3')
        self.bedrock_agent = boto3.client('bedrock-agent')
    
    def upload_document(self, file_path: str, key: str):
        """Upload document to S3 and trigger KB sync"""
        # Upload to S3
        self.s3.upload_file(file_path, self.bucket_name, key)
        
        # Trigger Knowledge Base sync
        self.bedrock_agent.start_ingestion_job(
            knowledgeBaseId=self.knowledge_base_id,
            dataSourceId=self.data_source_id
        )
    
    def list_documents(self):
        """List all documents in the knowledge base"""
        response = self.s3.list_objects_v2(Bucket=self.bucket_name)
        return [obj['Key'] for obj in response.get('Contents', [])]
```

## Testing the Integration

### Test 1: Basic RAG Query
```python
# test_aws_kb_integration.py
import asyncio
from aws_knowledge_base_rag import AWSKnowledgeBaseRAG

async def test_basic_query():
    kb = AWSKnowledgeBaseRAG("your-kb-id")
    results = kb.retrieve_documents("manufacturing error troubleshooting")
    print(f"Retrieved {len(results)} documents")
    for doc in results:
        print(f"- {doc['source']}: {doc['content'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_basic_query())
```

### Test 2: End-to-End Integration
```bash
# Test the complete pipeline
curl -X POST http://localhost:8000/claude \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What should I do if I see error code 103 on the manufacturing line?",
    "enable_rag": true
  }'
```

## Benefits of AWS Knowledge Base Integration

1. **Scalable Vector Search**: Managed OpenSearch with automatic scaling
2. **Hybrid Search**: Combines semantic and keyword search
3. **Automatic Chunking**: Intelligent document processing
4. **Real-time Updates**: Automatic re-indexing when documents change
5. **Enterprise Security**: IAM-based access control
6. **Cost Optimization**: Pay-per-use pricing model

## Migration Path

1. **Phase 1**: Deploy infrastructure with `EnableRagInfra=true`
2. **Phase 2**: Create Knowledge Base via AWS Console
3. **Phase 3**: Upload existing documents to S3
4. **Phase 4**: Update Lambda with Knowledge Base ID
5. **Phase 5**: Test hybrid RAG functionality
6. **Phase 6**: Gradually migrate from local to AWS RAG

## Monitoring and Optimization

- **CloudWatch Metrics**: Monitor retrieval latency and accuracy
- **Cost Tracking**: Track OpenSearch and Bedrock usage
- **Performance Tuning**: Optimize chunk size and retrieval parameters
- **A/B Testing**: Compare AWS KB vs local RAG performance

## Next Steps

1. Deploy the enhanced template
2. Create the Knowledge Base
3. Upload your manufacturing documents
4. Test the integration
5. Monitor performance and costs