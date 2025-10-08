#!/usr/bin/env python3
"""
RAG Integration Test Script
===========================

This script tests the RAG integration with your AWS infrastructure.
It verifies that the manufacturing assistant can retrieve and use
documents from your S3 bucket through Bedrock Knowledge Base.

Usage:
    python test_rag_integration.py

Requirements:
    - AWS credentials configured
    - boto3 library installed
    - RAG infrastructure set up
"""

import asyncio
import json
import sys
import os
from typing import Dict, List
import boto3
from botocore.exceptions import ClientError

# Add the current directory to Python path to import our modules
sys.path.append('.')

try:
    from manufacturing_rag_implementation import (
        ManufacturingRAGClient,
        ManufacturingContext,
        ManufacturingAssistantIntegration
    )
except ImportError as e:
    print(f"❌ Error importing RAG modules: {e}")
    print("ℹ️ Make sure manufacturing_rag_implementation.py is in the current directory")
    sys.exit(1)

class RAGIntegrationTester:
    """
    Tests RAG integration with AWS infrastructure
    """
    
    def __init__(self):
        self.config = {
            'HTTP_BASE_URL': 'https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev',
            'WS_URL': 'wss://sz0alheq5d.execute-api.us-west-2.amazonaws.com/dev',
            'DOCUMENTS_BUCKET_NAME': 'live2d-aws-backend-documentsbucket-gvqh2hzqj761',
            'AWS_REGION': 'us-west-2',
            'KNOWLEDGE_BASE_ID': None,  # Will be detected or set manually
            'VERBOSE': True
        }
        
        # Initialize AWS clients
        self.s3_client = boto3.client('s3', region_name=self.config['AWS_REGION'])
        self.bedrock_agent_client = boto3.client('bedrock-agent', region_name=self.config['AWS_REGION'])
        
        print("🧪 RAG Integration Tester Initialized")
        print(f"📍 Region: {self.config['AWS_REGION']}")
        print(f"🪣 Bucket: {self.config['DOCUMENTS_BUCKET_NAME']}")
        print(f"🌐 HTTP Base: {self.config['HTTP_BASE_URL']}")
    
    def test_aws_connectivity(self) -> bool:
        """
        Test basic AWS connectivity
        """
        print("\n🔗 Testing AWS Connectivity...")
        
        try:
            # Test S3 access
            response = self.s3_client.head_bucket(Bucket=self.config['DOCUMENTS_BUCKET_NAME'])
            print("✅ S3 bucket accessible")
            
            # List some objects in the bucket
            objects = self.s3_client.list_objects_v2(
                Bucket=self.config['DOCUMENTS_BUCKET_NAME'],
                MaxKeys=5
            )
            
            if 'Contents' in objects:
                print(f"✅ Found {len(objects['Contents'])} objects in bucket")
                for obj in objects['Contents'][:3]:
                    print(f"   📄 {obj['Key']}")
            else:
                print("ℹ️ No objects found in bucket")
            
            return True
            
        except ClientError as e:
            print(f"❌ AWS connectivity test failed: {e}")
            return False
    
    def detect_knowledge_base(self) -> str:
        """
        Detect existing knowledge base or return None
        """
        print("\n🔍 Detecting Knowledge Base...")
        
        try:
            response = self.bedrock_agent_client.list_knowledge_bases()
            
            if response.get('knowledgeBaseSummaries'):
                kb = response['knowledgeBaseSummaries'][0]
                kb_id = kb['knowledgeBaseId']
                kb_name = kb['name']
                print(f"✅ Found Knowledge Base: {kb_name} ({kb_id})")
                return kb_id
            else:
                print("ℹ️ No Knowledge Base found")
                return None
                
        except ClientError as e:
            print(f"⚠️ Could not check Knowledge Bases: {e}")
            return None
    
    def test_rag_client_creation(self) -> ManufacturingRAGClient:
        """
        Test creating the RAG client
        """
        print("\n🏭 Testing RAG Client Creation...")
        
        try:
            # Detect knowledge base
            kb_id = self.detect_knowledge_base()
            self.config['KNOWLEDGE_BASE_ID'] = kb_id
            
            # Create RAG client
            rag_client = ManufacturingAssistantIntegration.create_manufacturing_client(
                self.config
            )
            
            print("✅ RAG Client created successfully")
            return rag_client
            
        except Exception as e:
            print(f"❌ RAG Client creation failed: {e}")
            return None
    
    def test_context_extraction(self) -> List[ManufacturingContext]:
        """
        Test manufacturing context extraction from voice input
        """
        print("\n🎤 Testing Context Extraction...")
        
        test_inputs = [
            "Machine PL1-CNC-001 is showing error code E456",
            "I need help with safety protocols in the welding area",
            "What's the maintenance schedule for conveyor belt CV-BELT-001?",
            "Emergency stop procedure for production line 2"
        ]
        
        contexts = []
        
        for input_text in test_inputs:
            try:
                context = ManufacturingAssistantIntegration.extract_manufacturing_context_from_voice(
                    input_text
                )
                contexts.append(context)
                
                print(f"✅ Input: '{input_text[:50]}...'")
                print(f"   📋 Machine ID: {context.machine_id}")
                print(f"   🚨 Error Code: {context.error_code}")
                print(f"   🏢 Department: {context.department}")
                
            except Exception as e:
                print(f"❌ Context extraction failed for '{input_text}': {e}")
        
        return contexts
    
    async def test_rag_queries(self, rag_client: ManufacturingRAGClient) -> bool:
        """
        Test RAG queries with different scenarios
        """
        print("\n💬 Testing RAG Queries...")
        
        if not rag_client:
            print("❌ No RAG client available for testing")
            return False
        
        test_queries = [
            {
                'query': 'What is the lockout tagout procedure?',
                'context': ManufacturingContext(department='safety', safety_level='critical'),
                'expected_keywords': ['lockout', 'tagout', 'energy', 'isolation']
            },
            {
                'query': 'Machine error code E001 troubleshooting',
                'context': ManufacturingContext(machine_id='CNC-001', error_code='E001'),
                'expected_keywords': ['spindle', 'overload', 'cutting', 'tools']
            },
            {
                'query': 'Conveyor belt part number',
                'context': ManufacturingContext(department='maintenance'),
                'expected_keywords': ['CV-BELT-001', 'conveyor', 'belt']
            }
        ]
        
        success_count = 0
        
        for i, test in enumerate(test_queries, 1):
            print(f"\n🔍 Test Query {i}: {test['query']}")
            
            try:
                # Test the RAG query
                response_parts = []
                async for part in rag_client.chat_iter_with_rag(
                    test['query'], 
                    context=test['context']
                ):
                    response_parts.append(part)
                
                response = ''.join(response_parts)
                
                if response and len(response) > 50:
                    print(f"✅ Got response ({len(response)} chars)")
                    
                    # Check for expected keywords
                    found_keywords = []
                    for keyword in test['expected_keywords']:
                        if keyword.lower() in response.lower():
                            found_keywords.append(keyword)
                    
                    if found_keywords:
                        print(f"✅ Found expected keywords: {found_keywords}")
                        success_count += 1
                    else:
                        print(f"⚠️ Expected keywords not found: {test['expected_keywords']}")
                    
                    # Show first 200 chars of response
                    print(f"📝 Response preview: {response[:200]}...")
                    
                else:
                    print(f"❌ Empty or short response: {response}")
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        success_rate = success_count / len(test_queries)
        print(f"\n📊 Query Success Rate: {success_count}/{len(test_queries)} ({success_rate:.1%})")
        
        return success_rate > 0.5
    
    def test_http_endpoint(self) -> bool:
        """
        Test the HTTP endpoint directly
        """
        print("\n🌐 Testing HTTP Endpoint...")
        
        try:
            import requests
            
            # Test basic connectivity
            response = requests.get(
                f"{self.config['HTTP_BASE_URL']}/health",
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ HTTP endpoint is accessible")
                return True
            else:
                print(f"⚠️ HTTP endpoint returned status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ HTTP endpoint test failed: {e}")
            return False
        except ImportError:
            print("⚠️ requests library not available, skipping HTTP test")
            return True
    
    def generate_test_report(self, results: Dict[str, bool]) -> str:
        """
        Generate a comprehensive test report
        """
        report = "\n" + "="*60 + "\n"
        report += "🧪 RAG INTEGRATION TEST REPORT\n"
        report += "="*60 + "\n"
        
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        report += f"📊 Overall Results: {passed_tests}/{total_tests} tests passed\n"
        report += f"✅ Success Rate: {passed_tests/total_tests:.1%}\n\n"
        
        report += "📋 Test Details:\n"
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            report += f"   {status} {test_name}\n"
        
        report += "\n🔧 Recommendations:\n"
        
        if not results.get('aws_connectivity', False):
            report += "   • Check AWS credentials and permissions\n"
            report += "   • Verify S3 bucket exists and is accessible\n"
        
        if not results.get('knowledge_base_detection', False):
            report += "   • Run setup_rag_infrastructure.py to create Knowledge Base\n"
            report += "   • Manually create Knowledge Base in AWS Console\n"
        
        if not results.get('rag_queries', False):
            report += "   • Upload sample documents to S3\n"
            report += "   • Check Knowledge Base ingestion status\n"
            report += "   • Verify document chunking and indexing\n"
        
        if not results.get('http_endpoint', False):
            report += "   • Check API Gateway deployment\n"
            report += "   • Verify Lambda function is running\n"
        
        report += "\n📞 Support:\n"
        report += "   • Check AWS CloudWatch logs for detailed errors\n"
        report += "   • Review IAM permissions for Bedrock and S3\n"
        report += "   • Ensure all required AWS services are enabled\n"
        
        report += "\n" + "="*60
        
        return report
    
    async def run_all_tests(self) -> bool:
        """
        Run all RAG integration tests
        """
        print("🚀 Starting RAG Integration Tests")
        print("="*50)
        
        results = {}
        
        # Test 1: AWS Connectivity
        results['aws_connectivity'] = self.test_aws_connectivity()
        
        # Test 2: Knowledge Base Detection
        kb_id = self.detect_knowledge_base()
        results['knowledge_base_detection'] = kb_id is not None
        
        # Test 3: RAG Client Creation
        rag_client = self.test_rag_client_creation()
        results['rag_client_creation'] = rag_client is not None
        
        # Test 4: Context Extraction
        contexts = self.test_context_extraction()
        results['context_extraction'] = len(contexts) > 0
        
        # Test 5: RAG Queries (only if client exists)
        if rag_client:
            results['rag_queries'] = await self.test_rag_queries(rag_client)
        else:
            results['rag_queries'] = False
        
        # Test 6: HTTP Endpoint
        results['http_endpoint'] = self.test_http_endpoint()
        
        # Generate and display report
        report = self.generate_test_report(results)
        print(report)
        
        # Overall success
        overall_success = sum(results.values()) >= len(results) * 0.7
        
        if overall_success:
            print("\n🎉 RAG Integration Tests: OVERALL SUCCESS")
            print("✅ Your RAG system is ready for use!")
        else:
            print("\n⚠️ RAG Integration Tests: NEEDS ATTENTION")
            print("🔧 Please address the failed tests above")
        
        return overall_success

async def main():
    """
    Main test function
    """
    print("🏭 Manufacturing VTuber RAG Integration Tests")
    print("=" * 60)
    
    # Create tester
    tester = RAGIntegrationTester()
    
    # Run all tests
    success = await tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())