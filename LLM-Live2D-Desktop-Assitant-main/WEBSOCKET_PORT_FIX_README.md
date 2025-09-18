# WebSocket Port Configuration Fix

## Problem Diagnosed

The project had a **WebSocket handshake error** caused by port mismatches between the Python server (`server.py`) and the frontend WebSocket client (`websocket.js`).

### Root Causes Identified:

1. **Server Dynamic Port Allocation**: `server.py` uses dynamic port finding starting from 1018, but may bind to different ports (1019, 1020, etc.) if 1018 is occupied
2. **Frontend Port Hardcoding**: `websocket.js` had hardcoded port list `[1018, 1025, 1026, 1027, 1028, 1029, 1030]` that didn't match server's dynamic allocation logic
3. **Configuration Mismatch**: `conf.yaml` sets both `SERVER_PORT: 1018` and `WEBSOCKET_PORT: 1018`, but server ignores `WEBSOCKET_PORT`
4. **Port Manager Logic Gap**: `port_config.py` searches forward from base port but frontend didn't follow the same search pattern
5. **No Communication**: No mechanism for server to communicate actual port to frontend

## Solution Implemented

### 1. Server-Side Changes (`server.py`)

**Added port file communication:**
```python
# WEBSOCKET PORT FIX: Write actual port to a file for frontend to read
port_file_path = os.path.join(os.path.dirname(__file__), 'server_port.txt')
try:
    with open(port_file_path, 'w') as f:
        f.write(str(actual_port))
    logger.info(f"Server port {actual_port} written to {port_file_path}")
except Exception as e:
    logger.warning(f"Could not write port file: {e}")
```

**Enhanced logging:**
- Server now clearly displays which port it's actually using
- Logs when port differs from requested port

### 2. Frontend Changes (`websocket.js`)

**Added intelligent port discovery:**
```javascript
async function readServerPortFromFile() {
    try {
        // Try to read the port file written by the server
        const response = await fetch('/server_port.txt').catch(() => null);
        if (response && response.ok) {
            const portText = await response.text();
            const port = parseInt(portText.trim());
            if (!isNaN(port) && port > 0) {
                console.log(`[WEBSOCKET PORT FIX] Found server port from file: ${port}`);
                return port;
            }
        }
    } catch (e) {
        console.log(`[WEBSOCKET PORT FIX] Could not read port file: ${e.message}`);
    }
    return null;
}
```

**Improved port search pattern:**
- First tries to read actual port from `server_port.txt`
- Falls back to systematic port discovery: `[1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030]`
- Enhanced logging throughout the connection process

### 3. Configuration Documentation (`conf.yaml`)

**Added clear comments:**
```yaml
# Server settings - WEBSOCKET PORT FIX
# Both server and WebSocket use the same port for consistency
# The server will automatically find an available port starting from this base port
# Frontend will read the actual port from server_port.txt file
SERVER_PORT: 1018
WEBSOCKET_PORT: 1018  # This is kept for backward compatibility but server uses SERVER_PORT
```

## How It Works

1. **Server Startup**: 
   - Server tries to bind to port 1018 (from `SERVER_PORT` config)
   - If 1018 is occupied, it finds next available port (1019, 1020, etc.)
   - Writes actual port to `server_port.txt` file
   - Logs the actual port being used

2. **Frontend Connection**:
   - Frontend first tries to read `server_port.txt` via HTTP request
   - If successful, verifies the port with a health check
   - If file method fails, falls back to systematic port discovery
   - Connects to WebSocket using the discovered port

3. **Validation**:
   - Enhanced logging shows exactly which port is being used
   - Both server and client log successful connections with port numbers

## Testing the Fix

### 1. Start the Server
```bash
cd LLM-Live2D-Desktop-Assitant-main
python server.py
```

**Expected Output:**
```
============================================================
Server is running: http://0.0.0.0:1018
WS endpoint:       ws://0.0.0.0:1018/client-ws
Health check:      http://0.0.0.0:1018/health
Static files:      http://0.0.0.0:1018/static/
WEBSOCKET PORT FIX: Frontend should connect to port 1018
============================================================
```

### 2. Start the Frontend
```bash
npm start
```

**Expected Console Output:**
```
[WEBSOCKET PORT FIX] Starting WebSocket connection process...
[WEBSOCKET PORT FIX] Found server port from file: 1018
[WEBSOCKET PORT FIX] Verified server on port 1018 from file
[WEBSOCKET PORT FIX] Attempting WebSocket connection to ws://localhost:1018/client-ws
[WEBSOCKET PORT FIX] WebSocket connected successfully to port 1018
```

### 3. Verify Connection
- Check browser console for WebSocket connection success
- Look for `server_port.txt` file in project root
- Verify no "WebSocket handshake failed" errors

## Port Conflict Scenarios

### Scenario 1: Port 1018 Available
- Server binds to 1018
- Frontend reads 1018 from file
- Direct connection succeeds

### Scenario 2: Port 1018 Occupied
- Server finds next available port (e.g., 1019)
- Server writes 1019 to `server_port.txt`
- Frontend reads 1019 from file
- Connection succeeds on correct port

### Scenario 3: File Method Fails
- Frontend can't read `server_port.txt`
- Falls back to port discovery: 1018, 1019, 1020...
- Finds server and connects

## Files Modified

1. **`server.py`** - Added port file writing and enhanced logging
2. **`static/desktop/websocket.js`** - Added intelligent port discovery
3. **`conf.yaml`** - Added documentation comments
4. **`WEBSOCKET_PORT_FIX_README.md`** - This documentation file

## Troubleshooting

### If WebSocket Still Fails:

1. **Check server logs** for actual port being used
2. **Verify `server_port.txt`** exists and contains correct port
3. **Check browser console** for detailed connection logs
4. **Test health endpoint** manually: `http://localhost:PORT/health`
5. **Verify no firewall** blocking the ports

### Common Issues:

- **File permissions**: Ensure server can write `server_port.txt`
- **CORS issues**: Server has CORS enabled for all origins
- **Port conflicts**: Check if other services are using the ports
- **Timing issues**: Frontend waits for server startup in development mode

## Benefits of This Fix

✅ **Automatic Port Discovery**: No more manual port configuration  
✅ **Robust Fallback**: Multiple discovery methods ensure connection  
✅ **Clear Logging**: Easy to diagnose connection issues  
✅ **Backward Compatible**: Existing configurations still work  
✅ **Development Friendly**: Works in both dev and production modes  

The WebSocket handshake errors should now be completely resolved!