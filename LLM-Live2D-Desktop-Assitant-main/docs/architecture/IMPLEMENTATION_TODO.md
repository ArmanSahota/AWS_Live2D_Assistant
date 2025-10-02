# React + Vite Migration - Implementation Todo List

## Phase 1: Backend Standardization (Days 1-2)

### 1.1 Port Configuration Updates
- [ ] **Update [`server.py`](server.py)** - Change from dynamic port allocation to fixed port 8000
  - [ ] Remove dynamic port finding logic
  - [ ] Set default port to 8000
  - [ ] Update command line argument parsing
- [ ] **Update [`conf.yaml`](conf.yaml)** - Set SERVER_PORT to 8000
- [ ] **Modify [`port_config.py`](port_config.py)** - Use standard port configuration
- [ ] **Update [`tests/http/api.js`](tests/http/api.js)** - Change hardcoded localhost:8000 references

### 1.2 FastAPI Endpoint Additions
- [ ] **Add health endpoint** - `GET /health`
  - [ ] Return server status and port information
  - [ ] Include timestamp and version info
- [ ] **Add WebSocket echo endpoint** - `WS /ws/echo`
  - [ ] Simple echo functionality for testing
  - [ ] Connection logging and error handling
- [ ] **Add mock TTS endpoint** - `POST /api/tts/mock`
  - [ ] Accept text and voice parameters
  - [ ] Return mock audio data for development
- [ ] **Add mock STT endpoint** - `POST /api/stt/mock`
  - [ ] Accept audio data
  - [ ] Return mock transcription for development

### 1.3 CORS Configuration
- [ ] **Update CORS middleware** in [`server.py`](server.py)
  - [ ] Add localhost:5173 to allowed origins
  - [ ] Add localhost:3000 for backup
  - [ ] Ensure WebSocket CORS support

### 1.4 Graceful Shutdown
- [ ] **Implement signal handlers** in [`server.py`](server.py)
  - [ ] Handle SIGINT and SIGTERM
  - [ ] Clean up resources properly
  - [ ] Log shutdown process

## Phase 2: Frontend Infrastructure Setup (Days 3-4)

### 2.1 Directory Structure Creation
- [ ] **Create [`frontend/`](frontend/) directory**
- [ ] **Create React app structure**
  - [ ] [`frontend/src/`](frontend/src/) - Source code
  - [ ] [`frontend/src/components/`](frontend/src/components/) - React components
  - [ ] [`frontend/src/hooks/`](frontend/src/hooks/) - Custom hooks
  - [ ] [`frontend/src/services/`](frontend/src/services/) - API clients
  - [ ] [`frontend/src/types/`](frontend/src/types/) - TypeScript types
  - [ ] [`frontend/src/config/`](frontend/src/config/) - Configuration
  - [ ] [`frontend/src/utils/`](frontend/src/utils/) - Utility functions
  - [ ] [`frontend/public/`](frontend/public/) - Static assets

### 2.2 Package Configuration
- [ ] **Create [`frontend/package.json`](frontend/package.json)**
  - [ ] Add React and TypeScript dependencies
  - [ ] Add Vite and build tools
  - [ ] Configure scripts for dev/build/preview
- [ ] **Create [`frontend/tsconfig.json`](frontend/tsconfig.json)**
  - [ ] Configure TypeScript for React
  - [ ] Set up path aliases
  - [ ] Configure module resolution

### 2.3 Vite Configuration
- [ ] **Create [`frontend/vite.config.ts`](frontend/vite.config.ts)**
  - [ ] Configure React plugin
  - [ ] Set up proxy for `/api` routes to localhost:8000
  - [ ] Set up proxy for `/ws` routes to localhost:8000
  - [ ] Configure build output to `../dist-frontend`
  - [ ] Set up aliases for `@static` directory
  - [ ] Configure public directory for Live2D assets

### 2.4 Environment Configuration
- [ ] **Create [`frontend/.env.development`](frontend/.env.development)**
  - [ ] Set VITE_API_BASE_URL for development
  - [ ] Set VITE_WS_BASE_URL for development
- [ ] **Create [`frontend/.env.production`](frontend/.env.production)**
  - [ ] Set production API URLs
- [ ] **Create [`frontend/src/config/api.ts`](frontend/src/config/api.ts)**
  - [ ] Single source of truth for API URLs
  - [ ] Environment-based configuration
  - [ ] Endpoint definitions

## Phase 3: Component Migration (Days 5-7)

### 3.1 Core React Setup
- [ ] **Create [`frontend/src/main.tsx`](frontend/src/main.tsx)** - React entry point
- [ ] **Create [`frontend/src/App.tsx`](frontend/src/App.tsx)** - Main app component
- [ ] **Create [`frontend/src/index.css`](frontend/src/index.css)** - Global styles
- [ ] **Create [`frontend/public/index.html`](frontend/public/index.html)** - HTML template

### 3.2 WebSocket Integration
- [ ] **Create [`frontend/src/hooks/useWebSocket.ts`](frontend/src/hooks/useWebSocket.ts)**
  - [ ] WebSocket connection management
  - [ ] Automatic reconnection logic
  - [ ] Message handling and state management
- [ ] **Create [`frontend/src/components/WebSocket/WebSocketClient.tsx`](frontend/src/components/WebSocket/WebSocketClient.tsx)**
  - [ ] WebSocket component wrapper
  - [ ] Connection status display
  - [ ] Message logging for debugging
- [ ] **Migrate [`static/desktop/websocket.js`](static/desktop/websocket.js)** functionality
  - [ ] Port detection logic
  - [ ] Reconnection strategies
  - [ ] Message formatting

### 3.3 Live2D Integration
- [ ] **Create [`frontend/src/components/Live2D/Live2DViewer.tsx`](frontend/src/components/Live2D/Live2DViewer.tsx)**
  - [ ] Canvas element management
  - [ ] Live2D initialization
  - [ ] Model loading and display
- [ ] **Create [`frontend/src/components/Live2D/Live2DManager.ts`](frontend/src/components/Live2D/Live2DManager.ts)**
  - [ ] Port Live2D functionality from [`static/desktop/live2d.js`](static/desktop/live2d.js)
  - [ ] Model management
  - [ ] Animation control
  - [ ] Expression handling
- [ ] **Create [`frontend/src/hooks/useLive2D.ts`](frontend/src/hooks/useLive2D.ts)**
  - [ ] Live2D state management
  - [ ] Model switching
  - [ ] Animation triggers

### 3.4 Audio Pipeline Integration
- [ ] **Create [`frontend/src/components/Audio/AudioManager.tsx`](frontend/src/components/Audio/AudioManager.tsx)**
  - [ ] Audio recording interface
  - [ ] Playback controls
  - [ ] Volume and settings management
- [ ] **Create [`frontend/src/components/Audio/TTSClient.ts`](frontend/src/components/Audio/TTSClient.ts)**
  - [ ] TTS API integration
  - [ ] Audio playback handling
  - [ ] Queue management
- [ ] **Create [`frontend/src/components/Audio/STTClient.ts`](frontend/src/components/Audio/STTClient.ts)**
  - [ ] STT API integration
  - [ ] Audio recording
  - [ ] Voice activity detection
- [ ] **Create [`frontend/src/hooks/useAudio.ts`](frontend/src/hooks/useAudio.ts)**
  - [ ] Audio state management
  - [ ] Recording controls
  - [ ] Playback controls
- [ ] **Migrate [`static/desktop/audio.js`](static/desktop/audio.js)** functionality
  - [ ] Audio task queue
  - [ ] Audio processing
  - [ ] Device management

### 3.5 Diagnostics and Testing
- [ ] **Create [`frontend/src/components/Diagnostics/DiagnosticsPanel.tsx`](frontend/src/components/Diagnostics/DiagnosticsPanel.tsx)**
  - [ ] Port existing test panel functionality
  - [ ] API testing interface
  - [ ] Connection status monitoring
  - [ ] Debug information display
- [ ] **Migrate [`static/desktop/diagnostics.js`](static/desktop/diagnostics.js)** functionality
  - [ ] Test functions
  - [ ] Logging and monitoring
  - [ ] Error reporting

### 3.6 API Integration
- [ ] **Create [`frontend/src/services/api.ts`](frontend/src/services/api.ts)**
  - [ ] HTTP client setup with axios
  - [ ] Error handling
  - [ ] Request/response interceptors
- [ ] **Create [`frontend/src/hooks/useAPI.ts`](frontend/src/hooks/useAPI.ts)**
  - [ ] API call management
  - [ ] Loading states
  - [ ] Error handling
  - [ ] Caching strategies

## Phase 4: Electron Integration Updates (Days 8-9)

### 4.1 Main Process Updates
- [ ] **Update [`main.js`](main.js)**
  - [ ] Detect development vs production mode
  - [ ] Load from Vite dev server in development (http://localhost:5173)
  - [ ] Load from built files in production (dist-frontend/index.html)
  - [ ] Update BrowserWindow configuration
  - [ ] Ensure preload scripts still work

### 4.2 Build Process Updates
- [ ] **Update root [`package.json`](package.json)**
  - [ ] Add concurrently, cross-env, wait-on dependencies
  - [ ] Create `dev` script for concurrent FE+BE development
  - [ ] Create `build` script for production builds
  - [ ] Update electron-builder configuration
- [ ] **Update electron-builder configuration**
  - [ ] Include dist-frontend in build
  - [ ] Update file patterns
  - [ ] Ensure Live2D assets are included

### 4.3 IPC Communication
- [ ] **Verify [`static/desktop/preload.js`](static/desktop/preload.js)** compatibility
  - [ ] Test IPC handlers with React app
  - [ ] Update if necessary for new architecture
- [ ] **Test existing IPC functionality**
  - [ ] Configuration management
  - [ ] File operations
  - [ ] System integration

## Phase 5: Testing & Validation (Days 10-12)

### 5.1 Connection Testing
- [ ] **Create [`tests/connection-test.js`](tests/connection-test.js)**
  - [ ] Test health endpoint
  - [ ] Test WebSocket echo
  - [ ] Test proxy routing
  - [ ] Validate CORS configuration
- [ ] **Update existing test files**
  - [ ] [`tests/http/test_api.js`](tests/http/test_api.js) - Update for new port
  - [ ] [`tests/ws/test_websocket.js`](tests/ws/test_websocket.js) - Update for new endpoints

### 5.2 Mock Endpoint Testing
- [ ] **Create [`tests/mock-endpoints-test.js`](tests/mock-endpoints-test.js)**
  - [ ] Test TTS mock endpoint
  - [ ] Test STT mock endpoint
  - [ ] Validate response formats
- [ ] **Integration testing**
  - [ ] Frontend to backend communication
  - [ ] WebSocket message flow
  - [ ] Audio pipeline functionality

### 5.3 Live2D Integration Testing
- [ ] **Test Live2D model loading**
  - [ ] Verify asset paths work in React
  - [ ] Test model switching
  - [ ] Validate animations and expressions
- [ ] **Performance testing**
  - [ ] Load time measurements
  - [ ] Memory usage monitoring
  - [ ] Animation smoothness

### 5.4 Electron Integration Testing
- [ ] **Test development mode**
  - [ ] Verify Vite dev server loading
  - [ ] Test hot module replacement
  - [ ] Validate IPC communication
- [ ] **Test production build**
  - [ ] Build process completion
  - [ ] App packaging
  - [ ] Distribution testing

## Phase 6: Documentation & Deployment (Days 13-15)

### 6.1 Documentation Updates
- [ ] **Create [`DEVELOPMENT_GUIDE.md`](DEVELOPMENT_GUIDE.md)**
  - [ ] Quick start instructions
  - [ ] Architecture overview
  - [ ] Available scripts
  - [ ] Troubleshooting guide
- [ ] **Update [`README.md`](README.md)**
  - [ ] New setup instructions
  - [ ] Updated requirements
  - [ ] Development workflow

### 6.2 Migration Documentation
- [ ] **Create migration guide**
  - [ ] Step-by-step migration process
  - [ ] Rollback procedures
  - [ ] Common issues and solutions
- [ ] **Update existing documentation**
  - [ ] API documentation
  - [ ] Configuration guides
  - [ ] Deployment instructions

### 6.3 Final Validation
- [ ] **End-to-end testing**
  - [ ] Complete user workflow testing
  - [ ] Performance validation
  - [ ] Cross-platform testing
- [ ] **Production readiness checklist**
  - [ ] Security review
  - [ ] Performance optimization
  - [ ] Error handling validation
  - [ ] Logging and monitoring setup

## Dependencies and Prerequisites

### Required Software
- [ ] Node.js 18+ installed
- [ ] Python 3.8+ installed
- [ ] Git for version control

### Required Packages (Root)
- [ ] `concurrently` - Run multiple commands
- [ ] `cross-env` - Cross-platform environment variables
- [ ] `wait-on` - Wait for services to be available

### Required Packages (Frontend)
- [ ] `react` and `react-dom` - React framework
- [ ] `vite` and `@vitejs/plugin-react` - Build tool
- [ ] `typescript` and React type definitions
- [ ] `axios` - HTTP client

## Risk Mitigation Checklist

- [ ] **Backup current working state** before starting migration
- [ ] **Create feature branch** for migration work
- [ ] **Test each phase** before proceeding to next
- [ ] **Maintain backward compatibility** during transition
- [ ] **Document rollback procedures** for each phase
- [ ] **Keep original static files** until migration is complete
- [ ] **Test on multiple platforms** (Windows, macOS, Linux)

## Success Criteria Validation

### Technical Requirements
- [ ] Frontend runs on port 5173 with Vite HMR
- [ ] Backend runs on port 8000 with proper CORS
- [ ] Proxy handles `/api` and `/ws` routes correctly
- [ ] Live2D integration works in React environment
- [ ] TTS/STT pipeline functions properly
- [ ] Electron app packages and runs correctly

### Performance Requirements
- [ ] Frontend load time < 3 seconds
- [ ] WebSocket connection established < 1 second
- [ ] Live2D model loading < 5 seconds
- [ ] Audio pipeline latency < 500ms

### Development Experience
- [ ] Single command starts full development environment
- [ ] Hot module replacement works for React components
- [ ] WebSocket connections maintain during development
- [ ] Build process generates production-ready Electron app

---

**Total Tasks: 89**
**Estimated Completion: 15 days (3 weeks)**

This todo list provides a comprehensive checklist for the React + Vite migration, ensuring no critical steps are missed during implementation.