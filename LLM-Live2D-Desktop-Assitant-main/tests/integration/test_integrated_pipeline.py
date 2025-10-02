"""
Integrated Pipeline Test - Tests the actual program implementations
This test uses the same factories and configurations as the main program
"""

import asyncio
import os
import sys
import yaml
import numpy as np
from pathlib import Path
from loguru import logger

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the actual factories used by the program
from tts.tts_factory import TTSFactory
from asr.asr_factory import ASRFactory
from llm.llm_factory import LLMFactory

def load_config():
    """Load the actual configuration file"""
    with open("conf.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

async def test_integrated_tts(config):
    """Test TTS using the actual program's factory and configuration"""
    print("\n=== Testing Integrated TTS (EDGE_TTS) ===")
    
    try:
        # Use the same configuration as the main program
        tts_model = config.get("TTS_MODEL")
        tts_config = config.get(tts_model, {})
        
        print(f"TTS Model: {tts_model}")
        print(f"TTS Config: {tts_config}")
        
        # Create TTS engine using the factory
        tts_engine = TTSFactory.get_tts_engine(tts_model, **tts_config)
        
        # Test synthesis
        test_text = "Hello! This is a test of the integrated TTS system."
        print(f"Synthesizing: {test_text}")
        
        # Call the synthesize method (this is synchronous)
        if hasattr(tts_engine, 'synthesize'):
            result = tts_engine.synthesize(test_text)
            if isinstance(result, tuple):
                filepath, duration = result
                print(f"✅ TTS Success: Generated {filepath} (duration: {duration}s)")
                return True
            else:
                print(f"✅ TTS Success: {result}")
                return True
        else:
            print("❌ TTS engine missing synthesize method")
            return False
            
    except Exception as e:
        print(f"❌ TTS Error: {e}")
        logger.exception("TTS test failed")
        return False

def test_integrated_asr(config):
    """Test ASR using the actual program's factory and configuration"""
    print("\n=== Testing Integrated ASR (Faster-Whisper) ===")
    
    try:
        # Use the same configuration as the main program
        asr_model = config.get("ASR_MODEL")
        asr_config = config.get(asr_model, {})
        
        print(f"ASR Model: {asr_model}")
        print(f"ASR Config: {asr_config}")
        
        # Create ASR engine using the factory
        asr_engine = ASRFactory.get_asr_system(asr_model, **asr_config)
        
        # Test with dummy audio data (simulate 5 seconds of silence)
        sample_rate = 16000
        duration = 5
        dummy_audio = np.zeros(sample_rate * duration, dtype=np.float32)
        
        print(f"Testing with {duration}s of dummy audio data...")
        
        # Call the transcribe method
        if hasattr(asr_engine, 'transcribe'):
            result = asr_engine.transcribe(dummy_audio)
            print(f"✅ ASR Success: Transcription result: {result}")
            return True
        else:
            print("❌ ASR engine missing transcribe method")
            return False
            
    except Exception as e:
        print(f"❌ ASR Error: {e}")
        logger.exception("ASR test failed")
        return False

def test_integrated_llm(config):
    """Test LLM using the actual program's factory and configuration"""
    print("\n=== Testing Integrated LLM (Claude) ===")
    
    try:
        # Use the same configuration as the main program
        llm_provider = config.get("LLM_PROVIDER")
        llm_config = config.get(llm_provider, {})
        
        print(f"LLM Provider: {llm_provider}")
        print(f"LLM Config: {llm_config}")
        
        # Add system prompt and other config
        llm_config.update({
            "SYSTEM_PROMPT": config.get("SYSTEM_PROMPT"),
            "VERBOSE": config.get("VERBOSE", False)
        })
        
        # Create LLM using the factory
        llm_engine = LLMFactory.create_llm(llm_provider, **llm_config)
        
        # Test chat
        test_prompt = "Hello! Please respond with a brief greeting."
        print(f"Sending prompt: {test_prompt}")
        
        if hasattr(llm_engine, 'chat_iter'):
            # Collect response from iterator
            response_parts = []
            for token in llm_engine.chat_iter(test_prompt):
                response_parts.append(token)
                if len(response_parts) > 50:  # Limit for testing
                    break
            
            response = ''.join(response_parts)
            print(f"✅ LLM Success: {response[:100]}...")
            return True
        else:
            print("❌ LLM engine missing chat_iter method")
            return False
            
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        logger.exception("LLM test failed")
        return False

async def test_full_pipeline(config):
    """Test the complete pipeline integration"""
    print("\n=== Testing Full Pipeline Integration ===")
    
    try:
        # Initialize all components
        print("Initializing components...")
        
        # TTS
        tts_model = config.get("TTS_MODEL")
        tts_config = config.get(tts_model, {})
        tts_engine = TTSFactory.get_tts_engine(tts_model, **tts_config)
        
        # ASR
        asr_model = config.get("ASR_MODEL")
        asr_config = config.get(asr_model, {})
        asr_engine = ASRFactory.get_asr_system(asr_model, **asr_config)
        
        # LLM
        llm_provider = config.get("LLM_PROVIDER")
        llm_config = config.get(llm_provider, {})
        llm_config.update({
            "SYSTEM_PROMPT": config.get("SYSTEM_PROMPT"),
            "VERBOSE": config.get("VERBOSE", False)
        })
        llm_engine = LLMFactory.create_llm(llm_provider, **llm_config)
        
        print("✅ All components initialized")
        
        # Simulate pipeline: Text -> LLM -> TTS
        input_text = "What is the weather like today?"
        print(f"Pipeline input: {input_text}")
        
        # Step 1: LLM processing
        print("Step 1: Processing with LLM...")
        response_parts = []
        for token in llm_engine.chat_iter(input_text):
            response_parts.append(token)
            if len(response_parts) > 30:  # Limit for testing
                break
        
        llm_response = ''.join(response_parts)
        print(f"LLM Response: {llm_response[:100]}...")
        
        # Step 2: TTS synthesis
        print("Step 2: Synthesizing response...")
        if hasattr(tts_engine, 'synthesize'):
            tts_result = tts_engine.synthesize(llm_response[:100])  # Limit length
            print(f"✅ Pipeline Success: Generated audio from LLM response")
            return True
        else:
            print("❌ Pipeline failed at TTS step")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline Error: {e}")
        logger.exception("Pipeline test failed")
        return False

async def main():
    """Run all integrated tests"""
    print("🔧 INTEGRATED PIPELINE TESTING")
    print("=" * 50)
    print("Testing actual program implementations...")
    
    # Load configuration
    try:
        config = load_config()
        print(f"✅ Configuration loaded")
        print(f"Voice Input: {config.get('VOICE_INPUT_ON')}")
        print(f"TTS: {config.get('TTS_ON')}")
        print(f"LLM Provider: {config.get('LLM_PROVIDER')}")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return
    
    # Run tests
    results = {}
    
    # Test individual components
    results['tts'] = await test_integrated_tts(config)
    results['asr'] = test_integrated_asr(config)
    results['llm'] = test_integrated_llm(config)
    
    # Test full pipeline
    results['pipeline'] = await test_full_pipeline(config)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 INTEGRATED TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.upper().ljust(15)}: {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integrated tests PASSED!")
        print("The pipeline should work in the actual program.")
    else:
        print("⚠️  Some integrated tests FAILED.")
        print("This explains why the pipeline doesn't work in action.")
        print("Check the error messages above for specific issues.")

if __name__ == "__main__":
    asyncio.run(main())