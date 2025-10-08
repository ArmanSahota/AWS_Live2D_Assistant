#!/usr/bin/env python3
"""
Test Demo RAG Client
====================

Quick test to show the demo RAG functionality without any AWS setup.
Perfect for proof-of-concept demonstrations.
"""

from demo_rag_client import DemoManufacturingRAG

def main():
    print("🏭 Manufacturing VTuber Demo RAG Test")
    print("=" * 60)
    print("This demo shows RAG functionality without complex AWS setup!")
    print()
    
    # Create demo client
    demo_rag = DemoManufacturingRAG()
    
    # Test queries that show different capabilities
    test_scenarios = [
        {
            'title': '🚨 Safety Query',
            'query': 'What is the lockout tagout procedure?',
            'description': 'Shows safety-first responses with clear procedures'
        },
        {
            'title': '🔧 Error Code Troubleshooting', 
            'query': 'Machine error code E001 troubleshooting',
            'description': 'Context-aware troubleshooting with part numbers'
        },
        {
            'title': '🔊 Equipment Issue',
            'query': 'Conveyor belt making unusual noise',
            'description': 'Diagnostic steps for common equipment problems'
        },
        {
            'title': '📋 Maintenance Schedule',
            'query': 'CNC machine maintenance schedule',
            'description': 'Detailed maintenance procedures and schedules'
        },
        {
            'title': '📦 Parts Lookup',
            'query': 'Part number for conveyor belt',
            'description': 'Specific part numbers and specifications'
        },
        {
            'title': '🚨 Emergency Procedure',
            'query': 'Emergency stop procedure',
            'description': 'Critical safety procedures with step-by-step guidance'
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"Test {i}: {scenario['title']}")
        print(f"Query: '{scenario['query']}'")
        print(f"Purpose: {scenario['description']}")
        print("-" * 60)
        
        response = demo_rag.query(scenario['query'])
        print(response)
        print("=" * 60)
        print()
    
    print("🎯 Demo Features Demonstrated:")
    print("✅ Safety-first responses with clear warnings")
    print("✅ Context extraction (machine IDs, error codes)")
    print("✅ Manufacturing-specific knowledge")
    print("✅ Voice-optimized formatting")
    print("✅ Step-by-step procedures")
    print("✅ Part numbers and specifications")
    print("✅ No complex AWS setup required!")
    print()
    
    print("🚀 Integration with Your VTuber:")
    print("This demo RAG can be easily integrated with your existing")
    print("VTuber assistant to provide manufacturing expertise!")
    print()
    
    # Interactive mode
    print("🎮 Try it yourself! Ask manufacturing questions:")
    print("(Type 'quit' to exit)")
    
    while True:
        try:
            question = input("\n❓ Your question: ").strip()
            if question.lower() in ['quit', 'exit', 'q', '']:
                break
            
            response = demo_rag.query(question)
            print(f"\n🤖 Manufacturing Assistant Response:")
            print("-" * 40)
            print(response)
            
        except KeyboardInterrupt:
            break
    
    print("\n👋 Demo complete! Your manufacturing RAG is ready for integration.")

if __name__ == "__main__":
    main()