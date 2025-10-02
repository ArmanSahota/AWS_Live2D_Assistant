#!/usr/bin/env python3
"""
Debug script to add diagnostic logging for audio playback and conversation loop issues.
This will help validate our assumptions about the root causes.
"""

import os
import sys
import shutil
from pathlib import Path

def add_conversation_loop_diagnostics():
    """Add diagnostic logging to server.py for conversation loop issues"""
    
    server_file = "server.py"
    
    # Read the current file
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add diagnostic logging after conversation completion
    diagnostic_insertion = '''                                print("One Conversation Loop Completed")
                                
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
    
    # Replace the existing "One Conversation Loop Completed" line
    updated_content = content.replace(
        '                                print("One Conversation Loop Completed")',
        diagnostic_insertion
    )
    
    # Write back to file
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✓ Added conversation loop diagnostics to server.py")

def add_audio_playback_diagnostics():
    """Add diagnostic logging to main.py for audio playback issues"""
    
    main_file = "main.py"
    
    # Read the current file
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add diagnostic logging to _play_audio_file method
    diagnostic_code = '''        try:
            if self.verbose:
                print(f">> Playing {filepath}...")
            
            # DIAGNOSTIC: Check audio playback method
            print(f"[AUDIO DEBUG] About to play audio file: {filepath}")
            print(f"[AUDIO DEBUG] File exists: {os.path.exists(filepath)}")
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"[AUDIO DEBUG] File size: {file_size} bytes")
            
            # DIAGNOSTIC: Try local playback first
            try:
                print("[AUDIO DEBUG] Attempting local audio playback...")
                self.tts.play_audio_file_local(filepath)
                print("[AUDIO DEBUG] Local audio playback completed successfully")
            except Exception as local_error:
                print(f"[AUDIO DEBUG] Local audio playback failed: {local_error}")
                print("[AUDIO DEBUG] This explains why you can't hear the audio!")
                
                # Try alternative playback method
                try:
                    import pygame
                    pygame.mixer.init()
                    pygame.mixer.music.load(filepath)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                    print("[AUDIO DEBUG] Pygame audio playback completed")
                except Exception as pygame_error:
                    print(f"[AUDIO DEBUG] Pygame audio playback also failed: {pygame_error}")
                    
                    # Try system command as last resort
                    try:
                        import subprocess
                        if sys.platform == "win32":
                            subprocess.run(["start", filepath], shell=True, check=True)
                        elif sys.platform == "darwin":
                            subprocess.run(["afplay", filepath], check=True)
                        else:
                            subprocess.run(["aplay", filepath], check=True)
                        print("[AUDIO DEBUG] System command audio playback completed")
                    except Exception as system_error:
                        print(f"[AUDIO DEBUG] System command audio playback failed: {system_error}")

            self.tts.remove_file(filepath, verbose=self.verbose)'''
    
    # Replace the existing try block in _play_audio_file
    original_try_block = '''        try:
            if self.verbose:
                print(f">> Playing {filepath}...")
            self.tts.play_audio_file_local(filepath)

            self.tts.remove_file(filepath, verbose=self.verbose)'''
    
    updated_content = content.replace(original_try_block, diagnostic_code)
    
    # Write back to file
    with open(main_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✓ Added audio playback diagnostics to main.py")

def add_tts_interface_diagnostics():
    """Add diagnostic logging to TTS interface for playsound issues"""
    
    tts_interface_file = "tts/tts_interface.py"
    
    # Read the current file
    with open(tts_interface_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add diagnostic logging to play_audio_file_local method
    diagnostic_code = '''    def play_audio_file_local(self, audio_file_path: str) -> None:
        """
        Play the audio file locally on this device (not stream to some kind of live2d front end).

        audio_file_path: str
            the path to the audio file
        """
        print(f"[TTS DEBUG] Attempting to play audio file: {audio_file_path}")
        print(f"[TTS DEBUG] File exists: {os.path.exists(audio_file_path)}")
        
        if not os.path.exists(audio_file_path):
            print(f"[TTS DEBUG] ERROR: Audio file does not exist!")
            return
            
        try:
            print(f"[TTS DEBUG] Using playsound3 to play: {audio_file_path}")
            playsound(audio_file_path)
            print(f"[TTS DEBUG] playsound3 completed successfully")
        except Exception as e:
            print(f"[TTS DEBUG] playsound3 failed with error: {e}")
            print(f"[TTS DEBUG] This is likely why you can't hear the audio!")
            raise e'''
    
    # Replace the existing play_audio_file_local method
    original_method = '''    def play_audio_file_local(self, audio_file_path: str) -> None:
        """
        Play the audio file locally on this device (not stream to some kind of live2d front end).

        audio_file_path: str
            the path to the audio file
        """
        playsound(audio_file_path)'''
    
    updated_content = content.replace(original_method, diagnostic_code)
    
    # Write back to file
    with open(tts_interface_file, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("✓ Added TTS interface diagnostics to tts_interface.py")

def main():
    """Run all diagnostic additions"""
    print("Adding diagnostic logging to validate assumptions...")
    print()
    
    try:
        add_conversation_loop_diagnostics()
        add_audio_playback_diagnostics()
        add_tts_interface_diagnostics()
        
        print()
        print("✅ All diagnostic logging added successfully!")
        print()
        print("NEXT STEPS:")
        print("1. Run the application and test with one voice input")
        print("2. Check the console output for [CONVERSATION DEBUG] and [AUDIO DEBUG] messages")
        print("3. This will confirm our diagnosis:")
        print("   - Issue 1: Missing 'start-mic' signal after conversation")
        print("   - Issue 2: playsound3 library failing to play audio")
        print()
        print("After testing, share the debug output to confirm the diagnosis.")
        
    except Exception as e:
        print(f"❌ Error adding diagnostics: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())