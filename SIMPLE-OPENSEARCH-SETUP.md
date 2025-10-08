# Simple OpenSearch Serverless Setup Guide

## 🎯 Clear Step-by-Step Instructions

### Step 1: Navigate to OpenSearch Service
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. **Make sure you're in the `us-west-2` region** (top right corner)
3. In the search bar at the top, type: `OpenSearch Service`
4. Click on **Amazon OpenSearch Service**

### Step 2: Access Serverless Collections
1. In the left sidebar, you'll see several options
2. Look for the **"Serverless"** section (not the regular OpenSearch section)
3. Under **Serverless**, click on **"Collections"**

### Step 3: Create Security Policies FIRST
**Important**: You must create policies BEFORE creating the collection!

#### 3a. Create Network Policy
1. In the left sidebar under **Serverless**, click **"Security policies"**
2. Click the **"Network policies"** tab
3. Click **"Create network policy"**
4. Fill in:
   - **Policy name**: `manufacturing-kb-net`
   - **Policy definition**: Select **"JSON"** and paste:
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
5. Click **"Create"**

#### 3b. Create Encryption Policy
1. Still in **"Security policies"**, click the **"Encryption policies"** tab
2. Click **"Create encryption policy"**
3. Fill in:
   - **Policy name**: `manufacturing-kb-enc`
   - **Policy definition**: Select **"JSON"** and paste:
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
4. Click **"Create"**

#### 3c. Create Data Access Policy
1. In the left sidebar under **Serverless**, click **"Access policies"**
2. Click **"Create access policy"**
3. Fill in:
   - **Policy name**: `manufacturing-kb-data`
   - **Policy type**: Keep as **"Data access policy"**
   - **Policy definition**: Select **"JSON"** and paste (replace `615299772411` with your account ID):
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
4. Click **"Create"**

### Step 4: Create the Collection
1. Go back to **"Collections"** in the left sidebar (under Serverless)
2. Click **"Create collection"**
3. Fill in:
   - **Collection name**: `manufacturing-kb`
   - **Collection type**: **Vector search**
   - **Description**: `Manufacturing Knowledge Base vector collection`
4. Click **"Create collection"**

### Step 5: Wait for Collection to Become Active
- The collection will show status **"Creating"**
- Wait 2-5 minutes for it to become **"Active"**
- ✅ When it shows **"Active"**, you're done!

### Step 6: Note the Collection Details
Once active, click on your collection name and note:
- **Collection endpoint**: Something like `https://xxxxxxxxxx.us-west-2.aoss.amazonaws.com`
- **Collection ARN**: `arn:aws:aoss:us-west-2:615299772411:collection/manufacturing-kb`

## 🎉 After Manual Setup

### Continue with RAG Setup
Now run the RAG infrastructure setup:
```bash
python setup_rag_infrastructure.py
```

This should now work because the OpenSearch collection exists!

## 🔍 Where to Find Things in AWS Console

### OpenSearch Service Structure:
```
AWS Console
└── OpenSearch Service
    ├── Domains (regular OpenSearch - NOT what we want)
    └── Serverless
        ├── Collections ← Create collection here
        ├── Security policies ← Create network & encryption policies here
        └── Access policies ← Create data access policy here
```

## 🚨 Common Mistakes to Avoid

1. **Wrong Section**: Don't use "Domains" - use "Serverless"
2. **Wrong Order**: Create policies BEFORE creating collection
3. **Wrong Region**: Make sure you're in `us-west-2`
4. **Policy Names**: Keep them short (under 32 characters)

## 💡 Visual Confirmation

You'll know it's working when:
- ✅ All 3 policies show "Active" status
- ✅ Collection shows "Active" status  
- ✅ Collection has an endpoint URL
- ✅ RAG setup script runs without OpenSearch errors

---

**🎯 This manual approach is the most reliable way to get your OpenSearch collection set up correctly!**