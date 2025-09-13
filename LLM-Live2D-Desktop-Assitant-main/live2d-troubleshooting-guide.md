# Live2D Model Loading Troubleshooting Guide

This guide focuses specifically on fixing issues with Live2D models not loading correctly in the application.

## Common Issues and Solutions

### 1. Model Path Resolution Problems

The most common issue is that the code cannot correctly locate the model files.

**Diagnosis:**
- Check the console logs for errors like "Model URL is undefined or empty" or "Error loading model"
- Look for 404 errors when trying to load model files

**Solutions:**

#### Fix Absolute Path Resolution:

```javascript
// Add this debugging to getDefaultModelConfig() in live2d.js
console.log("DEBUG: Attempting to locate model in these paths:");
const possiblePaths = [
  "static/desktop/models/default/default.model3.json",
  "desktop/models/default/default.model3.json", 
  "models/default/default.model3.json"
];
possiblePaths.forEach(path => console.log(`- ${path} (absolute: ${require('path').resolve(path)})`));
```

#### Hardcode Working Path:

If you know the correct path, temporarily hardcode it to verify:

```javascript
// In getDefaultModelConfig() function
return {
  url: "file:///absolute/path/to/your/model/default.model3.json",
  kScale: 0.15,
  initialXshift: 0,
  initialYshift: 0,
  emotionMap: {}
};
```

### 2. Initialization Timing Issues

The model initialization might happen before the DOM or PIXI.js is fully ready.

**Diagnosis:**
- Check for errors like "Cannot read property of undefined" related to the canvas or app
- Look for timing-related issues in the console

**Solutions:**

#### Add Explicit DOM Ready Check:

```javascript
function ensureDOMReady() {
  return new Promise(resolve => {
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
      console.log("DOM already ready");
      setTimeout(resolve, 100); // Small delay to ensure everything is initialized
    } else {
      console.log("Waiting for DOM ready event");
      document.addEventListener('DOMContentLoaded', () => {
        console.log("DOM content loaded event fired");
        setTimeout(resolve, 100);
      });
    }
  });
}

// Use in bootLive2D
async function bootLive2D(retryCount = 3, retryDelay = 1000) {
  console.log("Booting Live2D model");
  
  try {
    // Wait for DOM to be ready
    await ensureDOMReady();
    
    // Check if canvas exists
    const canvas = document.getElementById("live2d-canvas");
    if (!canvas) {
      console.error("Live2D canvas element not found!");
      document.getElementById("message").textContent = "Error: Canvas not found";
      return false;
    }
    
    // Continue with initialization
    await window.live2dModule.init();
    // ...rest of function remains the same
  }
  catch(error) {
    // ...error handling
  }
}
```

### 3. WebGL Context Issues

WebGL might not be available or might fail to initialize.

**Diagnosis:**
- Look for errors related to WebGL or context creation
- Check if other WebGL applications work on the same system

**Solutions:**

#### Add WebGL Detection:

```javascript
function checkWebGLSupport() {
  const canvas = document.createElement('canvas');
  let gl = null;
  
  try {
    gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
  } catch(e) {
    return false;
  }
  
  if (gl) {
    return true;
  }
  
  return false;
}

// Add to bootLive2D
if (!checkWebGLSupport()) {
  console.error("WebGL not supported in this browser/environment!");
  document.getElementById("message").textContent = "Error: WebGL not supported";
  return false;
}
```

### 4. PIXI or Live2D Core Issues

PIXI.js or Live2D Cubism core libraries might not be loading correctly.

**Diagnosis:**
- Check if PIXI or Live2D are defined in the console
- Look for script loading errors in the Network tab

**Solutions:**

#### Check Library Loading Status:

```javascript
// Add to bootLive2D at the start
if (!window.PIXI) {
  console.error("PIXI is not defined! Make sure pixi.min.js is loaded.");
  document.getElementById("message").textContent = "Error: PIXI library not loaded";
  return false;
}

if (!window.PIXI.live2d) {
  console.error("PIXI.live2d is not defined! Make sure Live2D plugin is loaded.");
  document.getElementById("message").textContent = "Error: Live2D plugin not loaded";
  return false;
}
```

#### Ensure Proper Script Loading Order:

Review script tags in HTML to ensure proper loading order:

```html
<script src="libs/live2dcubismcore.min.js"></script>
<script src="libs/pixi.min.js"></script>
<script src="libs/live2d.min.js"></script>
<script src="libs/index.min.js"></script>
<!-- Only after these, load your app scripts -->
<script src="desktop/live2d.js"></script>
```

### 5. Debugging Live2D Initialization

Add extensive logging to trace the initialization process:

```javascript
// Modify live2dModule.init() function to include more logging
async function init() {
  console.log("TRACE: Starting live2dModule.init()");
  console.log("TRACE: Creating PIXI application");
  
  try {
    app = new PIXI.Application({
      view: document.getElementById("live2d-canvas"),
      autoStart: true,
      resizeTo: document.getElementById("live2d-stage"),
      transparent: true,
      backgroundAlpha: 0,
    });
    
    console.log("TRACE: PIXI application created successfully");
    console.log("TRACE: Canvas:", document.getElementById("live2d-canvas"));
    console.log("TRACE: Stage:", document.getElementById("live2d-stage"));
    
    // Check if app was created properly
    if (!app || !app.stage) {
      console.error("TRACE: Failed to create PIXI application properly");
      throw new Error("PIXI application not initialized correctly");
    }
    
    console.log("TRACE: live2dModule.init() completed successfully");
  } catch (e) {
    console.error("TRACE: Error in live2dModule.init():", e);
    throw e;
  }
}
```

### 6. Fixing Model Loading Itself

The problem might be in the model loading function. Add more robust error handling:

```javascript
// Enhanced loadModel function with better error handling and debugging
async function loadModel(modelInfo = {}) {
  console.log("DEBUG: loadModel called with modelInfo:", JSON.stringify(modelInfo));
  
  try {
    // Check if model info is valid
    if (!modelInfo || !modelInfo.url) {
      console.error("DEBUG: Invalid model info:", modelInfo);
      throw new Error("Invalid model info or URL");
    }
    
    // Store emotion map
    emoMap = modelInfo["emotionMap"];

    // Clear existing model
    if (window.model2) {
      console.log("DEBUG: Removing existing model");
      app.stage.removeChild(window.model2);
      window.model2.destroy({ children: true, texture: true, baseTexture: true });
      window.model2 = null;
      model2 = null;
    }

    const options = {
      autoInteract: false,
      autoUpdate: true,
    };

    // Make sure the URL is valid
    let modelUrl = modelInfo.url;
    console.log("DEBUG: Original model URL:", modelUrl);
    
    // If URL doesn't start with file://, convert it
    if (modelUrl && !modelUrl.startsWith('file://')) {
      modelUrl = pathToFileURL(modelUrl);
      console.log("DEBUG: Converted model URL:", modelUrl);
    }

    console.log("DEBUG: Attempting to load model from:", modelUrl);
    
    // Try to verify file exists (for file:// URLs)
    if (modelUrl.startsWith('file://') && window.electronAPI && window.electronAPI.checkFileExists) {
      const filePath = fileURLToPath(modelUrl);
      const exists = await window.electronAPI.checkFileExists(filePath);
      if (!exists) {
        console.error(`DEBUG: File does not exist: ${filePath}`);
        throw new Error(`Model file does not exist: ${filePath}`);
      } else {
        console.log(`DEBUG: Verified file exists: ${filePath}`);
      }
    }
    
    // Load the model with timeout
    console.log("DEBUG: Starting model loading with timeout");
    const modelLoadPromise = Promise.race([
      Promise.all([live2d.Live2DModel.from(modelUrl, options)]),
      new Promise((_, reject) => setTimeout(() => reject(new Error("Model loading timed out")), 10000))
    ]);
    
    const models = await modelLoadPromise;
    console.log("DEBUG: Model loaded successfully");
    
    // Continue with the rest of the function...
    // ...
  } catch (error) {
    console.error("DEBUG: Error loading model:", error);
    console.error("DEBUG: Error stack:", error.stack);
    throw error;
  }
}
```

### 7. Implement a Direct Test Function

Add a direct test function that bypasses all the abstractions:

```javascript
// Add this function to live2d.js
async function testDirectModelLoading() {
  try {
    console.log("TEST: Direct model loading test");
    
    // Create basic PIXI app
    const testCanvas = document.createElement('canvas');
    testCanvas.width = 512;
    testCanvas.height = 512;
    document.body.appendChild(testCanvas);
    
    const testApp = new PIXI.Application({
      view: testCanvas,
      width: 512,
      height: 512,
      transparent: true
    });
    
    console.log("TEST: PIXI app created");
    
    // Hardcoded model path - update with your actual path
    const modelPath = "static/desktop/models/default/default.model3.json";
    const modelUrl = pathToFileURL(modelPath);
    
    console.log(`TEST: Loading model from ${modelUrl}`);
    
    const options = {
      autoInteract: false,
      autoUpdate: true,
    };
    
    const model = await PIXI.live2d.Live2DModel.from(modelUrl, options);
    
    console.log("TEST: Model loaded successfully!");
    testApp.stage.addChild(model);
    
    // Position in center
    model.x = 256;
    model.y = 256;
    model.scale.set(0.2);
    
    return "Test successful - model loaded and displayed";
  } catch (error) {
    console.error("TEST: Direct model loading failed:", error);
    return `Test failed: ${error.message}`;
  }
}

// Expose for testing from console
window.testDirectModelLoading = testDirectModelLoading;
```

### 8. Monitor Network and File Access

If you're loading from a URL or file, you need to ensure the file is accessible:

**For Electron Apps:**
Add a helper function in preload.js to check file existence:

```javascript
// In preload.js
const fs = require('fs');
contextBridge.exposeInMainWorld('electronAPI', {
  // ... existing functions
  checkFileExists: (path) => {
    return new Promise((resolve) => {
      fs.access(path, fs.constants.F_OK, (err) => {
        resolve(!err);
      });
    });
  }
});
```

### 9. Try Loading a Different Model

Sometimes the specific model file might be corrupt or incompatible:

```javascript
// Add this to live2d.js
async function tryAlternativeModels() {
  const alternatives = [
    "static/desktop/models/default/default.model3.json",
    "static/desktop/models/test-model/test.model3.json",
    // Add other model paths you know should work
  ];
  
  for (const modelPath of alternatives) {
    try {
      console.log(`Trying alternative model: ${modelPath}`);
      const modelConfig = {
        url: pathToFileURL(modelPath),
        kScale: 0.15,
        initialXshift: 0,
        initialYshift: 0,
        emotionMap: {}
      };
      
      const result = await window.live2dModule.loadModel(modelConfig);
      if (result) {
        console.log(`Successfully loaded alternative model: ${modelPath}`);
        return true;
      }
    } catch (e) {
      console.error(`Failed to load alternative model ${modelPath}:`, e);
    }
  }
  
  console.error("All alternative models failed to load");
  return false;
}

// Expose for testing from console
window.tryAlternativeModels = tryAlternativeModels;
```

### 10. Check for Required File Structure

Live2D models require specific files to be present in the right structure:

```javascript
// Add this helper to check model directory structure
async function checkModelStructure(modelDir) {
  if (!window.electronAPI || !window.electronAPI.listFiles) {
    console.error("Cannot check model structure: electronAPI.listFiles not available");
    return false;
  }
  
  try {
    const files = await window.electronAPI.listFiles(modelDir);
    console.log(`Files in ${modelDir}:`, files);
    
    // Check for required files
    const hasModel3 = files.some(f => f.endsWith('.model3.json'));
    const hasMoc3 = files.some(f => f.endsWith('.moc3'));
    const hasTexture = files.some(f => f.includes('texture') || f.endsWith('.png'));
    
    console.log(`Model structure check: model3=${hasModel3}, moc3=${hasMoc3}, texture=${hasTexture}`);
    
    return hasModel3 && hasMoc3 && hasTexture;
  } catch (e) {
    console.error(`Error checking model structure for ${modelDir}:`, e);
    return false;
  }
}

// Add to preload.js
const fs = require('fs');
const path = require('path');
contextBridge.exposeInMainWorld('electronAPI', {
  // ... existing functions
  listFiles: (dir) => {
    return new Promise((resolve, reject) => {
      fs.readdir(dir, (err, files) => {
        if (err) reject(err);
        else resolve(files);
      });
    });
  }
});
```

## Implementation Steps to Fix the Issue

1. **Add Extensive Debug Logging**: First, add all the logging code from this guide
2. **Check Script Loading Order**: Verify scripts load in the right order in the HTML
3. **Test Basic Model Loading**: Use the `testDirectModelLoading` function to test direct loading
4. **Verify File Existence**: Add the file checking helper and verify model files exist
5. **Try Alternative Models**: Use the `tryAlternativeModels` function to test other models
6. **Check Model Structure**: Use the `checkModelStructure` helper to validate model files

## Additional Troubleshooting Steps

If the above solutions don't resolve the issue, try these additional steps:

1. **Clear Browser Cache**: If testing in a browser, clear the cache
2. **Update Live2D Cubism SDK**: Make sure you're using the latest version
3. **Check for Browser/OS Compatibility Issues**: Test in different environments
4. **Add Timeouts and Retry Logic**: Add more aggressive retry logic for loading
5. **Monitor Memory Usage**: Check if you're running out of memory
6. **Verify WebGL Support**: Make sure WebGL is supported and enabled
7. **Check Console Filters**: Make sure no errors are being filtered out in the console

By implementing these debugging steps and fixes, you should be able to identify and resolve the specific issue causing Live2D models not to load.