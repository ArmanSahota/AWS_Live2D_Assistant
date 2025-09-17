# Context Menu and Port Management Fixes

This document describes the fixes applied to resolve two critical issues in the LLM-Live2D-Desktop-Assistant application.

## Issue 1: Context Menu JavaScript Error

### Problem Description
The application was throwing a JavaScript error when users clicked on any UI elements:
```
TypeError: Error processing argument at index 3, conversion failure from a.popup (node:electron/js2c/browser_init:241655)
```

### Root Cause Analysis
After systematic debugging, the issue was identified in the `update-sensitivity` IPC handler at line 309 in `main.js`:

```javascript
const sensitivityMenu = contextMenu.items.find(item => item.label === 'Speech Sensitivity');
```

**The Problem**: `Menu.buildFromTemplate()` in Electron does not expose an `items` property that can be directly accessed. The Menu object created by this method doesn't have a publicly accessible `items` array.

### Solution Implemented
1. **Added currentSensitivity variable** to track the current sensitivity state
2. **Modified updateContextMenu() function** to use the tracked state when building the menu
3. **Replaced the problematic IPC handler** with a rebuild-based approach

#### Code Changes:

**Added variable declaration:**
```javascript
let currentSensitivity = 0.9; // Default sensitivity value (90%)
```

**Updated menu template to use current state:**
```javascript
{
  label: 'Speech Sensitivity',
  submenu: [
    { label: 'Very High (70%)', type: 'radio', checked: currentSensitivity === 0.7, click: () => setSensitivity(0.7) },
    { label: 'High (80%)', type: 'radio', checked: currentSensitivity === 0.8, click: () => setSensitivity(0.8) },
    { label: 'Medium (90%)', type: 'radio', checked: currentSensitivity === 0.9, click: () => setSensitivity(0.9) },
    { label: 'Low (95%)', type: 'radio', checked: currentSensitivity === 0.95, click: () => setSensitivity(0.95) },
    { label: 'Very Low (99%)', type: 'radio', checked: currentSensitivity === 0.99, click: () => setSensitivity(0.99) }
  ]
},
```

**Replaced the problematic IPC handler:**
```javascript
ipcMain.on('update-sensitivity', (event, value) => {
  console.log('[DEBUG] update-sensitivity called with value:', value);
  
  // FIXED: Instead of trying to access contextMenu.items (which doesn't exist),
  // we store the current sensitivity value and rebuild the menu with the correct checked state
  currentSensitivity = value;
  
  // Rebuild the context menu with the updated sensitivity
  updateContextMenu().then(() => {
    console.log('[DEBUG] Context menu updated with new sensitivity:', value);
  }).catch(error => {
    console.error('[ERROR] Failed to update context menu:', error);
  });
});
```

### Testing Results
- ✅ Application starts without errors
- ✅ Context menu displays correctly
- ✅ All menu interactions work properly
- ✅ No more JavaScript errors when clicking UI elements

## Issue 2: Inconsistent Port Management

### Problem Description
The application was using inconsistent ports between frontend and backend, with ports changing on each restart (e.g., backend using port 1029, frontend using port 1030), making development and testing difficult.

### Root Cause Analysis
1. **Inconsistent port configuration**: Backend used `SERVER_PORT=1018` from `.env` but then searched for available ports starting from `1025`
2. **No proper port cleanup**: Ports weren't being released properly when the app shut down
3. **No centralized port management**: Frontend and backend managed ports independently

### Solution Implemented
Created a centralized port management system with proper cleanup mechanisms.

#### New Port Manager (`port_config.py`)

**Key Features:**
- **Centralized Configuration**: Single source of truth for port management
- **Intelligent Port Selection**: Tries preferred port first, then searches nearby ports
- **Proper Cleanup**: Automatic port release on application shutdown
- **Signal Handling**: Handles SIGINT and SIGTERM for graceful shutdown
- **Environment Integration**: Respects `SERVER_PORT` and `PORT` environment variables

**Usage:**
```python
from port_config import get_available_port, cleanup_ports, get_current_port

# Get an available port (tries 1018 first, then nearby ports)
port = get_available_port()

# Get a specific preferred port
port = get_available_port(preferred_port=1018)

# Cleanup all allocated ports
cleanup_ports()
```

#### Updated Server Integration
Modified `server.py` to use the new port manager:

```python
from port_config import get_available_port, cleanup_ports, get_current_port

# In the run method:
actual_port = get_available_port(port)
atexit.register(cleanup_ports)
```

### Configuration Updates
The `.env` file already contains the correct configuration:
```env
# Local Server Configuration
SERVER_PORT=1018
WEBSOCKET_PORT=1018
```

### Benefits of the New System
1. **Consistent Ports**: Both frontend and backend will use the same port (1018) when available
2. **Proper Cleanup**: Ports are automatically released when the application shuts down
3. **Fallback Strategy**: If 1018 is in use, it tries nearby ports (1019, 1020, etc.)
4. **Signal Handling**: Gracefully handles Ctrl+C and other shutdown signals
5. **Environment Flexibility**: Can be configured via environment variables
6. **Logging**: Clear logging of port allocation and cleanup activities

### Testing the Port Management
To test the new port management:

1. **Start the application**: `npm start`
2. **Check the logs**: Should show "Using preferred port: 1018" or "Found available port: XXXX"
3. **Stop the application**: Use Ctrl+C
4. **Check cleanup**: Should show "Cleaning up ports: [XXXX]"
5. **Restart immediately**: Should be able to use the same port again

## Summary

Both fixes address fundamental issues that were affecting the application's stability and usability:

1. **Context Menu Fix**: Resolves JavaScript errors that prevented proper UI interaction
2. **Port Management Fix**: Ensures consistent, predictable port usage with proper cleanup

These improvements make the development and testing process much more reliable and user-friendly.

## Files Modified

### Context Menu Fix:
- `main.js`: Added currentSensitivity tracking and fixed IPC handler

### Port Management Fix:
- `port_config.py`: New centralized port management system
- `server.py`: Updated to use new port manager
- `.env`: Already contained correct port configuration

## Future Improvements

1. **Frontend Integration**: Update frontend code to also use the centralized port manager
2. **Health Checks**: Add port health checking mechanisms
3. **Port Persistence**: Consider persisting the last used port for even more consistency
4. **Configuration UI**: Add UI controls for port configuration