# Quick Fix Guide - Get TTS/STT Working

## Priority: Make the App Work First!

### Step 1: Check Python Dependencies

First, let's ensure all audio dependencies are installed:

```bash
# Install/reinstall audio dependencies
pip install --upgrade pydub sounddevice soundfile scipy
pip install --upgrade edge-tts faster-whisper
pip install --upgrade numpy pyaudio

# On Windows, if pyaudio fails:
pip install pipwin
pipwin install pyaudio
```

### Step 2: Test TTS Independently

Create `test_tts.py`:

```python
import asyncio
import edge_tts
import pygame

async def test_tts():
    # Test Edge TTS
    text = "Hello! TTS is working correctly now."
    voice = "en-US-AriaNeural"  # or "zh-CN-XiaoxiaoNeural" for Chinese
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save("test_output.mp3")
    
    # Play the audio
    pygame.mixer.init()
    pygame.mixer.music.load("test_output.mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    print("✅ TTS test completed!")

# Run test
asyncio.run(test_tts())
```

Run: `python test_tts.py`

### Step 3: Test STT Independently

Create `test_stt.py`:

```python
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import queue
import sys

# Initialize Whisper
print("Loading Whisper model...")
model = WhisperModel("base", device="cpu", compute_type="int8")

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
DURATION = 5  # seconds

print(f"Recording for {DURATION} seconds... Speak now!")

# Record audio
audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    audio_queue.put(indata.copy())

# Start recording
with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, 
                   callback=callback, dtype='float32'):
    sd.sleep(DURATION * 1000)

# Process audio
audio_data = []
while not audio_queue.empty():
    audio_data.append(audio_queue.get())

if audio_data:
    audio_data = np.concatenate(audio_data, axis=0)
    audio_data = audio_data.flatten()
    
    # Transcribe
    print("Transcribing...")
    segments, info = model.transcribe(audio_data, beam_size=5, language="en")
    
    for segment in segments:
        print(f"✅ Transcription: {segment.text}")
else:
    print("❌ No audio captured")
```

Run: `python test_stt.py`

### Step 4: Fix Configuration Issues

Update `conf.yaml` with working settings:

```yaml
# MINIMAL WORKING CONFIG
VOICE_INPUT_ON: true
TTS_ON: true
TRANSLATE_AUDIO: false  # Disable for now

# Use simple, working models
ASR_MODEL: Faster-Whisper
ASR_MODEL_SIZE: base
ASR_LANGUAGE: en
ASR_DEVICE: cpu

TTS_MODEL: edgeTTS
EDGE_TTS_VOICE: en-US-AriaNeural

# Simple LLM config
LLM_PROVIDER: Claude
Claude:
  BASE_URL: "https://your-aws-endpoint.execute-api.us-west-2.amazonaws.com/dev"
  MODEL: "claude-3-haiku"

# Disable complex features initially
LIVE2D: true
SAY_GREETING: false
PERSONA_CHOICE: "service_assistant"
MAX_TOKENS: 500
```

### Step 5: Quick Server Fix

Fix the server port issue in `server.py`:

```python
# Around line 50, replace the port finding logic with:
def find_available_port(start_port: int = 1018, max_attempts: int = 25) -> int:
    import socket
    for port_offset in range(max_attempts):
        port = start_port + port_offset
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                logger.info(f"Using port: {port}")
                return port
        except:
            continue
    return 1025  # Fallback port

# At the bottom of server.py, change:
if __name__ == "__main__":
    port = find_available_port()
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=port)
```

### Step 6: Test WebSocket Connection

Create `test_connection.js`:

```javascript
// Test WebSocket connection
const WebSocket = require('ws');

// Try different ports
const ports = [1018, 1019, 1020, 1025];

async function testPort(port) {
    return new Promise((resolve) => {
        const ws = new WebSocket(`ws://127.0.0.1:${port}/client-ws`);
        
        ws.on('open', () => {
            console.log(`✅ Port ${port} - Connected!`);
            ws.close();
            resolve(true);
        });
        
        ws.on('error', (err) => {
            console.log(`❌ Port ${port} - ${err.message}`);
            resolve(false);
        });
        
        setTimeout(() => resolve(false), 2000);
    });
}

async function findWorkingPort() {
    for (const port of ports) {
        if (await testPort(port)) {
            console.log(`\n✅ WebSocket server found on port ${port}`);
            return port;
        }
    }
    console.log("\n❌ No WebSocket server found");
}

findWorkingPort();
```

Run: `node test_connection.js`

### Step 7: Update WebSocket Connection

In `static/desktop/websocket.js`, make it try multiple ports:

```javascript
// Around line 70, replace WebSocket connection with:
const POSSIBLE_PORTS = [1018, 1019, 1020, 1025];
let currentPortIndex = 0;

function connectWebSocket() {
    return new Promise((resolve, reject) => {
        function tryNextPort() {
            if (currentPortIndex >= POSSIBLE_PORTS.length) {
                console.error("No working WebSocket port found");
                reject(new Error("No WebSocket server available"));
                return;
            }
            
            const port = POSSIBLE_PORTS[currentPortIndex];
            console.log(`Trying WebSocket on port ${port}...`);
            
            window.ws = new WebSocket(`ws://127.0.0.1:${port}/client-ws`);
            
            window.ws.onopen = function() {
                console.log(`✅ Connected on port ${port}`);
                setState("idle");
                resolve();
            };
            
            window.ws.onerror = function(error) {
                console.log(`Port ${port} failed, trying next...`);
                currentPortIndex++;
                setTimeout(tryNextPort, 500);
            };
        }
        
        tryNextPort();
    });
}
```

### Step 8: Fix Missing Functions

Add this to `src/main/ipc.js` before line 253:

```javascript
// Simple model path resolver
function resolveModel3Path(modelPath) {
    const path = require('path');
    const fs = require('fs');
    
    // Just return the path if it exists
    if (fs.existsSync(modelPath)) {
        return modelPath;
    }
    
    // Try common locations
    const basePath = app.isPackaged 
        ? process.resourcesPath 
        : __dirname;
    
    const possiblePaths = [
        modelPath,
        path.join(basePath, modelPath),
        path.join(basePath, 'static', 'desktop', 'models', modelPath)
    ];
    
    for (const p of possiblePaths) {
        if (fs.existsSync(p)) return p;
    }
    
    console.warn(`Model path not found: ${modelPath}, using default`);
    return modelPath; // Return original path anyway
}
```

### Step 9: Disable Wake Word (Temporarily)

In `static/desktop/vad.js`, disable wake word to simplify:

```javascript
// Around line 195, replace wake word loading with:
async function initializeWakeWord() {
    console.log("Wake word disabled for testing");
    return null; // Skip wake word for now
}
```

### Step 10: Start Everything

Create `start_app.bat` (Windows) or `start_app.sh` (Mac/Linux):

**Windows (`start_app.bat`):**
```batch
@echo off
echo Starting VTuber Assistant...

REM Kill any existing processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM electron.exe 2>nul

REM Start Python server
echo Starting Python server...
start /B python server.py

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Start Electron app
echo Starting Electron app...
npm start

pause
```

**Mac/Linux (`start_app.sh`):**
```bash
#!/bin/bash
echo "Starting VTuber Assistant..."

# Kill existing processes
pkill -f "python server.py"
pkill -f electron

# Start Python server
echo "Starting Python server..."
python server.py &
SERVER_PID=$!

# Wait for server
sleep 3

# Start Electron app
echo "Starting Electron app..."
npm start

# Cleanup on exit
trap "kill $SERVER_PID" EXIT
wait
```

## Testing Checklist

Run these tests in order:

1. **Test TTS**: `python test_tts.py`
   - Should play "Hello! TTS is working correctly now."

2. **Test STT**: `python test_stt.py`
   - Should transcribe what you say

3. **Start Server**: `python server.py`
   - Should show "Using port: XXXX"

4. **Test WebSocket**: `node test_connection.js`
   - Should find the working port

5. **Start Full App**: `start_app.bat` or `./start_app.sh`
   - Should launch the VTuber window

## Common Issues & Quick Fixes

### Issue: "No module named 'edge_tts'"
```bash
pip install edge-tts
```

### Issue: "No module named 'faster_whisper'"
```bash
pip install faster-whisper
```

### Issue: "Port already in use"
```bash
# Windows
netstat -ano | findstr :1018
taskkill /PID <PID_NUMBER> /F

# Mac/Linux
lsof -i :1018
kill -9 <PID>
```

### Issue: "Microphone not working"
1. Check Windows Privacy Settings → Microphone
2. Allow apps to access microphone
3. Test with: `python -c "import sounddevice; print(sounddevice.query_devices())"`

### Issue: "No audio output"
```python
# Test audio output
import pygame
pygame.mixer.init()
pygame.mixer.music.load("test.mp3")  # Any MP3 file
pygame.mixer.music.play()
```

## Minimal Working Setup

If everything else fails, here's the absolute minimum to get something working:

1. **Just test Claude API**:
```python
import requests

response = requests.post(
    "https://your-endpoint.amazonaws.com/dev/claude",
    json={"text": "Hello, Claude!"}
)
print(response.json())
```

2. **Just test Live2D**:
```bash
cd static
python -m http.server 8000
# Open http://localhost:8000/desktop.html
```

3. **Just test TTS**:
```python
import edge_tts
import asyncio

async def speak(text):
    tts = edge_tts.Communicate(text, "en-US-AriaNeural")
    await tts.save("output.mp3")

asyncio.run(speak("Testing TTS"))
# Play output.mp3
```

## Next Steps (After Everything Works)

Once basic TTS/STT is working:
1. ✅ Test with AWS Claude endpoint
2. ✅ Add the free-roaming feature
3. ✅ Fix security issues (later)
4. ✅ Add advanced features

---

**Focus: Get it working first, optimize later!**