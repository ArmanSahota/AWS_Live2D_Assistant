# AWS RAG Implementation Plan for VTuber Assistant

## Current Status Assessment
✅ **Existing Infrastructure:**
- AWS SAM template with Claude 3.7 Sonnet integration
- API Gateway + Lambda functions
- WebSocket support
- DynamoDB tables for sessions

❌ **Missing RAG Components:**
- Bedrock Knowledge Base
- S3 document storage
- OpenSearch vector database
- RAG-enhanced Lambda functions
- Proper IAM roles and policies

## Implementation Strategy

### Phase 1: Infrastructure Setup (1-2 days)
1. **Extend SAM Template** - Add RAG resources to existing template.yml
2. **Create S3 Document Bucket** - For manufacturing documents storage
3. **Set up OpenSearch Domain** - Vector database for embeddings
4. **Create Bedrock Knowledge Base** - Connect S3 and OpenSearch
5. **Update IAM Roles** - Add permissions for RAG operations

### Phase 2: Lambda Function Enhancement (1 day)
1. **Enhance Claude Lambda** - Add document retrieval capabilities
2. **Create RAG Processing Function** - Handle document ingestion
3. **Add Context Enhancement** - Improve prompt construction with retrieved docs

### Phase 3: Document Ingestion (1 day)
1. **Upload Sample Documents** - Manufacturing manuals, safety protocols
2. **Configure Knowledge Base Sync** - Set up automatic ingestion
3. **Test Document Retrieval** - Verify RAG pipeline works

### Phase 4: Integration & Testing (1 day)
1. **Update VTuber Client** - Connect to new RAG endpoints
2. **Test Manufacturing Queries** - Verify context-aware responses
3. **Performance Optimization** - Caching and response tuning

## Detailed Implementation Steps

### Step 1: Update SAM Template

Add these resources to your existing `template.yml`:

```yaml
# RAG Resources to Add
Parameters:
  DocumentBucketName:
    Type: String
    Default: !Sub "vtuber-manufacturing-docs-${AWS::AccountId}"
  
  KnowledgeBaseName:
    Type: String
    Default: "VTuberManufacturingKB"

Resources:
  # S3 Bucket for Documents
  DocumentsBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: !Ref DocumentBucketName
      VersioningConfiguration:
        Status: Enabled
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true

  # OpenSearch Domain for Vector Storage
  VectorSearchDomain:
    Type: AWS::OpenSearch::Domain
    Properties:
      DomainName: !Sub "vtuber-vectors-${Env}"
      EngineVersion: "OpenSearch_2.3"
      ClusterConfig:
        InstanceType: "t3.small.search"
        InstanceCount: 1
      EBSOptions:
        EBSEnabled: true
        VolumeType: "gp3"
        VolumeSize: 20
      AccessPolicies:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: "es:*"
            Resource: !Sub "arn:aws:es:${AWS::Region}:${AWS::AccountId}:domain/vtuber-vectors-${Env}/*"

  # IAM Role for Bedrock Knowledge Base
  BedrockKBRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: !Sub "BedrockKnowledgeBaseRole-${Env}"
      AssumeRolePolicyDocument:
        Version: "2012-10-17"
        Statement:
          - Effect: Allow
            Principal:
              Service: bedrock.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: BedrockKBPolicy
          PolicyDocument:
            Version: "2012-10-17"
            Statement:
              - Effect: Allow
                Action:
                  - s3:GetObject
                  - s3:ListBucket
                Resource:
                  - !Sub "${DocumentsBucket}/*"
                  - !GetAtt DocumentsBucket.Arn
              - Effect: Allow
                Action:
                  - es:ESHttpPost
                  - es:ESHttpPut
                  - es:ESHttpGet
                  - es:ESHttpDelete
                Resource: !GetAtt VectorSearchDomain.Arn
              - Effect: Allow
                Action: bedrock:InvokeModel
                Resource: "arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v1"
```

### Step 2: Enhanced Claude Lambda Function

Replace the current Claude function with RAG-enhanced version:

```python
import json, os, boto3
from typing import List, Dict, Any

# Initialize clients
bedrock_runtime = boto3.client("bedrock-runtime", region_name=os.environ["BEDROCK_REGION"])
bedrock_agent = boto3.client("bedrock-agent-runtime", region_name=os.environ["BEDROCK_REGION"])

def lambda_handler(event, context):
    try:
        # Parse request
        body = json.loads(event.get("body", "{}"))
        text = body.get("text", "").strip()
        system = body.get("system", "You are a helpful manufacturing assistant.")
        enable_rag = body.get("enable_rag", True)
        
        # RAG Enhancement: Retrieve relevant documents
        retrieved_context = []
        if enable_rag and text and os.environ.get("KNOWLEDGE_BASE_ID"):
            try:
                kb_response = bedrock_agent.retrieve(
                    knowledgeBaseId=os.environ["KNOWLEDGE_BASE_ID"],
                    retrievalQuery={"text": text},
                    retrievalConfiguration={
                        "vectorSearchConfiguration": {
                            "numberOfResults": 5,
                            "overrideSearchType": "HYBRID"
                        }
                    }
                )
                
                retrieved_context = [
                    {
                        "content": result["content"]["text"],
                        "source": result["metadata"].get("source", "Unknown"),
                        "score": result["score"]
                    }
                    for result in kb_response.get("retrievalResults", [])
                ]
                
                print(f"[RAG] Retrieved {len(retrieved_context)} relevant documents")
                
            except Exception as rag_error:
                print(f"[RAG] Error retrieving documents: {rag_error}")
                # Continue without RAG if retrieval fails
        
        # Enhance prompt with retrieved context
        if retrieved_context:
            context_sections = ["📋 RELEVANT DOCUMENTATION:"]
            for i, ctx in enumerate(retrieved_context, 1):
                context_sections.append(f"{i}. Source: {ctx['source']}")
                context_sections.append(f"   Content: {ctx['content'][:500]}...")
                context_sections.append("")
            
            context_sections.append("❓ USER QUESTION:")
            context_sections.append(text)
            enhanced_text = "\n".join(context_sections)
        else:
            enhanced_text = text
        
        # Prepare Claude request (existing logic)
        # ... rest of Claude invocation code ...
        
        return {
            "statusCode": 200,
            "headers": {
                "content-type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "reply": reply,
                "sources_used": len(retrieved_context),
                "rag_enabled": enable_rag and bool(retrieved_context)
            })
        }
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
```

### Step 3: Document Ingestion Process

1. **Create document structure in S3:**
```bash
aws s3api put-object --bucket vtuber-manufacturing-docs-123456789 --key manuals/
aws s3api put-object --bucket vtuber-manufacturing-docs-123456789 --key safety-protocols/
aws s3api put-object --bucket vtuber-manufacturing-docs-123456789 --key troubleshooting/
```

2. **Upload sample manufacturing documents**
3. **Create Bedrock Knowledge Base data source**
4. **Start ingestion job**

### Step 4: VTuber Client Integration

Update the existing Claude client to use RAG:

```python
# In llm/claude.py - add RAG support
class ClaudeRAG(Claude):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enable_rag = kwargs.get('enable_rag', True)
    
    def chat_iter(self, prompt: str, image_base64=None):
        # Add RAG flag to request
        payload = {
            "text": prompt,
            "system": self.system,
            "enable_rag": self.enable_rag
        }
        
        if image_base64:
            payload["image"] = image_base64
            payload["has_vision"] = True
        
        # Send to enhanced Lambda endpoint
        # ... existing HTTP request logic ...
```

## Implementation Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | 1-2 days | Infrastructure setup, SAM template updates |
| **Phase 2** | 1 day | Lambda function enhancements |
| **Phase 3** | 1 day | Document ingestion and testing |
| **Phase 4** | 1 day | Integration and optimization |
| **Total** | **4-5 days** | Complete RAG implementation |

## Cost Estimation

### Monthly AWS Costs (estimated):
- **OpenSearch t3.small**: ~$50/month
- **S3 Storage (10GB docs)**: ~$0.25/month
- **Bedrock Knowledge Base**: ~$0.10 per 1K queries
- **Lambda executions**: ~$5/month (moderate usage)
- **Total**: ~$55-60/month

## Success Criteria

✅ **Technical Validation:**
- [ ] Knowledge Base successfully ingests documents
- [ ] RAG retrieval returns relevant context
- [ ] Enhanced Claude responses include document references
- [ ] Response time < 3 seconds for RAG queries

✅ **Functional Validation:**
- [ ] Manufacturing queries return contextual answers
- [ ] Safety protocols are properly referenced
- [ ] Troubleshooting guides are accessible
- [ ] Part numbers and specifications are accurate

## Risk Mitigation

1. **Fallback Strategy**: RAG failures don't break basic Claude functionality
2. **Performance Monitoring**: CloudWatch metrics for response times
3. **Cost Controls**: Set up billing alerts for AWS services
4. **Document Quality**: Implement document validation before ingestion

## Next Actions

1. **Review and approve this plan**
2. **Set up AWS credentials and permissions**
3. **Begin Phase 1 implementation**
4. **Prepare sample manufacturing documents**
5. **Schedule testing and validation sessions**

---

This plan provides a complete roadmap for implementing RAG capabilities while maintaining your existing AWS infrastructure and VTuber assistant functionality.