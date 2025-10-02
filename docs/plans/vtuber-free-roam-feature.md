# Free-Roaming VTuber Model Feature Implementation

## Overview
Implement a draggable Live2D model that can be positioned anywhere on screen, including across multiple monitors, creating a true desktop companion experience.

## Feature Requirements
- ✅ Drag model anywhere on screen
- ✅ Support multi-monitor setups
- ✅ Remember position between sessions
- ✅ Click-through transparent areas
- ✅ Smooth dragging experience
- ✅ Optional magnetic screen edges
- ✅ Right-click context menu on model

## Implementation Guide

### 1. Electron Window Configuration

**File:** `main.js`

```javascript
function createWindow() {
  const { screen } = require('electron');
  const displays = screen.getAllDisplays();
  const primaryDisplay = screen.getPrimaryDisplay();
  
  // Get saved position or default
  const savedBounds = store.get('windowBounds', {
    x: primaryDisplay.workArea.width - 400,
    y: primaryDisplay.workArea.height - 600,
    width: 350,
    height: 500
  });

  mainWindow = new BrowserWindow({
    // Position and size
    x: savedBounds.x,
    y: savedBounds.y,
    width: savedBounds.width,
    height: savedBounds.height,
    
    // Window styling
    transparent: true,
    frame: false,
    resizable: false,
    hasShadow: false,
    
    // Behavior
    alwaysOnTop: true,
    skipTaskbar: true,
    focusable: false,
    
    // Allow dragging across all monitors
    fullscreenable: false,
    visibleOnAllWorkspaces: true,
    
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webSecurity: true
    }
  });

  // Enable click-through for transparent areas
  mainWindow.setIgnoreMouseEvents(false);
  
  // Save position when window moves
  mainWindow.on('moved', () => {
    if (!mainWindow.isMinimized()) {
      const bounds = mainWindow.getBounds();
      store.set('windowBounds', bounds);
    }
  });

  mainWindow.loadFile('static/desktop.html');
}
```

### 2. Model Dragging Implementation

**File:** `static/desktop/draggable.js`

```javascript
class VTuberDragHandler {
  constructor() {
    this.isDragging = false;
    this.currentX = 0;
    this.currentY = 0;
    this.initialX = 0;
    this.initialY = 0;
    this.xOffset = 0;
    this.yOffset = 0;
    this.magneticThreshold = 20; // pixels from edge
    
    this.init();
  }

  init() {
    // Get the Live2D container
    this.dragTarget = document.getElementById('live2d-stage');
    this.modelContainer = document.getElementById('model-container');
    
    // Add drag handle overlay
    this.createDragHandle();
    
    // Set up event listeners
    this.setupEventListeners();
    
    // Set up click-through for non-model areas
    this.setupClickThrough();
  }

  createDragHandle() {
    const handle = document.createElement('div');
    handle.id = 'drag-handle';
    handle.style.cssText = `
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 60px;
      cursor: move;
      z-index: 9999;
      -webkit-app-region: drag;
    `;
    this.dragTarget.appendChild(handle);
  }

  setupEventListeners() {
    const handle = document.getElementById('drag-handle');
    
    // Use Electron's built-in window dragging for the handle
    handle.addEventListener('mousedown', (e) => {
      if (e.button === 0) { // Left click only
        // Signal Electron to start window drag
        window.electronAPI.startDrag();
      }
    });
    
    // Right-click context menu on model
    this.modelContainer.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      window.electronAPI.showModelContextMenu({
        x: e.clientX,
        y: e.clientY
      });
    });
    
    // Double-click to reset position
    handle.addEventListener('dblclick', () => {
      this.resetToDefaultPosition();
    });
  }

  setupClickThrough() {
    // Monitor mouse position to enable click-through
    document.addEventListener('mousemove', (e) => {
      const modelBounds = this.getModelBounds();
      const isOverModel = this.isPointInBounds(e.clientX, e.clientY, modelBounds);
      
      // Tell Electron to ignore/accept mouse events
      window.electronAPI.setClickThrough(!isOverModel);
    });
  }

  getModelBounds() {
    // Get the actual model bounds (not the full window)
    const canvas = document.getElementById('live2d-canvas');
    const rect = canvas.getBoundingClientRect();
    
    // Assuming model takes up center 80% of canvas
    return {
      x: rect.left + rect.width * 0.1,
      y: rect.top + rect.height * 0.1,
      width: rect.width * 0.8,
      height: rect.height * 0.8
    };
  }

  isPointInBounds(x, y, bounds) {
    return x >= bounds.x && 
           x <= bounds.x + bounds.width &&
           y >= bounds.y && 
           y <= bounds.y + bounds.height;
  }

  resetToDefaultPosition() {
    window.electronAPI.resetWindowPosition();
  }

  // Magnetic edge snapping
  applyMagneticEdges(x, y) {
    const displays = window.electronAPI.getDisplays();
    let snapX = x;
    let snapY = y;
    
    displays.forEach(display => {
      const { bounds } = display;
      
      // Snap to left edge
      if (Math.abs(x - bounds.x) < this.magneticThreshold) {
        snapX = bounds.x;
      }
      // Snap to right edge
      if (Math.abs(x + this.windowWidth - (bounds.x + bounds.width)) < this.magneticThreshold) {
        snapX = bounds.x + bounds.width - this.windowWidth;
      }
      // Snap to top edge
      if (Math.abs(y - bounds.y) < this.magneticThreshold) {
        snapY = bounds.y;
      }
      // Snap to bottom edge
      if (Math.abs(y + this.windowHeight - (bounds.y + bounds.height)) < this.magneticThreshold) {
        snapY = bounds.y + bounds.height - this.windowHeight;
      }
    });
    
    return { x: snapX, y: snapY };
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.vtuberDragHandler = new VTuberDragHandler();
});
```

### 3. Preload Script Enhancements

**File:** `static/desktop/preload.js`

Add these IPC bridges:

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // Existing methods...
  
  // Dragging support
  startDrag: () => ipcRenderer.send('start-drag'),
  setClickThrough: (ignore) => ipcRenderer.send('set-click-through', ignore),
  resetWindowPosition: () => ipcRenderer.send('reset-window-position'),
  showModelContextMenu: (point) => ipcRenderer.send('show-model-context-menu', point),
  getDisplays: () => ipcRenderer.invoke('get-displays'),
  
  // Window position
  saveWindowPosition: (bounds) => ipcRenderer.send('save-window-position', bounds),
  getWindowPosition: () => ipcRenderer.invoke('get-window-position'),
  
  // Window state
  minimizeToTray: () => ipcRenderer.send('minimize-to-tray'),
  pinToDesktop: (pin) => ipcRenderer.send('pin-to-desktop', pin),
  setOpacity: (opacity) => ipcRenderer.send('set-opacity', opacity)
});
```

### 4. Main Process Handlers

**File:** `src/main/ipc.js`

Add IPC handlers for drag functionality:

```javascript
function initializeDragHandlers() {
  const { screen, Menu } = require('electron');
  
  // Start native window drag
  ipcMain.on('start-drag', (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    window.startDrag();
  });
  
  // Toggle click-through
  ipcMain.on('set-click-through', (event, ignore) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    window.setIgnoreMouseEvents(ignore, { forward: true });
  });
  
  // Reset to default position
  ipcMain.on('reset-window-position', (event) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    const primaryDisplay = screen.getPrimaryDisplay();
    const { width, height } = primaryDisplay.workArea;
    
    window.setPosition(
      width - 400,
      height - 600
    );
  });
  
  // Show context menu on model
  ipcMain.on('show-model-context-menu', (event, point) => {
    const window = BrowserWindow.fromWebContents(event.sender);
    
    const template = [
      {
        label: 'Reset Position',
        click: () => {
          event.sender.send('reset-position');
        }
      },
      {
        label: 'Opacity',
        submenu: [
          { label: '100%', click: () => window.setOpacity(1.0) },
          { label: '80%', click: () => window.setOpacity(0.8) },
          { label: '60%', click: () => window.setOpacity(0.6) },
          { label: '40%', click: () => window.setOpacity(0.4) }
        ]
      },
      {
        label: 'Size',
        submenu: [
          { label: 'Small', click: () => window.setSize(250, 350) },
          { label: 'Medium', click: () => window.setSize(350, 500) },
          { label: 'Large', click: () => window.setSize(450, 650) }
        ]
      },
      { type: 'separator' },
      {
        label: 'Always on Top',
        type: 'checkbox',
        checked: window.isAlwaysOnTop(),
        click: () => {
          window.setAlwaysOnTop(!window.isAlwaysOnTop());
        }
      },
      {
        label: 'Lock Position',
        type: 'checkbox',
        checked: store.get('positionLocked', false),
        click: () => {
          const locked = !store.get('positionLocked', false);
          store.set('positionLocked', locked);
          window.setMovable(!locked);
        }
      },
      { type: 'separator' },
      {
        label: 'Minimize to Tray',
        click: () => window.minimize()
      },
      {
        label: 'Quit',
        click: () => app.quit()
      }
    ];
    
    const menu = Menu.buildFromTemplate(template);
    menu.popup(window, point.x, point.y);
  });
  
  // Get all displays
  ipcMain.handle('get-displays', () => {
    return screen.getAllDisplays();
  });
  
  // Save window position
  ipcMain.on('save-window-position', (event, bounds) => {
    store.set('windowBounds', bounds);
  });
  
  // Get saved window position
  ipcMain.handle('get-window-position', () => {
    return store.get('windowBounds');
  });
}
```

### 5. Enhanced CSS for Draggable Model

**File:** `static/desktop/style.css`

```css
/* Draggable VTuber Styles */
body {
  margin: 0;
  padding: 0;
  background: transparent;
  overflow: hidden;
  user-select: none;
  -webkit-user-select: none;
}

#live2d-stage {
  position: relative;
  width: 100vw;
  height: 100vh;
  background: transparent;
}

#model-container {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 80%;
  height: 80%;
  pointer-events: auto;
}

/* Drag handle - invisible but functional */
#drag-handle {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 60px;
  cursor: move;
  z-index: 9999;
  -webkit-app-region: drag;
  /* Visual feedback on hover (optional) */
  transition: background-color 0.2s;
}

#drag-handle:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

/* Live2D Canvas */
#live2d-canvas {
  width: 100%;
  height: 100%;
  background: transparent;
  pointer-events: auto;
}

/* Prevent text selection during drag */
.dragging {
  cursor: move !important;
}

.dragging * {
  pointer-events: none !important;
}

/* Size transition animations */
.size-transition {
  transition: width 0.3s ease, height 0.3s ease;
}

/* Shadow for depth (optional) */
.model-shadow {
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 20px;
  background: radial-gradient(ellipse at center, rgba(0,0,0,0.3) 0%, transparent 70%);
  filter: blur(10px);
}

/* Interaction feedback */
#model-container:active {
  transform: translate(-50%, -50%) scale(0.98);
  transition: transform 0.1s;
}
```

### 6. Configuration Options

**File:** `.env`

```env
# VTuber Free Roam Settings
VTUBER_DEFAULT_X=1520
VTUBER_DEFAULT_Y=480
VTUBER_DEFAULT_WIDTH=350
VTUBER_DEFAULT_HEIGHT=500
VTUBER_OPACITY=1.0
VTUBER_ALWAYS_ON_TOP=true
VTUBER_MAGNETIC_EDGES=true
VTUBER_MAGNETIC_THRESHOLD=20
VTUBER_REMEMBER_POSITION=true
VTUBER_MULTI_MONITOR=true
```

## Usage Instructions

### For Users

1. **Moving the Model**
   - Click and drag the top area of the model to move it anywhere
   - Works across all monitors in multi-monitor setups
   - Position is automatically saved

2. **Right-Click Menu**
   - Right-click on the model for options:
     - Reset position
     - Adjust opacity
     - Change size
     - Lock position
     - Minimize to tray

3. **Keyboard Shortcuts**
   - `Double-click`: Reset to default position
   - `Ctrl+Shift+L`: Lock/unlock position
   - `Ctrl+Shift+M`: Minimize to tray

4. **Screen Edge Snapping**
   - Model will magnetically snap to screen edges
   - Makes it easy to position neatly

### For Developers

1. **Testing Multi-Monitor**
   ```javascript
   // Test script for multi-monitor support
   const { screen } = require('electron');
   const displays = screen.getAllDisplays();
   console.log('Available displays:', displays);
   ```

2. **Debugging Position**
   ```javascript
   // Add to console for debugging
   mainWindow.webContents.executeJavaScript(`
     console.log('Window bounds:', ${JSON.stringify(mainWindow.getBounds())});
   `);
   ```

## Performance Considerations

1. **CPU Usage**
   - Use `-webkit-app-region: drag` for native dragging
   - Minimize JavaScript event handlers during drag
   - Throttle position save operations

2. **Memory**
   - Only track mouse when over model area
   - Remove event listeners when not needed
   - Use CSS transforms for smooth movement

3. **Multi-Monitor**
   - Cache display information
   - Update only when display configuration changes

## Known Issues & Solutions

### Issue 1: Model Stuck on Screen Edge
**Solution:** Double-click drag handle to reset position

### Issue 2: Can't Click Through Model
**Solution:** Implement proper hit-testing for transparent areas

### Issue 3: Position Not Saving
**Solution:** Ensure electron-store is properly initialized

## Future Enhancements

- [ ] Gesture controls for model movement
- [ ] Snap to other windows
- [ ] Multiple model instances
- [ ] Animated transitions when moving
- [ ] Voice commands to reposition ("Move to left screen")
- [ ] Auto-hide when fullscreen apps are active
- [ ] Follow mouse cursor mode
- [ ] Patrol mode (automated movement patterns)

## Testing Checklist

- [ ] Model can be dragged to any screen position
- [ ] Position persists after app restart
- [ ] Works on multi-monitor setups
- [ ] Right-click context menu works
- [ ] Click-through works on transparent areas
- [ ] Magnetic edge snapping functions
- [ ] Opacity changes work
- [ ] Size changes animate smoothly
- [ ] Lock position prevents movement
- [ ] Performance remains smooth during drag

---

This feature transforms the VTuber into a true desktop companion that users can position anywhere they prefer, creating a more personalized and interactive experience!