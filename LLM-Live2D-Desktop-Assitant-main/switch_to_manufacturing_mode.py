#!/usr/bin/env python3
"""
Switch to Manufacturing RAG Mode
================================

This script switches the VTuber assistant to manufacturing RAG mode by updating the configuration.
"""

import yaml
import os
import shutil
from datetime import datetime

def backup_config():
    """Create a backup of the current configuration"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"conf_backup_{timestamp}.yaml"
    shutil.copy("conf.yaml", backup_path)
    print(f"✅ Configuration backed up to: {backup_path}")
    return backup_path

def switch_to_manufacturing_mode():
    """Switch to manufacturing RAG mode"""
    
    # Read current config
    with open("conf.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("🔧 Switching to Manufacturing RAG Mode...")
    
    # Update LLM provider to manufacturing RAG
    config['LLM_PROVIDER'] = 'manufacturing_rag'
    
    # Add manufacturing RAG configuration
    config['manufacturing_rag'] = {
        'BASE_URL': "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev",
        'MODEL': "manufacturing-rag-demo",
        'VERBOSE': True
    }
    
    # Update persona and system prompt
    config['PERSONA_CHOICE'] = 'manufacturing_assistant'
    config['SYSTEM_PROMPT'] = """You are a specialized manufacturing assistant VTuber with access to technical documentation, 
machine manuals, safety protocols, and troubleshooting guides. Your responses must:

🚨 PRIORITIZE SAFETY: Always highlight safety warnings and precautions first
📋 BE PRECISE: Provide exact part numbers, specifications, and procedures  
📖 CITE SOURCES: Reference specific manuals or documents when available
🗣️ USE CLEAR LANGUAGE: Explain technical terms, avoid unnecessary jargon
📝 PROVIDE STEP-BY-STEP GUIDANCE: Break complex procedures into numbered steps
⚠️ HIGHLIGHT CRITICAL INFORMATION: Emphasize important warnings or specifications
🔍 BE THOROUGH: Include relevant context like part numbers and compatibility

Format responses for voice output - use natural speech patterns and clear transitions."""
    
    # Enable verbose mode for better debugging
    config['VERBOSE'] = True
    
    # Write updated config
    with open("conf.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print("✅ Configuration updated for Manufacturing RAG mode!")
    print("\nManufacturing features enabled:")
    print("  [OK] Manufacturing knowledge base")
    print("  [OK] Safety-first responses")
    print("  [OK] Context-aware troubleshooting")
    print("  [OK] Parts and maintenance information")
    print("  [OK] Voice-optimized responses")
    
    return True

def switch_to_regular_mode():
    """Switch back to regular Claude mode"""
    
    # Read current config
    with open("conf.yaml", 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("🔄 Switching to Regular Claude Mode...")
    
    # Update LLM provider back to claude
    config['LLM_PROVIDER'] = 'claude'
    
    # Add claude configuration
    config['claude'] = {
        'BASE_URL': "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev",
        'MODEL': "anthropic.claude-3-7-sonnet-20250219-v1:0"
    }
    
    # Remove manufacturing RAG config if it exists
    if 'manufacturing_rag' in config:
        del config['manufacturing_rag']
    
    # Update persona and system prompt
    config['PERSONA_CHOICE'] = 'service_assistant'
    config['SYSTEM_PROMPT'] = "You are a helpful AI assistant. Keep responses brief and friendly."
    
    # Write updated config
    with open("conf.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print("✅ Configuration updated for Regular Claude mode!")
    return True

if __name__ == "__main__":
    print("🏭 Manufacturing RAG Mode Switcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("conf.yaml"):
        print("❌ Error: conf.yaml not found!")
        print("Please run this script from the LLM-Live2D-Desktop-Assitant-main directory")
        exit(1)
    
    # Show current mode
    try:
        with open("conf.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        current_provider = config.get('LLM_PROVIDER', 'unknown')
        print(f"Current mode: {current_provider}")
    except:
        print("Could not determine current mode")
    
    print("\nOptions:")
    print("1. Switch to Manufacturing RAG mode")
    print("2. Switch to Regular Claude mode")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        backup_config()
        if switch_to_manufacturing_mode():
            print("\n🎉 Successfully switched to Manufacturing RAG mode!")
            print("\nTo start the server:")
            print("  python server.py --web")
            print("  or run: start_manufacturing_rag.bat")
            
    elif choice == "2":
        backup_config()
        if switch_to_regular_mode():
            print("\n🎉 Successfully switched to Regular Claude mode!")
            print("\nTo start the server:")
            print("  python server.py --web")
            
    elif choice == "3":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice. Please run the script again.")