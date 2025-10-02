# Microphone Start/Stop Loop Diagnosis

## Problem Description
The microphone is stuck in a rapid start/stop cycle, continuously logging:
```
[STT] Starting microphone...
Mic start
[STT] Stopping microphone...
Mic stop
```

## Diagnostic Analysis

### Most Likely Root Causes (Ranked by Probability)

#### 1. **WebSocket Control Message Loop** (HIGH PROBABILITY)
- **Location**: [`websocket.js:217-221`](LLM-Live2D-Desktop-Assitant-main/static/desktop/websocket.js:217)
- **Issue**: Server is sending repeated `'start-mic'` control messages via WebSocket
- **Evidence**: WebSocket handler automatically calls `window.start_mic()` when receiving control messages
- **Impact**: Creates external trigger loop independent of VAD system

#### 2. **VAD Misfire/Error Handling** (MEDIUM PROBABILITY)  
- **Location**: [`vad.js:104-110`](LLM-Live2D-Desktop-Assitant-main/static/desktop/vad.js:104)
- **Issue**: VAD system detecting false speech events, triggering STT, then immediately stopping
- **Evidence**: `onVADMisfire` callback exists but may not prevent restart cycle
- **Impact**: Creates internal feedback loop within speech detection system

### Secondary Contributing Factors

#### 3. **Audio Stream Initialization Failures**
- **Location**: [`vad.js:140-154`](LLM-Live2D-Desktop-Assitant-main/static/desktop/vad.js:140)
- **Issue**: Microphone stream fails to initialize, causing restart attempts
- **Evidence**: Try-catch block in `start_mic()` function

#### 4. **Timeout-Based Restart Logic**
- **Location**: [`vad.js:333-339`](LLM-Live2D-Desktop-Assitant-main/static/desktop/vad.js:333)
- **Issue**: 15-second timeout stops mic, then something immediately restarts it
- **Evidence**: `resetNoSpeechTimeout()` function with automatic restart

#### 5. **Wake Word Detection Interference**
- **Location**: [`vad.js:167-168`](LLM-Live2D-Desktop-Assitant-main/static/desktop/vad.js:167)
- **Issue**: Wake word detection restart logic conflicts with manual mic control
- **Evidence**: `start_wake_word_detection()` called after mic stop

## Diagnostic Tools Implemented

### 1. Comprehensive Logging System
- **File**: [`mic-debug-diagnostics.js`](LLM-Live2D-Desktop-Assitant-main/static/desktop/mic-debug-diagnostics.js)
- **Features**:
  - Tracks all mic start/stop events with timestamps and sources
  - Detects rapid cycling patterns (5+ actions in 5 seconds)
  - Monitors WebSocket control messages
  - Provides stack traces for each action
  - Auto-logs periodic state updates

### 2. Debug Functions Available
```javascript
// Get complete diagnostic information
window.getMicDiagnostics()

// Log current state to console
window.logMicState()
```

### 3. Automatic Detection
- Rapid cycling detection with alerts
- WebSocket message monitoring
- Timeout event tracking
- State history maintenance (last 20 actions)

## Next Steps for Validation

### Phase 1: Confirm Diagnosis
1. **Restart the application** to load diagnostic tools
2. **Trigger the mic start/stop loop** (should happen automatically)
3. **Check console logs** for detailed diagnostic information
4. **Run diagnostic commands**:
   ```javascript
   window.getMicDiagnostics()
   window.logMicState()
   ```

### Phase 2: Identify Primary Source
Based on diagnostic logs, look for:

**If WebSocket Control Messages are the cause:**
- Multiple `[MIC DEBUG] start from websocket_control` entries
- Rapid succession of WebSocket messages
- Server-side investigation needed

**If VAD Misfires are the cause:**
- `[MIC DEBUG] start from function_call` with VAD-related stack traces
- "VAD Misfire" messages in logs
- Audio input/threshold configuration issues

**If Audio Stream Issues are the cause:**
- Error messages in `start_mic()` try-catch blocks
- Microphone permission or device access problems
- Hardware/driver conflicts

### Phase 3: Apply Targeted Fix
Once the primary source is identified, implement the appropriate fix:

1. **For WebSocket Issues**: Add rate limiting or state checking
2. **For VAD Issues**: Adjust sensitivity thresholds or add debouncing
3. **For Audio Issues**: Improve error handling and device management
4. **For Timeout Issues**: Modify restart logic or timeout values

## Expected Diagnostic Output

When the diagnostic tools are active, you should see logs like:
```
[MIC DEBUG] Loading microphone diagnostics...
[MIC DEBUG 1] START from websocket_control at +1234ms
[MIC DEBUG 2] STOP from function_call at +1456ms
[MIC DEBUG] RAPID CYCLING DETECTED! {actionsInLast5Seconds: 5, timeSpan: 2341}
```

## Files Modified
1. [`desktop.html`](LLM-Live2D-Desktop-Assitant-main/static/desktop.html) - Added diagnostic script
2. [`mic-debug-diagnostics.js`](LLM-Live2D-Desktop-Assitant-main/static/desktop/mic-debug-diagnostics.js) - New diagnostic tool

## User Confirmation Required

**Please restart the application and confirm:**
1. Are the diagnostic logs appearing in the console?
2. What does `window.getMicDiagnostics()` show?
3. Which source is triggering the most start/stop events?

This information will allow us to proceed with the targeted fix for the specific root cause.