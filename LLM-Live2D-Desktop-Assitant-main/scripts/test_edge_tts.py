#!/usr/bin/env python3
"""
Test script for Edge TTS engine validation.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from tts
sys.path.append(str(Path(__file__).parent.parent))

from tts.edge_tts_engine import EdgeTTSEngine

def test_edge_tts():
    """Test the Edge TTS engine with basic functionality."""
    print("Testing Edge TTS Engine...")
    
    try:
        # Create engine with default settings
        tts = EdgeTTSEngine(voice="en-US-JennyNeural")
        print(f"✓ Engine created successfully")
        
        # Test synthesis
        test_text = "Hello! This is Edge TTS speaking from the Agentic VTuber."
        print(f"Synthesizing: '{test_text}'")
        
        path, duration = tts.synthesize(test_text)
        
        print(f"✓ Synthesis completed")
        print(f"  File: {path}")
        print(f"  Duration: {duration:.2f} seconds")
        
        # Verify file exists
        if os.path.exists(path):
            file_size = os.path.getsize(path)
            print(f"  File size: {file_size} bytes")
            print("✓ Audio file created successfully")
        else:
            print("✗ Audio file not found")
            return False
            
        # Test with advanced parameters
        print("\nTesting with advanced parameters...")
        tts_advanced = EdgeTTSEngine(
            voice="en-US-GuyNeural",
            rate="+20%",
            pitch="+2Hz",
            volume="+10%"
        )
        
        path2, duration2 = tts_advanced.synthesize("Testing advanced voice parameters.")
        print(f"✓ Advanced synthesis completed: {path2}, duration: {duration2:.2f}s")
        
        print("\n🎉 All tests passed!")
        print(f"OK: {path} duration: {duration:.2f}")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_edge_tts()
    sys.exit(0 if success else 1)