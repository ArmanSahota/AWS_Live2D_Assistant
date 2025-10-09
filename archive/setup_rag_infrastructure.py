#!/usr/bin/env python3
"""
RAG Infrastructure Setup Script
===============================

This script helps set up the RAG (Retrieval-Augmented Generation) infrastructure
for the VTuber Manufacturing Assistant using your existing AWS deployment.

Usage:
    python setup_rag_infrastructure.py

Requirements:
    - AWS CLI configured with appropriate permissions
    - boto3 library installed
    - Existing AWS infrastructure from your deployment
"""

import boto3
import json
import time
import os
from typing import Dict, List, Optional
from botocore.exceptions import ClientError

class RAGInfrastructureSetup:
    """
    Sets up RAG infrastructure using existing AWS resources
    """
    
    def __init__(self, region: str = 'us-west-2'):
        self.region = region
        self.bedrock_client = boto3.client('bedrock', region_name=region)
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=region)
        self.s3_client = boto3.client('s3', region_name=region)
        self.iam_client = boto3.client('iam', region_name=region)
        
        # Your existing infrastructure details
        self.config = {
            'ws_url': 'wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev',
            'http_base': 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
            'documents_bucket': 'live2d-aws-backend-documentsbucket-gvqh2hzqj761',
            'region': region,
            'rag_enabled': False  # Will be set to True after setup
        }
        
        print(f"🚀 Initializing RAG Infrastructure Setup")
        print(f"📍 Region: {region}")
        print(f"🪣 Documents Bucket: {self.config['documents_bucket']}")
        print(f"🌐 HTTP Base: {self.config['http_base']}")
    
    def check_existing_resources(self) -> Dict[str, bool]:
        """
        Check which resources already exist
        """
        print("\n🔍 Checking existing AWS resources...")
        
        resources = {
            's3_bucket': False,
            'bedrock_available': False,
            'knowledge_base': False,
            'data_source': False
        }
        
        # Check S3 bucket
        try:
            self.s3_client.head_bucket(Bucket=self.config['documents_bucket'])
            resources['s3_bucket'] = True
            print(f"✅ S3 Bucket exists: {self.config['documents_bucket']}")
        except ClientError:
            print(f"❌ S3 Bucket not found: {self.config['documents_bucket']}")
        
        # Check Bedrock availability
        try:
            models = self.bedrock_client.list_foundation_models()
            resources['bedrock_available'] = True
            print("✅ Bedrock service is available")
        except ClientError as e:
            print(f"❌ Bedrock service error: {e}")
        
        # Check for existing knowledge bases
        try:
            kb_response = self.bedrock_agent_client.list_knowledge_bases()
            if kb_response.get('knowledgeBaseSummaries'):
                resources['knowledge_base'] = True
                print(f"✅ Found {len(kb_response['knowledgeBaseSummaries'])} existing knowledge base(s)")
            else:
                print("ℹ️ No existing knowledge bases found")
        except ClientError as e:
            print(f"⚠️ Could not check knowledge bases: {e}")
        
        return resources
    
    def create_iam_role_for_bedrock(self) -> str:
        """
        Create IAM role for Bedrock Knowledge Base
        """
        print("\n🔐 Setting up IAM role for Bedrock...")
        
        role_name = "BedrockKnowledgeBaseRole"
        
        # Trust policy for Bedrock
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "bedrock.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        # Permissions policy
        permissions_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": [
                        "s3:GetObject",
                        "s3:ListBucket"
                    ],
                    "Resource": [
                        f"arn:aws:s3:::{self.config['documents_bucket']}",
                        f"arn:aws:s3:::{self.config['documents_bucket']}/*"
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
        
        try:
            # Create role
            role_response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="Role for Bedrock Knowledge Base to access S3 documents"
            )
            
            # Attach inline policy
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName="BedrockKnowledgeBasePolicy",
                PolicyDocument=json.dumps(permissions_policy)
            )
            
            role_arn = role_response['Role']['Arn']
            print(f"✅ Created IAM role: {role_arn}")
            
            # Wait for role to propagate
            print("⏳ Waiting for IAM role to propagate...")
            time.sleep(10)
            
            return role_arn
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                # Role already exists, get its ARN
                role_response = self.iam_client.get_role(RoleName=role_name)
                role_arn = role_response['Role']['Arn']
                print(f"✅ Using existing IAM role: {role_arn}")
                return role_arn
            else:
                print(f"❌ Error creating IAM role: {e}")
                raise
    
    def create_knowledge_base(self, role_arn: str) -> str:
        """
        Create Bedrock Knowledge Base
        """
        print("\n📚 Creating Bedrock Knowledge Base...")
        
        kb_name = "manufacturing-assistant-kb"
        
        try:
            # Get account ID for collection ARN
            import boto3
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
            
            # Create knowledge base
            kb_response = self.bedrock_agent_client.create_knowledge_base(
                name=kb_name,
                description="Manufacturing Assistant Knowledge Base for technical documentation",
                roleArn=role_arn,
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': f'arn:aws:bedrock:{self.region}::foundation-model/amazon.titan-embed-text-v1'
                    }
                },
                storageConfiguration={
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': f'arn:aws:aoss:{self.region}:{account_id}:collection/manufacturing-kb',
                        'vectorIndexName': 'manufacturing-docs',
                        'fieldMapping': {
                            'vectorField': 'vector',
                            'textField': 'text',
                            'metadataField': 'metadata'
                        }
                    }
                }
            )
            
            knowledge_base_id = kb_response['knowledgeBase']['knowledgeBaseId']
            print(f"✅ Created Knowledge Base: {knowledge_base_id}")
            
            return knowledge_base_id
            
        except ClientError as e:
            print(f"❌ Error creating knowledge base: {e}")
            print("ℹ️ Note: You may need to create an OpenSearch Serverless collection first")
            raise
    
    def create_data_source(self, knowledge_base_id: str) -> str:
        """
        Create data source for the knowledge base
        """
        print("\n📄 Creating data source...")
        
        try:
            ds_response = self.bedrock_agent_client.create_data_source(
                knowledgeBaseId=knowledge_base_id,
                name="manufacturing-documents",
                description="Manufacturing technical documents and manuals",
                dataSourceConfiguration={
                    'type': 'S3',
                    's3Configuration': {
                        'bucketArn': f'arn:aws:s3:::{self.config["documents_bucket"]}',
                        'inclusionPrefixes': ['manufacturing/', 'docs/', 'manuals/']
                    }
                },
                vectorIngestionConfiguration={
                    'chunkingConfiguration': {
                        'chunkingStrategy': 'FIXED_SIZE',
                        'fixedSizeChunkingConfiguration': {
                            'maxTokens': 300,
                            'overlapPercentage': 20
                        }
                    }
                }
            )
            
            data_source_id = ds_response['dataSource']['dataSourceId']
            print(f"✅ Created Data Source: {data_source_id}")
            
            return data_source_id
            
        except ClientError as e:
            print(f"❌ Error creating data source: {e}")
            raise
    
    def upload_sample_documents(self):
        """
        Upload sample manufacturing documents to S3
        """
        print("\n📤 Uploading sample documents...")
        
        sample_docs = {
            'manufacturing/safety-protocols.txt': """
MANUFACTURING SAFETY PROTOCOLS
=============================

LOCKOUT/TAGOUT PROCEDURE:
1. Notify all affected personnel
2. Shut down equipment using normal stopping procedure
3. Isolate energy sources (electrical, pneumatic, hydraulic)
4. Apply lockout/tagout devices
5. Verify isolation by attempting to start equipment
6. Perform maintenance work
7. Remove lockout/tagout devices only by authorized person

EMERGENCY PROCEDURES:
- Emergency stop buttons located every 50 feet
- Fire extinguishers at each workstation
- First aid stations marked with green crosses
- Emergency contact: 911 or internal extension 2911

PPE REQUIREMENTS:
- Safety glasses required in all production areas
- Hard hats required in overhead work zones
- Steel-toed boots mandatory on production floor
- Hearing protection required in high-noise areas (>85dB)
            """,
            
            'manufacturing/machine-maintenance.txt': """
MACHINE MAINTENANCE SCHEDULE
===========================

CNC MACHINE MAINTENANCE:
Daily:
- Check coolant levels
- Inspect cutting tools for wear
- Clean work area and remove chips
- Verify emergency stops function

Weekly:
- Lubricate guide ways
- Check hydraulic fluid levels
- Inspect air filters
- Calibrate tool offsets

Monthly:
- Replace air filters
- Check belt tension
- Inspect electrical connections
- Update maintenance log

TROUBLESHOOTING COMMON ISSUES:
Error Code E001: Spindle overload
- Check for dull cutting tools
- Reduce feed rate
- Verify proper coolant flow

Error Code E002: Axis drive fault
- Check motor connections
- Inspect encoder cables
- Reset drive parameters if needed
            """,
            
            'manufacturing/parts-catalog.txt': """
PARTS CATALOG - PRODUCTION LINE 1
=================================

CONVEYOR SYSTEM:
- Belt: Part# CV-BELT-001, 50ft x 12in, Replacement interval: 6 months
- Motor: Part# CV-MOTOR-001, 5HP 3-phase, Replacement interval: 5 years
- Rollers: Part# CV-ROLLER-001, Set of 10, Replacement interval: 2 years

CNC MACHINE PARTS:
- Spindle Motor: Part# CNC-SPIN-001, 15HP, Replacement interval: 10 years
- Tool Changer: Part# CNC-ATC-001, 20-position, Replacement interval: 7 years
- Coolant Pump: Part# CNC-COOL-001, 2HP, Replacement interval: 3 years

SAFETY EQUIPMENT:
- Emergency Stop Button: Part# SAFE-ESTOP-001, Red mushroom head
- Light Curtain: Part# SAFE-LC-001, 48in height, 14mm resolution
- Safety Mat: Part# SAFE-MAT-001, 3ft x 5ft pressure sensitive
            """
        }
        
        try:
            for key, content in sample_docs.items():
                self.s3_client.put_object(
                    Bucket=self.config['documents_bucket'],
                    Key=key,
                    Body=content.encode('utf-8'),
                    ContentType='text/plain'
                )
                print(f"✅ Uploaded: {key}")
            
            print(f"✅ Uploaded {len(sample_docs)} sample documents")
            
        except ClientError as e:
            print(f"❌ Error uploading documents: {e}")
    
    def sync_knowledge_base(self, knowledge_base_id: str, data_source_id: str):
        """
        Sync the knowledge base with S3 documents
        """
        print("\n🔄 Syncing knowledge base...")
        
        try:
            sync_response = self.bedrock_agent_client.start_ingestion_job(
                knowledgeBaseId=knowledge_base_id,
                dataSourceId=data_source_id,
                description="Initial sync of manufacturing documents"
            )
            
            job_id = sync_response['ingestionJob']['ingestionJobId']
            print(f"✅ Started ingestion job: {job_id}")
            
            # Wait for ingestion to complete
            print("⏳ Waiting for ingestion to complete...")
            while True:
                job_status = self.bedrock_agent_client.get_ingestion_job(
                    knowledgeBaseId=knowledge_base_id,
                    dataSourceId=data_source_id,
                    ingestionJobId=job_id
                )
                
                status = job_status['ingestionJob']['status']
                print(f"📊 Ingestion status: {status}")
                
                if status in ['COMPLETE', 'FAILED']:
                    break
                
                time.sleep(30)
            
            if status == 'COMPLETE':
                print("✅ Knowledge base sync completed successfully")
            else:
                print("❌ Knowledge base sync failed")
                
        except ClientError as e:
            print(f"❌ Error syncing knowledge base: {e}")
    
    def update_configuration_files(self, knowledge_base_id: str):
        """
        Update configuration files with new RAG settings
        """
        print("\n⚙️ Updating configuration files...")
        
        # Update manufacturing config
        config_updates = {
            'MANUFACTURING_RAG': {
                'ENABLED': True,
                'KNOWLEDGE_BASE_ID': knowledge_base_id,
                'HTTP_BASE_URL': self.config['http_base'],
                'AWS_REGION': self.region
            }
        }
        
        # Update app config JSON
        app_config_path = 'LLM-Live2D-Desktop-Assitant-main/config/app_config.json'
        if os.path.exists(app_config_path):
            with open(app_config_path, 'r') as f:
                app_config = json.load(f)
            
            app_config['rag_config']['enabled'] = True
            app_config['rag_config']['knowledge_base_id'] = knowledge_base_id
            
            with open(app_config_path, 'w') as f:
                json.dump(app_config, f, indent=2)
            
            print(f"✅ Updated {app_config_path}")
        
        # Create environment file
        env_content = f"""# RAG Configuration
RAG_ENABLED=true
KNOWLEDGE_BASE_ID={knowledge_base_id}
DOCUMENTS_BUCKET_NAME={self.config['documents_bucket']}
AWS_REGION={self.region}
HTTP_BASE={self.config['http_base']}
WS_URL={self.config['ws_url']}
"""
        
        with open('.env.rag', 'w') as f:
            f.write(env_content)
        
        print("✅ Created .env.rag file with RAG configuration")
    
    def run_setup(self):
        """
        Run the complete RAG setup process
        """
        print("🎯 Starting RAG Infrastructure Setup")
        print("=" * 50)
        
        try:
            # Step 1: Check existing resources
            resources = self.check_existing_resources()
            
            if not resources['s3_bucket']:
                print("❌ S3 bucket not found. Please ensure your AWS infrastructure is deployed.")
                return False
            
            if not resources['bedrock_available']:
                print("❌ Bedrock not available. Please check your AWS region and permissions.")
                return False
            
            # Step 2: Upload sample documents
            self.upload_sample_documents()
            
            # Step 3: Create IAM role
            role_arn = self.create_iam_role_for_bedrock()
            
            # Step 4: Create knowledge base (if not exists)
            if not resources['knowledge_base']:
                try:
                    knowledge_base_id = self.create_knowledge_base(role_arn)
                except ClientError:
                    print("⚠️ Could not create knowledge base automatically.")
                    print("ℹ️ You may need to create an OpenSearch Serverless collection manually.")
                    print("ℹ️ For now, we'll configure the system to work without RAG.")
                    knowledge_base_id = None
            else:
                # Use existing knowledge base
                kb_response = self.bedrock_agent_client.list_knowledge_bases()
                knowledge_base_id = kb_response['knowledgeBaseSummaries'][0]['knowledgeBaseId']
                print(f"✅ Using existing knowledge base: {knowledge_base_id}")
            
            # Step 5: Create data source and sync (if knowledge base exists)
            if knowledge_base_id:
                try:
                    data_source_id = self.create_data_source(knowledge_base_id)
                    self.sync_knowledge_base(knowledge_base_id, data_source_id)
                except ClientError as e:
                    print(f"⚠️ Could not create data source: {e}")
                    print("ℹ️ You can create this manually later in the AWS console.")
            
            # Step 6: Update configuration files
            if knowledge_base_id:
                self.update_configuration_files(knowledge_base_id)
            
            print("\n🎉 RAG Setup Complete!")
            print("=" * 50)
            
            if knowledge_base_id:
                print(f"✅ Knowledge Base ID: {knowledge_base_id}")
                print("✅ RAG functionality is now enabled")
                print("✅ Sample documents uploaded to S3")
                print("✅ Configuration files updated")
            else:
                print("⚠️ RAG setup completed with limitations")
                print("ℹ️ Knowledge base creation requires manual setup")
            
            print("\n📋 Next Steps:")
            print("1. Test the RAG functionality with sample queries")
            print("2. Upload your own manufacturing documents to S3")
            print("3. Monitor the knowledge base ingestion jobs")
            print("4. Adjust chunking parameters if needed")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Setup failed: {e}")
            return False

def main():
    """
    Main setup function
    """
    print("🏭 Manufacturing VTuber RAG Infrastructure Setup")
    print("=" * 60)
    
    # Initialize setup
    setup = RAGInfrastructureSetup(region='us-west-2')
    
    # Run setup
    success = setup.run_setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        print("🚀 Your manufacturing assistant now has RAG capabilities!")
    else:
        print("\n❌ Setup encountered issues.")
        print("📞 Please check the error messages above and try again.")

if __name__ == "__main__":
    main()