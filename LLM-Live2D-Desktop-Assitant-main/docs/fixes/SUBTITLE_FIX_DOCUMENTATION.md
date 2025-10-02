# Subtitle Display Fix Documentation

## Problem
Subtitles were not showing in the application despite text being properly passed to the display function.

## Root Cause Analysis

### Issue 1: Default Toggle State Mismatch
- **Location**: [`main.js:50`](main.js:50)
- **Problem**: The "Show Subtitles" checkbox was set to `checked: false` by default
- **Impact**: Subtitles were hidden on application startup

### Issue 2: Missing Initialization
- **Location**: [`static/desktop/electron.js`](static/desktop/electron.js)
- **Problem**: No initialization code to sync the subtitle visibility with the default menu state
- **Impact**: The message element remained visible even when the menu said subtitles were off

## Applied Fixes

### 1. Changed Default Subtitle State
**File**: `main.js`
```javascript
// Before:
{ label: 'Show Subtitles', type: 'checkbox', checked: false, click: (menuItem) => toggleSubtitles(menuItem.checked) },

// After:
{ label: 'Show Subtitles', type: 'checkbox', checked: true, click: (menuItem) => toggleSubtitles(menuItem.checked) },
```

### 2. Added Initialization on Page Load
**File**: `static/desktop/electron.js`
```javascript
// Added initialization to ensure subtitles are visible by default
document.addEventListener('DOMContentLoaded', () => {
    console.log("[SUBTITLE DEBUG] Initializing subtitle visibility on page load");
    const messageDiv = document.getElementById('message');
    if (messageDiv) {
        // Remove hidden class to ensure subtitles are visible by default
        messageDiv.classList.remove('hidden');
        console.log("[SUBTITLE DEBUG] Initialized: Subtitles are visible by default");
    }
});
```

### 3. Added Diagnostic Logging
**Files Modified**:
- `static/desktop/audio.js` - Added logging to track text flow
- `static/desktop/electron.js` - Added logging for toggle events

## How Subtitles Work

1. **Text Generation**: When audio is played, text is passed to `playAudioLipSync()` in `audio.js`
2. **Display Update**: The function updates `document.getElementById("message").textContent`
3. **Visibility Control**: The toggle in the system tray menu adds/removes the 'hidden' class
4. **Styling**: CSS in `style.css` positions the subtitle at the bottom center with a semi-transparent background

## Testing the Fix

1. **Start the application**
   ```bash
   npm start
   ```

2. **Check initial state**
   - Subtitles should be visible by default
   - Right-click tray icon → "Show Subtitles" should be checked

3. **Test toggle functionality**
   - Uncheck "Show Subtitles" → subtitles should disappear
   - Check "Show Subtitles" → subtitles should reappear

4. **Test with audio playback**
   - Use "Test TTS" button in the test panel
   - Subtitles should display the spoken text

## Debug Logs
Look for these log messages in the console:
- `[SUBTITLE DEBUG] playAudioLipSync called with text:` - Shows when text is being processed
- `[SUBTITLE DEBUG] Text set to message element:` - Confirms text was set
- `[SUBTITLE DEBUG] Toggle subtitles called with:` - Shows toggle state changes
- `[SUBTITLE DEBUG] Initialized: Subtitles are visible by default` - Confirms initialization

## Rollback Instructions
If you need to revert these changes:

1. In `main.js`, change line 50 back to:
   ```javascript
   { label: 'Show Subtitles', type: 'checkbox', checked: false, click: (menuItem) => toggleSubtitles(menuItem.checked) },
   ```

2. Remove the initialization code from `static/desktop/electron.js` (lines added after the toggle handler)

3. Remove debug logging by searching for `[SUBTITLE DEBUG]` and removing those console.log statements

## Related Files
- `main.js` - Main process, contains menu configuration
- `static/desktop/electron.js` - Renderer process, handles UI events
- `static/desktop/audio.js` - Audio playback and subtitle text updates
- `static/desktop/style.css` - Subtitle styling
- `static/desktop.html` - HTML structure with message div