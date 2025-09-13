# Next Steps - Execution Guide

## Step 1: Deploy AWS Backend (15 minutes)

Open a terminal and run these commands:

```bash
# 1. Navigate to backend directory
cd LLM-Live2D-Desktop-Assitant-main/backend

# 2. Build the SAM application
sam build

# 3. Deploy (first time setup)
sam deploy --guided

# When prompted, use these settings:
#   Stack Name: live2d-opus-backend
#   AWS Region: us-west-2
#   Parameter Env: dev
#   Confirm changes: Y
#   Allow SAM to create IAM roles: Y
#   Save parameters to samconfig.toml: Y
```

**🔴 IMPORTANT**: Copy the `HttpBase` URL from the output. It will look like:
```
https://abc123xyz.execute-api.us-west-2.amazonaws.com/dev
```

## Step 2: Configure Environment (2 minutes)

Create `.env` file in the root directory:

```bash
# Create .env file
echo HTTP_BASE=YOUR_ACTUAL_ENDPOINT_HERE > .env

# Example:
echo HTTP_BASE=https://abc123xyz.execute-api.us-west-2.amazonaws.com/dev > .env
```

## Step 3: Test Individual Components (5 minutes)

Run these tests in order:

```bash
# Test 1: TTS (should hear "Hello! Text to speech is working correctly")
python test_tts.py

# Test 2: STT (will record 5 seconds of your speech)
python test_stt.py

# Test 3: Claude Opus (tests the AWS endpoint)
python test_claude_opus.py

# Test 4: WebSocket connection
node test_connection.js
```

✅ **Success Criteria**:
- TTS: You hear audio
- STT: Your speech is transcribed
- Claude: All 4 tests pass
- WebSocket: Finds port 1018 or similar

## Step 4: Start the Application (2 minutes)

### Option A: Use the batch file (Windows)
```bash
start_app.bat
```

### Option B: Manual start
```bash
# Terminal 1 - Start Python server
cd LLM-Live2D-Desktop-Assitant-main
python server.py

# Terminal 2 - Start Electron app
cd LLM-Live2D-Desktop-Assitant-main
npm start
```

## Step 5: Verify Everything Works (5 minutes)

When the app starts:

1. **Live2D Model**: Should see the animated character
2. **Microphone**: Click mic button, speak, should see transcription
3. **Claude Response**: Ask "Hello, how are you?" - should get response
4. **TTS Playback**: Response should be spoken aloud

## Step 6: Add Free-Roaming Feature (10 minutes)

### 6.1 Create the draggable handler

<create file: `LLM-Live2D-Desktop-Assitant-main/static/desktop/draggable.js`>

```javascript
// Simple drag implementation for VTuber model
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;

function initDraggable() {
    const dragArea = document.createElement('div');
    dragArea.id = 'drag-area';
    dragArea.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 60px;
        cursor: move;
        z-index: 9999;
        background: transparent;
    `;
    
    document.body.appendChild(dragArea);
    
    dragArea.addEventListener('mousedown', (e) => {
        isDragging = true;
        dragStartX = e.screenX;
        dragStartY = e.screenY;
        
        // Tell Electron to start window drag
        if (window.electronAPI && window.electronAPI.startDrag) {
            window.electronAPI.startDrag();
        }
    });
    
    // Double-click to reset position
    dragArea.addEventListener('dblclick', () => {
        if (window.electronAPI && window.electronAPI.resetPosition) {
            window.electronAPI.resetPosition();
        }
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initDraggable);
```

### 6.2 Update desktop.html

Add this line in `LLM-Live2D-Desktop-Assitant-main/static/desktop.html` before `</body>`:

```html
<script src="desktop/draggable.js"></script>
```

### 6.3 Update main.js window config

In `LLM-Live2D-Desktop-Assitant-main/main.js`, update the window creation (around line 85):

```javascript
mainWindow = new BrowserWindow({
    width: 350,
    height: 500,
    transparent: true,
    frame: false,  // Add this for borderless
    resizable: false,
    hasShadow: false,
    alwaysOnTop: true,
    skipTaskbar: false,
    webPreferences: {
      preload: path.join(basePath, 'static', 'desktop', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false
    }
});
```

## Step 7: Test Free-Roaming (2 minutes)

1. Restart the app
2. Click and hold the top area of the VTuber
3. Drag to move around screen
4. Double-click to reset position

## Troubleshooting Quick Fixes

### Issue: "Cannot find module 'ws'"
```bash
npm install ws
```

### Issue: "No module named 'edge_tts'"
```bash
pip install edge-tts
```

### Issue: Port 1018 already in use
```bash
# Windows
netstat -ano | findstr :1018
taskkill /F /PID [NUMBER]

# Mac/Linux
lsof -i :1018
kill -9 [PID]
```

### Issue: AWS endpoint returns 403
1. Check Bedrock model access in AWS Console
2. Request access to Claude Opus model
3. Wait 5 minutes for propagation

## ✅ Success Checklist

Complete these in order:

- [ ] AWS backend deployed
- [ ] Endpoint URL saved in .env
- [ ] TTS test works (audio plays)
- [ ] STT test works (speech recognized)
- [ ] Claude Opus test passes
- [ ] WebSocket connects
- [ ] App launches with Live2D model
- [ ] Microphone input works
- [ ] Claude responds to questions
- [ ] Responses are spoken aloud
- [ ] Model can be dragged around screen

## 🎉 Congratulations!

Once all checkboxes are complete, you have:
- ✅ Working VTuber assistant
- ✅ Claude Opus AI brain
- ✅ Local TTS/STT for fast response
- ✅ Free-roaming desktop pet
- ✅ AWS cloud integration

## Optional Enhancements

### Change the Voice
Edit `conf.yaml`:
```yaml
edgeTTS:
  voice: en-US-AriaNeural  # Female
  # or: en-US-GuyNeural    # Male
  # or: ja-JP-NanamiNeural # Japanese
```

### Change the Personality
Edit `conf.yaml`:
```yaml
SYSTEM_PROMPT: |
  You are a cheerful anime-style VTuber assistant.
  You love helping with coding and creative tasks.
  Use emotes like (◕‿◕) and speak enthusiastically!
```

### Add More Animations
Check `static/desktop/models/default/motions/` for available animations

---

**Need Help?** 
- Check `OPUS_SETUP_GUIDE.md` for detailed instructions
- Review `quick-fix-guide.md` for common issues
- Test individual components with the test scripts