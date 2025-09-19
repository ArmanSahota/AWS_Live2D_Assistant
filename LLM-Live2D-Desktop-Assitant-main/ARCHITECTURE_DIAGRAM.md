# AWS Live2D Assistant - React + Vite Architecture

## System Architecture Overview

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Developer]
        DEV --> CMD[npm run dev]
    end
    
    subgraph "Concurrent Processes"
        CMD --> BE[Backend Server<br/>Python FastAPI<br/>Port 8000]
        CMD --> FE[Frontend Dev Server<br/>Vite + React<br/>Port 5173]
        CMD --> EL[Electron Main Process<br/>BrowserWindow]
    end
    
    subgraph "Frontend (React + Vite)"
        FE --> PROXY[Vite Proxy]
        PROXY --> |/api/*| BE
        PROXY --> |/ws/*| BE
        
        FE --> REACT[React App]
        REACT --> LIVE2D[Live2D Viewer]
        REACT --> AUDIO[Audio Manager]
        REACT --> WS[WebSocket Client]
        REACT --> DIAG[Diagnostics Panel]
    end
    
    subgraph "Backend (FastAPI)"
        BE --> HEALTH[/health endpoint]
        BE --> WSECHO[/ws/echo WebSocket]
        BE --> MOCKTTS[/api/tts/mock]
        BE --> MOCKSTT[/api/stt/mock]
        BE --> MAINWS[/client-ws WebSocket]
        BE --> CORS[CORS Middleware]
    end
    
    subgraph "Electron Integration"
        EL --> |Development| DEVLOAD[Load http://localhost:5173]
        EL --> |Production| PRODLOAD[Load dist-frontend/index.html]
        EL --> IPC[IPC Communication]
        EL --> PRELOAD[Preload Scripts]
    end
    
    subgraph "Static Assets"
        STATIC[static/ directory]
        STATIC --> MODELS[Live2D Models]
        STATIC --> LIBS[Live2D Libraries]
        STATIC --> ASSETS[Audio/Image Assets]
        
        REACT --> |Access via Vite| STATIC
    end
    
    subgraph "Build Process"
        BUILD[npm run build]
        BUILD --> FEBUILD[Frontend Build<br/>Vite → dist-frontend/]
        BUILD --> ELBUILD[Electron Build<br/>electron-builder]
        FEBUILD --> ELBUILD
    end
```

## Component Architecture

```mermaid
graph TB
    subgraph "React Component Hierarchy"
        APP[App.tsx<br/>Main Container]
        
        APP --> LIVE2D_VIEWER[Live2DViewer.tsx<br/>Canvas Management]
        APP --> AUDIO_MGR[AudioManager.tsx<br/>TTS/STT Controls]
        APP --> WS_CLIENT[WebSocketClient.tsx<br/>Connection Management]
        APP --> DIAG_PANEL[DiagnosticsPanel.tsx<br/>Debug Interface]
        
        LIVE2D_VIEWER --> LIVE2D_MGR[Live2DManager.ts<br/>Model Control]
        AUDIO_MGR --> TTS_CLIENT[TTSClient.ts<br/>Speech Synthesis]
        AUDIO_MGR --> STT_CLIENT[STTClient.ts<br/>Speech Recognition]
    end
    
    subgraph "Custom Hooks"
        USE_WS[useWebSocket.ts<br/>WS State Management]
        USE_AUDIO[useAudio.ts<br/>Audio State]
        USE_LIVE2D[useLive2D.ts<br/>Model State]
        USE_API[useAPI.ts<br/>HTTP Requests]
        
        WS_CLIENT --> USE_WS
        AUDIO_MGR --> USE_AUDIO
        LIVE2D_VIEWER --> USE_LIVE2D
        APP --> USE_API
    end
    
    subgraph "Services Layer"
        API_SERVICE[api.ts<br/>HTTP Client]
        WS_SERVICE[websocket.ts<br/>WS Client]
        CONFIG[api.ts<br/>Configuration]
        
        USE_API --> API_SERVICE
        USE_WS --> WS_SERVICE
        API_SERVICE --> CONFIG
        WS_SERVICE --> CONFIG
    end
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant React as React App
    participant Vite as Vite Proxy
    participant FastAPI as Backend
    participant Live2D as Live2D Engine
    participant Electron as Electron Main
    
    User->>React: Interact with UI
    React->>Vite: API Request (/api/*)
    Vite->>FastAPI: Proxy to localhost:8000
    FastAPI->>Vite: Response
    Vite->>React: Response Data
    React->>Live2D: Update Model
    Live2D->>React: Animation Complete
    
    User->>React: Start Audio Recording
    React->>Vite: WebSocket (/ws/*)
    Vite->>FastAPI: WS Connection
    FastAPI->>Vite: Audio Data
    Vite->>React: Process Audio
    React->>User: Display Results
    
    React->>Electron: IPC Message
    Electron->>React: IPC Response
```

## File Structure Mapping

```mermaid
graph LR
    subgraph "Current Structure"
        CURR_HTML[static/desktop.html]
        CURR_WS[static/desktop/websocket.js]
        CURR_LIVE2D[static/desktop/live2d.js]
        CURR_AUDIO[static/desktop/audio.js]
        CURR_DIAG[static/desktop/diagnostics.js]
    end
    
    subgraph "New React Structure"
        NEW_APP[frontend/src/App.tsx]
        NEW_WS[frontend/src/hooks/useWebSocket.ts]
        NEW_LIVE2D[frontend/src/components/Live2D/]
        NEW_AUDIO[frontend/src/components/Audio/]
        NEW_DIAG[frontend/src/components/Diagnostics/]
    end
    
    CURR_HTML -.->|Migrate| NEW_APP
    CURR_WS -.->|Migrate| NEW_WS
    CURR_LIVE2D -.->|Migrate| NEW_LIVE2D
    CURR_AUDIO -.->|Migrate| NEW_AUDIO
    CURR_DIAG -.->|Migrate| NEW_DIAG
```

## Network Architecture

```mermaid
graph TB
    subgraph "Development Network Flow"
        BROWSER[Browser/Electron<br/>localhost:5173]
        VITE_SERVER[Vite Dev Server<br/>Port 5173]
        BACKEND[FastAPI Server<br/>Port 8000]
        
        BROWSER --> VITE_SERVER
        VITE_SERVER --> |Proxy /api/*| BACKEND
        VITE_SERVER --> |Proxy /ws/*| BACKEND
        VITE_SERVER --> |Static Assets| STATIC_DIR[static/ directory]
    end
    
    subgraph "Production Network Flow"
        ELECTRON_PROD[Electron App]
        BUILT_FILES[dist-frontend/<br/>Built React App]
        BACKEND_PROD[FastAPI Server<br/>Port 8000]
        
        ELECTRON_PROD --> BUILT_FILES
        BUILT_FILES --> |Direct API Calls| BACKEND_PROD
        BUILT_FILES --> |Direct WS| BACKEND_PROD
    end
```

## Configuration Management

```mermaid
graph TB
    subgraph "Environment Configuration"
        DEV_ENV[.env.development<br/>VITE_API_BASE_URL=/api<br/>VITE_WS_BASE_URL=/ws]
        PROD_ENV[.env.production<br/>VITE_API_BASE_URL=http://localhost:8000<br/>VITE_WS_BASE_URL=ws://localhost:8000]
        
        API_CONFIG[frontend/src/config/api.ts<br/>Single Source of Truth]
        
        DEV_ENV --> API_CONFIG
        PROD_ENV --> API_CONFIG
    end
    
    subgraph "Backend Configuration"
        CONF_YAML[conf.yaml<br/>SERVER_PORT: 8000]
        SERVER_PY[server.py<br/>Port Configuration]
        
        CONF_YAML --> SERVER_PY
    end
    
    subgraph "Build Configuration"
        VITE_CONFIG[vite.config.ts<br/>Proxy Setup<br/>Build Output]
        PACKAGE_JSON[package.json<br/>Scripts & Dependencies]
        TSCONFIG[tsconfig.json<br/>TypeScript Config]
        
        VITE_CONFIG --> API_CONFIG
    end
```

## Development Workflow

```mermaid
graph TB
    START[Developer runs<br/>npm run dev]
    
    START --> CONCURRENT[Concurrently starts:]
    CONCURRENT --> BACKEND_START[python server.py --port 8000]
    CONCURRENT --> FRONTEND_START[cd frontend && npm run dev]
    CONCURRENT --> ELECTRON_WAIT[wait-on http://localhost:5173]
    
    BACKEND_START --> BACKEND_READY[Backend Ready<br/>Port 8000]
    FRONTEND_START --> FRONTEND_READY[Frontend Ready<br/>Port 5173<br/>Proxy Configured]
    ELECTRON_WAIT --> ELECTRON_START[electron . --dev]
    
    FRONTEND_READY --> PROXY_ACTIVE[Vite Proxy Active<br/>/api → :8000<br/>/ws → :8000]
    ELECTRON_START --> LOAD_DEV[Load http://localhost:5173]
    
    PROXY_ACTIVE --> DEV_READY[Development Environment Ready<br/>Hot Module Replacement<br/>WebSocket Connections<br/>Live2D Integration]
    LOAD_DEV --> DEV_READY
    BACKEND_READY --> DEV_READY
```

## Build and Deployment Flow

```mermaid
graph TB
    BUILD_START[npm run build]
    
    BUILD_START --> FE_BUILD[cd frontend && npm run build]
    FE_BUILD --> VITE_BUILD[Vite builds React app<br/>Output: ../dist-frontend/]
    
    VITE_BUILD --> ELECTRON_BUILD[electron-builder]
    ELECTRON_BUILD --> PACKAGE[Package Electron App<br/>Include dist-frontend/<br/>Include static/ assets]
    
    PACKAGE --> DIST[Distributable App<br/>Windows: .exe<br/>macOS: .dmg<br/>Linux: .AppImage]
```

## Key Integration Points

### 1. Vite Proxy Configuration
- **Development**: Routes `/api/*` and `/ws/*` to `localhost:8000`
- **Production**: Direct API calls to configured backend URL
- **Asset Serving**: Static Live2D assets served through Vite

### 2. WebSocket Handling
- **Development**: Proxy WebSocket connections through Vite
- **Production**: Direct WebSocket connections to backend
- **Reconnection**: Automatic reconnection logic in React hooks

### 3. Live2D Integration
- **Asset Loading**: Live2D models and libraries served as static assets
- **React Integration**: Canvas management through React refs
- **State Management**: Live2D state managed through React hooks

### 4. Electron Integration
- **Development**: Load Vite dev server URL
- **Production**: Load built React app files
- **IPC**: Maintain existing IPC communication patterns

This architecture ensures a clean separation of concerns while maintaining all existing functionality and providing a modern, maintainable development experience.