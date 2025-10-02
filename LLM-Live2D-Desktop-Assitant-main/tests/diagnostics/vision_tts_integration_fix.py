#!/usr/bin/env python3
"""
Vision TTS Integration Fix

This script implements the complete solution to integrate vision analysis results
with the text-to-speech pipeline, ensuring the model speaks object analysis
results instead of only displaying them.
"""

import json
from pathlib import Path

def apply_vision_tts_integration_fix():
    """Apply the comprehensive fix to integrate vision analysis with TTS"""
    
    print("🔧 VISION TTS INTEGRATION FIX")
    print("=" * 50)
    
    # Step 1: Modify server.py to integrate with TTS pipeline
    server_fix = '''
# REPLACE the vision analysis result sending section in server.py (around lines 706-740)
# Find the section that starts with "# Send response back to client" and replace with:

                                # Send response back to client
                                response_message = {
                                    "type": "object-analysis-result",
                                    "analysisId": analysis_id,
                                    "result": analysis_result
                                }
                                
                                print(f"[VISION FIX] Sending vision analysis result to client...")
                                
                                # === NEW: INTEGRATE WITH TTS PIPELINE ===
                                print(f"[VISION TTS DEBUG] Vision analysis completed:")
                                print(f"[VISION TTS DEBUG] - Analysis text length: {len(response_text)} chars")
                                print(f"[VISION TTS DEBUG] - TTS integration: ENABLED")
                                print(f"[VISION TTS DEBUG] - Audio manager available: {hasattr(open_llm_vtuber, 'audio_manager') if open_llm_vtuber else False}")
                                print(f"[VISION TTS DEBUG] - Conversation manager available: {hasattr(open_llm_vtuber, 'conversation_manager') if open_llm_vtuber else False}")
                                
                                # Generate TTS for vision analysis result
                                if open_llm_vtuber and hasattr(open_llm_vtuber, 'audio_manager') and open_llm_vtuber.audio_manager:
                                    try:
                                        print(f"[VISION TTS] Generating speech for vision analysis...")
                                        
                                        # Clean the analysis text for TTS
                                        tts_text = response_text
                                        
                                        # Remove emotion keywords if Live2D is enabled
                                        if hasattr(open_llm_vtuber, 'live2d') and open_llm_vtuber.live2d:
                                            tts_text = open_llm_vtuber.live2d.remove_emotion_keywords(tts_text)
                                        
                                        # Generate audio file
                                        audio_filepath = open_llm_vtuber.audio_manager.generate_audio_file(
                                            tts_text, 
                                            file_name_no_ext=f"vision_analysis_{analysis_id}"
                                        )
                                        
                                        if audio_filepath:
                                            print(f"[VISION TTS] ✅ Audio generated: {audio_filepath}")
                                            
                                            # Play the audio
                                            open_llm_vtuber.audio_manager.play_audio_file(
                                                sentence=response_text,
                                                filepath=audio_filepath,
                                                instrument_filepath=None
                                            )
                                            print(f"[VISION TTS] ✅ Vision analysis spoken successfully")
                                        else:
                                            print(f"[VISION TTS] ⚠️ No audio generated (empty text)")
                                            
                                    except Exception as tts_error:
                                        print(f"[VISION TTS] ❌ TTS generation failed: {tts_error}")
                                        # Continue with normal response even if TTS fails
                                else:
                                    print(f"[VISION TTS] ⚠️ Audio manager not available - vision analysis will be silent")
                                
                                # Log first 200 chars of analysis for verification
                                analysis_preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
                                print(f"[VISION TTS DEBUG] Analysis preview: {analysis_preview}")
'''

    # Step 2: Create a helper method in audio_manager.py for vision TTS
    audio_manager_addition = '''
# ADD this method to AudioManager class in audio_manager.py:

    def speak_vision_analysis(self, analysis_text: str, analysis_id: str) -> bool:
        """
        Generate and play TTS for vision analysis results.
        
        Args:
            analysis_text: The vision analysis text to speak
            analysis_id: Unique identifier for the analysis
            
        Returns:
            bool: True if TTS was successful, False otherwise
        """
        try:
            print(f"[VISION AUDIO] Speaking vision analysis {analysis_id}")
            
            # Clean text for TTS
            clean_text = self.clean_text(analysis_text)
            
            # Remove Live2D emotion keywords if needed
            if self.live2d:
                clean_text = self.live2d.remove_emotion_keywords(clean_text)
            
            # Handle translation if enabled
            if self.translator and self.config.get("TRANSLATE_AUDIO", False):
                try:
                    print("[VISION AUDIO] Translating vision analysis...")
                    clean_text = self.translator.translate(clean_text)
                    print(f"[VISION AUDIO] Translated: {clean_text[:100]}...")
                except Exception as e:
                    print(f"[VISION AUDIO] Translation failed: {e}")
            
            # Generate audio
            audio_filepath = self.generate_audio_file(
                clean_text, 
                file_name_no_ext=f"vision_{analysis_id}"
            )
            
            if audio_filepath:
                # Play the audio
                self.play_audio_file(
                    sentence=analysis_text,
                    filepath=audio_filepath,
                    instrument_filepath=None
                )
                print(f"[VISION AUDIO] ✅ Vision analysis spoken successfully")
                return True
            else:
                print(f"[VISION AUDIO] ⚠️ No audio generated")
                return False
                
        except Exception as e:
            print(f"[VISION AUDIO] ❌ Error speaking vision analysis: {e}")
            return False
'''

    # Step 3: Alternative approach using conversation manager
    conversation_integration = '''
# ALTERNATIVE: Add this method to ConversationManager class for better integration:

    def speak_vision_analysis(self, analysis_text: str, analysis_id: str) -> None:
        """
        Speak vision analysis results using the existing TTS pipeline.
        
        Args:
            analysis_text: The vision analysis text to speak
            analysis_id: Unique identifier for the analysis
        """
        try:
            print(f"[VISION CONVERSATION] Speaking vision analysis via conversation pipeline")
            
            # Check if TTS is enabled
            if not self.config.get("TTS_ON", False):
                print(f"[VISION CONVERSATION] TTS is disabled - skipping speech")
                return
            
            # Use the existing audio manager to speak the text
            if self.audio_manager:
                success = self.audio_manager.speak_vision_analysis(analysis_text, analysis_id)
                if success:
                    print(f"[VISION CONVERSATION] ✅ Vision analysis spoken via conversation manager")
                else:
                    print(f"[VISION CONVERSATION] ❌ Failed to speak vision analysis")
            else:
                print(f"[VISION CONVERSATION] ❌ Audio manager not available")
                
        except Exception as e:
            print(f"[VISION CONVERSATION] ❌ Error in vision speech integration: {e}")
'''

    print("\n🔧 IMPLEMENTATION STEPS:")
    print("\n1️⃣ SERVER.PY INTEGRATION:")
    print("Replace the vision analysis response section with TTS integration:")
    print(server_fix)
    
    print("\n2️⃣ AUDIO MANAGER ENHANCEMENT:")
    print("Add vision-specific TTS method to AudioManager:")
    print(audio_manager_addition)
    
    print("\n3️⃣ CONVERSATION MANAGER INTEGRATION (Alternative):")
    print("Add vision TTS method to ConversationManager:")
    print(conversation_integration)
    
    print("\n🎯 EXPECTED RESULTS AFTER FIX:")
    print("✅ Vision analysis will generate TTS audio")
    print("✅ Model will speak object analysis results")
    print("✅ Both text display AND speech will work")
    print("✅ Logs will show [VISION TTS] success messages")
    
    print("\n🧪 TESTING PROCEDURE:")
    print("1. Apply the server.py integration fix")
    print("2. Add the speak_vision_analysis method to AudioManager")
    print("3. Restart the server")
    print("4. Test vision analysis - should hear speech")
    print("5. Check logs for [VISION TTS] success messages")

if __name__ == "__main__":
    apply_vision_tts_integration_fix()