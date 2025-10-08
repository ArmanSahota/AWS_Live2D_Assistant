#!/usr/bin/env python3
"""
Test script to verify the more flexible LLM responses
====================================================

This tests that the system now properly handles:
1. Manufacturing errors like E001 (from your image)
2. General questions with helpful responses
3. Technical questions even if not strictly manufacturing
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.manufacturing_rag_llm import LLM as ManufacturingRAGLLM
from demo_rag_client import DemoManufacturingRAG

def test_error_code_recognition():
    """Test that E001 spindle overload error is properly recognized"""
    print("🔧 Testing Error Code Recognition")
    print("=" * 50)
    
    llm = ManufacturingRAGLLM(verbose=True)
    
    test_cases = [
        "I have a spindle overload error code E001",
        "What is error code E001?",
        "Spindle overload E001 troubleshooting",
        "My machine shows E001 error",
        "How to fix spindle overload?"
    ]
    
    for query in test_cases:
        print(f"\n❓ Query: {query}")
        print("-" * 30)
        
        # Check if it's recognized as manufacturing
        is_manufacturing = llm._is_manufacturing_query(query)
        print(f"🏭 Recognized as manufacturing: {is_manufacturing}")
        
        if is_manufacturing:
            print("✅ Good: Should provide E001 troubleshooting information")
        else:
            print("❌ Problem: Should recognize this as manufacturing query")

def test_general_helpfulness():
    """Test that the system is more helpful with general questions"""
    print("\n💬 Testing General Helpfulness")
    print("=" * 50)
    
    llm = ManufacturingRAGLLM(verbose=False)
    
    test_cases = [
        {
            "query": "Hello, how are you?",
            "expected": "Should respond warmly and offer help"
        },
        {
            "query": "I have a technical problem",
            "expected": "Should try to help with technical issues"
        },
        {
            "query": "What can you help me with?",
            "expected": "Should list capabilities helpfully"
        },
        {
            "query": "My computer is broken",
            "expected": "Should try to help even if not manufacturing"
        }
    ]
    
    for test_case in test_cases:
        query = test_case["query"]
        expected = test_case["expected"]
        
        print(f"\n❓ Query: {query}")
        print(f"📋 Expected: {expected}")
        print("-" * 30)
        
        # Get the response
        response_parts = []
        try:
            for chunk in llm.chat_iter(query):
                response_parts.append(chunk)
            
            full_response = ''.join(response_parts)
            print(f"🤖 Response: {full_response[:200]}...")
            
            # Check if response is helpful
            if "I'm specialized in manufacturing" in full_response and "can't help" in full_response:
                print("⚠️  May still be too restrictive")
            elif len(full_response) > 50 and ("help" in full_response.lower() or "assist" in full_response.lower()):
                print("✅ Good: Providing helpful response")
            else:
                print("❓ Response needs review")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_rag_client_directly():
    """Test the RAG client directly for E001"""
    print("\n🔍 Testing RAG Client for E001")
    print("=" * 50)
    
    rag_client = DemoManufacturingRAG()
    
    test_queries = [
        "Error code E001",
        "Spindle overload E001",
        "What is E001 error?",
        "E001 troubleshooting"
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 30)
        
        response = rag_client.query(query)
        
        if "E001" in response and "Spindle Overload" in response:
            print("✅ Good: Found specific E001 information")
        elif "I don't have specific information" in response:
            print("❌ Problem: Should find E001 in knowledge base")
        else:
            print("❓ Response needs review")
        
        print(f"Response preview: {response[:150]}...")

def main():
    """Run all tests"""
    print("🚀 Testing Flexible Response System")
    print("=" * 60)
    
    try:
        # Test error code recognition
        test_error_code_recognition()
        
        # Test general helpfulness
        test_general_helpfulness()
        
        # Test RAG client directly
        test_rag_client_directly()
        
        print("\n✅ All tests completed!")
        print("\n📋 Summary:")
        print("- The system should now recognize E001 spindle overload errors")
        print("- General questions should get more helpful responses")
        print("- Technical questions should be handled even if not strictly manufacturing")
        print("- The assistant should be friendly first, manufacturing-focused second")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()