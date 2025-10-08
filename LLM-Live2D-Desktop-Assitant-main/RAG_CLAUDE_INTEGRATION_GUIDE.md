# RAG-Enhanced Claude Integration Guide

## Overview

This guide explains how the RAG (Retrieval-Augmented Generation) system has been integrated with your existing Claude model to provide additional context from your S3 document buckets without changing Claude's core prompting behavior.

## What Was Added

### 1. RAG-Enhanced Claude Client (`src/main/ragEnhancedClaudeClient.js`)

A new JavaScript module that extends your existing Claude client with RAG capabilities:

- **Automatic Context Retrieval**: Searches your S3 documents for relevant information based on user queries
- **Seamless Integration**: Works as a drop-in replacement for the original Claude client
- **Configurable**: Can be enabled/disabled via configuration
- **Non-Intrusive**: Adds context without changing Claude's personality or core prompting

### 2. Enhanced Server Endpoint (`server.py`)

The `/claude` endpoint has been enhanced to:

- Automatically retrieve relevant context from S3 documents
- Add context to Claude requests when relevant information is found
- Provide metadata about RAG enhancement in responses
- Gracefully handle RAG system failures

### 3. Configuration Updates (`src/config/appConfig.js`)

- RAG is now **enabled by default**
- Can be disabled by setting `RAG_ENABLED=false` environment variable
- Uses existing S3 bucket configuration

## How It Works

### 1. Query Processing Flow

```
User Query → RAG System → S3 Document Search → Context Retrieval → Enhanced Claude Request → Response
```

### 2. Context Enhancement

When a user asks a question:

1. **Query Analysis**: The system analyzes the user's question for relevant keywords
2. **Document Search**: Searches your S3 bucket (`live2d-aws-backend-documentsbucket-gvqh2hzqj761`) for relevant documents
3. **Context Extraction**: Extracts the most relevant chunks from matching documents
4. **Context Addition**: Adds context to the Claude request in a structured format:

```
Original User Question

=== RELEVANT INFORMATION FROM KNOWLEDGE BASE ===
From Manufacturing Safety Manual: [relevant content]
From Equipment Troubleshooting Guide: [relevant content]
=== END KNOWLEDGE BASE ===
```

5. **Claude Processing**: Claude processes the enhanced request with additional context
6. **Response**: Claude responds with knowledge from both its training and your documents

### 3. Smart Context Filtering

The system only adds context when:
- Relevant documents are found (relevance score > 0.5)
- The query appears to be related to your domain (manufacturing, safety, etc.)
- The S3 RAG system is available and functioning

## Configuration

### Environment Variables

```bash
# Enable/disable RAG (default: enabled)
RAG_ENABLED=true

# S3 bucket containing your documents
DOCUMENTS_BUCKET_NAME=live2d-aws-backend-documentsbucket-gvqh2hzqj761

# AWS credentials (required for S3 access)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-west-2
```

### Document Structure

Your S3 bucket should contain text files (`.txt`) in the `manufacturing/` folder:

```
s3://your-bucket/
└── manufacturing/
    ├── safety-procedures.txt
    ├── equipment-manual.txt
    ├── troubleshooting-guide.txt
    └── maintenance-schedules.txt
```

## Testing

### 1. Run the Integration Test

```bash
# Test the RAG integration
python test_rag_claude_integration.py

# Or use the batch script on Windows
test_rag_integration.bat
```

### 2. Test Queries

Try these example queries to see RAG in action:

**Manufacturing/Safety Queries (should trigger RAG):**
- "What is the lockout tagout procedure?"
- "What PPE is required for maintenance?"
- "How do I troubleshoot error code E001?"
- "What are the machine maintenance schedules?"

**General Queries (should NOT trigger RAG):**
- "What's the weather like today?"
- "Tell me a joke"
- "How do I cook pasta?"

### 3. Check Response Metadata

RAG-enhanced responses include additional metadata:

```json
{
  "reply": "Enhanced response with context...",
  "status": "success",
  "tokens_used": 150,
  "rag_enhanced": true,
  "context_chunks": 2
}
```

## Usage Examples

### JavaScript Client Usage

```javascript
const { askClaudeWithRAG } = require('./src/main/ragEnhancedClaudeClient');

// This will automatically include relevant context from S3
const response = await askClaudeWithRAG("What safety procedures should I follow?");
console.log(response);
```

### HTTP API Usage

```bash
curl -X POST http://localhost:1025/claude \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the lockout tagout procedure?"}'
```

## Benefits

### 1. **No Prompt Changes**
- Claude's personality and behavior remain unchanged
- Context is added transparently
- Original prompting strategy is preserved

### 2. **Automatic Relevance**
- Only adds context when relevant
- Filters out irrelevant information
- Smart keyword matching for your domain

### 3. **Scalable**
- Works with any number of documents in S3
- Efficient caching reduces repeated S3 calls
- Graceful degradation if RAG system is unavailable

### 4. **Transparent Operation**
- Clear logging shows when RAG is active
- Response metadata indicates enhancement status
- Easy to debug and monitor

## Troubleshooting

### Common Issues

1. **RAG Not Working**
   - Check AWS credentials are configured
   - Verify S3 bucket access permissions
   - Ensure documents exist in the `manufacturing/` folder

2. **No Context Found**
   - Check document content matches query keywords
   - Verify documents are in `.txt` format
   - Review relevance scoring in logs

3. **Performance Issues**
   - Documents are cached after first load
   - Consider reducing document size or chunk count
   - Monitor S3 API call frequency

### Debug Commands

```bash
# Test S3 access directly
python -c "from simple_s3_rag import SimpleS3RAG; rag = SimpleS3RAG(); print(rag.load_documents_from_s3())"

# Test document search
python -c "from simple_s3_rag import SimpleS3RAG; rag = SimpleS3RAG(); print(rag.retrieve_relevant_chunks('safety procedure'))"

# Check server logs for RAG activity
# Look for [RAG] prefixed log messages
```

## Next Steps

1. **Add More Documents**: Upload additional `.txt` files to your S3 bucket's `manufacturing/` folder
2. **Customize Keywords**: Modify the `manufacturing_keywords` in `simple_s3_rag.py` for your specific domain
3. **Adjust Relevance**: Tune the relevance scoring algorithm for better context matching
4. **Monitor Usage**: Watch server logs to see how often RAG enhancement is triggered

## Security Notes

- RAG system respects existing AWS IAM permissions
- No sensitive data is logged (only document names and chunk counts)
- Context is only added to Claude requests, not stored permanently
- All S3 access uses your existing AWS credentials

---

**The RAG integration is now active and will automatically enhance Claude responses with relevant information from your S3 documents while preserving Claude's original behavior and personality.**