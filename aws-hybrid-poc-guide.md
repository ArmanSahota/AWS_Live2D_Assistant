# AWS Hybrid PoC Implementation Guide

## Quick Start Guide for Hybrid Architecture
*Keep local speech processing + AWS Claude/Storage*

## Architecture Overview

```
[Desktop] → Local STT/TTS → [AWS Claude API] → Response
           ↓                      ↓
        Electron App          DynamoDB/S3
```

## Phase 1: Immediate Actions (Day 1)

### 1. Fix Critical Security Issues
**MUST DO BEFORE DEPLOYMENT**

#### Fix 1: Python Injection Vulnerability
File: `src/main/ipc.js:296-298`

```javascript
// CURRENT (VULNERABLE):
const pythonCode = `
text = """${text}"""
# ... rest of code
`;

// FIXED VERSION:
// Add this BEFORE line 296
const sanitizedText = text
  .replace(/\\/g, '\\\\')  // Escape backslashes
  .replace(/"""/g, '\\"\\"\\"')  // Escape triple quotes
  .replace(/'/g, "\\'")  // Escape single quotes
  .replace(/\n/g, '\\n')  // Escape newlines

const pythonCode = `
import json
text = json.loads('${JSON.stringify(sanitizedText)}')
# ... rest of code
`;
```

#### Fix 2: Missing Function
File: `src/main/ipc.js:253`

```javascript
// Add this function before line 253
function resolveModel3Path(modelPath) {
  const path = require('path');
  const fs = require('fs');
  
  // Check if path exists
  if (fs.existsSync(modelPath)) {
    return modelPath;
  }
  
  // Try common locations
  const possiblePaths = [
    path.join(__dirname, '..', 'static', 'desktop', 'models', modelPath),
    path.join(process.resourcesPath, 'models', modelPath),
    modelPath
  ];
  
  for (const p of possiblePaths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  
  throw new Error(`Model not found: ${modelPath}`);
}
```

#### Fix 3: Wake Word File
File: `static/desktop.html:21` and `static/desktop/vad.js:196`

```javascript
// Option 1: Disable wake word for English (Quick fix)
// In vad.js, line 196:
try {
  const wakeWordFile = language === 'zh' 
    ? '伊蕾娜_zh_wasm_v3_0_0.ppn'
    : null; // Disable for English temporarily
  
  if (wakeWordFile) {
    // Load wake word
  } else {
    console.log('Wake word not available for', language);
  }
} catch (error) {
  console.warn('Wake word loading failed, continuing without it');
}
```

### 2. Test Existing AWS Endpoint

Create test file: `test-aws-hybrid.js`

```javascript
const axios = require('axios');
require('dotenv').config();

// Configuration
const HTTP_BASE = process.env.HTTP_BASE || 'https://your-api.execute-api.us-west-2.amazonaws.com/dev';

async function testClaudeEndpoint() {
  try {
    console.log('Testing AWS Claude endpoint...');
    
    const response = await axios.post(`${HTTP_BASE}/claude`, {
      text: "Hello, can you hear me?",
      system: "You are a helpful AI assistant."
    });
    
    console.log('✅ Success! Response:', response.data.reply);
    return true;
  } catch (error) {
    console.error('❌ Failed:', error.message);
    if (error.response) {
      console.error('Response:', error.response.data);
    }
    return false;
  }
}

async function testHealthEndpoint() {
  try {
    const response = await axios.get(`${HTTP_BASE}/health`);
    console.log('✅ Health check:', response.data);
    return true;
  } catch (error) {
    console.error('❌ Health check failed:', error.message);
    return false;
  }
}

// Run tests
async function runTests() {
  console.log('Starting AWS endpoint tests...\n');
  
  const healthOk = await testHealthEndpoint();
  if (!healthOk) {
    console.log('\n⚠️  Check your HTTP_BASE URL in .env file');
    return;
  }
  
  const claudeOk = await testClaudeEndpoint();
  if (claudeOk) {
    console.log('\n✅ All tests passed! AWS integration is working.');
  }
}

runTests();
```

Run: `node test-aws-hybrid.js`

## Phase 2: Minimal Integration (Day 2-3)

### 1. Update Electron to Use AWS Directly

File: `src/main/claudeClient.js`

```javascript
// This file already works! Just ensure HTTP_BASE is set in .env
// Current implementation is good for PoC
```

### 2. Keep Local Python Server Running
No changes needed - it handles STT/TTS perfectly

### 3. Update Configuration

File: `.env`
```env
# AWS Configuration
HTTP_BASE=https://your-actual-api.execute-api.us-west-2.amazonaws.com/dev
AWS_REGION=us-west-2

# Keep local for PoC
USE_LOCAL_TTS=true
USE_LOCAL_STT=true

# Optional for later
USE_DYNAMODB=false
USE_S3_MODELS=false
```

## Phase 3: Add Session Persistence (Day 4-5)

### 1. Update SAM Template for Sessions

Add to `backend/template.yml`:

```yaml
  SaveSessionFn:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.lambda_handler
      InlineCode: |
        import json, boto3, time
        ddb = boto3.resource('dynamodb')
        table = ddb.Table(os.environ['TABLE_NAME'])
        
        def lambda_handler(event, context):
          body = json.loads(event['body'])
          item = {
            'userId': body.get('userId', 'default'),
            'sessionId': body['sessionId'],
            'messages': body.get('messages', []),
            'timestamp': int(time.time()),
            'ttl': int(time.time()) + 86400  # 24 hour TTL
          }
          table.put_item(Item=item)
          return {
            'statusCode': 200,
            'body': json.dumps({'success': True})
          }
      Environment:
        Variables:
          TABLE_NAME: !Ref SessionsTable
      Events:
        SaveSession:
          Type: HttpApi
          Properties:
            ApiId: !Ref HttpApi
            Method: POST
            Path: /session
```

### 2. Integrate in Electron

```javascript
// Add session saving
async function saveConversation(sessionId, messages) {
  try {
    await fetch(`${HTTP_BASE}/session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId,
        userId: 'local-user',
        messages
      })
    });
  } catch (error) {
    console.error('Failed to save session:', error);
  }
}
```

## Phase 4: Move Assets to CDN (Optional, Day 6-7)

### 1. Upload Live2D Models to S3

```bash
# Create S3 bucket
aws s3 mb s3://your-live2d-models

# Upload models
aws s3 sync ./static/desktop/models s3://your-live2d-models/models --acl public-read

# Set up CloudFront
aws cloudfront create-distribution --origin-domain-name your-live2d-models.s3.amazonaws.com
```

### 2. Update Model Loading

```javascript
// In electron.js
const MODEL_CDN = process.env.USE_CDN 
  ? 'https://d123456.cloudfront.net/models'
  : './models';

// Load from CDN or local
const modelPath = `${MODEL_CDN}/default/default.model3.json`;
```

## Testing Checklist

### Basic Functionality
- [ ] Application launches without errors
- [ ] Microphone input works
- [ ] Local STT processes speech correctly
- [ ] AWS Claude endpoint responds
- [ ] Local TTS generates audio
- [ ] Live2D avatar animates

### AWS Integration
- [ ] Health endpoint returns 200
- [ ] Claude endpoint processes text
- [ ] Response time < 2 seconds
- [ ] Error handling works
- [ ] Reconnection logic functions

### Performance Metrics
- [ ] STT latency: < 200ms (local)
- [ ] Claude response: < 1500ms 
- [ ] TTS generation: < 100ms (local)
- [ ] Total round-trip: < 2000ms

## Deployment Commands

### 1. Deploy AWS Backend
```bash
cd backend
sam build
sam deploy --guided
# Note the HTTP_BASE URL from outputs
```

### 2. Start Local Components
```bash
# Terminal 1: Python server (for STT/TTS)
python server.py

# Terminal 2: Electron app
npm start
```

### 3. Test End-to-End
```bash
# Run test suite
npm test

# Test AWS integration
node test-aws-hybrid.js
```

## Common Issues & Solutions

### Issue 1: WebSocket Connection Fails
**Solution**: Keep using local WebSocket for now, only use AWS for Claude API

### Issue 2: CORS Errors
**Solution**: Already handled in SAM template, but can add:
```yaml
Cors:
  AllowOrigins:
    - "http://localhost:*"
    - "file://*"
  AllowHeaders:
    - "*"
  AllowMethods:
    - "*"
```

### Issue 3: Slow Response Times
**Solution**: 
- Ensure Lambda is warm (use provisioned concurrency for production)
- Check AWS region (use closest to users)
- Enable API Gateway caching

## Cost Estimate for PoC

| Service | Monthly Usage | Cost |
|---------|--------------|------|
| Lambda | 10K requests | $2 |
| API Gateway | 10K requests | $0.03 |
| DynamoDB | 1GB storage | $0.25 |
| CloudFront | 10GB transfer | $0.85 |
| **Total** | | **< $5/month** |

## Success Criteria

✅ **PoC is successful when:**
1. User can speak to the assistant
2. Local STT converts speech to text
3. AWS Claude processes the text
4. Response is generated
5. Local TTS speaks the response
6. Live2D avatar animates

## Next Steps After PoC

1. **Week 2**: Add user authentication with Cognito
2. **Week 3**: Implement conversation history UI
3. **Week 4**: Add more Live2D expressions
4. **Month 2**: Consider moving to container-based deployment for scale

## Quick Reference

### Environment Variables
```bash
HTTP_BASE=https://your-api.execute-api.us-west-2.amazonaws.com/dev
USE_LOCAL_TTS=true
USE_LOCAL_STT=true
AWS_REGION=us-west-2
```

### Key Files to Modify
1. `src/main/ipc.js` - Fix security issues
2. `.env` - Add AWS endpoint
3. `backend/template.yml` - Extend AWS services

### Testing Commands
```bash
# Test AWS
node test-aws-hybrid.js

# Run app
npm start

# Deploy backend
sam deploy
```

---

**This hybrid approach gives you:**
- ✅ Ultra-low latency speech (local)
- ✅ Powerful AI (AWS Claude)
- ✅ Scalable storage (AWS)
- ✅ Cost-effective PoC
- ✅ Privacy-first design

**Ready to start!** Follow Phase 1 first to fix critical issues, then test AWS endpoint.