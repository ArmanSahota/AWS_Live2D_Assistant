# Subtitle Display Diagnostic Report

## Diagnosis Summary

I've added comprehensive diagnostic logging to help identify why subtitles are not showing. The diagnostic system will help identify which of these potential issues is causing the problem:

### Potential Root Causes (in order of likelihood):

1. **Missing `displaySubtitles` Function** ⚠️
   - The WebSocket handler calls `window.displaySubtitles()` but this function was not defined
   - **Solution Applied**: Created `subtitle-handler.js` with the missing function

2. **Hidden Class Applied**
   - The message element might have the 'hidden' class applied
   - **Diagnostic**: Logs will show if 'hidden' class is present

3. **CSS Display Issues**
   - The element might be set to `display: none` or `visibility: hidden`
   - **Diagnostic**: Logs will show computed styles

4. **Text Not Being Passed**
   - Audio playback might not be receiving subtitle text
   - **Diagnostic**: Logs will show if text parameter is null/undefined

5. **DOM Element Missing**
   - The message element might not exist in the DOM
   - **Diagnostic**: Logs will show if element is found

## Diagnostic Features Added

### 1. Enhanced Audio Logging (`audio.js`)
- Comprehensive logging in `playAudioLipSync()` function
- Tracks text parameter, element state, CSS properties
- Logs before and after text update
- Checks parent element visibility

### 2. WebSocket Handler Logging (`websocket.js`)
- Logs when 'full-text' messages are received
- Fallback to directly update message element if `displaySubtitles` is missing
- Ensures 'hidden' class is removed when updating

### 3. New Subtitle Handler (`subtitle-handler.js`)
- Defines the missing `window.displaySubtitles()` function
- Startup diagnostic that checks initial DOM state
- MutationObserver to track dynamic changes
- Automatic test on startup

### 4. Test Script (`test-subtitles.bat`)
- Convenient script to start the app for testing
- Instructions for checking diagnostic logs

## How to Test

1. **Run the test script:**
   ```bash
   cd LLM-Live2D-Desktop-Assitant-main
   test-subtitles.bat
   ```

2. **Open Developer Tools:**
   - Press F12 or Ctrl+Shift+I
   - Go to Console tab

3. **Look for diagnostic messages:**
   - Search for `[SUBTITLE DEBUG]` in console
   - You should see:
     - Startup diagnostic
     - Initial state check
     - Test subtitle display

4. **Test with TTS:**
   - Click "Test TTS" button in the test panel
   - Watch console for subtitle flow:
     - Text being passed to `playAudioLipSync`
     - Element visibility checks
     - Text update confirmation

## What to Look For in Logs

### ✅ Good Signs:
- `Message element found: true`
- `Display: block` or any value except `none`
- `Visibility: visible`
- `Hidden class present: false`
- `Text updated: [your text]`
- `Is visible: true`

### ❌ Problem Indicators:
- `Message element found: false` - Element missing from DOM
- `Display: none` - CSS hiding the element
- `Hidden class present: true` - Class hiding the element
- `No text provided` - Text not being passed to function
- `Parent element Display: none` - Parent is hidden

## Most Likely Fix

Based on the code analysis, the most likely issue was the **missing `displaySubtitles` function**. The WebSocket handler was trying to call this function but it didn't exist. I've created this function in `subtitle-handler.js` which should resolve the issue.

## Quick Fix Verification

After running the application with the diagnostic code:

1. **If subtitles now work:** The missing function was the issue
2. **If subtitles still don't show:** Check the console logs for the specific problem:
   - Hidden class issue → Check menu toggle state
   - CSS display issue → Check style.css
   - Text not passed → Check audio pipeline

## Next Steps

1. Run the application with the diagnostic code
2. Test the subtitle display using the "Test TTS" button
3. Check console logs for `[SUBTITLE DEBUG]` messages
4. Report back with the specific error indicators from the logs

The diagnostic logs will pinpoint exactly which component is failing and we can apply a targeted fix.