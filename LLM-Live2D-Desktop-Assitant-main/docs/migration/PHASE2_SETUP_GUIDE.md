# Phase 2 Setup Guide - React + Vite Frontend

## Quick Setup Instructions

### 1. Install All Dependencies
```bash
cd LLM-Live2D-Desktop-Assitant-main
npm run install:all
```

This will:
- Install root dependencies (concurrently, cross-env, wait-on)
- Install frontend dependencies (React, Vite, TypeScript)

### 2. Validate Phase 2 Setup
```bash
node tests/phase2-validation.js
```

Expected result: **9/9 validations passed** ✅

### 3. Test Backend (Phase 1)
```bash
# Terminal 1: Start backend
python server.py --port 8000

# Terminal 2: Test backend endpoints
node tests/phase1-validation.js
```

Expected result: **5/5 tests passed** ✅

### 4. Test Frontend Development Server
```bash
# Start full development environment
npm run dev
```

This will:
1. **Start Python backend** on port 8000
2. **Start Vite dev server** on port 5173 with proxy
3. **Wait for frontend** to be ready
4. **Launch Electron app** loading from localhost:5173

### 5. Verify Setup

#### Backend Endpoints (Direct)
- Health: http://localhost:8000/health
- Mock TTS: POST http://localhost:8000/api/tts/mock
- Mock STT: POST http://localhost:8000/api/stt/mock
- WebSocket Echo: ws://localhost:8000/ws/echo

#### Frontend (Via Proxy)
- React App: http://localhost:5173
- Health (Proxied): http://localhost:5173/api/health
- WebSocket Echo (Proxied): ws://localhost:5173/ws/echo

#### Electron App
- Should automatically open and load React app
- Diagnostics panel should be visible in development
- All proxy connections should work through Vite

## Expected Behavior

### ✅ Successful Setup Indicators:
1. **Backend starts** with message: "Server is running: http://0.0.0.0:8000"
2. **Frontend starts** with message: "Local: http://localhost:5173/"
3. **Electron opens** and displays React app with Live2D placeholder
4. **Diagnostics panel** appears in top-right corner
5. **All diagnostic tests pass** when clicked

### ❌ Common Issues & Solutions:

#### Port Already in Use
```bash
# Kill processes on ports 8000 or 5173
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

#### Dependencies Not Installed
```bash
# Reinstall all dependencies
npm run install:all
```

#### Proxy Not Working
- Check that backend is running on port 8000
- Verify Vite config proxy settings
- Check browser network tab for proxy requests

## Development Workflow

### Daily Development
```bash
# Single command to start everything
npm run dev
```

### Frontend Only Development
```bash
cd frontend
npm run dev
```

### Backend Only Development
```bash
python server.py --port 8000
```

### Production Build
```bash
npm run build
```

## File Structure Overview

```
LLM-Live2D-Desktop-Assitant-main/
├── frontend/                    # React + Vite frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── config/api.ts        # API configuration
│   │   ├── main.tsx             # React entry point
│   │   └── App.tsx              # Main app component
│   ├── vite.config.ts           # Vite proxy configuration
│   └── package.json             # Frontend dependencies
├── static/                      # Live2D assets (served via proxy)
├── server.py                    # FastAPI backend (port 8000)
├── conf.yaml                    # Backend configuration
└── package.json                 # Root scripts and dependencies
```

## Next Steps - Phase 3

Once Phase 2 is validated and working:

1. **Component Migration**: Migrate existing Live2D, WebSocket, and Audio functionality
2. **Hook Implementation**: Create custom React hooks for state management
3. **Full Feature Parity**: Complete migration of all existing features
4. **Electron Integration**: Update main.js for production builds

---

**Phase 2 Status: ✅ READY FOR TESTING**  
**Next: Install dependencies and validate the complete setup**