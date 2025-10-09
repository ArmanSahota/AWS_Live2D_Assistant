# Manual OpenSearch Serverless Collection Setup

If the automated scripts fail, you can create the OpenSearch Serverless collection manually through the AWS Console. This is often the most reliable approach.

## Step-by-Step Manual Setup

### 1. Access AWS Console
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to **OpenSearch Service** → **Serverless collections**
3. Ensure you're in the **us-west-2** region

### 2. Create Security Policies

#### Network Policy
1. Go to **Security policies** → **Network policies**
2. Click **Create policy**
3. **Policy name**: `manufacturing-kb-network-policy`
4. **Policy JSON**:
```json
[
  {
    "Rules": [
      {
        "Resource": ["collection/manufacturing-kb"],
        "ResourceType": "collection"
      }
    ],
    "AllowFromPublic": true
  }
]
```
5. Click **Create**

#### Encryption Policy
1. Go to **Security policies** → **Encryption policies**
2. Click **Create policy**
3. **Policy name**: `manufacturing-kb-encryption-policy`
4. **Policy JSON**:
```json
[
  {
    "Rules": [
      {
        "Resource": ["collection/manufacturing-kb"],
        "ResourceType": "collection"
      }
    ],
    "AWSOwnedKey": true
  }
]
```
5. Click **Create**

#### Data Access Policy
1. Go to **Access policies** → **Data access policies**
2. Click **Create policy**
3. **Policy name**: `manufacturing-kb-access-policy`
4. **Policy JSON** (replace `615299772411` with your account ID):
```json
[
  {
    "Rules": [
      {
        "Resource": ["collection/manufacturing-kb"],
        "Permission": [
          "aoss:CreateCollectionItems",
          "aoss:DeleteCollectionItems",
          "aoss:UpdateCollectionItems",
          "aoss:DescribeCollectionItems"
        ],
        "ResourceType": "collection"
      },
      {
        "Resource": ["index/manufacturing-kb/*"],
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
      "arn:aws:iam::615299772411:root",
      "arn:aws:iam::615299772411:role/BedrockKnowledgeBaseRole"
    ]
  }
]
```
5. Click **Create**

### 3. Create Collection
1. Go to **Collections**
2. Click **Create collection**
3. **Collection name**: `manufacturing-kb`
4. **Collection type**: **Vector search**
5. **Description**: `Manufacturing Knowledge Base vector collection`
6. Click **Create**

### 4. Wait for Collection to Become Active
- The collection will show status "Creating" initially
- Wait 2-5 minutes for it to become "Active"
- Note the **Collection endpoint** (you'll need this)

### 5. Get Collection Details
Once active, note these details:
- **Collection name**: `manufacturing-kb`
- **Collection endpoint**: `https://xxxxxxxxxx.us-west-2.aoss.amazonaws.com`
- **Collection ARN**: `arn:aws:aoss:us-west-2:615299772411:collection/manufacturing-kb`

## After Manual Setup

### Continue with RAG Setup
Once the collection is active, run:
```bash
python setup_rag_infrastructure.py
```

The script should now successfully create the Bedrock Knowledge Base using your manually created collection.

### Verify Setup
Check that everything is working:
```bash
python test_rag_integration.py
```

## Troubleshooting Manual Setup

### Common Issues

#### 1. Policy JSON Validation Errors
- Ensure JSON is properly formatted
- Use the exact JSON provided above
- Check for missing commas or brackets

#### 2. Permission Denied
- Ensure your AWS user has permissions for:
  - `aoss:CreateSecurityPolicy`
  - `aoss:CreateAccessPolicy`
  - `aoss:CreateCollection`

#### 3. Collection Creation Fails
- Verify all three policies are created first
- Check that policy names match exactly
- Ensure you're in the correct region (us-west-2)

### Required AWS Permissions
Your AWS user/role needs these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "aoss:CreateSecurityPolicy",
        "aoss:CreateAccessPolicy",
        "aoss:CreateCollection",
        "aoss:BatchGetCollection",
        "aoss:ListCollections"
      ],
      "Resource": "*"
    }
  ]
}
```

## Expected Timeline
- **Security Policies**: 1-2 minutes each
- **Collection Creation**: 2-5 minutes
- **Total Time**: 5-10 minutes

## Success Indicators
✅ All three security policies show "Active" status
✅ Collection shows "Active" status
✅ Collection endpoint is available
✅ RAG infrastructure setup completes successfully

---

**💡 Tip**: The manual approach through AWS Console is often more reliable than automated scripts, especially for first-time setup. Once you have the collection created, the rest of the RAG setup should work smoothly.