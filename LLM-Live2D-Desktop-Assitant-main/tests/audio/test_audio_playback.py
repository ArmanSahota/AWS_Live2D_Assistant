#!/usr/bin/env python3
"""
Test script to verify audio playback functionality.
Run this after applying the fixes to test if audio works.
"""

import os
import sys
sys.path.append('.')

from tts.tts_interface import TTSInterface
from tts.edgeTTS import TTSEngine

def test_audio_playback():
    """Test audio playback with EdgeTTS"""
    
    print("Testing EdgeTTS audio playback...")
    
    # Create TTS engine
    tts = TTSEngine(voice="en-US-JennyNeural")
    
    # Generate test audio
    test_text = "Hello! This is a test of the audio playback system."
    print(f"Generating audio for: {test_text}")
    
    audio_file = tts.generate_audio(test_text, "audio_test")
    
    if audio_file and os.path.exists(audio_file):
        print(f"✓ Audio file generated: {audio_file}")
        print(f"File size: {os.path.getsize(audio_file)} bytes")
        
        # Test playback
        print("Testing audio playback...")
        try:
            tts.play_audio_file_local(audio_file)
            print("✓ Audio playback test completed!")
            print("If you heard the audio, the fix is working!")
        except Exception as e:
            print(f"✗ Audio playback failed: {e}")
        
        # Clean up
        tts.remove_file(audio_file)
    else:
        print("✗ Failed to generate audio file")

if __name__ == "__main__":
    test_audio_playback()
