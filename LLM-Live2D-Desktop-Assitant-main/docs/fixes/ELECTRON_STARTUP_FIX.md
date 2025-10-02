# Electron Startup Issue - DIAGNOSIS & FIX

## 🔍 Issue Identified

The Electron app is not opening because of a **port conflict**:

```
Port 8000 is in use. Using port 8002 instead.
```

**Root Cause**: The backend is starting on port 8002, but the Vite proxy is configured to proxy to port 8000, causing a connection mismatch.

## 🛠️ Immediate Fixes

### Fix 1: Kill Process on Port 8000
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace <PID> with actual process ID)
taskkill /PID <PID> /F

# Then try again
npm run dev
```

### Fix 2: Use Alternative Development Approach
```bash
# Start components individually to debug
cd LLM-Live2D-Desktop-Assitant-main

# Terminal 1: Start backend on port 8000
python server.py --port 8000

# Terminal 2: Start frontend (in new terminal)
cd frontend && npm run dev

# Terminal 3: Start Electron (in new terminal)
npm run electron:dev
```

### Fix 3: Update Vite Proxy for Dynamic Port
If port 8000 continues to be unavailable, we can make the Vite proxy dynamic.

## 🔧 Permanent Solution

### Option A: Force Port 8000 (Recommended)
Update the server startup to be more aggressive about using port 8000:

```python
# In server.py, modify the run method to fail if port 8000 is not available
# instead of falling back to another port
```

### Option B: Dynamic Proxy Configuration
Update Vite config to read the actual backend port from `server_port.txt`:

```typescript
// In vite.config.ts, read the actual port dynamically
const getBackendPort = () => {
  try {
    const portFile = fs.readFileSync('../server_port.txt', 'utf8');
    return parseInt(portFile.trim()) || 8000;
  } catch {
    return 8000;
  }
};
```

## 🚀 Quick Resolution Steps

### Step 1: Check What's Using Port 8000
```bash
netstat -ano | findstr :8000
```

### Step 2: Kill the Process
```bash
# If you find a process, kill it
taskkill /PID <PID> /F
```

### Step 3: Try Development Again
```bash
npm run dev
```

### Step 4: If Still Issues, Use Manual Startup
```bash
# Terminal 1
python server.py --port 8000

# Terminal 2  
cd frontend && npm run dev

# Terminal 3
npm run electron:dev
```

## 🔍 Debug Information

The debug script shows:
- ✅ All dependencies are installed correctly
- ✅ Backend starts successfully (but on wrong port)
- ❌ Port 8000 is occupied by another process
- ❌ Vite proxy expects backend on port 8000

## 💡 Prevention

To prevent this issue in the future:

1. **Check ports before starting**: Add port checking to the dev script
2. **Kill existing processes**: Add cleanup to the dev script
3. **Use unique ports**: Consider using less common ports
4. **Add port detection**: Make Vite proxy dynamic

## 🎯 Expected Behavior After Fix

When `npm run dev` works correctly:

1. **Backend starts** on port 8000 ✅
2. **Frontend starts** on port 5173 with proxy to port 8000 ✅
3. **Electron waits** for frontend to be ready ✅
4. **Electron opens** and loads React app from localhost:5173 ✅
5. **Diagnostics panel** appears and all tests pass ✅

---

**Status**: Issue identified and solutions provided  
**Next**: Apply one of the fixes above to resolve the port conflict