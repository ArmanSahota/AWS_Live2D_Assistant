#!/usr/bin/env python3
"""
AWS Knowledge Base RAG Deployment Script
Automates the deployment and setup of AWS Knowledge Base for Live2D VTuber Assistant
"""

import os
import sys
import json
import boto3
import time
import argparse
from typing import Dict, Any, Optional
import subprocess
from pathlib import Path

class AWSRAGDeployer:
    """Handles deployment of AWS Knowledge Base RAG infrastructure"""
    
    def __init__(self, region: str = "us-west-2", profile: str = None):
        """
        Initialize the deployer
        
        Args:
            region: AWS region
            profile: AWS profile name (optional)
        """
        self.region = region
        self.profile = profile
        
        # Initialize AWS clients
        session = boto3.Session(profile_name=profile) if profile else boto3.Session()
        self.cloudformation = session.client('cloudformation', region_name=region)
        self.bedrock = session.client('bedrock', region_name=region)
        self.bedrock_agent = session.client('bedrock-agent', region_name=region)
        self.s3 = session.client('s3', region_name=region)
        
        print(f"Initialized AWS clients for region: {region}")
        if profile:
            print(f"Using AWS profile: {profile}")
    
    def deploy_infrastructure(self, stack_name: str = "live2d-aws-backend", env: str = "dev") -> Dict[str, Any]:
        """
        Deploy the enhanced SAM template
        
        Args:
            stack_name: CloudFormation stack name
            env: Environment name
            
        Returns:
            Stack outputs
        """
        print(f"Deploying infrastructure stack: {stack_name}")
        
        # Check if enhanced template exists
        template_path = Path("backend/template-enhanced.yml")
        if not template_path.exists():
            raise FileNotFoundError("Enhanced template not found. Please ensure backend/template-enhanced.yml exists.")
        
        try:
            # Deploy using SAM CLI
            cmd = [
                "sam", "deploy",
                "--template-file", str(template_path),
                "--stack-name", stack_name,
                "--parameter-overrides", f"Env={env}", "EnableRagInfra=true",
                "--capabilities", "CAPABILITY_IAM", "CAPABILITY_NAMED_IAM",
                "--region", self.region
            ]
            
            if self.profile:
                cmd.extend(["--profile", self.profile])
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd="backend")
            
            if result.returncode != 0:
                print(f"SAM deploy failed: {result.stderr}")
                raise RuntimeError(f"SAM deployment failed: {result.stderr}")
            
            print("SAM deployment completed successfully")
            
            # Get stack outputs
            response = self.cloudformation.describe_stacks(StackName=stack_name)
            stack = response['Stacks'][0]
            
            outputs = {}
            for output in stack.get('Outputs', []):
                outputs[output['OutputKey']] = output['OutputValue']
            
            print("Stack outputs:")
            for key, value in outputs.items():
                print(f"  {key}: {value}")
            
            return outputs
            
        except subprocess.CalledProcessError as e:
            print(f"Deployment failed: {e}")
            raise
        except Exception as e:
            print(f"Error during deployment: {e}")
            raise
    
    def create_knowledge_base(
        self,
        name: str,
        opensearch_endpoint: str,
        role_arn: str,
        s3_bucket: str
    ) -> str:
        """
        Create AWS Bedrock Knowledge Base
        
        Args:
            name: Knowledge Base name
            opensearch_endpoint: OpenSearch domain endpoint
            role_arn: IAM role ARN for Bedrock
            s3_bucket: S3 bucket name for documents
            
        Returns:
            Knowledge Base ID
        """
        print(f"Creating Knowledge Base: {name}")
        
        try:
            # Create Knowledge Base
            response = self.bedrock_agent.create_knowledge_base(
                name=name,
                description="Manufacturing documentation knowledge base for Live2D VTuber Assistant",
                roleArn=role_arn,
                knowledgeBaseConfiguration={
                    'type': 'VECTOR',
                    'vectorKnowledgeBaseConfiguration': {
                        'embeddingModelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v1'
                    }
                },
                storageConfiguration={
                    'type': 'OPENSEARCH_SERVERLESS',
                    'opensearchServerlessConfiguration': {
                        'collectionArn': f"arn:aws:aoss:{self.region}:{self._get_account_id()}:collection/{opensearch_endpoint.split('.')[0]}",
                        'vectorIndexName': 'manufacturing-docs-index',
                        'fieldMapping': {
                            'vectorField': 'vector',
                            'textField': 'text',
                            'metadataField': 'metadata'
                        }
                    }
                }
            )
            
            knowledge_base_id = response['knowledgeBase']['knowledgeBaseId']
            print(f"Knowledge Base created with ID: {knowledge_base_id}")
            
            # Create Data Source
            data_source_response = self.bedrock_agent.create_data_source(
                knowledgeBaseId=knowledge_base_id,
                name=f"{name}-s3-source",
                description="S3 data source for manufacturing documents",
                dataSourceConfiguration={
                    'type': 'S3',
                    's3Configuration': {
                        'bucketArn': f"arn:aws:s3:::{s3_bucket}",
                        'inclusionPrefixes': ['manufacturing/']
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
            
            data_source_id = data_source_response['dataSource']['dataSourceId']
            print(f"Data Source created with ID: {data_source_id}")
            
            return knowledge_base_id, data_source_id
            
        except Exception as e:
            print(f"Error creating Knowledge Base: {e}")
            raise
    
    def upload_sample_documents(self, bucket_name: str) -> None:
        """
        Upload sample manufacturing documents to S3
        
        Args:
            bucket_name: S3 bucket name
        """
        print(f"Uploading sample documents to s3://{bucket_name}/manufacturing/")
        
        # Create sample documents
        sample_docs = {
            "manufacturing/heater_error_103_documentation.md": """
# Heater Error 103 - Troubleshooting Guide

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
""",
            "manufacturing/quality_control_procedures.md": """
# Quality Control Procedures

## Daily Inspection Checklist
- [ ] Visual inspection of all products
- [ ] Dimensional measurements
- [ ] Surface finish quality check
- [ ] Packaging integrity verification

## Defect Classification
### Class A Defects (Critical)
- Safety-related issues
- Functional failures
- Dimensional out-of-spec

### Class B Defects (Major)
- Cosmetic issues affecting customer perception
- Minor functional issues

### Class C Defects (Minor)
- Cosmetic issues not affecting function
- Documentation errors

## Corrective Actions
1. Immediate containment
2. Root cause analysis
3. Corrective action implementation
4. Verification of effectiveness
""",
            "manufacturing/equipment_maintenance_schedule.md": """
# Equipment Maintenance Schedule

## Daily Maintenance
- Lubrication of moving parts
- Visual inspection for wear
- Cleaning of work surfaces
- Safety system checks

## Weekly Maintenance
- Calibration verification
- Filter replacements
- Belt tension checks
- Electrical connection inspection

## Monthly Maintenance
- Complete system calibration
- Wear part replacement
- Preventive part replacement
- Documentation update

## Emergency Procedures
### Equipment Failure
1. Immediate shutdown
2. Safety assessment
3. Isolation of affected area
4. Notification of maintenance team

### Safety Incidents
1. Ensure personnel safety
2. Emergency stop activation
3. Incident documentation
4. Investigation initiation
"""
        }
        
        try:
            for key, content in sample_docs.items():
                self.s3.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=content.encode('utf-8'),
                    ContentType='text/markdown'
                )
                print(f"  Uploaded: {key}")
            
            print(f"Successfully uploaded {len(sample_docs)} sample documents")
            
        except Exception as e:
            print(f"Error uploading documents: {e}")
            raise
    
    def start_ingestion_job(self, knowledge_base_id: str, data_source_id: str) -> str:
        """
        Start ingestion job to process documents
        
        Args:
            knowledge_base_id: Knowledge Base ID
            data_source_id: Data Source ID
            
        Returns:
            Ingestion Job ID
        """
        print("Starting document ingestion job...")
        
        try:
            response = self.bedrock_agent.start_ingestion_job(
                knowledgeBaseId=knowledge_base_id,
                dataSourceId=data_source_id,
                description="Initial ingestion of manufacturing documents"
            )
            
            job_id = response['ingestionJob']['ingestionJobId']
            print(f"Ingestion job started with ID: {job_id}")
            
            # Wait for job completion
            print("Waiting for ingestion to complete...")
            while True:
                job_response = self.bedrock_agent.get_ingestion_job(
                    knowledgeBaseId=knowledge_base_id,
                    dataSourceId=data_source_id,
                    ingestionJobId=job_id
                )
                
                status = job_response['ingestionJob']['status']
                print(f"  Status: {status}")
                
                if status in ['COMPLETE', 'FAILED']:
                    break
                
                time.sleep(30)
            
            if status == 'COMPLETE':
                print("✅ Document ingestion completed successfully")
            else:
                print("❌ Document ingestion failed")
                raise RuntimeError("Ingestion job failed")
            
            return job_id
            
        except Exception as e:
            print(f"Error starting ingestion job: {e}")
            raise
    
    def update_lambda_environment(self, stack_name: str, knowledge_base_id: str, data_source_id: str) -> None:
        """
        Update Lambda function environment variables with Knowledge Base ID
        
        Args:
            stack_name: CloudFormation stack name
            knowledge_base_id: Knowledge Base ID
            data_source_id: Data Source ID
        """
        print("Updating Lambda function environment variables...")
        
        try:
            # Get Lambda function names from stack
            response = self.cloudformation.describe_stack_resources(StackName=stack_name)
            
            lambda_functions = []
            for resource in response['StackResources']:
                if resource['ResourceType'] == 'AWS::Lambda::Function':
                    lambda_functions.append(resource['PhysicalResourceId'])
            
            # Update each Lambda function
            lambda_client = boto3.client('lambda', region_name=self.region)
            
            for function_name in lambda_functions:
                try:
                    # Get current environment
                    response = lambda_client.get_function_configuration(FunctionName=function_name)
                    current_env = response.get('Environment', {}).get('Variables', {})
                    
                    # Update with Knowledge Base ID
                    current_env['KNOWLEDGE_BASE_ID'] = knowledge_base_id
                    current_env['DATA_SOURCE_ID'] = data_source_id
                    
                    # Update function
                    lambda_client.update_function_configuration(
                        FunctionName=function_name,
                        Environment={'Variables': current_env}
                    )
                    
                    print(f"  Updated: {function_name}")
                    
                except Exception as e:
                    print(f"  Warning: Could not update {function_name}: {e}")
            
            print("Lambda environment variables updated")
            
        except Exception as e:
            print(f"Error updating Lambda environment: {e}")
            raise
    
    def test_knowledge_base(self, knowledge_base_id: str) -> None:
        """
        Test the Knowledge Base with sample queries
        
        Args:
            knowledge_base_id: Knowledge Base ID
        """
        print("Testing Knowledge Base with sample queries...")
        
        test_queries = [
            "What should I do for heater error 103?",
            "What are the safety procedures for equipment maintenance?",
            "How do I classify defects in quality control?"
        ]
        
        try:
            bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=self.region)
            
            for query in test_queries:
                print(f"\nQuery: {query}")
                
                response = bedrock_agent_runtime.retrieve(
                    knowledgeBaseId=knowledge_base_id,
                    retrievalQuery={'text': query},
                    retrievalConfiguration={
                        'vectorSearchConfiguration': {
                            'numberOfResults': 3,
                            'overrideSearchType': 'HYBRID'
                        }
                    }
                )
                
                results = response.get('retrievalResults', [])
                print(f"Found {len(results)} relevant documents:")
                
                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    content = result['content']['text'][:200]
                    source = result['metadata'].get('source', 'Unknown')
                    
                    print(f"  {i}. Score: {score:.3f} | Source: {source}")
                    print(f"     Content: {content}...")
            
            print("\n✅ Knowledge Base testing completed successfully")
            
        except Exception as e:
            print(f"Error testing Knowledge Base: {e}")
            raise
    
    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        sts = boto3.client('sts')
        return sts.get_caller_identity()['Account']
    
    def generate_env_file(self, knowledge_base_id: str, bucket_name: str, stack_outputs: Dict[str, Any]) -> None:
        """
        Generate .env file with AWS configuration
        
        Args:
            knowledge_base_id: Knowledge Base ID
            bucket_name: S3 bucket name
            stack_outputs: CloudFormation stack outputs
        """
        print("Generating .env file...")
        
        env_content = f"""# AWS Knowledge Base RAG Configuration
# Generated by deploy_aws_rag.py

# AWS Configuration
AWS_REGION={self.region}
AWS_KNOWLEDGE_BASE_ID={knowledge_base_id}
DOCUMENTS_BUCKET_NAME={bucket_name}

# RAG Configuration
RAG_ENABLED=true
RAG_MODE=hybrid
PREFER_AWS_RAG=true

# API Endpoints
HTTP_API_BASE={stack_outputs.get('HttpBase', '')}
WEBSOCKET_URL={stack_outputs.get('WSUrl', '')}

# Enhanced RAG Settings
RAG_MAX_RESULTS=5
RAG_SCORE_THRESHOLD=0.5
RAG_SEARCH_TYPE=HYBRID

# Safety Features
SAFETY_KEYWORDS_ENABLED=true
MANUFACTURING_MODE=true
"""
        
        env_file_path = Path(".env.aws-rag")
        with open(env_file_path, 'w') as f:
            f.write(env_content)
        
        print(f"Environment file created: {env_file_path}")
        print("To use this configuration, run: cp .env.aws-rag .env")


def main():
    parser = argparse.ArgumentParser(description="Deploy AWS Knowledge Base RAG for Live2D VTuber Assistant")
    parser.add_argument("--region", default="us-west-2", help="AWS region")
    parser.add_argument("--profile", help="AWS profile name")
    parser.add_argument("--stack-name", default="live2d-aws-backend", help="CloudFormation stack name")
    parser.add_argument("--env", default="dev", help="Environment name")
    parser.add_argument("--kb-name", default="live2d-manufacturing-kb", help="Knowledge Base name")
    parser.add_argument("--skip-deploy", action="store_true", help="Skip infrastructure deployment")
    parser.add_argument("--skip-kb", action="store_true", help="Skip Knowledge Base creation")
    parser.add_argument("--skip-docs", action="store_true", help="Skip document upload")
    parser.add_argument("--skip-test", action="store_true", help="Skip testing")
    
    args = parser.parse_args()
    
    try:
        deployer = AWSRAGDeployer(region=args.region, profile=args.profile)
        
        # Step 1: Deploy infrastructure
        if not args.skip_deploy:
            print("=" * 60)
            print("STEP 1: Deploying Infrastructure")
            print("=" * 60)
            stack_outputs = deployer.deploy_infrastructure(args.stack_name, args.env)
        else:
            print("Skipping infrastructure deployment")
            # Get existing stack outputs
            response = deployer.cloudformation.describe_stacks(StackName=args.stack_name)
            stack = response['Stacks'][0]
            stack_outputs = {}
            for output in stack.get('Outputs', []):
                stack_outputs[output['OutputKey']] = output['OutputValue']
        
        bucket_name = stack_outputs.get('DocumentsBucketName')
        opensearch_endpoint = stack_outputs.get('OpenSearchDomainEndpoint')
        role_arn = stack_outputs.get('BedrockKBRoleArn')
        
        if not all([bucket_name, opensearch_endpoint, role_arn]):
            print("Error: Missing required stack outputs. Ensure RAG infrastructure is enabled.")
            sys.exit(1)
        
        # Step 2: Create Knowledge Base
        knowledge_base_id = None
        data_source_id = None
        
        if not args.skip_kb:
            print("\n" + "=" * 60)
            print("STEP 2: Creating Knowledge Base")
            print("=" * 60)
            knowledge_base_id, data_source_id = deployer.create_knowledge_base(
                args.kb_name, opensearch_endpoint, role_arn, bucket_name
            )
        else:
            print("Skipping Knowledge Base creation")
            # You would need to provide existing IDs here
        
        # Step 3: Upload documents
        if not args.skip_docs and bucket_name:
            print("\n" + "=" * 60)
            print("STEP 3: Uploading Sample Documents")
            print("=" * 60)
            deployer.upload_sample_documents(bucket_name)
        else:
            print("Skipping document upload")
        
        # Step 4: Start ingestion
        if knowledge_base_id and data_source_id and not args.skip_docs:
            print("\n" + "=" * 60)
            print("STEP 4: Starting Document Ingestion")
            print("=" * 60)
            deployer.start_ingestion_job(knowledge_base_id, data_source_id)
        
        # Step 5: Update Lambda environment
        if knowledge_base_id and data_source_id:
            print("\n" + "=" * 60)
            print("STEP 5: Updating Lambda Environment")
            print("=" * 60)
            deployer.update_lambda_environment(args.stack_name, knowledge_base_id, data_source_id)
        
        # Step 6: Test Knowledge Base
        if knowledge_base_id and not args.skip_test:
            print("\n" + "=" * 60)
            print("STEP 6: Testing Knowledge Base")
            print("=" * 60)
            deployer.test_knowledge_base(knowledge_base_id)
        
        # Step 7: Generate environment file
        if knowledge_base_id and bucket_name:
            print("\n" + "=" * 60)
            print("STEP 7: Generating Configuration")
            print("=" * 60)
            deployer.generate_env_file(knowledge_base_id, bucket_name, stack_outputs)
        
        print("\n" + "=" * 60)
        print("DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print(f"Knowledge Base ID: {knowledge_base_id}")
        print(f"S3 Bucket: {bucket_name}")
        print(f"HTTP API: {stack_outputs.get('HttpBase', 'N/A')}")
        print(f"WebSocket URL: {stack_outputs.get('WSUrl', 'N/A')}")
        print("\nNext steps:")
        print("1. Copy .env.aws-rag to .env")
        print("2. Run the enhanced server: python server_enhanced.py")
        print("3. Test RAG functionality with manufacturing queries")
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()