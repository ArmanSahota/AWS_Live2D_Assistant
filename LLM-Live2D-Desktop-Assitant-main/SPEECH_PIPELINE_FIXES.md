# Speech Pipeline Fixes Summary

## Issues Identified and Resolved

### 1. ✅ WebSocket Connection Port Mismatch
**Problem:** The frontend was trying to connect to WebSocket on port 1018, but the server was running on port 1026.

**Solution:** Modified `websocket.js` to try multiple ports (1018, 1025, 1026, 8050, 8051) automatically.

**Files Modified:**
- `static/desktop/websocket.js` (lines 70-107)

### 2. ✅ Missing "default" Live2D Model
**Problem:** The application was configured to use "default" model but it wasn't defined in `model_dict.json`.

**Error:** `KeyError: 'default not found in model dictionary model_dict.json.'`

**Solution:** Added "default" model entry to `model_dict.json`.

**Files Modified:**
- `model_dict.json` (added lines 2-20)

### 3. ✅ TTS JavaScript Injection Error
**Problem:** JavaScript code was inside a Python string template causing "escapedText is not defined" error.

**Solution:** Moved JavaScript code outside of the Python string template in `ipc.js`.

**Files Modified:**
- `src/main/ipc.js` (lines 299-300)

## Testing Instructions

1. **Restart the Application:**
   ```bash
   # Stop the current instance (Ctrl+C)
   # Start fresh
   cd LLM-Live2D-Desktop-Assitant-main
   npm start
   ```

2. **Test Speech-to-Text (STT):**
   - Click the microphone button in the UI
   - Speak clearly
   - Check if your speech appears as subtitles
   - Check the terminal for transcription logs

3. **Test Text-to-Speech (TTS):**
   - Type a message or use STT
   - Wait for Claude's response
   - Verify you hear the audio response

4. **Check WebSocket Connection:**
   - Open browser console (F12)
   - Look for: "Successfully connected to WebSocket on port 1026"
   - Verify no WebSocket errors

5. **Run Diagnostic Tool:**
   ```bash
   node debug-speech-pipeline.js
   ```

## Current Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend   │────▶│  WebSocket   │────▶│   Backend   │
│  (Electron) │     │  Port 1026   │     │  (Python)   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                                         │
       │                                         ▼
       ▼                                  ┌─────────────┐
┌─────────────┐                          │  AWS Claude │
│ Microphone  │                          │   Bedrock   │
│   (VAD)     │                          └─────────────┘
└─────────────┘                                 │
       │                                         ▼
       ▼                                  ┌─────────────┐
┌─────────────┐                          │  Response   │
│ Audio Data  │                          └─────────────┘
└─────────────┘                                 │
       │                                         ▼
       ▼                                  ┌─────────────┐
┌─────────────┐                          │    TTS      │
│   Whisper   │                          │  (EdgeTTS)  │
│    (STT)    │                          └─────────────┘
└─────────────┘

```

## Data Flow

1. **Voice Input:** Microphone → VAD → Audio Chunks
2. **STT Processing:** Audio → Whisper ASR → Text
3. **AI Processing:** Text → AWS Claude → Response
4. **TTS Output:** Response → EdgeTTS → Audio
5. **Display:** Response → Subtitles + Live2D Animation

## Debugging Tips

### If STT Still Not Working:
1. Check microphone permissions in Windows Settings
2. Verify microphone is not used by another app
3. Check `conf.yaml`: `VOICE_INPUT_ON: true`
4. Look for Python errors in terminal

### If Subtitles Not Showing:
1. Check browser console for errors
2. Verify element with id="message" exists
3. Check `audio.js` line 41

### If WebSocket Fails:
1. Ensure no other app is using ports 1018/1026
2. Check Windows Firewall settings
3. Try manually setting port in `websocket.js`

## Next Steps

- [ ] Add robust error recovery
- [ ] Implement wake word detection
- [ ] Add DynamoDB session storage
- [ ] Optimize audio chunk size
- [ ] Add voice activity visualization

## Files Modified Summary

1. `static/desktop/websocket.js` - Multi-port connection support
2. `model_dict.json` - Added default model entry
3. `src/main/ipc.js` - Fixed TTS JavaScript injection
4. `debug-speech-pipeline.js` - Created diagnostic tool

## Known Limitations

- Wake word detection requires specific .ppn files
- Port conflicts may still occur with other applications
- Audio quality depends on microphone quality
- Network latency affects Claude response time