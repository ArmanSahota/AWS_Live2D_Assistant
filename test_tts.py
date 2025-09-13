"""
Quick TTS Test - Run this to verify Text-to-Speech is working
Usage: python test_tts.py
"""
import asyncio
import edge_tts
import pygame
import os

async def test_tts():
    print("Testing Edge TTS...")
    
    # Test text
    text = "Hello! Text to speech is working correctly. I can now speak to you!"
    voice = "en-US-AriaNeural"  # Female voice
    # Alternative voices:
    # "en-US-GuyNeural" - Male voice
    # "zh-CN-XiaoxiaoNeural" - Chinese female
    
    print(f"Text: {text}")
    print(f"Voice: {voice}")
    print("Generating speech...")
    
    try:
        # Generate speech
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save("test_tts_output.mp3")
        
        print("✅ TTS file generated: test_tts_output.mp3")
        
        # Play the audio
        print("Playing audio...")
        pygame.mixer.init()
        pygame.mixer.music.load("test_tts_output.mp3")
        pygame.mixer.music.play()
        
        # Wait for playback to finish
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        print("✅ TTS test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ TTS test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Install edge-tts: pip install edge-tts")
        print("2. Install pygame: pip install pygame")
        print("3. Check internet connection (edge-tts needs internet)")
        return False

if __name__ == "__main__":
    # Run test
    success = asyncio.run(test_tts())
    
    if success:
        print("\n✅ TTS is working! You should have heard the test message.")
    else:
        print("\n❌ TTS is not working. Please check the error messages above.")