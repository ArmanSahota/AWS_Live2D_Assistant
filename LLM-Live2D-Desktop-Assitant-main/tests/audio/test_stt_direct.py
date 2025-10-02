#!/usr/bin/env python3
"""Direct test of speech recognition components"""

import sys
import os
import numpy as np
import sounddevice as sd
import time
from loguru import logger

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_microphone():
    """Test if microphone is working"""
    print("Testing microphone...")
    try:
        # List audio devices
        devices = sd.query_devices()
        print("\nAvailable audio devices:")
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  {i}: {device['name']} (inputs: {device['max_input_channels']})")
        
        # Record 3 seconds of audio
        print("\n🎤 Recording 3 seconds of audio... Speak now!")
        duration = 3  # seconds
        fs = 16000  # Sample rate
        
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
        sd.wait()  # Wait until recording is finished
        
        print(f"✅ Recorded {len(recording)} samples")
        print(f"   Audio range: {np.min(recording):.4f} to {np.max(recording):.4f}")
        
        # Check if audio has content
        if np.max(np.abs(recording)) < 0.001:
            print("⚠️  Warning: Audio appears to be silent!")
            return None
        
        return recording
        
    except Exception as e:
        print(f"❌ Microphone test failed: {e}")
        return None

def test_whisper():
    """Test Whisper ASR"""
    print("\n" + "="*50)
    print("Testing Whisper ASR...")
    
    try:
        from asr.faster_whisper_asr import FasterWhisperASR
        
        # Initialize ASR with simple config
        config = {
            "model_size": "base",
            "device": "cpu",
            "compute_type": "int8",
            "language": "en"
        }
        
        print(f"Initializing Faster Whisper with config: {config}")
        asr = FasterWhisperASR(config)
        print("✅ ASR initialized successfully")
        
        # Record audio
        audio = test_microphone()
        if audio is None:
            print("❌ No audio to transcribe")
            return
        
        # Transcribe
        print("\n🔄 Transcribing audio...")
        start_time = time.time()
        
        # Convert to the format expected by Whisper
        audio_data = audio.flatten()
        
        # Call transcribe
        result = asr.transcribe(audio_data)
        
        elapsed = time.time() - start_time
        print(f"✅ Transcription completed in {elapsed:.2f} seconds")
        print(f"📝 Result: '{result}'")
        
        if not result or result.strip() == "":
            print("⚠️  Warning: Transcription is empty. Try speaking louder or more clearly.")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure faster-whisper is installed: pip install faster-whisper")
    except Exception as e:
        print(f"❌ Whisper test failed: {e}")
        import traceback
        traceback.print_exc()

def test_vad():
    """Test Voice Activity Detection"""
    print("\n" + "="*50)
    print("Testing Voice Activity Detection...")
    
    try:
        from asr.asr_with_vad import ASRWithVAD
        
        # Simple config
        config = {
            "model_size": "base",
            "device": "cpu",
            "compute_type": "int8",
            "language": "en"
        }
        
        print("Initializing ASR with VAD...")
        asr_vad = ASRWithVAD(asr_model="Faster-Whisper", config=config)
        print("✅ ASR with VAD initialized")
        
        # Record audio
        audio = test_microphone()
        if audio is None:
            print("❌ No audio to process")
            return
        
        # Process with VAD
        print("\n🔄 Processing with VAD...")
        result = asr_vad.transcribe_with_vad(audio.flatten())
        print(f"📝 VAD Result: '{result}'")
        
    except Exception as e:
        print(f"❌ VAD test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("="*50)
    print("SPEECH RECOGNITION DIAGNOSTIC TEST")
    print("="*50)
    
    # Test basic microphone
    print("\n1. Testing Microphone Access...")
    test_microphone()
    
    # Test Whisper
    print("\n2. Testing Whisper ASR...")
    test_whisper()
    
    # Test VAD
    print("\n3. Testing VAD...")
    test_vad()
    
    print("\n" + "="*50)
    print("DIAGNOSTIC COMPLETE")
    print("="*50)