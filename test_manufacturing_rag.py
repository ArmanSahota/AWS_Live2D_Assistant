#!/usr/bin/env python3
"""
Test Manufacturing RAG Setup
============================

This script tests the manufacturing RAG functionality to ensure everything is working.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_demo_rag():
    """Test the demo RAG client"""
    print("🔧 Testing Demo Manufacturing RAG...")
    
    try:
        from demo_rag_client import DemoManufacturingRAG
        
        # Create RAG client
        rag_client = DemoManufacturingRAG()
        
        # Test queries
        test_queries = [
            "What is the lockout tagout procedure?",
            "Machine error code E001 troubleshooting",
            "Conveyor belt maintenance schedule",
            "Part number for conveyor belt"
        ]
        
        print("✅ Demo RAG client loaded successfully!")
        print("\n📋 Testing sample queries:")
        
        for query in test_queries:
            print(f"\n❓ Query: {query}")
            print("-" * 50)
            response = rag_client.query(query)
            print(response[:200] + "..." if len(response) > 200 else response)
            
        return True
        
    except Exception as e:
        print(f"❌ Demo RAG test failed: {e}")
        return False

def test_manufacturing_llm():
    """Test the manufacturing LLM integration"""
    print("\n🏭 Testing Manufacturing LLM Integration...")
    
    try:
        # Add the LLM directory to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'LLM-Live2D-Desktop-Assitant-main'))
        
        from llm.manufacturing_rag_llm import LLM as ManufacturingRAGLLM
        
        # Create manufacturing LLM
        manufacturing_llm = ManufacturingRAGLLM(
            verbose=True
        )
        
        print("✅ Manufacturing RAG LLM loaded successfully!")
        
        # Test a simple query
        test_prompt = "What should I do for error code E001?"
        print(f"\n❓ Testing query: {test_prompt}")
        print("-" * 50)
        
        response_parts = []
        for part in manufacturing_llm.chat_iter(test_prompt):
            response_parts.append(part)
            
        response = ''.join(response_parts)
        print(response[:300] + "..." if len(response) > 300 else response)
        
        return True
        
    except Exception as e:
        print(f"❌ Manufacturing LLM test failed: {e}")
        return False

def test_llm_factory():
    """Test the LLM factory integration"""
    print("\n🏗️ Testing LLM Factory Integration...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'LLM-Live2D-Desktop-Assitant-main'))
        
        from llm.llm_factory import LLMFactory
        
        # Test creating manufacturing RAG LLM through factory
        manufacturing_llm = LLMFactory.create_llm(
            "manufacturing_rag",
            SYSTEM_PROMPT="You are a manufacturing assistant.",
            BASE_URL="https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev",
            MODEL="manufacturing-rag-demo",
            VERBOSE=True
        )
        
        print("✅ LLM Factory created Manufacturing RAG LLM successfully!")
        return True
        
    except Exception as e:
        print(f"❌ LLM Factory test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Manufacturing RAG Setup Test")
    print("=" * 50)
    
    # Run tests
    demo_ok = test_demo_rag()
    llm_ok = test_manufacturing_llm()
    factory_ok = test_llm_factory()
    
    print("\n📊 Test Results:")
    print("=" * 50)
    print(f"Demo RAG Client: {'✅ PASS' if demo_ok else '❌ FAIL'}")
    print(f"Manufacturing LLM: {'✅ PASS' if llm_ok else '❌ FAIL'}")
    print(f"LLM Factory: {'✅ PASS' if factory_ok else '❌ FAIL'}")
    
    if all([demo_ok, llm_ok, factory_ok]):
        print("\n🎉 All tests passed! Your Manufacturing RAG setup is ready!")
        print("\nNext steps:")
        print("1. Run: start_manufacturing_rag.bat")
        print("2. Or run: python server.py --config config/manufacturing_rag_config.yaml")
        print("3. Test with manufacturing queries like:")
        print("   - 'What is the lockout tagout procedure?'")
        print("   - 'Machine error code E001 troubleshooting'")
        print("   - 'Conveyor belt maintenance schedule'")
    else:
        print("\n⚠️ Some tests failed. Check the error messages above.")