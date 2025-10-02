#!/usr/bin/env python3
"""
Test script to verify ASR (Automatic Speech Recognition) initialization fix.
This tests that the Faster-Whisper model can be properly initialized with the configuration.
"""

import sys
import yaml
from loguru import logger

# Configure logger for testing
logger.remove()
logger.add(sys.stdout, level="DEBUG")

def test_asr_initialization():
    """Test ASR initialization with the current configuration."""
    
    print("=" * 60)
    print("ASR INITIALIZATION TEST")
    print("=" * 60)
    
    # Load configuration
    try:
        with open("conf.yaml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load configuration: {e}")
        return False
    
    # Check ASR configuration
    asr_model = config.get("ASR_MODEL")
    print(f"\nASR Model: {asr_model}")
    
    if asr_model != "Faster-Whisper":
        print(f"✗ Expected 'Faster-Whisper' but got '{asr_model}'")
        return False
    
    asr_config = config.get(asr_model, {})
    print(f"ASR Config: {asr_config}")
    
    # Verify required parameters
    model_path = asr_config.get("model_path") or asr_config.get("model_size")
    if not model_path:
        print("✗ No model_path or model_size specified in configuration")
        return False
    
    print(f"✓ Model path/size: {model_path}")
    print(f"✓ Device: {asr_config.get('device', 'auto')}")
    print(f"✓ Compute type: {asr_config.get('compute_type', 'int8')}")
    print(f"✓ Language: {asr_config.get('language', 'auto')}")
    
    # Try to initialize ASR
    print("\n" + "-" * 40)
    print("Attempting to initialize ASR...")
    print("-" * 40)
    
    try:
        from asr.asr_factory import ASRFactory
        
        asr = ASRFactory.get_asr_system(asr_model, **asr_config)
        
        if asr is None:
            print("✗ ASR initialization returned None")
            return False
        
        if not hasattr(asr, 'model'):
            print("✗ ASR object doesn't have 'model' attribute")
            return False
            
        if asr.model is None:
            print("✗ ASR model is None")
            return False
        
        print("✓ ASR initialized successfully!")
        print(f"✓ Model type: {type(asr.model)}")
        print(f"✓ Model path: {asr.MODEL_PATH}")
        
        # Test transcription with dummy audio
        import numpy as np
        print("\n" + "-" * 40)
        print("Testing transcription with silent audio...")
        print("-" * 40)
        
        # Create 1 second of silent audio (16kHz sample rate)
        silent_audio = np.zeros(16000, dtype=np.float32)
        
        try:
            result = asr.transcribe_np(silent_audio)
            print(f"✓ Transcription completed (result: '{result}')")
            print("  (Empty result is expected for silent audio)")
        except Exception as e:
            print(f"✗ Transcription failed: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - ASR IS WORKING!")
        print("=" * 60)
        return True
        
    except ImportError as e:
        print(f"✗ Failed to import ASR modules: {e}")
        print("\nMake sure you have installed the required packages:")
        print("  pip install faster-whisper")
        return False
    except Exception as e:
        print(f"✗ Failed to initialize ASR: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    success = test_asr_initialization()
    
    if success:
        print("\n🎉 ASR fix verified successfully!")
        print("The speech recognition should now work in the VTuber application.")
        print("\nNext steps:")
        print("1. Restart the server (Ctrl+C and run 'python server.py' again)")
        print("2. Test voice input in the application")
        print("3. Check that the WebSocket connection remains stable")
    else:
        print("\n❌ ASR initialization still has issues.")
        print("\nTroubleshooting steps:")
        print("1. Check that 'faster-whisper' is installed: pip install faster-whisper")
        print("2. Verify the model name in conf.yaml (should be 'base', 'small', 'medium', etc.)")
        print("3. Check the terminal output for specific error messages")
        print("4. Try running with VERBOSE: true in conf.yaml for more details")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())