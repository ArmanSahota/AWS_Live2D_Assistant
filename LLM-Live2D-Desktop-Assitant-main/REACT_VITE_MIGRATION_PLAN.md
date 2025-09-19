# AWS Live2D Assistant - React + Vite Migration Implementation Plan

## Project Overview

This plan outlines the migration of the AWS_Live2D_Assistant from static HTML/JS to a modern React frontend with Vite build tool, ensuring reliable frontend/backend connection via Vite proxy.

## Current Architecture Analysis

### Existing Structure
- **Backend**: FastAPI server (server.py) with dynamic port allocation (1017-1030)
- **Frontend**: Static HTML/JS files in `static/desktop/` directory
- **Electron**: Desktop app wrapper with IPC communication
- **Live2D**: Complex asset management and animation system
- **Audio Pipeline**: TTS (Edge-TTS) and STT (Faster-Whisper) integration
- **WebSocket**: Real-time communication for audio/chat data

### Key Requirements
- Frontend port: 5173 (Vite default)
- Backend port: 8000 (standardized)
- Vite proxy for `/api` and `/ws` routes
- Single source of truth for API/WS URLs
- FastAPI CORS, health endpoint, WebSocket echo, graceful shutdown
- Edge-TTS mock endpoints and STT mock routes
- npm scripts for concurrent FE+BE development
- Minimal Electron integration changes
- Replace hardcoded localhost:8000 URLs

## Implementation Phases

### Phase 1: Backend Standardization (Days 1-2)

#### 1.1 Port Standardization
**File**: [`server.py`](server.py)
- Change from dynamic port allocation to fixed port 8000
- Update port configuration in [`conf.yaml`](conf.yaml)
- Modify [`port_config.py`](port_config.py) to use standard port

#### 1.2 API Endpoint Additions
**File**: [`server.py`](server.py)
```python
# Add new endpoints
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Server is running", "port": 8000}

@app.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket):
    await websocket.accept()
    # Echo implementation for testing

@app.post("/api/tts/mock")
async def mock_tts_endpoint(request: dict):
    # Mock TTS for development

@app.post("/api/stt/mock") 
async def mock_stt_endpoint(request: dict):
    # Mock STT for development
```

#### 1.3 CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 1.4 Graceful Shutdown
```python
import signal
import sys

def signal_handler(sig, frame):
    logger.info("Gracefully shutting down server...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### Phase 2: Frontend Infrastructure Setup (Days 3-4)

#### 2.1 Directory Structure Creation
```
LLM-Live2D-Desktop-Assitant-main/
├── frontend/                    # New React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── Live2D/
│   │   │   │   ├── Live2DViewer.tsx
│   │   │   │   └── Live2DManager.ts
│   │   │   ├── Audio/
│   │   │   │   ├── AudioManager.tsx
│   │   │   │   ├── TTSClient.ts
│   │   │   │   └── STTClient.ts
│   │   │   ├── WebSocket/
│   │   │   │   ├── WebSocketClient.tsx
│   │   │   │   └── useWebSocket.ts
│   │   │   ├── Diagnostics/
│   │   │   │   └── DiagnosticsPanel.tsx
│   │   │   └── Settings/
│   │   │       └── SettingsPanel.tsx
│   │   ├── hooks/
│   │   │   ├── useAPI.ts
│   │   │   ├── useAudio.ts
│   │   │   └── useLive2D.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── websocket.ts
│   │   ├── types/
│   │   │   └── index.ts
│   │   ├── config/
│   │   │   └── api.ts
│   │   ├── utils/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   │   └── index.html
│   ├── vite.config.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.development
├── static/                      # Keep for Live2D assets
└── dist-frontend/              # Vite build output
```

#### 2.2 Dependencies Installation
**File**: [`frontend/package.json`](frontend/package.json)
```json
{
  "name": "live2d-assistant-frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "ws": "^8.14.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@types/ws": "^8.5.0",
    "@vitejs/plugin-react": "^4.0.0",
    "typescript": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

#### 2.3 Vite Configuration
**File**: [`frontend/vite.config.ts`](frontend/vite.config.ts)
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: '../dist-frontend',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          live2d: ['pixi.js'] // Live2D related chunks
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@static': path.resolve(__dirname, '../static')
    }
  },
  publicDir: '../static' // Serve Live2D assets
})
```

#### 2.4 API Configuration
**File**: [`frontend/src/config/api.ts`](frontend/src/config/api.ts)
```typescript
const isDevelopment = import.meta.env.DEV

export const API_CONFIG = {
  baseURL: isDevelopment 
    ? '/api'  // Proxy in development
    : import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  
  wsURL: isDevelopment
    ? '/ws'   // Proxy in development  
    : import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000',
    
  timeout: 10000
}

export const ENDPOINTS = {
  health: '/health',
  tts: '/tts',
  stt: '/stt',
  websocket: '/client-ws',
  echo: '/ws/echo'
}
```

### Phase 3: Component Migration (Days 5-7)

#### 3.1 Core React Components

**File**: [`frontend/src/App.tsx`](frontend/src/App.tsx)
```typescript
import React from 'react'
import { Live2DViewer } from './components/Live2D/Live2DViewer'
import { AudioManager } from './components/Audio/AudioManager'
import { WebSocketClient } from './components/WebSocket/WebSocketClient'
import { DiagnosticsPanel } from './components/Diagnostics/DiagnosticsPanel'
import './App.css'

function App() {
  return (
    <div className="app">
      <div className="live2d-container">
        <Live2DViewer />
      </div>
      
      <AudioManager />
      <WebSocketClient />
      
      {import.meta.env.DEV && <DiagnosticsPanel />}
    </div>
  )
}

export default App
```

#### 3.2 WebSocket Hook
**File**: [`frontend/src/hooks/useWebSocket.ts`](frontend/src/hooks/useWebSocket.ts)
```typescript
import { useEffect, useRef, useState } from 'react'
import { API_CONFIG } from '../config/api'

export const useWebSocket = (endpoint: string) => {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<any>(null)
  const ws = useRef<WebSocket | null>(null)
  
  const connect = () => {
    const wsUrl = `${API_CONFIG.wsURL}${endpoint}`
    ws.current = new WebSocket(wsUrl)
    
    ws.current.onopen = () => setIsConnected(true)
    ws.current.onclose = () => setIsConnected(false)
    ws.current.onmessage = (event) => {
      setLastMessage(JSON.parse(event.data))
    }
  }
  
  const sendMessage = (message: any) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message))
    }
  }
  
  useEffect(() => {
    connect()
    return () => ws.current?.close()
  }, [endpoint])
  
  return { isConnected, lastMessage, sendMessage, reconnect: connect }
}
```

#### 3.3 Live2D Integration
**File**: [`frontend/src/components/Live2D/Live2DViewer.tsx`](frontend/src/components/Live2D/Live2DViewer.tsx)
```typescript
import React, { useEffect, useRef } from 'react'
import { Live2DManager } from './Live2DManager'

export const Live2DViewer: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const managerRef = useRef<Live2DManager | null>(null)
  
  useEffect(() => {
    if (canvasRef.current) {
      managerRef.current = new Live2DManager(canvasRef.current)
      managerRef.current.initialize()
    }
    
    return () => {
      managerRef.current?.dispose()
    }
  }, [])
  
  return (
    <div className="live2d-stage">
      <canvas 
        ref={canvasRef}
        id="live2d-canvas"
        width={800}
        height={600}
      />
    </div>
  )
}
```

### Phase 4: Electron Integration Updates (Days 8-9)

#### 4.1 Main Process Updates
**File**: [`main.js`](main.js)
```javascript
const isDevelopment = !app.isPackaged

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'static/desktop/preload.js')
    }
  })

  if (isDevelopment) {
    // Development: Load from Vite dev server
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    // Production: Load from built files
    mainWindow.loadFile('dist-frontend/index.html')
  }
}
```

#### 4.2 Updated Package Scripts
**File**: [`package.json`](package.json)
```json
{
  "scripts": {
    "dev": "concurrently \"npm run dev:backend\" \"npm run dev:frontend\" \"wait-on http://localhost:5173 && npm run electron:dev\"",
    "dev:frontend": "cd frontend && npm run dev",
    "dev:backend": "python server.py --port 8000",
    "electron:dev": "cross-env NODE_ENV=development electron .",
    "build": "npm run build:frontend && npm run build:electron",
    "build:frontend": "cd frontend && npm run build",
    "build:electron": "electron-builder",
    "start": "npm run build && electron .",
    "test:connection": "node tests/connection-test.js",
    "install:all": "npm install && cd frontend && npm install"
  },
  "devDependencies": {
    "concurrently": "^8.2.0",
    "cross-env": "^7.0.3",
    "wait-on": "^7.0.1"
  }
}
```

### Phase 5: Testing & Validation (Days 10-12)

#### 5.1 Connection Test Suite
**File**: [`tests/connection-test.js`](tests/connection-test.js)
```javascript
const axios = require('axios')
const WebSocket = require('ws')

async function testConnections() {
  console.log('Testing backend health...')
  
  try {
    // Test health endpoint
    const health = await axios.get('http://localhost:8000/health')
    console.log('✓ Health check:', health.data)
    
    // Test WebSocket echo
    const ws = new WebSocket('ws://localhost:8000/ws/echo')
    ws.on('open', () => {
      console.log('✓ WebSocket connected')
      ws.send(JSON.stringify({ test: 'echo' }))
    })
    
    ws.on('message', (data) => {
      console.log('✓ WebSocket echo received:', JSON.parse(data))
      ws.close()
    })
    
  } catch (error) {
    console.error('✗ Connection test failed:', error.message)
  }
}

testConnections()
```

#### 5.2 Mock Endpoints Testing
**File**: [`tests/mock-endpoints-test.js`](tests/mock-endpoints-test.js)
```javascript
const axios = require('axios')

async function testMockEndpoints() {
  const baseURL = 'http://localhost:8000'
  
  // Test TTS mock
  const ttsResponse = await axios.post(`${baseURL}/api/tts/mock`, {
    text: 'Hello world',
    voice: 'en-US-JennyNeural'
  })
  
  console.log('✓ TTS Mock:', ttsResponse.data)
  
  // Test STT mock  
  const sttResponse = await axios.post(`${baseURL}/api/stt/mock`, {
    audio: 'base64audiodata'
  })
  
  console.log('✓ STT Mock:', sttResponse.data)
}

testMockEndpoints()
```

### Phase 6: Documentation & Deployment (Days 13-15)

#### 6.1 Development Guide
**File**: [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md)
```markdown
# Development Guide

## Quick Start
1. `npm run install:all` - Install all dependencies
2. `npm run dev` - Start development servers
3. Open http://localhost:5173 for frontend
4. Backend runs on http://localhost:8000

## Architecture
- Frontend: React + Vite (port 5173)
- Backend: FastAPI (port 8000)  
- Proxy: Vite handles /api and /ws routes
- Electron: Desktop wrapper

## Available Scripts
- `npm run dev` - Full development environment
- `npm run build` - Production build
- `npm run test:connection` - Test connectivity
```

## File Dependencies & Relationships

### Critical Files to Modify
1. **[`server.py`](server.py)** - Backend port standardization, new endpoints
2. **[`main.js`](main.js)** - Electron integration updates
3. **[`package.json`](package.json)** - Root package scripts
4. **[`conf.yaml`](conf.yaml)** - Port configuration updates

### Files to Replace/Migrate
1. **[`static/desktop.html`](static/desktop.html)** → **[`frontend/src/App.tsx`](frontend/src/App.tsx)**
2. **[`static/desktop/websocket.js`](static/desktop/websocket.js)** → **[`frontend/src/hooks/useWebSocket.ts`](frontend/src/hooks/useWebSocket.ts)**
3. **[`static/desktop/live2d.js`](static/desktop/live2d.js)** → **[`frontend/src/components/Live2D/`](frontend/src/components/Live2D/)**
4. **[`static/desktop/audio.js`](static/desktop/audio.js)** → **[`frontend/src/components/Audio/`](frontend/src/components/Audio/)**

### Files to Preserve
1. **[`static/libs/`](static/libs/)** - Live2D libraries and assets
2. **[`static/desktop/models/`](static/desktop/models/)** - Live2D model files
3. **[`src/config/appConfig.js`](src/config/appConfig.js)** - Electron configuration
4. **[`tts/`](tts/)** and **[`asr/`](asr/)** - Audio processing modules

## Risk Mitigation Strategies

### 1. Incremental Migration
- Keep original static files during migration
- Implement feature flags for old/new frontend switching
- Test each component individually before integration

### 2. Backward Compatibility
- Maintain existing IPC communication patterns
- Preserve Live2D asset loading mechanisms
- Keep original WebSocket message formats

### 3. Rollback Plan
- Git branching strategy for safe rollback
- Backup of working static implementation
- Environment variable toggles for quick switching

## Success Criteria

### Technical Requirements
- ✅ Frontend runs on port 5173 with Vite HMR
- ✅ Backend runs on port 8000 with proper CORS
- ✅ Proxy handles `/api` and `/ws` routes correctly
- ✅ Live2D integration works in React environment
- ✅ TTS/STT pipeline functions properly
- ✅ Electron app packages and runs correctly

### Development Experience
- ✅ Single command starts full development environment
- ✅ Hot module replacement works for React components
- ✅ WebSocket connections maintain during development
- ✅ Build process generates production-ready Electron app

### Performance Metrics
- ✅ Frontend load time < 3 seconds
- ✅ WebSocket connection established < 1 second
- ✅ Live2D model loading < 5 seconds
- ✅ Audio pipeline latency < 500ms

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| 1 | Days 1-2 | Backend standardization, port 8000, new endpoints |
| 2 | Days 3-4 | Vite setup, React structure, proxy configuration |
| 3 | Days 5-7 | Component migration, hooks, Live2D integration |
| 4 | Days 8-9 | Electron updates, build process |
| 5 | Days 10-12 | Testing, validation, bug fixes |
| 6 | Days 13-15 | Documentation, deployment preparation |

**Total Estimated Time: 15 days (3 weeks)**

## Next Steps

1. **Review and Approve Plan** - Stakeholder sign-off on approach
2. **Environment Setup** - Prepare development environment
3. **Phase 1 Execution** - Begin backend standardization
4. **Continuous Testing** - Validate each phase before proceeding
5. **Documentation Updates** - Maintain current documentation throughout

This migration will modernize the frontend architecture while preserving all existing functionality, providing a robust foundation for future development and maintenance.