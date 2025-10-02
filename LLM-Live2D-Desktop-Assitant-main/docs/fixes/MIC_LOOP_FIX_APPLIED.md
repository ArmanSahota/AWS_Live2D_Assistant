# Microphone Loop Fix Applied

## Problem Description
The application was experiencing a severe microphone cycling issue with over 100k errors in an infinite loop:
- `vad.js:141 Mic start`
- `electron.js:254 [STT] Stopping microphone...`
- `vad.js:159 Mic stop`
- `electron.js:245 [STT] Starting microphone...`
- Repeat infinitely

## Root Cause Analysis

### Primary Cause: IPC Feedback Loop
1. **VAD detects speech** (possibly false positive from ambient noise)
2. **`onSpeechEnd` calls `window.stop_mic()`** (vad.js:115)
3. **`stop_mic()` calls `window.electronAPI.updateMenuChecked("Microphone", false)`** (vad.js:164)
4. **Menu update triggers `onToggleMicrophone` event** (electron.js:103)
5. **Event handler calls `window.start_mic()` again** (electron.js:105)
6. **Infinite loop created**

### Secondary Cause: VAD Hypersensitivity
- VAD immediately detecting ambient noise as speech
- Microphone feedback or system audio bleeding
- Hardware sensitivity issues

## Fix Implementation

### 1. IPC Feedback Loop Prevention (electron.js)
```javascript
// Add state guard to prevent IPC feedback loop
window.micToggleInProgress = false;
window.lastMicToggleTime = 0;
const MIC_TOGGLE_DEBOUNCE_MS = 500; // 500ms debounce

window.electronAPI.onToggleMicrophone((isChecked) => {
    const now = Date.now();
    
    // Prevent rapid cycling with debounce
    if (now - window.lastMicToggleTime < MIC_TOGGLE_DEBOUNCE_MS) {
        console.log('[MIC LOOP FIX] Debouncing microphone toggle, ignoring rapid call');
        return;
    }
    
    // Prevent feedback loop during programmatic updates
    if (window.micToggleInProgress) {
        console.log('[MIC LOOP FIX] Microphone toggle in progress, ignoring IPC event');
        return;
    }
    
    console.log(`[MIC LOOP FIX] User-initiated microphone toggle: ${isChecked}`);
    window.lastMicToggleTime = now;
    
    if (isChecked) {
        window.start_mic();
    } else {
        window.stop_mic();
    }
});
```

### 2. State Guard Implementation (vad.js)
```javascript
// In start_mic() and stop_mic() functions
window.micToggleInProgress = true;
window.electronAPI.updateMenuChecked("Microphone", state);
setTimeout(() => { window.micToggleInProgress = false; }, 100);
```

### 3. Circuit Breaker for Speech End Events (vad.js)
```javascript
onSpeechEnd: (audio) => {
    // Circuit breaker to prevent rapid cycling
    const now = Date.now();
    if (!window.lastSpeechEndTime) window.lastSpeechEndTime = 0;
    if (!window.speechEndCount) window.speechEndCount = 0;
    
    // Reset counter if enough time has passed
    if (now - window.lastSpeechEndTime > 5000) {
        window.speechEndCount = 0;
    }
    
    window.speechEndCount++;
    window.lastSpeechEndTime = now;
    
    // Circuit breaker: if too many speech end events in short time, don't stop mic
    if (window.speechEndCount > 3) {
        console.warn('[MIC LOOP FIX] Circuit breaker activated - too many speech end events, not stopping mic');
        resetNoSpeechTimeout();
        return;
    }
    
    if (!window.voiceInterruptionOn) {
        console.log('[MIC LOOP FIX] Stopping mic due to speech end (count:', window.speechEndCount, ')');
        window.stop_mic();
    }
    // ... rest of function
}
```

## Fix Components

### 1. Debouncing
- 500ms debounce on microphone toggle events
- Prevents rapid successive calls

### 2. State Guards
- `micToggleInProgress` flag prevents IPC feedback loops
- Temporary flag set during programmatic menu updates

### 3. Circuit Breaker
- Tracks speech end event frequency
- Prevents microphone stop if too many events occur rapidly
- Resets counter after 5 seconds of normal operation

### 4. Enhanced Logging
- Clear logging for debugging and monitoring
- Identifies user-initiated vs programmatic calls
- Tracks circuit breaker activations

## Files Modified
1. `static/desktop/electron.js` - IPC event handler with debouncing and state guards
2. `static/desktop/vad.js` - State guards in mic functions and circuit breaker in onSpeechEnd

## Expected Results
- Elimination of infinite microphone cycling
- Proper separation of user-initiated vs programmatic microphone toggles
- Graceful handling of VAD sensitivity issues
- Maintained functionality for legitimate microphone operations

## Testing
After applying this fix:
1. Monitor console logs for `[MIC LOOP FIX]` messages
2. Verify microphone can be toggled manually without issues
3. Confirm speech detection works normally
4. Check that rapid cycling is prevented

## Rollback Instructions
If issues occur, revert changes to:
- `static/desktop/electron.js` (lines 103-125)
- `static/desktop/vad.js` (start_mic, stop_mic, and onSpeechEnd functions)