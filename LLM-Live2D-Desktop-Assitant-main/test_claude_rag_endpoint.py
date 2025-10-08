#!/usr/bin/env python3
"""
Test Claude RAG Endpoint
========================

This script tests the Claude endpoint with RAG enhancement to ensure it's calling
the actual AWS Claude API and including relevant context from S3 documents.
"""

import requests
import json
import time

def test_claude_rag_endpoint():
    """Test the Claude endpoint with RAG enhancement"""
    print("🧪 Testing Claude RAG Endpoint")
    print("=" * 40)
    
    # Server endpoint - try common ports
    possible_ports = [8000, 8001, 8002, 1018, 1019, 1020, 1025]
    base_url = None
    claude_endpoint = None
    
    # Find the running server
    print("🔍 Looking for running server...")
    for port in possible_ports:
        try:
            import requests
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
            "query": "What is error code E001?",
            "description": "Specific error code - should find RAG content",
            "expect_rag": True
        },
        {
            "query": "What is the lockout tagout procedure?",
            "description": "Safety procedure - should find RAG content",
            "expect_rag": True
        },
        {
            "query": "What's the weather like today?",
            "description": "Non-manufacturing query - should NOT find RAG content",
            "expect_rag": False
        }
    ]
    
    print(f"Testing endpoint: {claude_endpoint}")
    print()
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"Test {i}: {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print(f"Expected RAG: {test_case['expect_rag']}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            # Send request to Claude endpoint
            response = requests.post(
                claude_endpoint,
                json={
                    "text": test_case['query'],
                    "max_tokens": 500
                },
                timeout=60  # Increased timeout for AWS API calls
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status: {data.get('status', 'unknown')}")
                print(f"⏱️  Response time: {duration:.2f}s")
                print(f"🔍 RAG Enhanced: {data.get('rag_enhanced', False)}")
                print(f"📚 Context Chunks: {data.get('context_chunks', 0)}")
                print(f"🔢 Tokens Used: {data.get('tokens_used', 0)}")
                
                # Show response preview
                reply = data.get('reply', 'No reply')
                print(f"📝 Reply preview: {reply[:200]}...")
                
                # Check if RAG expectation matches reality
                rag_enhanced = data.get('rag_enhanced', False)
                if test_case['expect_rag'] and rag_enhanced:
                    print("🎉 ✅ RAG enhancement working as expected!")
                elif not test_case['expect_rag'] and not rag_enhanced:
                    print("✅ No RAG enhancement as expected")
                elif test_case['expect_rag'] and not rag_enhanced:
                    print("⚠️  Expected RAG enhancement but didn't get it")
                else:
                    print("⚠️  Got unexpected RAG enhancement")
                
                # Check if we got a real Claude response vs fallback
                if data.get('status') == 'success':
                    print("🤖 Real Claude API response received!")
                elif data.get('status') == 'partial_success':
                    print("⚠️  Fallback response (AWS API issue)")
                    if 'error' in data:
                        print(f"   Error: {data['error']}")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error: Could not connect to server")
            print("Make sure the server is running: python server.py")
            return False
        except requests.exceptions.Timeout:
            print("❌ Timeout Error: Request took too long (>60s)")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    return True

def main():
    """Main test function"""
    print("🚀 Claude RAG Endpoint Test")
    print("=" * 30)
    print()
    
    print("This test will:")
    print("1. Send queries to your Claude endpoint")
    print("2. Check if RAG enhancement is working")
    print("3. Verify AWS Claude API integration")
    print()
    
    success = test_claude_rag_endpoint()
    
    if success:
        print("🎯 Test Summary")
        print("=" * 15)
        print("✅ If you see 'Real Claude API response received!' - AWS integration is working")
        print("✅ If you see 'RAG Enhanced: True' for manufacturing queries - RAG is working")
        print("✅ If you see specific information about error codes or procedures - everything is working!")
        print()
        print("💡 Next Steps:")
        print("1. Try asking Claude about 'error code E001' in your app")
        print("2. Ask about 'lockout tagout procedure'")
        print("3. Check that Claude now has access to your S3 documents")

if __name__ == "__main__":
    main()