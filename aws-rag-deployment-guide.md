# AWS RAG Deployment Guide for Manufacturing VTuber Assistant

This guide provides step-by-step instructions for deploying the RAG-enhanced manufacturing assistant using AWS services.

## Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.11+ installed
- Node.js and npm installed
- Access to AWS Bedrock (request access if needed)
- Manufacturing documents ready for ingestion

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   VTuber App    │    │   API Gateway    │    │   Lambda        │
│   (Local)       │◄──►│   (HTTP API)     │◄──►│   (Claude)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                       ┌──────────────────┐             │
                       │   S3 Bucket      │◄────────────┘
                       │   (Documents)    │
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │   Bedrock KB     │
                       │   (RAG Engine)   │
                       └──────────────────┘
                                │
                       ┌──────────────────┐
                       │   OpenSearch     │
                       │   (Vector Store) │
                       └──────────────────┘
```

## Step 1: Set Up AWS Infrastructure

### 1.1 Create S3 Bucket for Documents

```bash
# Create S3 bucket for manufacturing documents
aws s3 mb s3://manufacturing-docs-kb-$(date +%s) --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket manufacturing-docs-kb-$(date +%s) \
    --versioning-configuration Status=Enabled

# Set up bucket policy for Bedrock access
cat > bucket-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::manufacturing-docs-kb-*",
                "arn:aws:s3:::manufacturing-docs-kb-*/*"
            ]
        }
    ]
}
EOF

aws s3api put-bucket-policy \
    --bucket manufacturing-docs-kb-$(date +%s) \
    --policy file://bucket-policy.json
```

### 1.2 Create OpenSearch Domain

```bash
# Create OpenSearch domain for vector storage
aws opensearch create-domain \
    --domain-name manufacturing-vectors \
    --engine-version "OpenSearch_2.3" \
    --cluster-config InstanceType=t3.small.search,InstanceCount=1 \
    --ebs-options EBSEnabled=true,VolumeType=gp3,VolumeSize=20 \
    --access-policies '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "es:*",
                "Resource": "arn:aws:es:us-east-1:*:domain/manufacturing-vectors/*"
            }
        ]
    }'
```

### 1.3 Create IAM Role for Bedrock Knowledge Base

```bash
# Create trust policy
cat > bedrock-trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "bedrock.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create IAM role
aws iam create-role \
    --role-name BedrockKnowledgeBaseRole \
    --assume-role-policy-document file://bedrock-trust-policy.json

# Create permission policy
cat > bedrock-permissions.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::manufacturing-docs-kb-*",
                "arn:aws:s3:::manufacturing-docs-kb-*/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "es:ESHttpPost",
                "es:ESHttpPut",
                "es:ESHttpGet",
                "es:ESHttpDelete",
                "es:ESHttpHead"
            ],
            "Resource": "arn:aws:es:us-east-1:*:domain/manufacturing-vectors/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        }
    ]
}
EOF

# Attach policy to role
aws iam put-role-policy \
    --role-name BedrockKnowledgeBaseRole \
    --policy-name BedrockKnowledgeBasePolicy \
    --policy-document file://bedrock-permissions.json
```

### 1.4 Create Bedrock Knowledge Base

```bash
# Get the role ARN
ROLE_ARN=$(aws iam get-role --role-name BedrockKnowledgeBaseRole --query 'Role.Arn' --output text)

# Get OpenSearch endpoint
OPENSEARCH_ENDPOINT=$(aws opensearch describe-domain --domain-name manufacturing-vectors --query 'DomainStatus.Endpoint' --output text)

# Create Knowledge Base
aws bedrock-agent create-knowledge-base \
    --name "ManufacturingKnowledgeBase" \
    --description "Knowledge base for manufacturing documentation and procedures" \
    --role-arn "$ROLE_ARN" \
    --knowledge-base-configuration '{
        "type": "VECTOR",
        "vectorKnowledgeBaseConfiguration": {
            "embeddingModelArn": "arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-embed-text-v1"
        }
    }' \
    --storage-configuration '{
        "type": "OPENSEARCH_SERVERLESS",
        "opensearchServerlessConfiguration": {
            "collectionArn": "arn:aws:aoss:us-east-1:123456789012:collection/manufacturing-vectors",
            "vectorIndexName": "manufacturing-index",
            "fieldMapping": {
                "vectorField": "vector",
                "textField": "text",
                "metadataField": "metadata"
            }
        }
    }'

# Save the Knowledge Base ID
KB_ID=$(aws bedrock-agent list-knowledge-bases --query 'knowledgeBaseSummaries[?name==`ManufacturingKnowledgeBase`].knowledgeBaseId' --output text)
echo "Knowledge Base ID: $KB_ID"
```

## Step 2: Set Up Lambda Function for Claude Integration

### 2.1 Create Lambda Function

```python
# lambda_function.py
import json
import boto3
import base64
from typing import Dict, Any

def lambda_handler(event, context):
    """
    Lambda function to handle Claude requests with RAG integration
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        text = body.get('text', '')
        system_prompt = body.get('system', '')
        image_data = body.get('image')
        has_vision = body.get('has_vision', False)
        retrieved_context = body.get('retrieved_context', [])
        
        # Initialize Bedrock client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        bedrock_agent = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
        
        # If we have retrieved context, use it directly
        # Otherwise, perform RAG retrieval
        if not retrieved_context and text:
            # Retrieve from Knowledge Base
            kb_response = bedrock_agent.retrieve(
                knowledgeBaseId=os.environ['KNOWLEDGE_BASE_ID'],
                retrievalQuery={'text': text},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 5,
                        'overrideSearchType': 'HYBRID'
                    }
                }
            )
            
            retrieved_context = [
                {
                    'content': result['content']['text'],
                    'source': result['metadata'].get('source', 'Unknown'),
                    'score': result['score']
                }
                for result in kb_response.get('retrievalResults', [])
            ]
        
        # Construct enhanced prompt
        enhanced_prompt = construct_rag_prompt(text, retrieved_context)
        
        # Prepare Claude request
        claude_request = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": enhanced_prompt if not has_vision else [
                        {"type": "text", "text": enhanced_prompt},
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ] if image_data else enhanced_prompt
                }
            ]
        }
        
        # Call Claude
        response = bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps(claude_request)
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        reply = response_body['content'][0]['text']
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'reply': reply,
                'retrieved_sources': [ctx.get('source', 'Unknown') for ctx in retrieved_context]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

def construct_rag_prompt(original_prompt: str, retrieved_context: list) -> str:
    """
    Construct enhanced prompt with retrieved context
    """
    if not retrieved_context:
        return original_prompt
    
    context_sections = ["📋 RELEVANT DOCUMENTATION:"]
    
    for i, ctx in enumerate(retrieved_context, 1):
        context_sections.append(f"{i}. Source: {ctx.get('source', 'Unknown')}")
        context_sections.append(f"   Content: {ctx.get('content', '')[:500]}...")
        context_sections.append("")
    
    context_sections.append("❓ USER QUESTION:")
    context_sections.append(original_prompt)
    
    return "\n".join(context_sections)
```

### 2.2 Deploy Lambda Function

```bash
# Create deployment package
mkdir lambda-deployment
cd lambda-deployment

# Copy function code
cp ../lambda_function.py .

# Create requirements.txt
cat > requirements.txt << EOF
boto3>=1.34.0
botocore>=1.34.0
EOF

# Install dependencies
pip install -r requirements.txt -t .

# Create deployment package
zip -r manufacturing-claude-lambda.zip .

# Create Lambda function
aws lambda create-function \
    --function-name manufacturing-claude-rag \
    --runtime python3.11 \
    --role arn:aws:iam::$(aws sts get-caller-identity --query Account --output text):role/lambda-execution-role \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://manufacturing-claude-lambda.zip \
    --timeout 60 \
    --memory-size 512 \
    --environment Variables="{KNOWLEDGE_BASE_ID=$KB_ID}"
```

## Step 3: Set Up API Gateway

### 3.1 Create HTTP API

```bash
# Create API Gateway
aws apigatewayv2 create-api \
    --name manufacturing-assistant-api \
    --protocol-type HTTP \
    --cors-configuration AllowOrigins="*",AllowMethods="*",AllowHeaders="*"

# Get API ID
API_ID=$(aws apigatewayv2 get-apis --query 'Items[?Name==`manufacturing-assistant-api`].ApiId' --output text)

# Create integration
aws apigatewayv2 create-integration \
    --api-id $API_ID \
    --integration-type AWS_PROXY \
    --integration-uri arn:aws:lambda:us-east-1:$(aws sts get-caller-identity --query Account --output text):function:manufacturing-claude-rag \
    --payload-format-version "2.0"

# Get integration ID
INTEGRATION_ID=$(aws apigatewayv2 get-integrations --api-id $API_ID --query 'Items[0].IntegrationId' --output text)

# Create route
aws apigatewayv2 create-route \
    --api-id $API_ID \
    --route-key "POST /claude" \
    --target integrations/$INTEGRATION_ID

# Create deployment
aws apigatewayv2 create-deployment \
    --api-id $API_ID \
    --stage-name prod

# Get API endpoint
API_ENDPOINT=$(aws apigatewayv2 get-api --api-id $API_ID --query 'ApiEndpoint' --output text)
echo "API Endpoint: $API_ENDPOINT"
```

## Step 4: Document Ingestion

### 4.1 Upload Manufacturing Documents

```bash
# Create document structure in S3
aws s3api put-object \
    --bucket manufacturing-docs-kb-$(date +%s) \
    --key manuals/ \
    --content-length 0

aws s3api put-object \
    --bucket manufacturing-docs-kb-$(date +%s) \
    --key schematics/ \
    --content-length 0

aws s3api put-object \
    --bucket manufacturing-docs-kb-$(date +%s) \
    --key safety-protocols/ \
    --content-length 0

aws s3api put-object \
    --bucket manufacturing-docs-kb-$(date +%s) \
    --key troubleshooting/ \
    --content-length 0

# Upload sample documents (replace with your actual documents)
aws s3 cp ./manufacturing-docs/ s3://manufacturing-docs-kb-$(date +%s)/ --recursive
```

### 4.2 Create Data Source and Sync

```bash
# Create data source
aws bedrock-agent create-data-source \
    --knowledge-base-id $KB_ID \
    --name "ManufacturingDocuments" \
    --data-source-configuration '{
        "type": "S3",
        "s3Configuration": {
            "bucketArn": "arn:aws:s3:::manufacturing-docs-kb-'$(date +%s)'",
            "inclusionPrefixes": ["manuals/", "schematics/", "safety-protocols/", "troubleshooting/"]
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
DATA_SOURCE_ID=$(aws bedrock-agent list-data-sources --knowledge-base-id $KB_ID --query 'dataSourceSummaries[0].dataSourceId' --output text)

# Start ingestion job
aws bedrock-agent start-ingestion-job \
    --knowledge-base-id $KB_ID \
    --data-source-id $DATA_SOURCE_ID

echo "Ingestion job started. Check status with:"
echo "aws bedrock-agent list-ingestion-jobs --knowledge-base-id $KB_ID --data-source-id $DATA_SOURCE_ID"
```

## Step 5: Configure VTuber Assistant

### 5.1 Update Configuration

```yaml
# Add to your existing conf.yaml
MANUFACTURING_RAG:
  ENABLED: true
  HTTP_BASE_URL: "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"
  KNOWLEDGE_BASE_ID: "your-knowledge-base-id"
  AWS_REGION: "us-east-1"
  CACHE_ENABLED: true
  SAFETY_PRIORITY: true

# Update LLM configuration to use manufacturing client
LLM_MODEL: "manufacturing_rag"
```

### 5.2 Install Additional Dependencies

```bash
# Add to requirements.txt
echo "boto3>=1.34.0" >> requirements.txt
echo "botocore>=1.34.0" >> requirements.txt

# Install
pip install -r requirements.txt
```

### 5.3 Update LLM Factory

```python
# Add to llm/llm_factory.py
from manufacturing_rag_implementation import ManufacturingRAGClient

def get_llm(config):
    llm_model = config.get("LLM_MODEL", "claude")
    
    if llm_model == "manufacturing_rag":
        return ManufacturingRAGClient(
            base_url=config.get("MANUFACTURING_RAG", {}).get("HTTP_BASE_URL"),
            knowledge_base_id=config.get("MANUFACTURING_RAG", {}).get("KNOWLEDGE_BASE_ID"),
            aws_region=config.get("MANUFACTURING_RAG", {}).get("AWS_REGION", "us-east-1"),
            verbose=config.get("VERBOSE", False)
        )
    
    # ... existing LLM configurations
```

## Step 6: Testing and Validation

### 6.1 Test API Endpoint

```bash
# Test Claude endpoint
curl -X POST $API_ENDPOINT/claude \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is the emergency shutdown procedure for machine XYZ-123?",
    "system": "You are a manufacturing assistant."
  }'
```

### 6.2 Test Knowledge Base Retrieval

```python
# test_rag.py
import boto3
import json

def test_knowledge_base():
    client = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
    
    response = client.retrieve(
        knowledgeBaseId='your-knowledge-base-id',
        retrievalQuery={'text': 'safety procedure'},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': 3
            }
        }
    )
    
    print("Retrieved documents:")
    for result in response['retrievalResults']:
        print(f"- {result['metadata'].get('source', 'Unknown')}")
        print(f"  Score: {result['score']}")
        print(f"  Content: {result['content']['text'][:200]}...")
        print()

if __name__ == "__main__":
    test_knowledge_base()
```

### 6.3 Test VTuber Integration

```bash
# Start the VTuber assistant with manufacturing RAG enabled
python server.py --config conf.yaml

# Test voice commands:
# "Hey assistant, what's the safety protocol for machine ABC-456?"
# "Show me the troubleshooting guide for error code E123"
# "What are the maintenance requirements for production line 2?"
```

## Step 7: Monitoring and Maintenance

### 7.1 Set Up CloudWatch Monitoring

```bash
# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
    --dashboard-name "ManufacturingAssistant" \
    --dashboard-body '{
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "metrics": [
                        ["AWS/Lambda", "Invocations", "FunctionName", "manufacturing-claude-rag"],
                        ["AWS/Lambda", "Errors", "FunctionName", "manufacturing-claude-rag"],
                        ["AWS/Lambda", "Duration", "FunctionName", "manufacturing-claude-rag"]
                    ],
                    "period": 300,
                    "stat": "Sum",
                    "region": "us-east-1",
                    "title": "Lambda Metrics"
                }
            }
        ]
    }'
```

### 7.2 Set Up Alerts

```bash
# Create SNS topic for alerts
aws sns create-topic --name manufacturing-assistant-alerts

# Create CloudWatch alarm for Lambda errors
aws cloudwatch put-metric-alarm \
    --alarm-name "ManufacturingAssistant-HighErrorRate" \
    --alarm-description "High error rate in manufacturing assistant" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --threshold 5 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value=manufacturing-claude-rag \
    --evaluation-periods 2
```

## Cost Optimization

### Expected Monthly Costs (for moderate usage)

- **Bedrock Claude**: ~$50-100 (based on token usage)
- **Bedrock Knowledge Base**: ~$20-40 (storage and retrieval)
- **OpenSearch**: ~$200-300 (t3.small instance)
- **Lambda**: ~$5-15 (execution time)
- **API Gateway**: ~$3-10 (requests)
- **S3**: ~$5-20 (document storage)

**Total estimated cost: $283-485/month**

### Cost Optimization Tips

1. **Use Reserved Instances** for OpenSearch if usage is predictable
2. **Implement caching** to reduce Bedrock API calls
3. **Optimize document chunking** to reduce storage costs
4. **Monitor usage patterns** and adjust instance sizes accordingly
5. **Use S3 Intelligent Tiering** for document storage

## Security Considerations

### 6.1 Network Security

```bash
# Create VPC endpoints for Bedrock (optional but recommended)
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-12345678 \
    --service-name com.amazonaws.us-east-1.bedrock-runtime \
    --route-table-ids rtb-12345678
```

### 6.2 IAM Best Practices

- Use least privilege access principles
- Rotate access keys regularly
- Enable CloudTrail for audit logging
- Use resource-based policies where appropriate

### 6.3 Data Protection

- Enable encryption at rest for all services
- Use HTTPS for all API communications
- Implement proper access controls for sensitive documents
- Regular security audits and penetration testing

## Troubleshooting

### Common Issues

1. **Knowledge Base sync fails**
   - Check S3 bucket permissions
   - Verify IAM role has correct policies
   - Check document formats are supported

2. **Lambda timeout errors**
   - Increase timeout settings
   - Optimize document retrieval queries
   - Implement proper error handling

3. **High API costs**
   - Implement response caching
   - Optimize prompt engineering
   - Monitor usage patterns

4. **Poor retrieval quality**
   - Adjust chunking parameters
   - Improve document metadata
   - Fine-tune embedding models

## Next Steps

1. **Performance Optimization**: Monitor usage patterns and optimize accordingly
2. **Advanced Features**: Add multi-modal search, real-time updates
3. **Integration**: Connect with existing manufacturing systems (MES, ERP)
4. **Analytics**: Implement usage analytics and insights
5. **Scaling**: Plan for horizontal scaling as usage grows

This deployment guide provides a comprehensive foundation for implementing RAG-enhanced manufacturing assistance. Adjust configurations based on your specific requirements and scale as needed.