# Fix AWS Permissions for RAG Setup

## 🚨 Root Cause
The AWS user `arn:aws:iam::615299772411:user/Vtuber` doesn't have the required permissions for OpenSearch Serverless and Bedrock operations.

## 🔧 Quick Fix - Apply IAM Policy

### Step 1: Apply the Required IAM Policy

You need to attach the policy in [`aws-permissions-fix.json`](aws-permissions-fix.json) to your `Vtuber` user.

#### Option A: Using AWS Console (Recommended)
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Navigate to **Users** → **Vtuber**
3. Click **Add permissions** → **Attach policies directly**
4. Click **Create policy** → **JSON**
5. Copy and paste the content from [`aws-permissions-fix.json`](aws-permissions-fix.json)
6. Name the policy: `VtuberRAGPermissions`
7. Create and attach the policy to the `Vtuber` user

#### Option B: Using AWS CLI
```bash
# Create the policy
aws iam create-policy \
    --policy-name VtuberRAGPermissions \
    --policy-document file://aws-permissions-fix.json

# Attach to user
aws iam attach-user-policy \
    --user-name Vtuber \
    --policy-arn arn:aws:iam::615299772411:policy/VtuberRAGPermissions
```

### Step 2: Fix Policy Name Length Issue
The encryption policy name is too long. Let me create a corrected version:

```bash
# Use shorter names for policies
manufacturing-kb-net-policy      # instead of manufacturing-kb-network-policy
manufacturing-kb-enc-policy      # instead of manufacturing-kb-encryption-policy  
manufacturing-kb-data-policy     # instead of manufacturing-kb-access-policy
```

## 🎯 Alternative: Manual AWS Console Setup

Since automated scripts require extensive permissions, the **manual approach is most reliable**:

### Step 1: Create OpenSearch Collection Manually
Follow the detailed guide in [`MANUAL-OPENSEARCH-SETUP.md`](MANUAL-OPENSEARCH-SETUP.md)

### Step 2: Skip Automated OpenSearch Setup
Once you have the collection created manually, run:
```bash
python setup_rag_infrastructure.py
```

This will create the Bedrock Knowledge Base using your existing collection.

## 📋 Required Permissions Summary

Your `Vtuber` user needs these key permissions:

### OpenSearch Serverless
- `aoss:CreateSecurityPolicy`
- `aoss:CreateAccessPolicy` 
- `aoss:CreateCollection`
- `aoss:BatchGetCollection`
- `aoss:ListCollections`

### Bedrock
- `bedrock-agent:CreateKnowledgeBase`
- `bedrock-agent:CreateDataSource`
- `bedrock-agent:StartIngestionJob`
- `bedrock:InvokeModel`

### S3 (for your bucket)
- `s3:GetObject`
- `s3:PutObject`
- `s3:ListBucket`

### IAM (for service roles)
- `iam:CreateRole`
- `iam:PutRolePolicy`
- `iam:PassRole`

## 🚀 Recommended Approach

**For fastest setup:**

1. **Apply the IAM policy** from [`aws-permissions-fix.json`](aws-permissions-fix.json)
2. **Use manual OpenSearch setup** from [`MANUAL-OPENSEARCH-SETUP.md`](MANUAL-OPENSEARCH-SETUP.md)
3. **Run RAG infrastructure setup**: `python setup_rag_infrastructure.py`
4. **Test integration**: `python test_rag_integration.py`

## ⚡ Quick Commands After Permissions Fix

```bash
# Manual OpenSearch setup (most reliable)
# Follow MANUAL-OPENSEARCH-SETUP.md

# Then run RAG setup
python setup_rag_infrastructure.py

# Test everything
python test_rag_integration.py
```

## 🔍 Verify Permissions

Test if permissions are working:
```bash
# Test OpenSearch access
aws opensearchserverless list-collections --region us-west-2

# Test Bedrock access  
aws bedrock-agent list-knowledge-bases --region us-west-2

# Test S3 access
aws s3 ls s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/
```

## 💡 Why Manual Setup is Better

1. **No complex permissions needed** - just basic console access
2. **Visual confirmation** - see each step working
3. **Error handling** - AWS Console provides clear error messages
4. **One-time setup** - once created, automated scripts work fine

---

**🎯 Bottom Line**: Apply the IAM policy, then use manual OpenSearch setup for the most reliable experience. Your RAG system will be running in 10-15 minutes!