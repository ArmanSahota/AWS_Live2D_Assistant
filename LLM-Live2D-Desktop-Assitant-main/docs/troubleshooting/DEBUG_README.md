# VTuber Debug Guide

This guide explains the changes made to improve debugging and fix issues with the VTuber application.

## Problem

The VTuber was getting stuck on "Thinking..." and not responding to voice input. Additionally, there was no way to see what the VTuber was hearing in the terminal.

## Changes Made

1. **Enhanced Logging in ASR Module**:
   - Added detailed logging in `faster_whisper_asr.py` to show transcription results
   - Added error handling and fallback to CPU if CUDA fails
   - Added logging of audio characteristics for debugging

2. **Improved Audio Processing Diagnostics**:
   - Added audio amplitude range logging in `asr_with_vad.py`
   - Added audio sample count logging
   - Added warning when no text is detected from audio

3. **Enhanced WebSocket Server Logging**:
   - Added logging of audio buffer size in `server.py`
   - Added logging of audio amplitude range
   - Added logging of text input received

4. **Added Debug Mode**:
   - Created `debug_vtuber.bat` script to run the application with enhanced logging
   - Sets the log level to DEBUG for more detailed output

## How to Use Debug Mode

1. Run the `debug_vtuber.bat` script to start the VTuber with enhanced logging:
   ```
   cd LLM-Live2D-Desktop-Assitant-main
   .\debug_vtuber.bat
   ```

2. Watch the terminal output to see:
   - What the VTuber is hearing (transcribed text)
   - Audio characteristics (sample count, amplitude range)
   - Any errors or warnings in the speech recognition process

## Troubleshooting

If the VTuber is still not responding to voice input:

1. Check the terminal output for any errors or warnings
2. Look for "Transcribed text:" messages to see what the VTuber is hearing
3. Check the audio amplitude range to ensure your microphone is working properly
4. If the amplitude range is very small (close to 0), check your microphone settings
5. If no text is being transcribed, try speaking louder or adjusting your microphone

## Common Issues

1. **No audio detected**:
   - Check if your microphone is properly connected and selected as the default input device
   - Check if the application has permission to access your microphone

2. **Audio detected but no transcription**:
   - The speech recognition model might not be able to understand your speech
   - Try speaking more clearly or adjusting your microphone position

3. **Transcription works but VTuber doesn't respond**:
   - Check if the LLM (Claude) is properly connected
   - Check for any errors in the LLM response processing

4. **CUDA errors**:
   - The application has been modified to always use CPU mode to avoid CUDA errors
   - If you see errors like "Could not locate cudnn_ops64_9.dll", this is normal and will be bypassed
   - The speech recognition will still work, just using CPU instead of GPU
   - If you want to use GPU acceleration, you would need to install the CUDA toolkit and cuDNN libraries
