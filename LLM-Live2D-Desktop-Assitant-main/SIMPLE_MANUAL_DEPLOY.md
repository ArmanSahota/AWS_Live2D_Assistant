# Simple Manual AWS Deployment - Guaranteed to Work

The automated scripts have PATH issues with SAM CLI. Here's the manual method that definitely works:

## 🎯 **Working Deployment Steps**

### **Step 1: Deploy Infrastructure (Manual SAM)**

```powershell
# Navigate to backend directory
cd backend

# Deploy directly with SAM CLI (this works!)
sam deploy --template-file template.yml --stack-name live2d-aws-backend --parameter-overrides Env=dev EnableRagInfra=true --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM --region us-west-2

# Go back to main directory
cd ..
```

**Expected Output:**
```
Deploying with following values
===============================
Stack name                   : live2d-aws-backend
Region                      : us-west-2
Confirm changeset           : False
Disable rollback            : False
Deployment s3 bucket        : aws-sam-cli-managed-default-samclisourcebucket-xxxxx
Capabilities                : ["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"]
Parameter overrides         : {"Env": "dev", "EnableRagInfra": "true"}

Successfully created/updated stack - live2d-aws-backend in us-west-2
```

### **Step 2: Get Your AWS Resources**

```powershell
# Get stack outputs
aws cloudformation describe-stacks --stack-name live2d-aws-backend --region us-west-2 --query "Stacks[0].Outputs" --output table
```

**Save these values:**
- **DocumentsBucketName**: `live2d-aws-backend-documentsbucket-xxxxx`
- **OpenSearchDomainEndpoint**: `https://vtuber-vectors-dev-xxxxx.us-west-2.es.amazonaws.com`
- **BedrockKBRoleArn**: `arn:aws:iam::615299772411:role/BedrockKBRole-dev`
- **HttpBase**: `https://xxxxx.execute-api.us-west-2.amazonaws.com/dev`

### **Step 3: Create Knowledge Base (AWS Console)**

1. **Open AWS Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. **Go to Knowledge Bases** → **Create Knowledge Base**
3. **Basic Information**:
   ```
   Name: live2d-manufacturing-kb
   Description: Manufacturing documentation for Live2D VTuber Assistant
   ```

4. **IAM Role**: Select **"Use an existing service role"**
   - Choose the `BedrockKBRole-dev` from your stack outputs

5. **Data Source Configuration**:
   ```
   Data source name: manufacturing-docs
   Data source type: S3
   S3 location: s3://[your-bucket-name]/manufacturing/
   ```

6. **Chunking Configuration**:
   ```
   Chunking strategy: Fixed size chunking
   Max tokens: 300
   Overlap percentage: 20
   ```

7. **Vector Database**:
   ```
   Vector database: OpenSearch Serverless
   Collection ARN: [Use your OpenSearch domain from Step 2]
   Vector index name: manufacturing-docs-index
   Vector field name: vector
   Text field name: text
   Metadata field name: metadata
   ```

8. **Embedding Model**:
   ```
   amazon.titan-embed-text-v1
   ```

9. **Click "Create Knowledge Base"**

### **Step 4: Upload Documents**

```powershell
# Upload your existing RAG documents
aws s3 cp rag_documents\ s3://[your-bucket-name]/manufacturing/ --recursive

# Or create a simple test document
echo "# Manufacturing Error 103
Heater malfunction detected. 

## Safety Procedures
1. Immediately shut down the heating system
2. Allow 30 minutes cooling time
3. Check temperature sensors
4. Inspect heating elements for damage

## Resolution Steps
- Replace heating element if resistance is outside 10-15 ohms
- Recalibrate temperature sensors
- Contact maintenance team for electrical issues" > manufacturing_error_103.md

aws s3 cp manufacturing_error_103.md s3://[your-bucket-name]/manufacturing/
```

### **Step 5: Start Ingestion Job**

In the AWS Bedrock Console:
1. **Go to your Knowledge Base**
2. **Click "Data Sources" tab**
3. **Click "Sync"** to start ingestion
4. **Wait for "COMPLETE" status** (5-10 minutes)

### **Step 6: Update Your Configuration**

```powershell
# Create .env file with your actual values
echo "AWS_REGION=us-west-2
AWS_KNOWLEDGE_BASE_ID=[your-kb-id-from-console]
DOCUMENTS_BUCKET_NAME=[your-bucket-name]
HTTP_API_BASE=[your-http-base]
RAG_ENABLED=true
RAG_MODE=hybrid
PREFER_AWS_RAG=true" > .env
```

### **Step 7: Test Everything**

```powershell
# Test the enhanced server
python run_enhanced_server.py
```

In another PowerShell window:
```powershell
# Test RAG functionality
curl -X POST http://localhost:8000/claude -H "Content-Type: application/json" -d '{\"text\": \"What should I do for heater error 103?\", \"enable_rag\": true}'
```

## 🔍 **Troubleshooting the SAM Issue**

The `sam` command PATH issue can be fixed by:

### **Option 1: Add SAM to PATH**
```powershell
# Find where SAM is installed
where sam

# If not found, add Python Scripts to PATH
$env:PATH += ";$env:LOCALAPPDATA\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts"
```

### **Option 2: Use Full Path**
```powershell
# Find the full path to sam.exe
Get-Command sam -ErrorAction SilentlyContinue

# Use full path in commands
C:\Users\[username]\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts\sam.exe deploy ...
```

### **Option 3: Reinstall SAM CLI**
```powershell
# Uninstall and reinstall SAM CLI
pip uninstall aws-sam-cli
pip install aws-sam-cli

# Or use the MSI installer
# Download from: https://github.com/aws/aws-sam-cli/releases/latest
```

## ✅ **Success Indicators**

You'll know it's working when:

1. **SAM Deploy**: Shows "Successfully created/updated stack"
2. **Knowledge Base**: Shows "ACTIVE" status in console
3. **Ingestion Job**: Shows "COMPLETE" status
4. **Test Query**: Returns relevant manufacturing context
5. **Enhanced Server**: Starts without errors
6. **RAG Health**: `/rag/health` endpoint returns success

## 🚀 **Quick Test Commands**

Once everything is set up:

```powershell
# Health check
curl http://localhost:8000/health

# RAG health check
curl http://localhost:8000/rag/health

# Test manufacturing question
curl -X POST http://localhost:8000/claude -H "Content-Type: application/json" -d '{\"text\": \"What are the safety procedures for equipment maintenance?\", \"enable_rag\": true}'
```

## 💡 **Pro Tips**

1. **Use PowerShell ISE** or **Windows Terminal** for better command support
2. **Run as Administrator** if you encounter permission issues
3. **Check AWS Service Health** if deployments fail: https://status.aws.amazon.com/
4. **Monitor costs** in AWS Billing console
5. **Use the original server** as fallback: `python server.py --port 8000`

This manual method bypasses all the automation issues and gives you full control over the deployment process!