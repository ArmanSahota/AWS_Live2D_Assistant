"""
Quick STT Test - Run this to verify Speech-to-Text is working
Usage: python test_stt.py
"""
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import queue
import sys
import time

def test_stt():
    print("Testing Speech-to-Text with Whisper...")
    print("-" * 50)
    
    # Audio settings
    SAMPLE_RATE = 16000
    CHANNELS = 1
    DURATION = 5  # seconds
    
    try:
        # Check available audio devices
        print("Available audio devices:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']} (inputs: {device['max_input_channels']})")
        print()
        
        # Initialize Whisper
        print("Loading Whisper model (this may take a moment)...")
        model = WhisperModel("base", device="cpu", compute_type="int8")
        print("✅ Whisper model loaded")
        print()
        
        print(f"📢 Recording for {DURATION} seconds... Speak now!")
        print("Say something like: 'Hello, testing speech to text'")
        
        # Record audio
        audio_queue = queue.Queue()
        
        def callback(indata, frames, time_info, status):
            if status:
                print(f"Recording status: {status}", file=sys.stderr)
            audio_queue.put(indata.copy())
        
        # Start recording
        with sd.InputStream(
            samplerate=SAMPLE_RATE, 
            channels=CHANNELS,
            callback=callback, 
            dtype='float32'
        ):
            # Show countdown
            for i in range(DURATION, 0, -1):
                print(f"  Recording... {i} seconds remaining", end='\r')
                time.sleep(1)
        
        print("\n✅ Recording complete!")
        
        # Process audio
        audio_data = []
        while not audio_queue.empty():
            audio_data.append(audio_queue.get())
        
        if audio_data:
            audio_data = np.concatenate(audio_data, axis=0)
            audio_data = audio_data.flatten()
            
            # Save audio for debugging
            import soundfile as sf
            sf.write("test_stt_recording.wav", audio_data, SAMPLE_RATE)
            print("📁 Audio saved to: test_stt_recording.wav")
            
            # Transcribe
            print("🔄 Transcribing...")
            segments, info = model.transcribe(
                audio_data, 
                beam_size=5, 
                language="en",
                vad_filter=True
            )
            
            # Display results
            print("\n" + "=" * 50)
            print("TRANSCRIPTION RESULTS:")
            print("=" * 50)
            
            text_found = False
            for segment in segments:
                text = segment.text.strip()
                if text:
                    print(f"✅ Text: {text}")
                    print(f"   [Time: {segment.start:.2f}s - {segment.end:.2f}s]")
                    text_found = True
            
            if not text_found:
                print("❌ No speech detected in the recording")
                print("\nTroubleshooting:")
                print("1. Check your microphone is working")
                print("2. Speak louder or closer to the microphone")
                print("3. Check Windows microphone permissions")
            else:
                print("\n✅ STT test completed successfully!")
            
            return text_found
            
        else:
            print("❌ No audio was captured")
            return False
            
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("pip install faster-whisper sounddevice soundfile numpy")
        return False
        
    except Exception as e:
        print(f"❌ STT test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Install faster-whisper: pip install faster-whisper")
        print("2. Install sounddevice: pip install sounddevice")
        print("3. Check microphone permissions in Windows Settings")
        print("4. Try a different microphone if available")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SPEECH-TO-TEXT TEST")
    print("=" * 50)
    print()
    
    success = test_stt()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ STT IS WORKING!")
        print("Your speech was successfully converted to text.")
    else:
        print("❌ STT IS NOT WORKING")
        print("Please check the troubleshooting steps above.")
    print("=" * 50)