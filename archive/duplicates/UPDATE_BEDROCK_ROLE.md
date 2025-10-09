
# Update BedrockKnowledgeBaseRole for OpenSearch Serverless

I can see you already have the `BedrockKnowledgeBaseRole` created with S3 and Bedrock permissions. You just need to add OpenSearch Serverless permissions to it.

## 🔍 **Your Current Setup:**

### **Existing Role**: `BedrockKnowledgeBaseRole`
### **S3 Bucket**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761`
### **Current Permissions**: ✅ S3 access, ✅ Bedrock access

## 🔧 **Add OpenSearch Serverless Permissions**

### **Step 1: Go to IAM Console**
1. **Open**: https://console.aws.amazon.com/iam/
2. **Click "Roles"**
3. **Search for**: `BedrockKnowledgeBaseRole`
4. **Click on the role**

### **Step 2: Add OpenSearch Serverless Policy**
1. **Click "Add permissions" → "Create inline policy"**
2. **Click "JSON" tab**
3. **Paste this policy**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "aoss:APIAccessAll",
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex",
                "aoss:ReadDocument",
                "aoss:WriteDocument"
            ],
            "Resource": [
                "arn:aws:aoss:us-west-2:615299772411:collection/manufacturing-vectors",
                "arn:aws:aoss:us-west-2:615299772411:index/manufacturing-vectors/*"
            ]
        }
    ]
}
```

4. **Policy name**: `OpenSearchServerlessAccess`
5. **Click "Create policy"**

## 📋 **Your Complete Updated Role**

After adding the OpenSearch Serverless policy, your `BedrockKnowledgeBaseRole` will have:

### **Policy 1: BedrockKBPolicy (Existing)**
```json
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
                "arn:aws:s3:::live2d-aws-backend-documentsbucket-gvqh2hzqj761",
                "arn:aws:s3:::live2d-aws-backend-documentsbucket-gvqh2hzqj761/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel"
            ],
            "Resource": "*"
        }
    ]
}
```

### **Policy 2: OpenSearchServerlessAccess (New)**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "aoss:APIAccessAll",
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex",
                "aoss:ReadDocument",
                "aoss:WriteDocument"
            ],
            "Resource": [
                "arn:aws:aoss:us-west-2:615299772411:collection/manufacturing-vectors",
                "arn:aws:aoss:us-west-2:615299772411:index/manufacturing-vectors/*"
            ]
        }
    ]
}
```

## 🎯 **Updated OpenSearch Serverless Access Policy**

Since you have the role already created, update the OpenSearch Serverless access policy to use your existing role:

### **Access Policy JSON (Updated for your setup):**
```json
[
  {
    "Rules": [
      {
        "Resource": [
          "collection/manufacturing-vectors"
        ],
        "Permission": [
          "aoss:CreateCollectionItems",
          "aoss:DeleteCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ],
        "ResourceType": "collection"
      },
      {
        "Resource": [
          "index/manufacturing-vectors/*"
        ],
        "Permission": [
          "aoss:CreateIndex",
          "aoss:DeleteIndex",
          "aoss:UpdateIndex",
          "aoss:DescribeIndex",
          "aoss:ReadDocument",
          "aoss:WriteDocument"
        ],
        "ResourceType": "index"
      }
    ],
    "Principal": [
      "arn:aws:iam::615299772411:user/Vtuber",
      "arn:aws:iam::615299772411:role/BedrockKnowledgeBaseRole"
    ]
  }
]
```

## ✅ **Your Configuration Summary:**

### **Resources You Have:**
- ✅ **AWS Account ID**: `615299772411`
- ✅ **IAM User**: `Vtuber`
- ✅ **IAM Role**: `BedrockKnowledgeBaseRole` (existing)
- ✅ **S3 Bucket**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761`

### **What You Need to Create:**
- 🔧 **OpenSearch Serverless Collection**: `manufacturing-vectors`
- 🔧 **Access Policies**: Using the names and JSON above
- 🔧 **Knowledge Base**: In Bedrock Console

### **Your .env Configuration:**
```bash
AWS_REGION=us-west-2
AWS_ACCOUNT_ID=615299772411
DOCUMENTS_BUCKET_NAME=live2d-aws-backend-documentsbucket-gvqh2hzqj761
RAG_ENABLED=true
RAG_MODE=hybrid
PREFER_AWS_RAG=true
```

## 🚀 **Next Steps:**

1. **Update IAM Role**: Add OpenSearch Serverless permissions (instructions above)
2. **Create OpenSearch Serverless**: Follow [`OPENSEARCH_SERVERLESS_SETUP.md`](LLM-Live2D-Desktop-Assitant-main/OPENSEARCH_SERVERLESS_SETUP.md)
3. **Use Policy Names**: From [`OPENSEARCH_POLICY_NAMES.md`](LLM-Live2D-Desktop-Assitant-main/OPENSEARCH_POLICY_NAMES.md)
4. **Create Knowledge Base**: Connect to your existing S3 bucket and new collection
5. **Test Integration**: `python run_enhanced_server.py`

You're all set with the exact policy names, configurations, and your specific AWS account details!
</result>
</attempt_completion>