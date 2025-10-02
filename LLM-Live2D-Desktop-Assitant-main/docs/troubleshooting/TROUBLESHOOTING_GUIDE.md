# React + Vite Migration - Troubleshooting Guide

## 🚨 Common Issues & Solutions

### Issue 1: Electron App Not Opening

**Symptoms:**
- `npm run dev` runs but Electron window doesn't appear
- Backend starts on wrong port (8002 instead of 8000)
- Console shows "Port 8000 is in use"

**Root Cause:**
Port 8000 is occupied by another process, causing backend to use fallback port, breaking Vite proxy.

**Solution:**
```bash
# 1. Find process using port 8000
netstat -ano | findstr :8000

# 2. Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F

# 3. Verify port is free (should show no output)
netstat -ano | findstr :8000

# 4. Try development again
npm run dev
```

### Issue 2: Dependencies Not Installed

**Symptoms:**
- "Cannot find module" errors
- Scripts fail to run
- Missing node_modules directories

**Solution:**
```bash
cd LLM-Live2D-Desktop-Assitant-main
npm run install:all
```

### Issue 3: Frontend Not Starting

**Symptoms:**
- Vite dev server fails to start
- Port 5173 errors
- Frontend dependencies missing

**Solution:**
```bash
# Install frontend dependencies
cd LLM-Live2D-Desktop-Assitant-main/frontend
npm install

# Test frontend separately
npm run dev
```

### Issue 4: Backend Connection Errors

**Symptoms:**
- API calls fail in diagnostics panel
- WebSocket connection errors
- CORS errors in browser console

**Solution:**
```bash
# Test backend separately
cd LLM-Live2D-Desktop-Assitant-main
python server.py --port 8000

# Verify backend health
curl http://localhost:8000/health
```

### Issue 5: Live2D Libraries Not Loading

**Symptoms:**
- "PIXI is not defined" errors
- Live2D model fails to load
- Canvas shows error messages

**Solution:**
The Live2D libraries need to be loaded in the React app. Add to `frontend/public/index.html`:

```html
<script src="/libs/live2dcubismcore.min.js"></script>
<script src="/libs/live2d.min.js"></script>
<script src="/libs/pixi.min.js"></script>
<script src="/libs/index.min.js"></script>
```

## 🔧 Manual Startup (If npm run dev Fails)

### Step-by-Step Manual Startup:

```bash
cd LLM-Live2D-Desktop-Assitant-main

# Terminal 1: Start backend
python server.py --port 8000
# Wait for: "Server is running: http://0.0.0.0:8000"

# Terminal 2: Start frontend  
cd frontend
npm run dev
# Wait for: "Local: http://localhost:5173/"

# Terminal 3: Start Electron
npm run electron:dev
# Electron window should open
```

## 🧪 Validation & Testing

### Run All Validation Scripts:
```bash
cd LLM-Live2D-Desktop-Assitant-main

# Test all phases
node tests/phase1-validation.js  # Backend (should pass 5/5)
node tests/phase2-validation.js  # Frontend (should pass 9/9)
node tests/phase3-validation.js  # Components (should pass 5/5)
node tests/phase4-validation.js  # Electron (should pass 6/6)
```

### Debug Development Startup:
```bash
node debug-dev-startup.js
```

## 🌐 Browser Testing

### Direct Frontend Access:
- **React App**: http://localhost:5173
- **Diagnostics Panel**: Should appear in top-right corner
- **API Tests**: Click buttons in diagnostics panel

### Direct Backend Access:
- **Health Check**: http://localhost:8000/health
- **Mock TTS**: POST http://localhost:8000/api/tts/mock
- **Mock STT**: POST http://localhost:8000/api/stt/mock

## 🔍 Common Error Messages

### "Cannot find module 'react'"
**Solution**: Install frontend dependencies
```bash
cd frontend && npm install
```

### "ECONNREFUSED localhost:8000"
**Solution**: Backend not running or wrong port
```bash
python server.py --port 8000
```

### "WebSocket connection failed"
**Solution**: Check backend WebSocket endpoint
```bash
# Test WebSocket echo
wscat -c ws://localhost:8000/ws/echo
```

### "Live2D model failed to load"
**Solution**: Check model path and libraries
- Verify `/desktop/models/default/default.model3.json` exists
- Ensure Live2D libraries are loaded
- Check browser console for specific errors

## 📊 Expected Behavior

### ✅ Successful Development Startup:

1. **Backend Output:**
```
Server is running: http://0.0.0.0:8000
WS endpoint: ws://0.0.0.0:8000/client-ws
Health check: http://0.0.0.0:8000/health
```

2. **Frontend Output:**
```
VITE v5.0.8 ready in 1234 ms
➜ Local: http://localhost:5173/
➜ Network: use --host to expose
```

3. **Electron Output:**
```
Loading React app from Vite dev server: http://localhost:5173
```

4. **Browser Behavior:**
- Electron window opens with React app
- Diagnostics panel visible in top-right
- Live2D placeholder or model loads
- All diagnostic tests pass

## 🛠️ Advanced Troubleshooting

### Check Process Status:
```bash
# Check all processes on relevant ports
netstat -ano | findstr :8000
netstat -ano | findstr :5173

# Check if Python is available
python --version

# Check if Node.js is available  
node --version
npm --version
```

### Reset Everything:
```bash
# Kill all related processes
taskkill /F /IM python.exe
taskkill /F /IM node.exe
taskkill /F /IM electron.exe

# Clean install
rm -rf node_modules frontend/node_modules
npm run install:all

# Try again
npm run dev
```

## 📞 Support

If issues persist:

1. **Check all validation scripts pass**
2. **Verify all dependencies installed**
3. **Ensure ports 8000 and 5173 are free**
4. **Try manual startup process**
5. **Check browser console for errors**

The migration is complete and functional - most issues are related to environment setup rather than the migration code itself.