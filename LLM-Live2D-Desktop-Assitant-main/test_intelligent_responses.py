#!/usr/bin/env python3
"""
Test script to verify intelligent LLM responses
===============================================

This script tests the improved LLM behavior to ensure it provides
contextual, intelligent responses instead of generic information dumps.
"""

import sys
import os

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm.manufacturing_rag_llm import LLM as ManufacturingRAGLLM
from demo_rag_client import DemoManufacturingRAG

def test_manufacturing_rag_responses():
    """Test the Manufacturing RAG LLM with various scenarios"""
    print("🏭 Testing Manufacturing RAG LLM Intelligent Responses")
    print("=" * 60)
    
    # Initialize the Manufacturing RAG LLM
    llm = ManufacturingRAGLLM(verbose=True)
    
    test_cases = [
        {
            "query": "What is error code E999?",
            "expected_behavior": "Should acknowledge unknown error code and provide helpful next steps"
        },
        {
            "query": "How do I fix the quantum flux capacitor?",
            "expected_behavior": "Should acknowledge unknown equipment and suggest consulting manuals"
        },
        {
            "query": "What's the weather like?",
            "expected_behavior": "Should redirect to manufacturing topics politely"
        },
        {
            "query": "Error code E001 troubleshooting",
            "expected_behavior": "Should provide specific E001 information from knowledge base"
        },
        {
            "query": "Tell me about lockout tagout procedure",
            "expected_behavior": "Should provide specific safety procedure information"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}: {test_case['query']}")
        print(f"📋 Expected: {test_case['expected_behavior']}")
        print("-" * 50)
        
        # Get response from LLM
        response_parts = []
        try:
            for chunk in llm.chat_iter(test_case['query']):
                response_parts.append(chunk)
            
            full_response = ''.join(response_parts)
            print(f"🤖 Response:\n{full_response}")
            
            # Basic validation
            if "Based on our manufacturing documentation" in full_response and len(full_response) > 500:
                if any(keyword in test_case['query'].lower() for keyword in ['e999', 'quantum', 'weather']):
                    print("⚠️  WARNING: May be providing too much generic information for unknown query")
                else:
                    print("✅ Good: Providing detailed information for known query")
            elif "don't have" in full_response or "don't know" in full_response:
                print("✅ Good: Acknowledging limitation and providing alternatives")
            elif "manufacturing" in full_response and len(full_response) < 300:
                print("✅ Good: Providing focused, relevant response")
            else:
                print("❓ Response type unclear - manual review needed")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

def test_demo_rag_client():
    """Test the Demo RAG Client directly"""
    print("\n🔧 Testing Demo RAG Client Responses")
    print("=" * 60)
    
    rag_client = DemoManufacturingRAG()
    
    test_queries = [
        "What is error code E999?",  # Unknown error code
        "How to fix the flux capacitor?",  # Unknown equipment
        "Error code E001 troubleshooting",  # Known error code
        "Lockout tagout procedure",  # Known safety procedure
    ]
    
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 30)
        
        response = rag_client.query(query)
        print(f"🤖 Response:\n{response}")
        
        # Check if response is appropriate
        if "I can help you with manufacturing questions" in response:
            if any(unknown in query.lower() for unknown in ['e999', 'flux capacitor']):
                print("⚠️  May need more specific guidance for unknown items")
            else:
                print("✅ Providing general guidance appropriately")
        else:
            print("✅ Providing specific information")

def main():
    """Run all tests"""
    print("🚀 Starting Intelligent Response Tests")
    print("=" * 60)
    
    try:
        # Test Manufacturing RAG LLM
        test_manufacturing_rag_responses()
        
        # Test Demo RAG Client
        test_demo_rag_client()
        
        print("\n✅ All tests completed!")
        print("\n📋 Summary:")
        print("- The LLM should now provide more intelligent, contextual responses")
        print("- Unknown queries should get helpful guidance instead of information dumps")
        print("- Known queries should still get detailed, specific information")
        print("- The system should acknowledge limitations clearly")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()