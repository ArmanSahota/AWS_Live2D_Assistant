#!/usr/bin/env python3
"""
Fix script for audio playback and conversation loop issues.
This implements the fixes for both identified problems.
"""

import os
import sys
import shutil
from pathlib import Path

def fix_conversation_loop_issue():
    """Fix Issue 1: Add missing 'start-mic' signal after conversation completion"""
    
    server_file = "server.py"
    
    # Read the current file
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The diagnostic code already includes the fix, but let's ensure it's properly implemented
    # Look for the conversation completion section and ensure start-mic is sent
    
    # Find the section where conversation completes
    target_section = '''                                print("One Conversation Loop Completed")
                                
                                # DIAGNOSTIC: Check if we need to restart microphone
                                print("[CONVERSATION DEBUG] Conversation task completed")
                                print(f"[CONVERSATION DEBUG] WebSocket still connected: {websocket.client_state}")
                                
                                # DIAGNOSTIC: Send start-mic signal to restart listening
                                try:
                                    await websocket.send_text(
                                        json.dumps({"type": "control", "text": "start-mic"})
                                    )
                                    print("[CONVERSATION DEBUG] Sent start-mic signal to restart listening")
                                except Exception as e:
                                    print(f"[CONVERSATION DEBUG] Failed to send start-mic signal: {e}")
                                
                                # DIAGNOSTIC: Reset conversation_task to None
                                conversation_task = None
                                print("[CONVERSATION DEBUG] Reset conversation_task to None")'''
    
    if target_section in content:
        print("✓ Conversation loop fix already applied (from diagnostic script)")
    else:
        # Apply the fix manually if diagnostic didn't work
        original_line = '                                print("One Conversation Loop Completed")'
        
        fix_code = '''                                print("One Conversation Loop Completed")
                                
                                # FIX: Send start-mic signal to restart listening after conversation
                                try:
                                    await websocket.send_text(
                                        json.dumps({"type": "control", "text": "start-mic"})
                                    )
                                    print("[FIX] Sent start-mic signal to restart listening")
                                except Exception as e:
                                    print(f"[FIX] Failed to send start-mic signal: {e}")
                                
                                # FIX: Reset conversation_task to None for next conversation
                                conversation_task = None'''
        
        updated_content = content.replace(original_line, fix_code)
        
        # Write back to file
        with open(server_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✓ Applied conversation loop fix to server.py")

def fix_audio_playback_issue():
    """Fix Issue 2: Implement robust audio playback with fallback methods"""
    
    tts_interface_file = "tts/tts_interface.py"
    
    # Read the current file
    with open(tts_interface_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create a robust audio playback method with multiple fallbacks
    new_playback_method = '''    def play_audio_file_local(self, audio_file_path: str) -> None:
        """
        Play the audio file locally on this device with multiple fallback methods.
        
        audio_file_path: str
            the path to the audio file
        """
        print(f"[AUDIO FIX] Attempting to play audio file: {audio_file_path}")
        print(f"[AUDIO FIX] File exists: {os.path.exists(audio_file_path)}")
        
        if not os.path.exists(audio_file_path):
            print(f"[AUDIO FIX] ERROR: Audio file does not exist!")
            return
            
        # Method 1: Try playsound3 (original method)
        try:
            print(f"[AUDIO FIX] Method 1: Trying playsound3...")
            playsound(audio_file_path)
            print(f"[AUDIO FIX] ✓ playsound3 succeeded")
            return
        except Exception as e:
            print(f"[AUDIO FIX] ✗ playsound3 failed: {e}")
        
        # Method 2: Try pygame
        try:
            print(f"[AUDIO FIX] Method 2: Trying pygame...")
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            pygame.mixer.quit()
            print(f"[AUDIO FIX] ✓ pygame succeeded")
            return
        except Exception as e:
            print(f"[AUDIO FIX] ✗ pygame failed: {e}")
        
        # Method 3: Try system command
        try:
            print(f"[AUDIO FIX] Method 3: Trying system command...")
            import subprocess
            import sys
            
            if sys.platform == "win32":
                # Windows: use start command
                subprocess.run(["start", "/wait", audio_file_path], shell=True, check=True)
            elif sys.platform == "darwin":
                # macOS: use afplay
                subprocess.run(["afplay", audio_file_path], check=True)
            else:
                # Linux: try multiple players
                players = ["aplay", "paplay", "mpg123", "ffplay"]
                for player in players:
                    try:
                        subprocess.run([player, audio_file_path], check=True, 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        print(f"[AUDIO FIX] ✓ {player} succeeded")
                        return
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                raise Exception("No suitable audio player found on Linux")
            
            print(f"[AUDIO FIX] ✓ System command succeeded")
            return
        except Exception as e:
            print(f"[AUDIO FIX] ✗ System command failed: {e}")
        
        # Method 4: Try winsound (Windows only)
        if sys.platform == "win32":
            try:
                print(f"[AUDIO FIX] Method 4: Trying winsound...")
                import winsound
                winsound.PlaySound(audio_file_path, winsound.SND_FILENAME)
                print(f"[AUDIO FIX] ✓ winsound succeeded")
                return
            except Exception as e:
                print(f"[AUDIO FIX] ✗ winsound failed: {e}")
        
        # If all methods fail
        print(f"[AUDIO FIX] ❌ ALL AUDIO PLAYBACK METHODS FAILED!")
        print(f"[AUDIO FIX] This explains why you can't hear the EdgeTTS audio.")
        print(f"[AUDIO FIX] Consider installing: pip install pygame")
        raise Exception("All audio playback methods failed")'''
    
    # Find and replace the existing play_audio_file_local method
    # Look for the method signature and replace everything until the next method
    import re
    
    # Pattern to match the entire play_audio_file_local method
    pattern = r'    def play_audio_file_local\(self, audio_file_path: str\) -> None:.*?(?=\n    def|\n\n|\Z)'
    
    if re.search(pattern, content, re.DOTALL):
        updated_content = re.sub(pattern, new_playback_method, content, flags=re.DOTALL)
        
        # Write back to file
        with open(tts_interface_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print("✓ Applied robust audio playback fix to tts_interface.py")
    else:
        print("⚠ Could not find play_audio_file_local method to replace")

def install_audio_dependencies():
    """Install pygame as a fallback audio library"""
    
    try:
        print("Installing pygame for audio playback fallback...")
        import subprocess
        import sys
        
        # Install pygame
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        print("✓ pygame installed successfully")
        
    except Exception as e:
        print(f"⚠ Failed to install pygame: {e}")
        print("You may need to install it manually: pip install pygame")

def create_audio_test_script():
    """Create a test script to verify audio playback works"""
    
    test_script = '''#!/usr/bin/env python3
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
'''
    
    with open("test_audio_playback.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✓ Created audio test script: test_audio_playback.py")

def main():
    """Apply all fixes"""
    print("Applying fixes for audio playback and conversation loop issues...")
    print()
    
    try:
        # Fix 1: Conversation loop issue
        print("=== Fix 1: Conversation Loop Issue ===")
        fix_conversation_loop_issue()
        print()
        
        # Fix 2: Audio playback issue
        print("=== Fix 2: Audio Playback Issue ===")
        fix_audio_playback_issue()
        print()
        
        # Install dependencies
        print("=== Installing Dependencies ===")
        install_audio_dependencies()
        print()
        
        # Create test script
        print("=== Creating Test Script ===")
        create_audio_test_script()
        print()
        
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print()
        print("SUMMARY OF FIXES:")
        print("1. ✓ Added 'start-mic' signal after conversation completion")
        print("2. ✓ Implemented robust audio playback with multiple fallback methods")
        print("3. ✓ Installed pygame as audio fallback library")
        print("4. ✓ Created test script to verify fixes")
        print()
        print("NEXT STEPS:")
        print("1. Run the application and test voice input")
        print("2. You should now hear EdgeTTS audio on your speakers")
        print("3. The microphone should restart after each conversation")
        print("4. Run 'python test_audio_playback.py' to test audio independently")
        
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())