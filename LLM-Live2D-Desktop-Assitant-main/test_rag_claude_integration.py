#!/usr/bin/env python3
"""
Test RAG-Enhanced Claude Integration
===================================

This script tests the integration between the Claude client and the S3 RAG system.
"""

import requests
import json
import sys
import os

def test_claude_endpoint_with_rag():
    """Test the Claude endpoint with RAG enhancement"""
    print("🧪 Testing RAG-Enhanced Claude Integration")
    print("=" * 50)
    
    # Find the running server
    possible_ports = [8000, 8001, 8002, 1018, 1019, 1020, 1025]
    base_url = None
    claude_endpoint = None
    
    print("🔍 Looking for running server...")
    for port in possible_ports:
        try:
            test_url = f"http://localhost:{port}/health"
            response = requests.get(test_url, timeout=2)
            if response.status_code == 200:
                base_url = f"http://localhost:{port}"
                claude_endpoint = f"{base_url}/claude"
                print(f"✅ Found server running on port {port}")
                break
        except:
            continue
    
    if not base_url:
        print("❌ No server found running on common ports")
        print("Please start your server first:")
        print("  python server.py")
        print("  or")
        print("  python server.py --port 8000")
        return False
    
    # Test queries that should trigger RAG
    test_queries = [
        {
            "query": "What is the lockout tagout procedure?",
            "description": "Safety procedure query - should find RAG content"
        },
        {
            "query": "What PPE is required for maintenance?",
            "description": "PPE requirements - should find RAG content"
        },
        {
            "query": "How do I troubleshoot error code E001?",
            "description": "Error code query - should find specific RAG content"
        },
        {
            "query": "What's the weather like today?",
            "description": "Non-manufacturing query - should not find RAG content"
        },
        {
            "query": "Tell me about machine maintenance schedules",
            "description": "Maintenance query - should find RAG content"
        }
    ]
    
    print(f"Testing Claude endpoint: {claude_endpoint}")
    print()
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 40)
        
        try:
            # Send request to Claude endpoint
            response = requests.post(
                claude_endpoint,
                json={
                    "text": test_case['query'],
                    "max_tokens": 500
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: {data.get('status', 'unknown')}")
                print(f"📝 Reply: {data.get('reply', 'No reply')[:200]}...")
                print(f"🔍 RAG Enhanced: {data.get('rag_enhanced', False)}")
                print(f"📚 Context Chunks: {data.get('context_chunks', 0)}")
                print(f"🔢 Tokens Used: {data.get('tokens_used', 0)}")
                
                if data.get('rag_enhanced'):
                    print("🎉 RAG enhancement detected!")
                else:
                    print("ℹ️  No RAG enhancement (expected for non-manufacturing queries)")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Could not connect to server")
            print("Make sure the server is running on the expected port")
            return False
        except requests.exceptions.Timeout:
            print("❌ Timeout Error: Request took too long")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    return True

def test_rag_system_directly():
    """Test the RAG system directly"""
    print("🔍 Testing RAG System Directly")
    print("=" * 30)
    
    try:
        from simple_s3_rag import SimpleS3RAG
        
        rag = SimpleS3RAG()
        
        # Test document loading
        print("📥 Loading documents from S3...")
        documents = rag.load_documents_from_s3()
        
        if documents:
            print(f"✅ Loaded {len(documents)} documents")
            for doc_key in list(documents.keys())[:3]:  # Show first 3
                print(f"  - {doc_key}")
        else:
            print("❌ No documents loaded")
            return False
        
        # Test query
        test_query = "What is the lockout tagout procedure?"
        print(f"\n🔍 Testing query: {test_query}")
        
        chunks = rag.retrieve_relevant_chunks(test_query, max_chunks=2)
        
        if chunks:
            print(f"✅ Found {len(chunks)} relevant chunks")
            for i, chunk in enumerate(chunks, 1):
                print(f"  Chunk {i} (score: {chunk.relevance_score:.2f})")
                print(f"  Source: {chunk.source}")
                print(f"  Content: {chunk.content[:100]}...")
                print()
        else:
            print("❌ No relevant chunks found")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure boto3 and other dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_aws_credentials():
    """Check if AWS credentials are configured"""
    print("🔐 Checking AWS Credentials")
    print("=" * 25)
    
    import boto3
    
    try:
        # Try to create an S3 client
        s3_client = boto3.client('s3', region_name='us-west-2')
        
        # Try to list buckets (this will fail if credentials are wrong)
        response = s3_client.list_buckets()
        print("✅ AWS credentials are configured")
        
        # Check if our specific bucket exists
        bucket_name = "live2d-aws-backend-documentsbucket-gvqh2hzqj761"
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Target bucket '{bucket_name}' is accessible")
            return True
        except Exception as e:
            print(f"❌ Target bucket '{bucket_name}' is not accessible: {e}")
            return False
            
    except Exception as e:
        print(f"❌ AWS credentials issue: {e}")
        print("Make sure AWS credentials are configured (AWS CLI, environment variables, or IAM role)")
        return False

def main():
    """Main test function"""
    print("🚀 RAG-Enhanced Claude Integration Test Suite")
    print("=" * 60)
    print()
    
    # Check AWS credentials first
    if not check_aws_credentials():
        print("\n⚠️  AWS credentials not properly configured. RAG functionality may not work.")
        print("Please configure AWS credentials and try again.")
        return
    
    print()
    
    # Test RAG system directly
    if not test_rag_system_directly():
        print("\n❌ RAG system test failed. Skipping Claude integration test.")
        return
    
    print()
    
    # Test Claude endpoint integration
    test_claude_endpoint_with_rag()
    
    print("\n🎯 Test Summary")
    print("=" * 15)
    print("✅ If you see 'RAG Enhanced: True' for manufacturing queries, the integration is working!")
    print("✅ If you see 'RAG Enhanced: False' for non-manufacturing queries, that's expected!")
    print("📚 The system should automatically add relevant context from your S3 documents.")
    print("\n💡 Next Steps:")
    print("1. Start your server: python server.py")
    print("2. Test with your frontend or API calls")
    print("3. Check server logs for RAG activity")

if __name__ == "__main__":
    main()