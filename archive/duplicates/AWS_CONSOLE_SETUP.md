# AWS Console Setup Guide - Easy Visual Method

Since the CLI has encoding issues, let's set up AWS Knowledge Base using the AWS Console - much easier and more visual!

## 🎯 **AWS Console Setup (6 Easy Steps)**

### **Step 1: Create S3 Bucket for Documents**

1. **Go to S3 Console**: https://console.aws.amazon.com/s3/
2. **Click "Create bucket"**
3. **Configure bucket**:
   ```
   Bucket name: live2d-manufacturing-docs-[your-unique-suffix]
   Region: US West (Oregon) us-west-2
   Block all public access: ✅ (keep checked)
   Bucket versioning: Enable
   ```
4. **Click "Create bucket"**
5. **Create folder**: Click into your bucket → "Create folder" → Name: `manufacturing`

### **Step 2: Upload Sample Documents**

1. **In your S3 bucket**, click into the `manufacturing` folder
2. **Click "Upload"**
3. **Create a sample document** on your computer:

**File: `heater_error_103.md`**
```markdown
# Manufacturing Error 103 - Heater Malfunction

## Overview
Error 103 indicates a heater malfunction in the manufacturing line.

## Safety Warnings
⚠️ **CRITICAL SAFETY**: Always shut down the line before inspecting heater components.
⚠️ **HIGH TEMPERATURE**: Allow 30 minutes cooling time before maintenance.

## Troubleshooting Steps
1. Check power supply connections
2. Verify temperature sensor readings
3. Inspect heating element for damage
4. Test control circuit continuity

## Resolution
- Replace faulty heating element if resistance is outside 10-15 ohms
- Recalibrate temperature sensors if readings are inconsistent
- Contact maintenance team for electrical issues

## Prevention
- Regular monthly inspections
- Keep heating elements clean
- Monitor temperature logs daily
```

4. **Upload this file** to your S3 bucket under `manufacturing/`

### **Step 3: Create OpenSearch Domain**

1. **Go to OpenSearch Console**: https://console.aws.amazon.com/aos/
2. **Click "Create domain"**
3. **Configure domain**:
   ```
   Domain name: vtuber-vectors-dev
   Deployment type: Development and testing
   Version: OpenSearch 2.11 (or latest available)
   Instance type: t3.micro.search (cheapest option)
   OR: m6g.medium.search (if t3.micro not available)
   Number of nodes: 1
   Storage type: EBS
   EBS volume type: General Purpose (SSD - gp3)
   EBS volume size: 10 GiB (minimum for testing)
   ```
4. **Network configuration**:
   ```
   Network: Public access
   Fine-grained access control: Disabled
   Anonymous access: Enabled (for testing)
   ```
5. **Access policy**: Choose "Configure domain level access policy"
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "*"
         },
         "Action": "es:*",
         "Resource": "arn:aws:es:us-west-2:*:domain/vtuber-vectors-dev/*"
       }
     ]
   }
   ```
6. **Click "Create"** (takes 15-20 minutes)

**💡 Instance Type Options (choose what's available):**
- **t3.micro.search** - Cheapest (~$15/month)
- **t3.small.search** - Small workloads (~$30/month)
- **m6g.medium.search** - Better performance (~$45/month)
- **r6g.medium.search** - Memory optimized (~$50/month)

**Note**: If you don't see `t3.small.search`, use `t3.micro.search` for testing or `m6g.medium.search` for better performance.

### **Step 4: Create IAM Role for Bedrock**

1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Click "Roles" → "Create role"**
3. **Select trusted entity**:
   ```
   Trusted entity type: AWS service
   Use case: Bedrock
   ```
4. **Add permissions**: Search and add these policies:
   - `AmazonBedrockFullAccess`
   - `AmazonS3ReadOnlyAccess`
   - `AmazonOpenSearchServiceFullAccess`
5. **Role details**:
   ```
   Role name: BedrockKnowledgeBaseRole
   Description: Role for Bedrock Knowledge Base to access S3 and OpenSearch
   ```
6. **Click "Create role"**

### **Step 5: Create Knowledge Base**

1. **Go to Bedrock Console**: https://console.aws.amazon.com/bedrock/
2. **Click "Knowledge bases" → "Create knowledge base"**

#### **5a. Provide knowledge base details**
```
Name: live2d-manufacturing-kb
Description: Manufacturing documentation for Live2D VTuber Assistant
IAM role: BedrockKnowledgeBaseRole (from Step 4)
```

#### **5b. Set up data source**
```
Data source name: manufacturing-docs
S3 URI: s3://[your-bucket-name]/manufacturing/
Chunking and parsing configurations:
  - Chunking strategy: Fixed size chunking
  - Max tokens: 300
  - Overlap percentage: 20
```

#### **5c. Select embeddings model and configure vector store**
```
Embeddings model: Titan Embeddings G1 - Text v1.2
Vector database: OpenSearch Serverless
Collection: Create new collection
  - Collection name: manufacturing-vectors
  - Encryption: AWS owned key
Vector index name: manufacturing-docs-index
Vector field name: vector
Text field name: text
Metadata field name: metadata
```

3. **Click "Create knowledge base"**

### **Step 6: Test Your Knowledge Base**

1. **In the Knowledge Base console**, wait for status to show "Active"
2. **Click on your Knowledge Base**
3. **Go to "Data source" tab** → Click "Sync" to start ingestion
4. **Wait for sync to complete** (5-10 minutes)
5. **Test with sample query**:
   - Go to "Test knowledge base" section
   - Enter: "What should I do for heater error 103?"
   - You should see relevant results from your uploaded document

## 🔧 **Configure Your Application**

### **Step 7: Update Your Local Configuration**

Create a `.env` file with your AWS settings:

```bash
# Replace with your actual values from AWS Console
AWS_REGION=us-west-2
AWS_KNOWLEDGE_BASE_ID=[your-kb-id-from-bedrock-console]
DOCUMENTS_BUCKET_NAME=[your-s3-bucket-name]
RAG_ENABLED=true
RAG_MODE=hybrid
PREFER_AWS_RAG=true
RAG_MAX_RESULTS=5
RAG_SCORE_THRESHOLD=0.5
MANUFACTURING_MODE=true
```

### **Step 8: Test Your Enhanced Server**

```powershell
# Start the enhanced server
python run_enhanced_server.py

# In another window, test RAG
curl -X POST http://localhost:8000/claude -H "Content-Type: application/json" -d '{\"text\": \"What should I do for heater error 103?\", \"enable_rag\": true}'
```

## 📊 **Visual Verification Checklist**

### **In AWS Console, verify these show "Active" or "Complete":**
- [ ] **S3 Bucket**: Shows your bucket with `manufacturing/` folder
- [ ] **OpenSearch Domain**: Status shows "Active" (green)
- [ ] **IAM Role**: `BedrockKnowledgeBaseRole` exists
- [ ] **Knowledge Base**: Status shows "Active"
- [ ] **Data Source**: Last sync shows "COMPLETE"
- [ ] **Test Query**: Returns relevant results

### **In your application, verify these work:**
- [ ] **Health endpoint**: `curl http://localhost:8000/health` returns success
- [ ] **RAG health**: `curl http://localhost:8000/rag/health` shows AWS KB enabled
- [ ] **Enhanced responses**: Manufacturing questions get detailed context
- [ ] **Safety indicators**: Responses include warning symbols for safety content

## 💰 **Cost Management**

### **Monitor costs in AWS Console:**
1. **Go to AWS Billing Console**: https://console.aws.amazon.com/billing/
2. **Set up billing alerts** for $50/month
3. **Monitor these services**:
   - OpenSearch Service (~$25/month)
   - Bedrock Knowledge Base (~$5-10/month)
   - S3 Storage (~$1/month)

### **Cost optimization tips:**
- Use smallest OpenSearch instance (t3.small.search)
- Delete test resources when not needed
- Monitor query volume in CloudWatch

## 🚨 **Troubleshooting**

### **Common Issues:**

#### **Issue 1: Knowledge Base creation fails**
- **Check IAM role permissions**
- **Verify OpenSearch domain is "Active"**
- **Ensure S3 bucket exists and is accessible**

#### **Issue 2: No search results**
- **Check data source sync status**
- **Verify documents are uploaded to correct S3 path**
- **Try different search terms**

#### **Issue 3: Application can't connect**
- **Verify Knowledge Base ID in .env file**
- **Check AWS credentials are configured**
- **Test with: `aws sts get-caller-identity`**

## 🎉 **Success Indicators**

You'll know it's working when:

✅ **Knowledge Base test query** returns relevant manufacturing content
✅ **Enhanced server starts** without errors
✅ **RAG health endpoint** shows AWS KB enabled
✅ **Manufacturing questions** get enhanced responses with context
✅ **Safety warnings** appear for safety-critical content

## 🔗 **Useful AWS Console Links**

- **S3 Console**: https://console.aws.amazon.com/s3/
- **OpenSearch Console**: https://console.aws.amazon.com/aos/
- **Bedrock Console**: https://console.aws.amazon.com/bedrock/
- **IAM Console**: https://console.aws.amazon.com/iam/
- **CloudWatch Console**: https://console.aws.amazon.com/cloudwatch/
- **Billing Console**: https://console.aws.amazon.com/billing/

## 📱 **Mobile-Friendly Setup**

You can even do this setup from your phone using the AWS Mobile Console app! The visual interface makes it much easier than dealing with CLI encoding issues.

This console-based approach is much more reliable and gives you visual feedback at each step. No more encoding errors or PATH issues!