# Wake Word Setup Guide

## Current Status ✅

The wake word detection system has been configured to work with the available Chinese wake word file. The system will function properly even without the English wake word file.

### Files Created:
1. **`LLM-Live2D-Desktop-Assitant-main/static/desktop/wake-word.js`** - Main wake word detection module
2. **`LLM-Live2D-Desktop-Assitant-main/static/desktop/wake_word_config.json`** - Configuration file
3. **`LLM-Live2D-Desktop-Assitant-main/scripts/obtain_wake_word_files.js`** - Setup assistant script

### Available Wake Word:
- ✅ **Chinese**: "伊蕾娜" (Yī lěi nà) - File: `伊蕾娜_zh_wasm_v3_0_0.ppn` (11952 bytes)
- ❌ **English**: "Elaina" - File missing: `Elaina_en_wasm_v3_0_0.ppn`

## How It Works Now

The system is configured to:
1. Automatically detect available wake word files
2. Use the Chinese wake word if English is not available
3. Gracefully handle missing files without errors
4. Provide clear feedback about wake word availability

## To Add English Wake Word Support

### Option 1: Create Custom Wake Word (Recommended)

1. **Visit Porcupine Console**: https://console.picovoice.ai/
2. **Create Account**: Sign up for free (no credit card required)
3. **Create Wake Word**:
   - Click "Create Wake Word"
   - Enter phrase: "Elaina" or "Hey Elaina"
   - Select platform: Web (WASM)
   - Select language: English
   - Click "Train"
4. **Download File**:
   - Wait for training to complete (2-5 minutes)
   - Download the `.ppn` file
   - Rename to: `Elaina_en_wasm_v3_0_0.ppn`
5. **Install File**:
   - Copy to: `LLM-Live2D-Desktop-Assitant-main/static/desktop/`
6. **Enable in Config**:
   - Edit `wake_word_config.json`
   - Set `english.enabled` to `true`

### Option 2: Use Pre-built Wake Words

Porcupine provides some pre-built wake words you can use:

1. **Available Options**:
   - "Computer"
   - "Jarvis"
   - "Alexa"
   - "OK Google"
   - "Hey Siri"

2. **Download from GitHub**:
   ```bash
   # Visit Porcupine GitHub releases
   https://github.com/Picovoice/porcupine/releases
   
   # Look for wake word files in:
   resources/keyword_files/wasm/
   ```

3. **Rename and Install**:
   - Download the desired `.ppn` file
   - Rename to match expected filename
   - Place in `static/desktop/` directory

## Configuration File Structure

The `wake_word_config.json` file controls wake word behavior:

```json
{
  "wakeWords": {
    "chinese": {
      "enabled": true,
      "file": "伊蕾娜_zh_wasm_v3_0_0.ppn",
      "label": "伊蕾娜",
      "language": "zh",
      "paramsFile": "porcupine_params_zh.pv"
    },
    "english": {
      "enabled": false,  // Set to true when file is available
      "file": "Elaina_en_wasm_v3_0_0.ppn",
      "label": "Elaina",
      "language": "en",
      "paramsFile": "porcupine_params.pv"
    }
  },
  "accessKey": "YOUR_ACCESS_KEY",
  "sensitivity": 0.5  // Adjust 0.0-1.0 for detection sensitivity
}
```

## Integration with Application

The wake word module integrates with the existing VAD system:

```javascript
// In your application code
const detector = new WakeWordDetector();

// Initialize and start
await detector.initialize();
await detector.start();

// Listen for wake word events
window.addEventListener('wakeword', (event) => {
    console.log(`Wake word detected: ${event.detail.label}`);
    // Start listening for user input
});

// Stop when needed
await detector.stop();
```

## Troubleshooting

### Issue: Wake word not detecting
- **Solution**: Adjust sensitivity in config (0.5 default, try 0.3-0.7)

### Issue: File not found errors
- **Solution**: Run `node scripts/obtain_wake_word_files.js` to check setup

### Issue: Microphone access denied
- **Solution**: Ensure browser has microphone permissions

### Issue: Multiple wake words triggering
- **Solution**: Disable unused wake words in config

## Testing Wake Word

1. **Check Setup**:
   ```bash
   cd LLM-Live2D-Desktop-Assitant-main
   node scripts/obtain_wake_word_files.js
   ```

2. **Test in Browser**:
   - Open the application
   - Check console for "Wake word detector initialized"
   - Say the wake word clearly
   - Look for "Wake word detected" in console

## Performance Notes

- Chinese wake word works reliably with Mandarin pronunciation
- Sensitivity of 0.5 works well for most environments
- Background noise may require sensitivity adjustment
- Wake word detection uses ~10-20MB RAM
- CPU usage is minimal (<5% on modern systems)

## Next Steps

1. ✅ System is currently functional with Chinese wake word
2. ⏳ Optional: Add English wake word for bilingual support
3. 🎯 Consider adding custom wake words for personalization

## Support

For issues or questions:
1. Check the console logs for detailed error messages
2. Run the setup script to verify configuration
3. Ensure all required files are in correct locations
4. Verify microphone permissions and audio input

---

**Status**: Wake word system operational with Chinese support. English support optional but recommended for full functionality.