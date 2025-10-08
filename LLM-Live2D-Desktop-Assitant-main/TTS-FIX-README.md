# TTS Fix - EdgeTTS Style Parameter Issue

## Problem
The TTS (Text-to-Speech) was failing with the error:
```
TTS worker error: Error generating audio for sentence.
Communicate.__init__() got an unexpected keyword argument 'style'
```

This occurred because the `edge-tts` library version being used doesn't support the `style` parameter that was configured in `conf.yaml`.

## Root Cause
- The `conf.yaml` file had `style: friendly` configured under the `EDGE_TTS` section (line 10)
- The current version of the `edge-tts` library doesn't recognize the `style` parameter
- This caused the `edge_tts.Communicate()` constructor to fail with a TypeError

## Solution Applied

### 1. Configuration Fix
**File:** `conf.yaml`
- Commented out the `style: friendly` parameter on line 10
- Added explanatory comment: `# style: friendly  # Commented out - not supported by current edge-tts version`

### 2. Code Improvement
**File:** `tts/edge_tts_engine.py`
- Added error handling in the `_async_synthesize_to_file()` method
- If a TypeError occurs related to the `style` parameter, the code now:
  - Logs a warning message
  - Automatically retries without the style parameter
  - Continues TTS generation successfully

## Files Modified
1. `LLM-Live2D-Desktop-Assitant-main/conf.yaml` - Commented out unsupported style parameter
2. `LLM-Live2D-Desktop-Assitant-main/tts/edge_tts_engine.py` - Added graceful error handling

## Testing
After applying these fixes, the TTS should work properly:
- Audio generation will proceed without the style parameter
- No more "unexpected keyword argument 'style'" errors
- The system will log a warning if style is attempted but fall back gracefully

## Future Considerations
- If you upgrade to a newer version of `edge-tts` that supports the `style` parameter, you can uncomment the line in `conf.yaml`
- The error handling in `edge_tts_engine.py` will automatically detect and use the style parameter if supported

## Verification
To verify the fix is working:
1. Restart the application
2. Test TTS functionality by speaking to the assistant
3. Check that audio is generated without errors
4. Look for the log message: `[EdgeTTS] Synth: voice=en-US-JennyNeural rate=-20% pitch=+0Hz volume=+10%`