# WebSocket Connection Fix

This document explains the implementation of a robust WebSocket connection between the Electron frontend and Python backend server.

## Problem

Previously, the frontend Electron app and the backend Python server were not consistently using the same WebSocket connection. The frontend had to discover the backend's port through various methods:

1. Reading from a `server_port.txt` file
2. Trying a range of possible ports (1018-1030)
3. Defaulting to port 1018 if no server was found

This approach was unreliable and could lead to connection issues, especially if multiple instances of the application were running or if other services were using the same ports.

## Solution

The solution implements a direct communication channel between the main Electron process and the renderer process to share the backend port:

1. The main process detects the backend server's port from the server's console output
2. The port is stored in a global variable and shared with the renderer process
3. The renderer process uses this port to establish a WebSocket connection
4. Fallback mechanisms are maintained for robustness

## Implementation Details

### 1. Main Process (main.js)

The main Electron process now:
- Parses the backend server's console output to detect the port
- Stores the port in a global variable (`global.backendPort`)
- Exposes an IPC handler for the renderer to get the port
- Sends the port to the renderer when detected

```javascript
// Parse backend output for port detection
backendProcess.stdout.on('data', (data) => {
  const output = data.toString();
  const portMatch = output.match(/Server is running: http:\/\/[^:]+:(\d+)/);
  if (portMatch && portMatch[1]) {
    const serverPort = parseInt(portMatch[1]);
    global.backendPort = serverPort;
    
    // Send to renderer if window exists
    if (mainWindow) {
      mainWindow.webContents.send('backend-port', serverPort);
    }
  }
});

// IPC handler for renderer to get the port
ipcMain.handle('get-backend-port', () => {
  return global.backendPort || null;
});
```

### 2. Preload Script (preload.js)

The preload script exposes APIs for the renderer to:
- Get the backend port from the main process
- Listen for port detection events

```javascript
// Backend port communication
getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
onBackendPortDetected: (callback) => ipcRenderer.on('backend-port', (event, port) => callback(port)),
```

### 3. WebSocket Client (websocket.js)

The WebSocket client now:
- Listens for port detection events from the main process
- Tries to get the port from the main process first
- Falls back to file reading and port discovery if needed
- Reconnects if a different port is detected

```javascript
// Listen for backend port detection from main process
if (window.electronAPI && window.electronAPI.onBackendPortDetected) {
    window.electronAPI.onBackendPortDetected((port) => {
        detectedPort = port;
        
        // Reconnect if needed
        if (ws && ws.readyState === WebSocket.OPEN && ws._port !== port) {
            ws.close();
            connectWebSocket();
        }
    });
}

async function getServerPort() {
    // First try to get the port from the main process
    if (window.electronAPI && window.electronAPI.getBackendPort) {
        const port = await window.electronAPI.getBackendPort();
        if (port) {
            return port;
        }
    }
    
    // Fallback mechanisms...
}
```

## Testing

To test the WebSocket connection:

1. Run the `test_websocket_connection.bat` script
2. Check the console output for:
   - `[Backend] Detected server running on port: XXXX` - Shows the backend port was detected
   - `[WEBSOCKET PORT FIX] Using port from main process: XXXX` - Shows the frontend is using the correct port
   - `WebSocket connected successfully` - Confirms the connection was established

## Benefits

- **Reliability**: Direct communication between main and renderer processes ensures consistent port usage
- **Robustness**: Fallback mechanisms are maintained for edge cases
- **Flexibility**: The system can adapt if the backend port changes
- **Transparency**: Clear logging makes it easy to debug connection issues

## Future Improvements

- Add a configuration option to specify a fixed port
- Implement a heartbeat mechanism to detect disconnections
- Add reconnection attempts with exponential backoff
