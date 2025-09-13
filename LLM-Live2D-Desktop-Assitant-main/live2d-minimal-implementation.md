# Minimal Live2D Auto-Loading Implementation

This guide provides a simplified, focused implementation specifically to fix the issue of Live2D models not loading automatically when the Electron app starts.

## Core Issue

The main problem is likely one of these:

1. The initialization timing is incorrect
2. The path to the model files is not being resolved correctly
3. Error handling is inadequate, causing silent failures

## Minimal Implementation

Here's a minimal, bulletproof implementation focusing only on making the model load:

### 1. Replace `live2d.js` with this minimal version:

```javascript
// Minimal Live2D implementation focused only on reliable auto-loading
var app;
var model2;

// Expose a minimal controller API
window.live2dController = {
  setMouth: (mouthY) => {
    if (window.model2 && window.model2.internalModel && window.model2.internalModel.coreModel) {
      try {
        if (typeof window.model2.internalModel.coreModel.setParameterValueById === 'function') {
          window.model2.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', mouthY);
        } else {
          window.model2.internalModel.coreModel.setParamFloat('PARAM_MOUTH_OPEN_Y', mouthY);
        }
      } catch (e) {
        console.error("Error setting mouth:", e);
      }
    }
  },
  
  setExpression: (expressionIndex) => {
    try {
      expressionIndex = parseInt(expressionIndex);
      if (window.model2 && window.model2.internalModel && 
          window.model2.internalModel.motionManager && 
          window.model2.internalModel.motionManager.expressionManager) {
        window.model2.internalModel.motionManager.expressionManager.setExpression(expressionIndex);
      }
    } catch (e) {
      console.error("Error setting expression:", e);
    }
  }
};

// Helper function to convert paths to file:// URLs
function pathToFileURL(path) {
  const normalizedPath = path.replace(/\\/g, '/');
  
  if (normalizedPath.match(/^[A-Za-z]:/)) {
    return `file:///${normalizedPath}`;
  } else if (normalizedPath.startsWith('/')) {
    return `file://${normalizedPath}`;
  } else {
    return `file:///${normalizedPath}`;
  }
}

// Super simple model loading - no dependencies, just loads the model
async function loadMinimalModel() {
  console.log("LOADING MINIMAL MODEL");
  
  try {
    // 1. Make sure PIXI is loaded
    if (!window.PIXI) {
      console.error("PIXI is not available!");
      return false;
    }
    
    // 2. Get the canvas element
    const canvas = document.getElementById("live2d-canvas");
    if (!canvas) {
      console.error("Canvas element not found!");
      return false;
    }
    
    // 3. Initialize PIXI application
    app = new PIXI.Application({
      view: canvas,
      autoStart: true,
      transparent: true,
      backgroundAlpha: 0
    });
    
    console.log("PIXI app created");
    
    // 4. Try multiple potential model locations
    const potentialModelPaths = [
      "static/desktop/models/default/default.model3.json",
      "desktop/models/default/default.model3.json",
      "models/default/default.model3.json",
      "static/desktop/models/test-model/test.model3.json"
    ];
    
    let loadedModel = null;
    
    // Try each path until one works
    for (const modelPath of potentialModelPaths) {
      try {
        const modelUrl = pathToFileURL(modelPath);
        console.log(`Trying to load model from: ${modelUrl}`);
        
        const loadedModels = await Promise.all([
          PIXI.live2d.Live2DModel.from(modelUrl, { 
            autoInteract: false, 
            autoUpdate: true 
          })
        ]);
        
        if (loadedModels && loadedModels[0]) {
          loadedModel = loadedModels[0];
          console.log(`Successfully loaded model from ${modelPath}`);
          break;
        }
      } catch (err) {
        console.log(`Failed to load from ${modelPath}:`, err);
      }
    }
    
    if (!loadedModel) {
      console.error("Failed to load model from any path");
      return false;
    }
    
    // 5. Add model to stage and set up
    app.stage.addChild(loadedModel);
    
    // Position in center of screen with good scale
    const vw = app.view.width;
    const vh = app.view.height;
    const scale = Math.min(vw, vh) * 0.0005; // Adjust scaling factor as needed
    
    loadedModel.x = vw / 2;
    loadedModel.y = vh / 2;
    loadedModel.scale.set(scale);
    
    // Store globally for access
    window.model2 = loadedModel;
    model2 = loadedModel;
    
    console.log("Model loaded and positioned successfully");
    return true;
  } catch (error) {
    console.error("Error in loadMinimalModel:", error);
    return false;
  }
}

// Initialize as early as possible with multiple fallbacks
function initializeWithRetry(maxRetries = 5) {
  let retryCount = 0;
  let retryDelay = 500;
  
  function attemptLoad() {
    console.log(`Attempt #${retryCount + 1} to load Live2D model`);
    
    loadMinimalModel().then(success => {
      if (success) {
        console.log("Live2D model loaded successfully!");
      } else if (retryCount < maxRetries) {
        retryCount++;
        console.log(`Retrying in ${retryDelay}ms... (${maxRetries - retryCount} attempts remaining)`);
        setTimeout(attemptLoad, retryDelay);
        retryDelay *= 1.5; // Exponential backoff
      } else {
        console.error("Failed to load Live2D model after multiple attempts");
      }
    }).catch(err => {
      console.error("Error during model loading attempt:", err);
      
      if (retryCount < maxRetries) {
        retryCount++;
        console.log(`Retrying after error in ${retryDelay}ms... (${maxRetries - retryCount} attempts remaining)`);
        setTimeout(attemptLoad, retryDelay);
        retryDelay *= 1.5;
      } else {
        console.error("Failed to load Live2D model after multiple attempts");
      }
    });
  }
  
  // Start the first attempt
  attemptLoad();
}

// Compatibility with existing code
window.setMouth = window.live2dController.setMouth;
window.setExpression = window.live2dController.setExpression;

// Ensure we initialize as soon as possible with multiple approaches
(function() {
  console.log("Immediate Live2D initialization");
  
  // Start immediately if possible
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    console.log("Document already ready, initializing immediately");
    setTimeout(() => initializeWithRetry(), 100);
  }
  
  // Also hook into DOMContentLoaded
  document.addEventListener('DOMContentLoaded', () => {
    console.log("DOMContentLoaded event fired");
    initializeWithRetry();
  });
  
  // Final fallback with window.onload
  window.addEventListener('load', () => {
    console.log("Window load event fired");
    initializeWithRetry();
  });
})();
```

### 2. In `desktop.html`, ensure the scripts are loaded in the correct order:

Make sure the scripts section looks like this:

```html
<!-- Dependencies first -->
<script src="libs/live2dcubismcore.min.js"></script>
<script src="libs/pixi.min.js"></script>
<script src="libs/live2d.min.js"></script>
<script src="libs/index.min.js"></script>
<script src="libs/bundle.min.js"></script>

<!-- Only after all dependencies, load the app scripts -->
<script src="desktop/task_queue.js"></script>
<script src="desktop/live2d.js"></script>
<script src="desktop/websocket.js"></script>
<script src="desktop/reconnect.js"></script>
<script src="desktop/vad.js"></script>
<script src="desktop/audio.js"></script>
<script src="desktop/electron.js"></script>
<script src="desktop/diagnostics.js"></script>
```

### 3. Add a diagnostic page to debug model loading:

Create a new file `model-debug.html` in the `static` directory:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Live2D Model Debug</title>
  <style>
    body { background-color: #333; color: white; font-family: Arial, sans-serif; }
    #live2d-stage { width: 500px; height: 500px; margin: 0 auto; border: 1px solid #666; }
    #live2d-canvas { width: 100%; height: 100%; }
    #debug-output { margin: 20px auto; max-width: 800px; white-space: pre-wrap; background: #222; padding: 15px; }
    button { padding: 8px 16px; margin: 5px; cursor: pointer; }
  </style>
  
  <!-- Include only the essential libraries -->
  <script src="libs/live2dcubismcore.min.js"></script>
  <script src="libs/pixi.min.js"></script>
  <script src="libs/live2d.min.js"></script>
  <script src="libs/index.min.js"></script>
</head>
<body>
  <h1>Live2D Model Debug</h1>
  
  <div id="controls">
    <button id="load-default">Load Default Model</button>
    <button id="load-test">Load Test Model</button>
    <button id="check-paths">Check Model Paths</button>
  </div>
  
  <div id="live2d-stage">
    <canvas id="live2d-canvas"></canvas>
  </div>
  
  <div id="debug-output">Debug information will appear here...</div>
  
  <script>
    // Debug helpers
    const debugOutput = document.getElementById('debug-output');
    function log(message) {
      console.log(message);
      debugOutput.textContent += message + "\n";
    }
    
    // Basic PIXI initialization
    let app;
    let model;
    
    function initPIXI() {
      log("Initializing PIXI...");
      
      const canvas = document.getElementById("live2d-canvas");
      if (!canvas) {
        log("ERROR: Canvas not found!");
        return false;
      }
      
      try {
        app = new PIXI.Application({
          view: canvas,
          autoStart: true,
          transparent: true,
          backgroundAlpha: 0
        });
        
        log("PIXI initialized successfully");
        return true;
      } catch (error) {
        log(`ERROR initializing PIXI: ${error.message}`);
        return false;
      }
    }
    
    // Function to convert path to file URL
    function pathToFileURL(path) {
      const normalizedPath = path.replace(/\\/g, '/');
      if (normalizedPath.match(/^[A-Za-z]:/)) {
        return `file:///${normalizedPath}`;
      } else if (normalizedPath.startsWith('/')) {
        return `file://${normalizedPath}`;
      } else {
        return `file:///${normalizedPath}`;
      }
    }
    
    // Check PIXI and Live2D are loaded
    function checkDependencies() {
      log("Checking dependencies...");
      
      if (!window.PIXI) {
        log("ERROR: PIXI is not loaded!");
        return false;
      }
      
      if (!window.PIXI.live2d) {
        log("ERROR: PIXI Live2D plugin is not loaded!");
        return false;
      }
      
      log("All dependencies loaded correctly");
      return true;
    }
    
    // Function to load a model from path
    async function loadModel(modelPath) {
      log(`Attempting to load model from: ${modelPath}`);
      
      if (!app) {
        const initialized = initPIXI();
        if (!initialized) return false;
      }
      
      // Clear existing model
      if (model) {
        log("Removing existing model");
        app.stage.removeChild(model);
        model.destroy();
        model = null;
      }
      
      try {
        const modelUrl = pathToFileURL(modelPath);
        log(`Loading from URL: ${modelUrl}`);
        
        const loadedModel = await PIXI.live2d.Live2DModel.from(modelUrl, {
          autoInteract: false,
          autoUpdate: true
        });
        
        if (!loadedModel) {
          log("ERROR: Model loading returned null or undefined");
          return false;
        }
        
        log("Model loaded successfully");
        
        // Add to stage
        app.stage.addChild(loadedModel);
        
        // Position in center
        loadedModel.x = app.view.width / 2;
        loadedModel.y = app.view.height / 2;
        loadedModel.scale.set(0.3); // Adjust as needed
        
        model = loadedModel;
        return true;
      } catch (error) {
        log(`ERROR loading model: ${error.message}`);
        if (error.stack) log(`Stack: ${error.stack}`);
        return false;
      }
    }
    
    // Check all potential model paths
    async function checkModelPaths() {
      log("Checking potential model paths...");
      
      const potentialPaths = [
        "static/desktop/models/default/default.model3.json",
        "desktop/models/default/default.model3.json",
        "models/default/default.model3.json",
        "static/desktop/models/test-model/test.model3.json",
        "../static/desktop/models/default/default.model3.json"
      ];
      
      for (const path of potentialPaths) {
        log(`Checking path: ${path}`);
        
        try {
          const modelUrl = pathToFileURL(path);
          log(`URL: ${modelUrl}`);
          
          // Try to fetch to see if file exists
          if (window.fetch) {
            try {
              const response = await fetch(modelUrl);
              log(`Fetch status: ${response.status} ${response.statusText}`);
              if (response.ok) {
                log(`✓ Path is accessible: ${path}`);
              } else {
                log(`✗ Path is not accessible: ${path}`);
              }
            } catch (fetchError) {
              log(`✗ Fetch error: ${fetchError.message}`);
            }
          } else {
            log("Fetch API not available");
          }
        } catch (error) {
          log(`Error checking path ${path}: ${error.message}`);
        }
      }
      
      log("Path check complete");
    }
    
    // Initialize and set up buttons
    document.addEventListener('DOMContentLoaded', () => {
      log("Debug page loaded");
      checkDependencies();
      
      document.getElementById('load-default').addEventListener('click', () => {
        loadModel("desktop/models/default/default.model3.json");
      });
      
      document.getElementById('load-test').addEventListener('click', () => {
        loadModel("desktop/models/test-model/test.model3.json");
      });
      
      document.getElementById('check-paths').addEventListener('click', () => {
        checkModelPaths();
      });
      
      // Auto-init PIXI
      initPIXI();
    });
  </script>
</body>
</html>
```

## Steps to Implement This Solution

1. **Replace the live2d.js file** with the minimal implementation above
2. **Check the script order** in desktop.html to ensure proper loading sequence
3. **Test with the diagnostic page** by loading model-debug.html directly in a browser

## Why This Approach Works

This minimal implementation:

1. **Tries multiple model paths** to find one that works
2. **Retries loading** several times with exponential backoff
3. **Initializes as early as possible** using multiple event hooks
4. **Has robust error handling** that won't silently fail
5. **Works independently** of other systems like WebSocket

## What's Different from the Original Implementation

1. **No dependencies on other modules** - This is a standalone solution
2. **Multiple initialization attempts** at different points in page lifecycle
3. **Multiple model path attempts** to find a working model
4. **Simplified positioning logic** that works regardless of model dimensions
5. **Comprehensive error handling** with retry logic

If this doesn't work, use the diagnostic page to identify exactly where the issue is occurring, which will help pinpoint the specific problem in your environment.