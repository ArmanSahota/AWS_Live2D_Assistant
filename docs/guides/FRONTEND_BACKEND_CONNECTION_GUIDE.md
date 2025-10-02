# Frontend-Backend Connection Troubleshooting Guide

## Problem
The frontend (Electron app) is not connecting to the backend (Python server) properly. The server is running on port 1018 while the frontend is trying to use port 1020.

## Root Cause
Multiple backend instances may be running on different ports (1018, 1019, 1020), which is confusing the frontend's port discovery mechanism. The port configuration needs to be consistent between the backend and frontend.

## Solution

### Step 1: Run the Diagnostic Tool
First, check what's currently running:
```bash
node test_connection_diagnostic.js
```

This will show you:
- Which ports have active backend servers
- If the server_port.txt file exists and what port it contains
- Recommendations based on the current state

### Step 2: Clean Everything Up
Run the fix script:
```bash
fix_frontend_backend_connection.bat
```

This script will:
1. Kill all Python processes
2. Kill all Electron processes
3. Delete the port file
4. Set up environment variables to ensure consistent port usage (1018)

Or manually:
1. Close all terminals
2. Kill all Python processes: `taskkill /F /IM python.exe`
3. Kill all Electron processes: `taskkill /F /IM electron.exe`
4. Delete the port file: `del LLM-Live2D-Desktop-Assitant-main\server_port.txt`
5. Create/update .env file with SERVER_PORT=1018 and WEBSOCKET_PORT=1018

### Step 2: Start Backend First
1. Open a new terminal
2. Navigate to the project directory:
   ```bash
   cd LLM-Live2D-Desktop-Assitant-main
   ```
3. Start the backend:
   ```bash
   python server.py
   ```
4. **IMPORTANT**: Wait for the server to fully start. You should see:
   ```
   ============================================================
   Server is running: http://0.0.0.0:1018
   WS endpoint:       ws://0.0.0.0:1018/client-ws
   Health check:      http://0.0.0.0:1018/health
   Static files:      http://0.0.0.0:1018/static/
   ============================================================
   ```
5. Note the port number (usually 1018)

### Step 3: Start Frontend After Backend
1. Open a **new** terminal (keep the backend running)
2. Navigate to the project directory:
   ```bash
   cd LLM-Live2D-Desktop-Assitant-main
   ```
3. Start the Electron app:
   ```bash
   npm start
   ```

### Step 4: Verify Connection
1. In the Electron app, press `Ctrl+Shift+I` to open Developer Tools
2. Go to the Console tab
3. Look for these messages:
   - `[WEBSOCKET PORT FIX] Found server port from file: 1018`
   - `WebSocket connected successfully`
   - `Connection established`

## Alternative: Use Web Interface
If the Electron app continues to have issues, you can use the web interface:

1. Start the backend with web mode:
   ```bash
   python server.py --web
   ```
2. Open your browser to: `http://localhost:1018`
3. The web interface will automatically connect to the backend

## Common Issues

### Issue 1: "Port already in use"
- Solution: Another process is using the port. Run the cleanup script or manually kill Python processes.

### Issue 2: "WebSocket connection failed"
- Check Windows Firewall isn't blocking the connection
- Make sure you started the backend BEFORE the frontend
- Check the backend console for errors

### Issue 3: Multiple backend instances
- This happens when you start `python server.py` multiple times without stopping the previous instance
- Always stop the backend with `Ctrl+C` before starting a new one

## Port Discovery Mechanism
The frontend uses this order to find the backend:
1. Reads `server_port.txt` file (written by backend)
2. Tests common ports (1018-1030)
3. Defaults to 1018 if nothing found

## Quick Test
To quickly test if the backend is running:
```bash
node test_connection_diagnostic.js
```

This diagnostic tool will:
- Scan ports 1018-1030 for active backend servers
- Check if server_port.txt exists and what port it contains
- Provide color-coded output showing which ports are active
- Give recommendations based on what it finds

## Best Practices
1. Always start backend first, frontend second
2. Use only ONE backend instance at a time
3. Check the backend console for the actual port being used
4. If in doubt, restart everything cleanly

## Still Having Issues?
1. Check the backend logs for errors
2. Make sure all dependencies are installed:
   - Backend: `pip install -r requirements.txt`
   - Frontend: `npm install`
3. Try the web interface as an alternative
4. Check that your antivirus isn't blocking the connection
