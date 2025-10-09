# AWS Knowledge Base RAG Integration Setup Guide

This guide provides step-by-step instructions for integrating AWS Knowledge Base with your Live2D VTuber Assistant for enhanced RAG (Retrieval-Augmented Generation) capabilities.

## Overview

The AWS Knowledge Base integration provides:
- **Scalable Vector Search**: Managed OpenSearch with automatic scaling
- **Hybrid Search**: Combines semantic and keyword search
- **Automatic Document Processing**: Intelligent chunking and indexing
- **Real-time Updates**: Automatic re-indexing when documents change
- **Enterprise Security**: IAM-based access control
- **Fallback Support**: Hybrid system with local RAG fallback

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Live2D App    │    │  Enhanced Server │    │  AWS Lambda     │
│                 │◄──►│                  │◄──►│                 │
│ - Frontend      │    │ - Hybrid RAG     │    │ - Claude API    │
│ - WebSocket     │    │ - Local Fallback │    │ - Knowledge Base│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Local RAG       │    │ AWS Knowledge   │
                       │                  │    │ Base            │
                       │ - SimpleS3RAG    │    │                 │
                       │ - DemoRAG        │    │ - OpenSearch    │
                       └──────────────────┘    │ - S3 Documents  │
                                               │ - Vector Index  │
                                               └─────────────────┘
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** configured with credentials
3. **SAM CLI** installed
4. **Python 3.11+** with required packages
5. **Node.js** (for frontend components)

### Required AWS Permissions

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:*",
                "lambda:*",
                "apigateway:*",
                "s3:*",
                "dynamodb:*",
                "es:*",
                "bedrock:*",
                "bedrock-agent:*",
                "iam:CreateRole",
                "iam:AttachRolePolicy",
                "iam:PassRole"
            ],
            "Resource": "*"
        }
    ]
}
```

## Installation Steps

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt
pip install boto3 aiohttp

# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Install SAM CLI
pip install aws-sam-cli
```

### Step 2: Configure AWS Credentials

```bash
# Configure AWS CLI
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-west-2
```

### Step 3: Deploy Infrastructure

Use the automated deployment script:

```bash
# Full deployment (recommended for first-time setup)
python deploy_aws_rag.py --region us-west-2 --stack-name live2d-aws-backend

# Or step-by-step deployment
python deploy_aws_rag.py --region us-west-2 --skip-test

# Deploy only infrastructure (if Knowledge Base exists)
python deploy_aws_rag.py --skip-kb --skip-docs
```

### Step 4: Manual Knowledge Base Creation (Alternative)

If the automated script fails, create the Knowledge Base manually:

1. **Go to AWS Bedrock Console** → Knowledge Bases
2. **Create Knowledge Base**:
   - Name: `live2d-manufacturing-kb`
   - Description: `Manufacturing documentation for Live2D VTuber Assistant`
3. **Configure Data Source**:
   - Type: S3
   - Bucket: Use the bucket from CloudFormation outputs
   - Prefix: `manufacturing/`
4. **Configure Vector Store**:
   - Use the OpenSearch domain from CloudFormation
   - Index name: `manufacturing-docs-index`
5. **Set Chunking Strategy**:
   - Fixed size: 300 tokens
   - Overlap: 20%

### Step 5: Configure Environment

Copy the generated environment file:

```bash
# Use the generated configuration
cp .env.aws-rag .env

# Or manually create .env file
cat > .env << EOF
# AWS Knowledge Base Configuration
AWS_REGION=us-west-2
AWS_KNOWLEDGE_BASE_ID=your-kb-id-here
DOCUMENTS_BUCKET_NAME=your-bucket-name
HTTP_API_BASE=https://your-api-id.execute-api.us-west-2.amazonaws.com/dev
WEBSOCKET_URL=wss://your-ws-id.execute-api.us-west-2.amazonaws.com/dev

# RAG Configuration
RAG_ENABLED=true
RAG_MODE=hybrid
PREFER_AWS_RAG=true
RAG_MAX_RESULTS=5
RAG_SCORE_THRESHOLD=0.5
RAG_SEARCH_TYPE=HYBRID

# Safety Features
SAFETY_KEYWORDS_ENABLED=true
MANUFACTURING_MODE=true
EOF
```

## Usage

### Running the Enhanced Server

```bash
# Start the enhanced server with AWS Knowledge Base support
python server_enhanced.py --config conf.yaml --host 127.0.0.1 --port 8000

# Or use the original server (will fall back to local RAG)
python server.py --port 8000
```

### Testing the Integration

```bash
# Run comprehensive tests
python test_aws_kb_integration.py --test all --save-report

# Test specific components
python test_aws_kb_integration.py --test aws-kb
python test_aws_kb_integration.py --test hybrid
python test_aws_kb_integration.py --test server
python test_aws_kb_integration.py --test lambda
python test_aws_kb_integration.py --test accuracy
```

### Using the API

#### Local Server Endpoint

```bash
# Test RAG-enhanced Claude endpoint
curl -X POST http://localhost:8000/claude \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What should I do if I see heater error 103?",
    "enable_rag": true,
    "rag_mode": "hybrid",
    "system": "You are a manufacturing assistant."
  }'
```

#### AWS Lambda Endpoint

```bash
# Test AWS Lambda Claude endpoint
curl -X POST https://your-api-id.execute-api.us-west-2.amazonaws.com/dev/claude \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What are the safety procedures for equipment maintenance?",
    "enable_rag": true,
    "system": "You are a manufacturing assistant with access to technical documentation."
  }'
```

## Document Management

### Uploading Documents

```bash
# Upload documents to S3 (triggers automatic indexing)
aws s3 cp your-document.pdf s3://your-bucket-name/manufacturing/
aws s3 cp documentation/ s3://your-bucket-name/manufacturing/ --recursive

# Or use the Python API
python -c "
from aws_knowledge_base_rag import AWSKnowledgeBaseRAG
rag = AWSKnowledgeBaseRAG('your-kb-id')
# Upload and index documents programmatically
"
```

### Supported Document Formats

- **Text**: `.txt`, `.md`
- **Documents**: `.pdf`, `.docx`
- **Web**: `.html`
- **Data**: `.json`, `.csv`

### Document Structure

Organize documents in S3 with clear prefixes:

```
s3://your-bucket/manufacturing/
├── procedures/
│   ├── quality_control.md
│   ├── safety_protocols.pdf
│   └── maintenance_schedule.docx
├── troubleshooting/
│   ├── heater_errors.md
│   ├── sensor_issues.pdf
│   └── electrical_problems.txt
└── specifications/
    ├── equipment_specs.pdf
    └── tolerance_requirements.md
```

## Configuration Options

### RAG System Configuration

```python
# In your configuration file or environment
RAG_CONFIG = {
    "AWS_KNOWLEDGE_BASE_ID": "your-kb-id",
    "AWS_REGION": "us-west-2",
    "RAG_MODE": "hybrid",  # aws, local, hybrid
    "PREFER_AWS_RAG": True,
    "MAX_RESULTS": 5,
    "SCORE_THRESHOLD": 0.5,
    "SEARCH_TYPE": "HYBRID"  # HYBRID, SEMANTIC, KEYWORD
}
```

### Search Types

- **HYBRID**: Combines semantic and keyword search (recommended)
- **SEMANTIC**: Vector-based semantic search only
- **KEYWORD**: Traditional keyword-based search only

### Fallback Behavior

The hybrid system provides automatic fallback:

1. **Primary**: AWS Knowledge Base (if available)
2. **Secondary**: Local S3 RAG (if configured)
3. **Tertiary**: Local document cache
4. **Fallback**: No RAG enhancement (original query)

## Monitoring and Optimization

### CloudWatch Metrics

Monitor these key metrics:

- **Retrieval Latency**: Time to retrieve documents
- **Query Volume**: Number of RAG queries per hour
- **Success Rate**: Percentage of successful retrievals
- **Cost**: OpenSearch and Bedrock usage costs

### Performance Tuning

```python
# Optimize retrieval parameters
aws_rag = AWSKnowledgeBaseRAG(
    knowledge_base_id="your-kb-id",
    max_results=3,  # Reduce for faster queries
    score_threshold=0.7  # Increase for higher quality
)

# Configure chunking for better results
chunking_config = {
    "chunkingStrategy": "FIXED_SIZE",
    "fixedSizeChunkingConfiguration": {
        "maxTokens": 300,  # Adjust based on document type
        "overlapPercentage": 20  # Increase for better context
    }
}
```

### Cost Optimization

1. **Right-size OpenSearch**: Start with t3.small.search
2. **Optimize Chunking**: Balance chunk size vs. accuracy
3. **Monitor Usage**: Set up billing alerts
4. **Use Caching**: Implement response caching for common queries

## Troubleshooting

### Common Issues

#### 1. Knowledge Base Not Found

```bash
# Check if Knowledge Base exists
aws bedrock-agent list-knowledge-bases --region us-west-2

# Verify permissions
aws sts get-caller-identity
```

#### 2. No Documents Retrieved

```bash
# Check ingestion status
aws bedrock-agent list-ingestion-jobs \
  --knowledge-base-id your-kb-id \
  --data-source-id your-data-source-id

# Verify documents in S3
aws s3 ls s3://your-bucket-name/manufacturing/ --recursive
```

#### 3. High Latency

- Reduce `max_results` parameter
- Increase `score_threshold` to filter results
- Use `SEMANTIC` search type for faster queries
- Consider caching frequent queries

#### 4. Poor Retrieval Quality

- Adjust chunking parameters
- Use `HYBRID` search type
- Lower `score_threshold` to get more results
- Improve document structure and metadata

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set environment variable
export LOG_LEVEL=DEBUG
```

### Health Checks

```bash
# Check system health
curl http://localhost:8000/health
curl http://localhost:8000/rag/health

# Test Knowledge Base directly
python -c "
from aws_knowledge_base_rag import AWSKnowledgeBaseRAG
rag = AWSKnowledgeBaseRAG('your-kb-id')
print(rag.health_check())
"
```

## Security Considerations

### IAM Best Practices

1. **Principle of Least Privilege**: Grant only necessary permissions
2. **Role-based Access**: Use IAM roles instead of user credentials
3. **Resource-specific Policies**: Limit access to specific resources
4. **Regular Audits**: Review and rotate credentials regularly

### Data Protection

1. **Encryption at Rest**: S3 and OpenSearch encryption enabled
2. **Encryption in Transit**: HTTPS/TLS for all API calls
3. **Access Logging**: Enable CloudTrail and API Gateway logging
4. **Data Classification**: Mark sensitive documents appropriately

### Network Security

1. **VPC Endpoints**: Use VPC endpoints for AWS services
2. **Security Groups**: Restrict network access
3. **API Gateway**: Use API keys and throttling
4. **CORS Configuration**: Limit allowed origins

## Advanced Features

### Custom Embeddings

```python
# Use custom embedding models
embedding_config = {
    'embeddingModelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v2'
}
```

### Metadata Filtering

```python
# Filter documents by metadata
retrieval_config = {
    'vectorSearchConfiguration': {
        'numberOfResults': 5,
        'overrideSearchType': 'HYBRID',
        'filter': {
            'equals': {
                'key': 'document_type',
                'value': 'safety_procedure'
            }
        }
    }
}
```

### Multi-language Support

```python
# Configure for multiple languages
chunking_config = {
    'chunkingStrategy': 'SEMANTIC',
    'semanticChunkingConfiguration': {
        'maxTokens': 300,
        'bufferSize': 0,
        'breakpointPercentileThreshold': 95
    }
}
```

## Migration from Local RAG

### Gradual Migration

1. **Phase 1**: Deploy AWS infrastructure alongside local RAG
2. **Phase 2**: Configure hybrid mode with AWS preference
3. **Phase 3**: Test and validate AWS Knowledge Base
4. **Phase 4**: Gradually increase AWS preference
5. **Phase 5**: Disable local RAG (optional)

### Data Migration

```bash
# Export existing RAG documents
python -c "
from simple_s3_rag import SimpleS3RAG
local_rag = SimpleS3RAG()
documents = local_rag.export_documents()
# Upload to AWS S3
"

# Bulk upload to S3
aws s3 sync ./local_documents/ s3://your-bucket-name/manufacturing/
```

## Support and Resources

### Documentation

- [AWS Bedrock Knowledge Base Documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base.html)
- [OpenSearch Service Documentation](https://docs.aws.amazon.com/opensearch-service/)
- [AWS SAM Documentation](https://docs.aws.amazon.com/serverless-application-model/)

### Community

- [GitHub Issues](https://github.com/your-repo/issues)
- [Discord Community](https://discord.gg/your-server)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/aws-bedrock)

### Professional Support

For enterprise deployments, consider:
- AWS Professional Services
- AWS Support Plans
- Third-party consulting services

## Changelog

### Version 1.0.0 (Current)
- Initial AWS Knowledge Base integration
- Hybrid RAG system with fallback
- Enhanced server with RAG support
- Comprehensive testing suite
- Automated deployment scripts

### Planned Features
- Multi-modal document support (images, videos)
- Real-time document synchronization
- Advanced analytics and reporting
- Custom embedding fine-tuning
- Integration with other AWS AI services

---

## Quick Start Checklist

- [ ] AWS account with appropriate permissions
- [ ] AWS CLI and SAM CLI installed
- [ ] Python dependencies installed
- [ ] Run `python deploy_aws_rag.py`
- [ ] Copy `.env.aws-rag` to `.env`
- [ ] Upload sample documents
- [ ] Run `python test_aws_kb_integration.py --test all`
- [ ] Start enhanced server: `python server_enhanced.py`
- [ ] Test with manufacturing queries

For questions or issues, please refer to the troubleshooting section or create an issue in the repository.