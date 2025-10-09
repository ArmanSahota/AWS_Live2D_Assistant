# Add OpenSearch Serverless Policy to Existing BedrockKnowledgeBaseRole

I can see you already have the `BedrockKnowledgeBaseRole` with S3 and Bedrock permissions. You just need to add OpenSearch Serverless access.

## 🔍 **Your Current Role Status:**

### **✅ What You Already Have:**
- **Role Name**: `BedrockKnowledgeBaseRole`
- **S3 Bucket Access**: `live2d-aws-backend-documentsbucket-gvqh2hzqj761` ✅
- **Bedrock Model Access**: `bedrock:InvokeModel` ✅

### **🔧 What You Need to Add:**
- **OpenSearch Serverless permissions** for Knowledge Base integration

## 🚀 **Step-by-Step: Add OpenSearch Serverless Policy**

### **Step 1: Go to Your Existing Role**
1. **Go to IAM Console**: https://console.aws.amazon.com/iam/
2. **Click "Roles"**
3. **Search for**: `BedrockKnowledgeBaseRole`
4. **Click on the role**

### **Step 2: Add Inline Policy**
1. **Click "Add permissions" → "Create inline policy"**
2. **Click "JSON" tab**
3. **Paste this exact policy**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "aoss:APIAccessAll"
            ],
            "Resource": "arn:aws:aoss:us-west-2:615299772411:collection/manufacturing-vectors"
        },
        {
            "Effect": "Allow",
            "Action": [
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex",
                "aoss:ReadDocument",
                "aoss:WriteDocument"
            ],
            "Resource": "arn:aws:aoss:us-west-2:615299772411:index/manufacturing-vectors/*"
        }
    ]
}
```

4. **Policy name**: `OpenSearchServerlessAccess`
5. **Description**: `Allows access to OpenSearch Serverless collection for Knowledge Base`
6. **Click "Create policy"**

## ✅ **Your Complete Role After Update**

Your `BedrockKnowledgeBaseRole` will now have **3 policies**:

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
                "aoss:APIAccessAll"
            ],
            "Resource": "arn:aws:aoss:us-west-2:615299772411:collection/manufacturing-vectors"
        },
        {
            "Effect": "Allow",
            "Action": [
                "aoss:CreateIndex",
                "aoss:DeleteIndex",
                "aoss:UpdateIndex",
                "aoss:DescribeIndex",
                "aoss:ReadDocument",
                "aoss:WriteDocument"
            ],
            "Resource": "arn:aws:aoss:us-west-2:615299772411:index/manufacturing-vectors/*"
        }
    ]
}
```

## 🎯 **Updated OpenSearch Serverless Access Policy**

Now that I know your exact setup, here's the **updated access policy** for OpenSearch Serverless:

### **Policy Name**: `live2d-manufacturing-access-policy`
### **Policy JSON**:
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

## 🔧 **Your Knowledge Base Configuration**

When creating the Knowledge Base, use these **exact values**:

### **Knowledge Base Settings:**
```
Name: live2d-manufacturing-kb
Description: Manufacturing documentation for Live2D VTuber Assistant
IAM role: BedrockKnowledgeBaseRole (your existing role)
```

### **Data Source Settings:**
```
Data source name: manufacturing-docs
S3 URI: s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/manufacturing/
```

### **Vector Store Settings:**
```
Vector database: OpenSearch Serverless
Collection: manufacturing-vectors (create new or select existing)
Vector index name: manufacturing-docs-index
```

## 🎉 **Ready to Proceed**

After updating your IAM role with OpenSearch Serverless permissions:

1. **Create OpenSearch Serverless collection** using the policies above
2. **Create Knowledge Base** using your existing S3 bucket and role
3. **Upload documents** to: `s3://live2d-aws-backend-documentsbucket-gvqh2hzqj761/manufacturing/`
4. **Test with**: `python run_enhanced_server.py`

Your existing infrastructure is perfect - you just need to add the OpenSearch Serverless component!