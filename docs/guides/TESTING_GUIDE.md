# Live Testing Guide - LLM Live2D Desktop Assistant

## 🚀 Application is Now Running!

The desktop assistant should now be visible on your screen with a Live2D character.

## 🎯 What You Can Test:

### 1. **Voice Input (Microphone)**
- Look for the microphone icon in the system tray menu
- Click to enable/disable microphone
- When enabled, speak naturally and the assistant should transcribe your speech

### 2. **Live2D Character**
- The animated character should be visible
- It should have idle animations
- Click and drag to move the window around

### 3. **System Tray Menu**
Right-click the system tray icon to access:
- **Show Subtitles** - Toggle subtitle display
- **Microphone** - Enable/disable voice input
- **Select Microphone** - Choose audio input device
- **Speech Sensitivity** - Adjust voice detection sensitivity
- **Hide** - Minimize to system tray

### 4. **Speech Recognition Test**
1. Enable microphone from system tray
2. Say something like:
   - "Hello, can you hear me?"
   - "What's the weather today?"
   - "Tell me a joke"
3. Watch for transcription to appear as subtitles

### 5. **Text-to-Speech Test**
- The assistant should speak responses out loud
- Audio should play through your default speakers

## ⚠️ Known Limitations:

Since AWS Claude endpoint is not configured:
- The assistant won't generate AI responses
- You'll only see transcription of your speech
- TTS will work for any pre-configured responses

## 🔧 Troubleshooting:

### If you don't see the Live2D character:
1. Check if the window is minimized
2. Look in system tray and click "Show"
3. Check if it's behind other windows

### If microphone doesn't work:
1. Check Windows microphone permissions
2. Try selecting a different microphone from the menu
3. Adjust speech sensitivity to "Very High (70%)"

### If no audio output:
1. Check your system volume
2. Ensure speakers are not muted
3. Check Windows audio output device

## 📊 What's Working:
- ✅ Live2D character display and animations
- ✅ Microphone input and speech recognition (Whisper)
- ✅ Text-to-Speech output (Edge TTS)
- ✅ WebSocket connection to backend
- ✅ System tray controls

## 🔴 What Needs AWS Setup:
- ❌ AI responses from Claude (requires AWS endpoint)
- ❌ Intelligent conversation (requires LLM connection)

## 📝 Testing Checklist:

- [ ] Can you see the Live2D character?
- [ ] Can you drag the window around?
- [ ] Does the microphone icon work in system tray?
- [ ] Can you select a microphone device?
- [ ] Does it transcribe your speech?
- [ ] Can you adjust speech sensitivity?
- [ ] Does the Hide/Show function work?

## 💡 Next Steps:

To enable full AI functionality:
1. Deploy AWS backend with Claude 3.5 Sonnet
2. Configure HTTP_BASE environment variable
3. Restart the application

---

**Current Status:** Running in LOCAL MODE (no AI responses)
**Server:** Running on port 1025
**WebSocket:** Connected