# Coding Mistakes and Fixes

## Critical Issues Fixed

### 1. Missing Variable Declarations in main.js
**Issue**: Variables `pythonExecutable` and `backendProcess` were not declared
**Location**: main.js:220, 225

### 2. Python Code Injection Vulnerability in ipc.js
**Issue**: Text parameter in Python command could allow code injection
**Location**: src/main/ipc.js:296

### 3. Missing Function Definition
**Issue**: `resolveModel3Path` function doesn't exist
**Location**: src/main/ipc.js:253

### 4. Duplicate Model Variable Management
**Issue**: Confusing dual management of model2 variable
**Location**: static/desktop/live2d.js

### 5. Incomplete Event Handler
**Issue**: setSensitivity handler appears incomplete
**Location**: static/desktop/electron.js:100

## Files Modified
1. main.js - Fixed variable declarations
2. src/main/ipc.js - Fixed security vulnerability and missing function
3. static/desktop/live2d.js - Cleaned up model variable management
4. static/desktop/electron.js - Fixed incomplete event handler

## How to Apply
Run the following commands to apply all fixes:
```bash
# Backup current files first
cp main.js main.js.backup
cp src/main/ipc.js src/main/ipc.js.backup
cp static/desktop/live2d.js static/desktop/live2d.js.backup
cp static/desktop/electron.js static/desktop/electron.js.backup

# Then apply the fixes using the modified files