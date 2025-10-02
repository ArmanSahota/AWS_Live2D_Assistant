# Live2D Debugging Tool

This document contains the HTML code for a Live2D model debugging tool that can be used to diagnose and fix model loading issues.

## How to Use This Tool

1. Create a new file called `model-debug.html` in the `static` directory
2. Copy the HTML code below into that file
3. Open the file in a browser to test Live2D model loading independently of the Electron app
4. Use the buttons to test different model paths and diagnose issues

## HTML Code for model-debug.html

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

## How This Helps

This standalone debugging tool helps identify:

1. If the Live2D libraries are loading correctly
2. If the model files can be found in the expected paths
3. If there are any errors during model loading

By running this separately from the main application, you can isolate model loading problems from other issues in the application.

## Additional Debugging Steps

Once you've identified the correct model path using this tool, you can apply that knowledge to fix the `live2d.js` implementation using the minimal implementation provided in the `live2d-minimal-implementation.md` file.

## Common Issues This Tool Helps Diagnose

1. **Library Loading Issues**: If PIXI or Live2D libraries aren't loading
2. **Path Resolution Problems**: If the model files can't be found
3. **Model Format Issues**: If the model files are corrupt or incompatible
4. **WebGL Issues**: If there are rendering context problems
5. **Initialization Timing Issues**: By testing in isolation