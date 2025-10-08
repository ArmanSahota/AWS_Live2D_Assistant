#!/usr/bin/env python3
"""
Test script to verify RAG integration with vision analysis
"""

import os
import sys
import json
import base64
from pathlib import Path

def test_rag_integration():
    """Test the RAG integration for vision analysis"""
    print("="*60)
    print("RAG VISION INTEGRATION TEST")
    print("="*60)
    
    # Test 1: Check if RAG documents exist
    print("\n1. Checking RAG documents...")
    rag_dir = Path("rag_documents")
    if rag_dir.exists():
        docs = list(rag_dir.glob("*.md"))
        print(f"   ✅ Found {len(docs)} RAG documents:")
        for doc in docs:
            print(f"      - {doc.name}")
    else:
        print("   ❌ RAG documents directory not found")
        return False
    
    # Test 2: Check if local RAG index exists
    print("\n2. Checking local RAG index...")
    index_file = Path("rag_documents_index.json")
    if index_file.exists():
        try:
            with open(index_file, 'r') as f:
                index_data = json.load(f)
            doc_count = len(index_data.get('documents', []))
            print(f"   ✅ Local RAG index found with {doc_count} documents")
        except Exception as e:
            print(f"   ⚠️ RAG index exists but couldn't load: {e}")
    else:
        print("   ⚠️ Local RAG index not found (will be created when needed)")
    
    # Test 3: Check manufacturing mode configuration
    print("\n3. Checking manufacturing mode configuration...")
    config_file = Path("conf.yaml")
    if config_file.exists():
        try:
            import yaml
            # Try different encodings to handle special characters
            config = None
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    with open(config_file, 'r', encoding=encoding) as f:
                        config = yaml.safe_load(f)
                    print(f"   Successfully read config with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if config is None:
                raise Exception("Could not read config file with any encoding")
            
            llm_provider = config.get('LLM_PROVIDER', '')
            persona = config.get('PERSONA_CHOICE', '')
            
            print(f"   LLM Provider: {llm_provider}")
            print(f"   Persona: {persona}")
            
            if 'manufacturing' in llm_provider.lower() or 'manufacturing' in persona.lower():
                print("   ✅ Manufacturing mode is ACTIVE")
                manufacturing_mode = True
            else:
                print("   ⚠️ Manufacturing mode is NOT active")
                manufacturing_mode = False
                
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
            return False
    else:
        print("   ❌ Configuration file not found")
        return False
    
    # Test 4: Test RAG document loading
    print("\n4. Testing RAG document loading...")
    try:
        # Import the server functions
        sys.path.append('.')
        from server import load_local_rag_documents, is_manufacturing_mode
        
        # Test manufacturing mode detection
        is_manufacturing = is_manufacturing_mode(config)
        print(f"   Manufacturing mode detected: {is_manufacturing}")
        
        # Test document loading
        rag_context = load_local_rag_documents()
        if rag_context:
            print(f"   ✅ Successfully loaded {len(rag_context)} characters of RAG context")
            print(f"   Preview: {rag_context[:200]}...")
        else:
            print("   ⚠️ No RAG context loaded")
            
    except Exception as e:
        print(f"   ❌ Error testing RAG functions: {e}")
        return False
    
    # Test 5: Check test images
    print("\n5. Checking test images...")
    test_photos_dir = Path("Test_Photos")
    if test_photos_dir.exists():
        images = list(test_photos_dir.glob("*.jpg")) + list(test_photos_dir.glob("*.png"))
        print(f"   ✅ Found {len(images)} test images:")
        for img in images:
            print(f"      - {img.name}")
    else:
        print("   ⚠️ Test_Photos directory not found")
    
    # Summary
    print("\n" + "="*60)
    print("INTEGRATION TEST SUMMARY")
    print("="*60)
    
    if manufacturing_mode and rag_context:
        print("✅ RAG-Vision integration is READY!")
        print("\nNext steps:")
        print("1. Start the server: python server.py")
        print("2. Open desktop.html in browser")
        print("3. Click '📁 Upload Image' button")
        print("4. Upload your heater error image")
        print("5. Expect enhanced analysis with manufacturing context")
        
        print("\nExpected behavior:")
        print("- Status will show '🏭 [Manufacturing Mode]'")
        print("- Analysis will include error code identification")
        print("- Response will reference safety protocols")
        print("- Troubleshooting steps will be provided")
        
    else:
        print("⚠️ RAG-Vision integration needs setup")
        if not manufacturing_mode:
            print("- Manufacturing mode is not active")
        if not rag_context:
            print("- RAG documents are not loaded")
        print("\nRun 'add_rag_documents.bat' to complete setup")
    
    return True

if __name__ == "__main__":
    test_rag_integration()