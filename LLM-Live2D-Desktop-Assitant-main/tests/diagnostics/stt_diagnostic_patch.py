#!/usr/bin/env python3
"""
STT Diagnostic Patch - Enhanced logging to identify STT pipeline issues
This script adds comprehensive logging to validate our assumptions about the STT problems.
"""

import json
import numpy as np
from typing import Dict, Any

def create_enhanced_websocket_handler_patch():
    """
    Creates a patch for the WebSocket message handler with enhanced diagnostic logging.
    This will help us identify:
    1. Unknown message types being received
    2. Audio data format issues
    3. Message parsing problems
    """
    
    patch_code = '''
# Enhanced WebSocket Message Handler Patch
# Add this to server.py around line 250-355

async def enhanced_websocket_handler(websocket, message):
    """Enhanced WebSocket message handler with comprehensive diagnostics"""
    try:
        print(f"\\n[STT DIAGNOSTIC] Raw message length: {len(message)}")
        
        # Parse JSON with error handling
        try:
            data = json.loads(message)
            message_type = data.get("type", "NO_TYPE")
            print(f"[STT DIAGNOSTIC] Message type: '{message_type}'")
            print(f"[STT DIAGNOSTIC] Message keys: {list(data.keys())}")
            
            # Log message size and structure
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "audio" and isinstance(value, dict):
                        print(f"[STT DIAGNOSTIC] Audio data: {len(value)} samples")
                        # Check audio data integrity
                        audio_values = list(value.values())
                        if audio_values:
                            audio_min = min(audio_values)
                            audio_max = max(audio_values)
                            print(f"[STT DIAGNOSTIC] Audio range: {audio_min:.4f} to {audio_max:.4f}")
                            
                            # Check for data corruption
                            nan_count = sum(1 for v in audio_values if not isinstance(v, (int, float)) or (isinstance(v, float) and (v != v)))  # NaN check
                            if nan_count > 0:
                                print(f"[STT DIAGNOSTIC] WARNING: {nan_count} invalid audio samples detected!")
                    else:
                        print(f"[STT DIAGNOSTIC] {key}: {type(value).__name__} ({len(str(value))} chars)")
            
        except json.JSONDecodeError as e:
            print(f"[STT DIAGNOSTIC] JSON Parse Error: {e}")
            print(f"[STT DIAGNOSTIC] Raw message preview: {message[:200]}...")
            return None
            
        # Enhanced message type handling
        if message_type == "mic-audio-data":
            audio_chunk = data.get("audio")
            if audio_chunk:
                try:
                    # Test audio conversion
                    chunk_array = np.array(list(audio_chunk.values()), dtype=np.float32)
                    print(f"[STT DIAGNOSTIC] Audio conversion successful: {len(chunk_array)} samples")
                    
                    # Check for audio quality issues
                    if len(chunk_array) > 0:
                        zero_count = np.sum(chunk_array == 0)
                        if zero_count > len(chunk_array) * 0.8:  # More than 80% zeros
                            print(f"[STT DIAGNOSTIC] WARNING: Audio mostly silent ({zero_count}/{len(chunk_array)} zeros)")
                            
                        # Check for clipping
                        clipped_count = np.sum(np.abs(chunk_array) >= 0.99)
                        if clipped_count > 0:
                            print(f"[STT DIAGNOSTIC] WARNING: {clipped_count} clipped audio samples detected")
                            
                except Exception as conv_error:
                    print(f"[STT DIAGNOSTIC] Audio conversion error: {conv_error}")
                    print(f"[STT DIAGNOSTIC] Audio chunk type: {type(audio_chunk)}")
                    if isinstance(audio_chunk, dict):
                        sample_keys = list(audio_chunk.keys())[:5]
                        sample_values = [audio_chunk[k] for k in sample_keys]
                        print(f"[STT DIAGNOSTIC] Sample keys: {sample_keys}")
                        print(f"[STT DIAGNOSTIC] Sample values: {sample_values}")
            else:
                print("[STT DIAGNOSTIC] WARNING: mic-audio-data message with no audio content")
                
        elif message_type == "mic-audio-end":
            print("[STT DIAGNOSTIC] Audio end signal received")
            
        elif message_type == "text-input":
            text = data.get("text", "")
            print(f"[STT DIAGNOSTIC] Text input: '{text}' ({len(text)} chars)")
            
        elif message_type == "interrupt-signal":
            print("[STT DIAGNOSTIC] Interrupt signal received")
            
        elif message_type == "config":
            print(f"[STT DIAGNOSTIC] Config message: {data}")
            
        elif message_type in ["switch-config", "fetch-backgrounds"]:
            print(f"[STT DIAGNOSTIC] Control message: {message_type}")
            
        else:
            print(f"[STT DIAGNOSTIC] UNKNOWN MESSAGE TYPE: '{message_type}'")
            print(f"[STT DIAGNOSTIC] Full message: {json.dumps(data, indent=2)}")
            
        return data
        
    except Exception as e:
        print(f"[STT DIAGNOSTIC] Handler error: {e}")
        import traceback
        traceback.print_exc()
        return None
'''
    
    return patch_code

def create_asr_diagnostic_patch():
    """
    Creates a patch for the ASR processing with enhanced diagnostics.
    """
    
    patch_code = '''
# Enhanced ASR Processing Patch
# Add this to faster_whisper_asr.py

def enhanced_transcribe_np(self, audio: np.ndarray) -> str:
    """Enhanced transcribe with comprehensive diagnostics"""
    print(f"\\n[ASR DIAGNOSTIC] Input audio shape: {audio.shape}")
    print(f"[ASR DIAGNOSTIC] Input audio dtype: {audio.dtype}")
    print(f"[ASR DIAGNOSTIC] Audio length: {len(audio)} samples ({len(audio)/16000:.2f} seconds)")
    
    if len(audio) > 0:
        audio_min = np.min(audio)
        audio_max = np.max(audio)
        audio_mean = np.mean(audio)
        audio_std = np.std(audio)
        
        print(f"[ASR DIAGNOSTIC] Audio stats - Min: {audio_min:.4f}, Max: {audio_max:.4f}")
        print(f"[ASR DIAGNOSTIC] Audio stats - Mean: {audio_mean:.4f}, Std: {audio_std:.4f}")
        
        # Check for common audio issues
        zero_count = np.sum(audio == 0)
        if zero_count > len(audio) * 0.9:
            print(f"[ASR DIAGNOSTIC] WARNING: Audio is mostly silent ({zero_count}/{len(audio)} zeros)")
            
        if audio_max - audio_min < 0.01:
            print(f"[ASR DIAGNOSTIC] WARNING: Very low audio dynamic range")
            
        # Check sample rate assumptions
        if len(audio) < 1600:  # Less than 0.1 seconds at 16kHz
            print(f"[ASR DIAGNOSTIC] WARNING: Audio too short for reliable transcription")
    else:
        print(f"[ASR DIAGNOSTIC] ERROR: Empty audio array")
        return ""
    
    try:
        print(f"[ASR DIAGNOSTIC] Starting Whisper transcription...")
        segments, info = self.model.transcribe(
            audio,
            beam_size=5 if self.BEAM_SEARCH else 1,
            language=self.LANG,
            condition_on_previous_text=False,
        )
        
        print(f"[ASR DIAGNOSTIC] Transcription info: {info}")
        
        text_segments = []
        for i, segment in enumerate(segments):
            print(f"[ASR DIAGNOSTIC] Segment {i}: '{segment.text}' (confidence: {getattr(segment, 'avg_logprob', 'N/A')})")
            text_segments.append(segment.text)
        
        if not text_segments:
            print(f"[ASR DIAGNOSTIC] WARNING: No text segments generated")
            return ""
        else:
            result = "".join(text_segments)
            print(f"[ASR DIAGNOSTIC] Final transcription: '{result}'")
            return result
            
    except Exception as e:
        print(f"[ASR DIAGNOSTIC] Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return ""
'''
    
    return patch_code

if __name__ == "__main__":
    print("STT Diagnostic Patches Generated")
    print("=" * 50)
    print("\\n1. WebSocket Handler Patch:")
    print(create_enhanced_websocket_handler_patch())
    print("\\n2. ASR Processing Patch:")
    print(create_asr_diagnostic_patch())
    
    print("\\n" + "=" * 50)
    print("INSTRUCTIONS:")
    print("1. Apply the WebSocket handler patch to server.py")
    print("2. Apply the ASR processing patch to faster_whisper_asr.py")
    print("3. Run the application and test STT functionality")
    print("4. Check logs for [STT DIAGNOSTIC] and [ASR DIAGNOSTIC] messages")