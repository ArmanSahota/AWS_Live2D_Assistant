# Frontend-Backend Connection Fix Guide

## Problem
The frontend (Electron app) and backend (Python server) are not connecting via WebSocket.

## Common Causes
1. **Port mismatch** - Server running on different port than frontend expects
2. **Server not running** - Python server needs to be started
3. **Stale port file** - `server_port.txt` contains wrong port
4. **Firewall blocking** - Windows Firewall blocking connection
5. **Multiple server instances** - Conflicting servers on different ports

## Quick Fix Steps

### Step 1: Run the Fix Script
```bash
cd LLM-Live2D-Desktop-Assitant-main
fix_connection.bat
```

This script will:
- Diagnose connection issues
- Find the correct server port
- Update `server_port.txt`
- Test WebSocket connection
- Start server if not running

### Step 2: Manual Verification
If the script doesn't work, follow these manual steps:

#### 1. Check if Server is Running
```bash
# In a new terminal
cd LLM-Live2D-Desktop-Assitant-main
python quick_connect_test.py
```

#### 2. Start Server if Needed
```bash
python server.py
```

Look for output like:
```
============================================================
Server is running: http://127.0.0.1:8000
WS endpoint:       ws://127.0.0.1:8000/client-ws
Health check:      http://127.0.0.1:8000/health
============================================================
```

Note the port number (e.g., 8000)

#### 3. Update Port File
Create/update `server_port.txt` with the correct port:
```bash
echo 8000 > server_port.txt
```

#### 4. Refresh Electron App
- Press `Ctrl+R` (Windows/Linux) or `Cmd+R` (Mac) in the Electron app
- Or restart the Electron app completely

### Step 3: Verify Connection
Open the browser console in Electron (F12) and check for:
- `[WEBSOCKET SIMPLIFIED] ✅ Found server on port 8000`
- `WebSocket connected successfully`

## Testing Connection

### Browser Console Test
Open browser console (F12) in Electron and run:
```javascript
// Test WebSocket connection
ws = new WebSocket('ws://localhost:8000/client-ws');
ws.onopen = () => console.log('✅ Connected!');
ws.onmessage = (e) => console.log('📥 Message:', e.data);
ws.onerror = (e) => console.error('❌ Error:', e);
ws.onclose = () => console.log('❌ Disconnected');
```

### Python Test
```python
# Run this to test connection
python test_websocket_audio.py
```

## Port Configuration

### Default Ports
The application tries these ports in order:
1. **8000-8002** - New port manager range
2. **1018-1025** - Legacy port range

### Setting a Specific Port
Set environment variable before starting server:
```bash
# Windows
set PORT=8000
python server.py

# Linux/Mac
PORT=8000 python server.py
```

## Troubleshooting

### Issue: "No server found on any port"
**Solution:**
```bash
# Start the server
cd LLM-Live2D-Desktop-Assitant-main
python server.py
```

### Issue: "WebSocket connection timeout"
**Possible causes:**
1. Firewall blocking - Add exception for Python
2. Wrong port in `server_port.txt`
3. Server crashed - Check server terminal for errors

**Solution:**
```bash
# Add firewall exception (Windows, run as admin)
netsh advfirewall firewall add rule name="VTuber Server" dir=in action=allow protocol=TCP localport=8000-8010

# Check server status
python quick_connect_test.py
```

### Issue: "Port already in use"
**Solution:**
```bash
# Windows - Find and kill process using port
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8000
kill -9 <PID>
```

### Issue: Multiple server instances
**Solution:**
1. Close all Python processes
2. Start fresh server instance
3. Update port file

## Files Involved

### Backend
- `server.py` - Main server file
- `port_config.py` - Port management
- `server_port.txt` - Stores current port

### Frontend
- `static/desktop/websocket.js` - WebSocket client
- `static/desktop.html` - Main HTML file
- `main.js` - Electron main process

## What Was Fixed

### 1. WebSocket Client (`websocket.js`)
- Extended port scanning to include 8000-8002
- Added more robust port discovery
- Improved error handling and logging

### 2. Server (`server.py`)
- Enhanced async message handling
- Added comprehensive logging
- Fixed WebSocket state checking
- Added test endpoint `/test-audio-payload`

### 3. Diagnostic Tools
- `diagnose_connection.py` - Full diagnostic
- `quick_connect_test.py` - Quick port finder
- `test_websocket_audio.py` - WebSocket tester
- `fix_connection.bat` - Automated fix script

## Expected Behavior

When properly connected:
1. Server starts and shows port number
2. `server_port.txt` contains correct port
3. Electron app connects automatically
4. Console shows "WebSocket connected successfully"
5. Audio and subtitles work properly

## Manual WebSocket Test

Create `test.html` and open in browser:
```html
<!DOCTYPE html>
<html>
<head><title>WS Test</title></head>
<body>
<h1>WebSocket Test</h1>
<div id="status">Connecting...</div>
<script>
const ws = new WebSocket('ws://localhost:8000/client-ws');
ws.onopen = () => {
    document.getElementById('status').textContent = '✅ Connected!';
    console.log('Connected');
};
ws.onmessage = (e) => console.log('Message:', e.data);
ws.onerror = (e) => {
    document.getElementById('status').textContent = '❌ Error';
    console.error('Error:', e);
};
</script>
</body>
</html>
```

## Summary

The connection issue is typically caused by port mismatch between frontend and backend. The fix involves:
1. Finding the correct server port
2. Updating `server_port.txt`
3. Ensuring WebSocket client checks the right ports
4. Refreshing the Electron app

Run `fix_connection.bat` for automated fix, or follow manual steps above.

## Need More Help?

If still having issues after trying all steps:
1. Check server logs for errors
2. Verify Python dependencies: `pip install -r requirements.txt`
3. Try running as Administrator
4. Disable antivirus temporarily for testing
5. Check if another application is using the ports

**Last Resort:**
```bash
# Complete reset
cd LLM-Live2D-Desktop-Assitant-main
rm server_port.txt
set PORT=8000
python server.py
```

Then refresh Electron app.