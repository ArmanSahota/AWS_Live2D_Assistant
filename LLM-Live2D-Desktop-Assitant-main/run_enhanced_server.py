#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick fix script to run the enhanced server with proper configuration
"""

import os
import sys
import yaml
from pathlib import Path

# Fix encoding issues on Windows
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def create_default_config():
    """Create a default configuration if none exists"""
    config = {
        "ASR_MODEL": "Faster-Whisper",
        "AUDIO_INPUT_DEVICE": None,
        "AUDIO_OUTPUT_DEVICE": None,
        "CONTROL_COMPUTER": False,
        "EDGE_TTS": {
            "pitch": "+0Hz",
            "rate": "-10%",
            "voice": "en-US-JennyNeural",
            "volume": "+10%"
        },
        "Faster-Whisper": {
            "compute_type": "int8",
            "device": "cpu",
            "language": "en",
            "model_path": "base",
            "model_size": "base"
        },
        "LIVE2D": True,
        "LIVE2D_Expression_Prompt": "live2d_expression_prompt",
        "LIVE2D_MODEL": "default",
        "LLM_PROVIDER": "claude",
        "MAX_TOKENS": 500,
        "MEMORY": False,
        "MIC_IN_BROWSER": False,
        "OPEN_WEBSITES": False,
        "PERSONA_CHOICE": "service_assistant",
        "RESPONSE_TIMEOUT": 30,
        "SAY_GREETING": False,
        "SEARCH_GOOGLE": False,
        "SERVER_PORT": 8000,
        "SYSTEM_PROMPT": "You are a helpful AI assistant with enhanced RAG capabilities.",
        "TAKE_SCREENSHOT": False,
        "TRANSLATE_AUDIO": False,
        "TTS_MODEL": "EDGE_TTS",
        "TTS_ON": True,
        "VERBOSE": True,
        "VOICE_INPUT_ON": True,
        "WAKE_UP_WORD_ON": False,
        "WEBSOCKET_PORT": 8000,
        "claude": {
            "BASE_URL": "https://xvalzve2ul.execute-api.us-west-2.amazonaws.com/dev",
            "MODEL": "anthropic.claude-3-7-sonnet-20250219-v1:0"
        },
        # Enhanced RAG Configuration
        "RAG_ENABLED": True,
        "RAG_MODE": "hybrid",
        "PREFER_AWS_RAG": True,
        "AWS_KNOWLEDGE_BASE_ID": "",  # Will be set when AWS KB is configured
        "DOCUMENTS_BUCKET_NAME": "",  # Will be set when AWS is configured
        "RAG_MAX_RESULTS": 5,
        "RAG_SCORE_THRESHOLD": 0.5,
        "MANUFACTURING_MODE": True
    }
    return config

def main():
    print("🚀 Enhanced Live2D VTuber Server with AWS Knowledge Base RAG")
    print("=" * 60)
    
    # Check if config file exists
    config_file = Path("conf.yaml")
    if not config_file.exists():
        print(f"⚠️  Configuration file {config_file} not found!")
        print("📝 Creating default configuration...")
        
        config = create_default_config()
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        print(f"✅ Created {config_file} with default settings")
    else:
        print(f"✅ Found configuration file: {config_file}")
    
    # Check for required modules
    missing_modules = []
    
    try:
        from module.live2d_model import Live2dModel
        print("✅ Live2D model module available")
    except ImportError as e:
        missing_modules.append(f"Live2D model: {e}")
    
    try:
        from module.openllm_vtuber_main import OpenLLMVTuberMain
        print("✅ OpenLLM VTuber main module available")
    except ImportError as e:
        missing_modules.append(f"OpenLLM VTuber: {e}")
    
    try:
        from aws_knowledge_base_rag import AWSKnowledgeBaseRAG
        print("✅ AWS Knowledge Base RAG available")
    except ImportError as e:
        print(f"⚠️  AWS Knowledge Base RAG not available: {e}")
        print("   (This is OK - will use local RAG fallback)")
    
    try:
        from simple_s3_rag import SimpleS3RAG
        print("✅ Simple S3 RAG available")
    except ImportError as e:
        print(f"⚠️  Simple S3 RAG not available: {e}")
    
    if missing_modules:
        print("\n❌ Missing required modules:")
        for module in missing_modules:
            print(f"   - {module}")
        print("\nPlease ensure all dependencies are installed.")
        return 1
    
    # Check for Live2D models
    models_dir = Path("static/desktop/models")
    if models_dir.exists():
        models = list(models_dir.iterdir())
        print(f"✅ Found {len(models)} Live2D models: {[m.name for m in models if m.is_dir()]}")
    else:
        print("⚠️  Live2D models directory not found")
    
    print("\n🎯 Starting Enhanced Server...")
    print("Features enabled:")
    print("  - 🤖 AWS Knowledge Base RAG (if configured)")
    print("  - 📚 Local RAG fallback")
    print("  - 🎭 Live2D character animation")
    print("  - 🎤 Voice input/output")
    print("  - 🔗 WebSocket communication")
    print("  - 👁️  Vision analysis with RAG context")
    
    # Import and run the enhanced server
    try:
        from server_enhanced import WebSocketServer, load_config_with_env
        
        # Load configuration
        config = load_config_with_env("conf.yaml")
        
        # Create and run server
        server = WebSocketServer(config, web=False)
        
        print(f"\n🌐 Server will start on http://127.0.0.1:8000")
        print("📡 WebSocket endpoint: ws://127.0.0.1:8000/client-ws")
        print("🏥 Health check: http://127.0.0.1:8000/health")
        print("🧠 RAG health: http://127.0.0.1:8000/rag/health")
        print("\nPress Ctrl+C to stop the server")
        print("=" * 60)
        
        server.run(host="127.0.0.1", port=8000, log_level="info")
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())