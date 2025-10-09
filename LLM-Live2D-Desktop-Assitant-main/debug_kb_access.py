#!/usr/bin/env python3
"""
Knowledge Base Access Diagnostic Tool
Systematically tests all potential failure points for KB access
"""

import os
import sys
import time
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def test_environment_variables():
    """Test 1: Environment Variables"""
    print_header("ENVIRONMENT VARIABLES TEST")
    
    # Load .env file if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        with open(env_file, 'r') as f:
            for line_num, line in enumerate(f, 1):
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        if 'AWS' in key:
                            print(f"   {key}: {'SET' if value else 'EMPTY'}")
    else:
        print("❌ .env file not found")
    
    print("\nRuntime Environment Variables:")
    aws_vars = ['AWS_KNOWLEDGE_BASE_ID', 'AWS_REGION', 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_SESSION_TOKEN']
    for var in aws_vars:
        value = os.environ.get(var)
        status = "SET" if value else "NOT SET"
        print(f"   {var}: {status}")
    
    return all(os.environ.get(var) for var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'])

def test_imports():
    """Test 2: Python Imports"""
    print_header("PYTHON IMPORTS TEST")
    
    results = {}
    
    # Test boto3
    try:
        import boto3
        print("✅ boto3 imported successfully")
        print(f"   Version: {boto3.__version__}")
        results['boto3'] = True
    except ImportError as e:
        print(f"❌ boto3 import failed: {e}")
        results['boto3'] = False
    
    # Test vision_rag_pipeline
    try:
        from vision_rag_pipeline import enhance_vision_analysis_with_rag, VisionRAGPipeline
        print("✅ vision_rag_pipeline imported successfully")
        results['vision_rag'] = True
    except ImportError as e:
        print(f"❌ vision_rag_pipeline import failed: {e}")
        results['vision_rag'] = False
    
    # Test server.py imports
    try:
        sys.path.insert(0, '.')
        import server
        print("✅ server.py imported successfully")
        
        # Check flags
        print(f"   RAG_AVAILABLE: {getattr(server, 'RAG_AVAILABLE', 'NOT FOUND')}")
        print(f"   S3_RAG_AVAILABLE: {getattr(server, 'S3_RAG_AVAILABLE', 'NOT FOUND')}")
        print(f"   VISION_RAG_AVAILABLE: {getattr(server, 'VISION_RAG_AVAILABLE', 'NOT FOUND')}")
        results['server'] = True
    except Exception as e:
        print(f"❌ server.py import failed: {e}")
        results['server'] = False
    
    return results

def test_aws_credentials():
    """Test 3: AWS Credentials"""
    print_header("AWS CREDENTIALS TEST")
    
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, PartialCredentialsError
        
        # Test STS (Security Token Service) to validate credentials
        print("Testing AWS credentials with STS...")
        sts_client = boto3.client('sts', region_name='us-west-2')
        
        # Set a timeout to prevent hanging
        import signal
        def timeout_handler(signum, frame):
            raise TimeoutError("AWS credential check timed out")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout
        
        try:
            identity = sts_client.get_caller_identity()
            signal.alarm(0)  # Cancel timeout
            print("✅ AWS credentials are valid")
            print(f"   Account ID: {identity.get('Account', 'Unknown')}")
            print(f"   User ARN: {identity.get('Arn', 'Unknown')}")
            return True
        except TimeoutError:
            print("❌ AWS credential check timed out (likely no credentials)")
            return False
        except (NoCredentialsError, PartialCredentialsError) as e:
            print(f"❌ AWS credentials error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ AWS credentials test failed: {e}")
        return False

def test_knowledge_base_access():
    """Test 4: Knowledge Base Access"""
    print_header("KNOWLEDGE BASE ACCESS TEST")
    
    try:
        import boto3
        
        kb_id = os.environ.get("AWS_KNOWLEDGE_BASE_ID", "HVTKAK0Q86")
        region = os.environ.get("AWS_REGION", "us-west-2")
        
        print(f"Testing Knowledge Base: {kb_id}")
        print(f"Region: {region}")
        
        # Create bedrock-agent-runtime client
        client = boto3.client('bedrock-agent-runtime', region_name=region)
        print("✅ bedrock-agent-runtime client created")
        
        # Test KB access with timeout
        import signal
        def timeout_handler(signum, frame):
            raise TimeoutError("Knowledge Base query timed out")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(15)  # 15 second timeout
        
        try:
            response = client.retrieve(
                knowledgeBaseId=kb_id,
                retrievalQuery={'text': 'manufacturing safety error'},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 2,
                        'overrideSearchType': 'SEMANTIC'
                    }
                }
            )
            signal.alarm(0)  # Cancel timeout
            
            results = response.get('retrievalResults', [])
            print(f"✅ Knowledge Base accessible - retrieved {len(results)} results")
            
            if results:
                print("   Sample result:")
                first_result = results[0]
                content = first_result.get('content', {}).get('text', 'No content')
                print(f"     Content preview: {content[:100]}...")
                print(f"     Score: {first_result.get('score', 'No score')}")
            
            return True
            
        except TimeoutError:
            print("❌ Knowledge Base query timed out")
            return False
            
    except Exception as e:
        print(f"❌ Knowledge Base access failed: {e}")
        return False

def test_server_kb_integration():
    """Test 5: Server KB Integration"""
    print_header("SERVER KB INTEGRATION TEST")
    
    try:
        # Test the load_rag_context_for_vision function
        from server import load_rag_context_for_vision
        print("✅ load_rag_context_for_vision function found")
        
        print("Testing RAG context loading...")
        context = load_rag_context_for_vision("test manufacturing error", "equipment malfunction")
        
        if context:
            print(f"✅ RAG context loaded successfully ({len(context)} characters)")
            print("   Context preview:")
            print(f"     {context[:200]}...")
            return True
        else:
            print("❌ RAG context loading returned empty result")
            return False
            
    except Exception as e:
        print(f"❌ Server KB integration test failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🔍 Knowledge Base Access Diagnostic Tool")
    print("This tool will systematically test all potential failure points")
    
    # Run tests
    results = {}
    
    results['env_vars'] = test_environment_variables()
    results['imports'] = test_imports()
    results['aws_creds'] = test_aws_credentials()
    results['kb_access'] = test_knowledge_base_access()
    results['server_integration'] = test_server_kb_integration()
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    print()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name.replace('_', ' ').title()}: {status}")
    
    print()
    
    # Diagnosis
    if all(results.values()):
        print("🎉 All tests passed! Knowledge Base should be accessible.")
    else:
        print("🔧 Issues found. Most likely causes:")
        
        if not results['aws_creds']:
            print("   1. AWS credentials not configured")
            print("      → Run: aws configure")
            print("      → Or set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        
        if not results['imports']['boto3']:
            print("   2. boto3 not installed")
            print("      → Run: pip install boto3")
        
        if not results['kb_access']:
            print("   3. Knowledge Base access issues")
            print("      → Check AWS permissions for bedrock-agent-runtime")
            print("      → Verify Knowledge Base ID: HVTKAK0Q86")
        
        if not results['imports']['vision_rag']:
            print("   4. vision_rag_pipeline module issues")
            print("      → Check if vision_rag_pipeline.py exists")
    
    print()
    print("📋 Next steps:")
    print("   1. Fix the issues identified above")
    print("   2. Re-run this diagnostic: python debug_kb_access.py")
    print("   3. Start server.py once all tests pass")

if __name__ == "__main__":
    main()