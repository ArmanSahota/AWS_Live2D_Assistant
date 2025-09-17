# STT Diagnostic Testing Guide

## Overview
Enhanced diagnostic logging has been applied to validate the STT pipeline diagnosis. This guide explains how to test and interpret the diagnostic output.

## Applied Diagnostic Patches

### 1. WebSocket Message Handler Enhancement (`server.py`)
- **Location**: Lines 250-270 (message reception and parsing)
- **Purpose**: Log all incoming WebSocket messages with detailed structure analysis
- **Diagnostic Tags**: `[STT DIAGNOSTIC]`

### 2. Unknown Message Type Enhancement (`server.py`)
- **Location**: Line 355 (unknown message handler)
- **Purpose**: Show exact content of unrecognized message types
- **Diagnostic Tags**: `[STT DIAGNOSTIC] UNKNOWN MESSAGE TYPE`

### 3. ASR Processing Enhancement (`asr/faster_whisper_asr.py`)
- **Location**: `transcribe_np()` method
- **Purpose**: Comprehensive audio data analysis and transcription diagnostics
- **Diagnostic Tags**: `[ASR DIAGNOSTIC]`

## Testing Instructions

### Step 1: Start the Application
```bash
cd LLM-Live2D-Desktop-Assitant-main
python server.py
```

### Step 2: Test STT Functionality
1. Open the desktop application
2. Activate the microphone
3. Speak a test phrase: "Testing, testing, 1, 2, 3"
4. Monitor the console output for diagnostic messages

### Step 3: Analyze Diagnostic Output

#### Expected WebSocket Diagnostic Messages:
```
[STT DIAGNOSTIC] Raw message length: 1234
[STT DIAGNOSTIC] Message type: 'mic-audio-data'
[STT DIAGNOSTIC] Message keys: ['type', 'audio']
[STT DIAGNOSTIC] Audio data: 4096 samples
[STT DIAGNOSTIC] Audio range: -0.3554 to 0.4384
```

#### Expected ASR Diagnostic Messages:
```
[ASR DIAGNOSTIC] Input audio shape: (95232,)
[ASR DIAGNOSTIC] Input audio dtype: float32
[ASR DIAGNOSTIC] Audio length: 95232 samples (5.95 seconds)
[ASR DIAGNOSTIC] Audio stats - Min: -0.3554, Max: 0.4384
[ASR DIAGNOSTIC] Audio stats - Mean: 0.0012, Std: 0.0856
[ASR DIAGNOSTIC] Starting Whisper transcription...
[ASR DIAGNOSTIC] Segment 0: ' Testing, testing, 1, 2, 3' (confidence: -0.234)
[ASR DIAGNOSTIC] Final transcription: ' Testing, testing, 1, 2, 3'
```

#### Unknown Message Type Detection:
```
[STT DIAGNOSTIC] UNKNOWN MESSAGE TYPE: 'some-unknown-type'
[STT DIAGNOSTIC] Full unknown message: {
  "type": "some-unknown-type",
  "data": "..."
}
```

## Diagnostic Analysis Checklist

### ✅ Normal Operation Indicators:
- [ ] WebSocket messages are parsed successfully
- [ ] Audio data contains reasonable amplitude ranges (-1.0 to 1.0)
- [ ] Audio length is appropriate for speech (>1 second)
- [ ] ASR transcription produces text output
- [ ] No "UNKNOWN MESSAGE TYPE" errors

### ⚠️ Problem Indicators:
- [ ] JSON Parse Errors in WebSocket messages
- [ ] Audio data is mostly zeros (silent)
- [ ] Audio dynamic range is very low (<0.01)
- [ ] Unknown message types being received
- [ ] ASR transcription errors or empty results

## Common Issues and Solutions

### Issue 1: Unknown Message Types
**Symptoms**: `[STT DIAGNOSTIC] UNKNOWN MESSAGE TYPE` messages
**Cause**: Frontend sending unrecognized WebSocket message types
**Solution**: Add handlers for the unknown message types or filter them in frontend

### Issue 2: Audio Data Corruption
**Symptoms**: Audio range outside -1.0 to 1.0, or mostly zeros
**Cause**: Audio format conversion issues between frontend and backend
**Solution**: Fix audio data serialization/deserialization

### Issue 3: JSON Parse Errors
**Symptoms**: `[STT DIAGNOSTIC] JSON Parse Error` messages
**Cause**: Malformed WebSocket messages
**Solution**: Fix message formatting in frontend

### Issue 4: Silent Audio
**Symptoms**: `WARNING: Audio is mostly silent` messages
**Cause**: Microphone not capturing audio or VAD issues
**Solution**: Check microphone permissions and VAD sensitivity

## Next Steps After Testing

1. **If diagnostics show unknown message types**: Identify and handle the unknown message types
2. **If audio data issues are found**: Fix audio format conversion between frontend/backend
3. **If ASR processing fails**: Debug Whisper model configuration or audio preprocessing
4. **If no issues are found**: The STT system is working correctly, and the original error messages may be cosmetic

## Removing Diagnostic Logging

Once testing is complete, you can remove the diagnostic logging by:
1. Reverting the changes to `server.py` and `asr/faster_whisper_asr.py`
2. Or keeping them for ongoing monitoring (recommended for development)

## Contact for Results

After running the diagnostic tests, please share:
1. The complete console output with `[STT DIAGNOSTIC]` and `[ASR DIAGNOSTIC]` messages
2. Any error messages or unexpected behavior
3. Whether STT functionality works despite the diagnostic messages

This will help determine if the root cause analysis was correct and guide the implementation of appropriate fixes.