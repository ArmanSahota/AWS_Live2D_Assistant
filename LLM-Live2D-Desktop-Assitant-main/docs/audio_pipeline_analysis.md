# Audio Pipeline Analysis for Live2D Desktop Assistant

## Current Architecture

The audio pipeline in the Live2D Desktop Assistant consists of several key components that work together to process speech input and output:

### 1. Text-to-Speech (TTS) Flow

```
[User Input or LLM Response]
         ↓
[TTS Bridge (ttsBridge.ts)] → Wrapper around Python TTS engines
         ↓
[Python TTS Engine] → Generates audio files from text
         ↓
[Audio Playback (audio.js)] → Plays audio & syncs with Live2D model
         ↓
[Live2D Model Animation] → Lip sync and expressions
```

### 2. Speech-to-Text (STT) Flow

```
[Microphone Input]
         ↓
[VAD.js] → Voice Activity Detection
         ↓
[ASR with VAD] → Transcribes speech to text
         ↓
[Faster Whisper] → Speech recognition
         ↓
[Chat Pipeline] → Forwards to LLM
```

## Component Analysis

### TTS Components

1. **ttsBridge.ts**
   - Acts as an interface between frontend and TTS engines
   - Handles fallback logic between local and cloud TTS
   - Currently lacks proper error handling and diagnostics

2. **Python TTS Engines**
   - Multiple TTS engine implementations (piperTTS.py, edgeTTS.py, etc.)
   - All implement the TTSInterface abstract class
   - Generate audio files that are sent to the frontend

3. **audio.js**
   - Handles audio playback in the browser
   - Uses `window.model2.speak()` for lip-sync with Live2D model
   - Has a fallback mechanism for standard HTML5 audio

### STT Components

1. **vad.js**
   - Handles Voice Activity Detection
   - Controls when to start/stop recording
   - Sets sensitivity thresholds

2. **asr_with_vad.py**
   - Combines VAD with speech recognition
   - Records audio while voice is detected

3. **faster_whisper_asr.py**
   - Transcribes speech using Faster Whisper model
   - CPU-only implementation to avoid CUDA errors

## Identified Issues

### TTS Issues

1. **Model2 Variable Accessibility**
   - `window.model2` is not properly initialized or exposed globally
   - Causes the Live2D model's speak function to fail

2. **Error Handling**
   - Insufficient error handling and recovery
   - No metrics or diagnostics for TTS operations

3. **Integration with HTTP Path**
   - Current implementation is tightly coupled to WebSocket flow
   - Needs adaptation for HTTP-based LLM communication

### STT Issues

1. **VAD Configuration**
   - Speech probability threshold may need tuning
   - Microphone selection and initialization issues

2. **Error Recovery**
   - No automatic recovery when speech detection fails
   - Lack of user feedback during speech recognition

3. **Integration with HTTP Path**
   - Similar to TTS, needs adaptation for HTTP-based communication

## Recommendations

### Short-term Fixes

1. **Fix Model2 Global Access**
   - Ensure `window.model2` is properly exposed to the global scope
   - Add initialization checks before using the Live2D model's speak function

2. **Enhance Error Handling**
   - Add comprehensive error handling for TTS/STT operations
   - Implement fallback mechanisms for all critical functions

3. **Improve Audio Component Initialization**
   - Add explicit initialization sequence for audio components
   - Add safety checks and proper error reporting

### Medium-term Improvements

1. **Refactor Speech Bridges**
   - Implement robust TypeScript wrappers around Python TTS/STT
   - Add proper logging and diagnostics

2. **Update VAD Implementation**
   - Improve speech detection reliability
   - Add user feedback for speech detection status

3. **Prepare for HTTP Integration**
   - Decouple speech components from WebSocket dependencies
   - Make components work with both HTTP and WebSocket communication

## Next Steps

1. Fix the immediate issues with `window.model2` initialization
2. Enhance error handling in the audio pipeline
3. Implement proper TTS/STT TypeScript bridges for HTTP integration
4. Add diagnostics and observability to the speech components
