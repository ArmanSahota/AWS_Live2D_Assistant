# How to Apply the Live2D Model Fix

This guide will walk you through applying the fixes from the `immediate-model-fix.md` file to your actual code.

## Step 1: Open the Live2D JavaScript File

1. Open the file at: `LLM-Live2D-Desktop-Assitant-main/static/desktop/live2d.js` in your code editor.

## Step 2: Replace the getDefaultModelConfig Function

1. Find the function called `getDefaultModelConfig` in the file. It should be around line 257 and look something like:

```javascript
async function getDefaultModelConfig() {
  try {
    console.log("DEBUG: Getting default model config");
    // First try to get config from app config
    if (window.electronAPI) {
      console.log("DEBUG: window.electronAPI is available, trying to get config");
      const config = await window.electronAPI.getConfig();
      console.log("DEBUG: Got config from electronAPI:", config);
      if (config && config.live2d) {
        console.log("Using Live2D config from app config:", config.live2d);
        return {
          url: config.live2d.defaultModel,
          kScale: config.live2d.scale || 0.15,
          initialXshift: config.live2d.initialXshift || 0,
          initialYshift: config.live2d.initialYshift || 0,
          emotionMap: config.live2d.emotionMap || {}
        };
      }
    }
    
    // If that fails, use the models API
    if (window.models) {
      console.log("DEBUG: App config doesn't have live2d settings, falling back to models API");
      console.log("DEBUG: window.models is available:", window.models);
      const defaultModel = await window.models.getDefault();
      console.log("Using default model from models API:", defaultModel);
      
      if (defaultModel) {
        let modelPath;
        
        // If we have a model3 path directly, use it
        if (defaultModel.model3) {
          modelPath = defaultModel.model3;
        }
        // Otherwise try to load from conf.yml (not implemented yet)
        else if (defaultModel.conf) {
          // In a real implementation, we would parse the YAML here
          // For now, just use the model3 path
          modelPath = defaultModel.model3;
        }
        
        if (modelPath) {
          // Convert to URL for the Live2D loader
          const modelUrl = pathToFileURL(modelPath);
          
          return {
            url: modelUrl,
            kScale: 0.15,
            initialXshift: 0,
            initialYshift: 0,
            emotionMap: {}
          };
        }
      }
    }
  } catch (error) {
    console.error("Error getting Live2D model config:", error);
  }
  
  // Fallback to default config - this should rarely happen now
  console.warn("No model found, using fallback config");
  return {
    url: "live2d-models/elaina/elaina.model3.json",
    kScale: 0.15,
    initialXshift: 0,
    initialYshift: 0,
    emotionMap: {}
  };
}
```

2. Replace it with this new version:

```javascript
async function getDefaultModelConfig() {
  try {
    console.log("DEBUG: Getting default model config");
    
    // CRITICAL FIX: Directly use the known model path
    // We can see from the error logs that you're working in D:\AWS_Vtuber_LLM - Copy\LLM-Live2D-Desktop-Assitant-main\
    // And we know the models are in static/desktop/models/
    
    // First try - Direct path to the default model we know exists
    const defaultModelPath = "static/desktop/models/default/default.model3.json";
    console.log(`DEBUG: Using direct path to default model: ${defaultModelPath}`);
    
    return {
      url: defaultModelPath,  // Don't use pathToFileURL yet - that's done in loadModel
      kScale: 0.15,
      initialXshift: 0,
      initialYshift: 0,
      emotionMap: {}
    };
  } catch (error) {
    console.error("Error getting Live2D model config:", error);
    
    // EMERGENCY FALLBACK - Use exact paths for models
    console.warn("Using emergency fallback path");
    return {
      url: "static/desktop/models/default/default.model3.json",  // This should exist
      kScale: 0.15,
      initialXshift: 0,
      initialYshift: 0,
      emotionMap: {}
    };
  }
}
```

## Step 3: Modify the loadModel Function

1. Find the `loadModel` function. It should look something like this:

```javascript
async function loadModel(modelInfo = {}) {
    console.log("DEBUG: loadModel called with modelInfo:", JSON.stringify(modelInfo));
    emoMap = modelInfo["emotionMap"];

    if (window.model2) {
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

    try {
        console.log("DEBUG: Attempting to load model from:", modelUrl);
        const models = await Promise.all([
            live2d.Live2DModel.from(modelUrl, options),
        ]);

        // ...rest of function...
    } catch (error) {
        console.error("DEBUG: Error loading model:", error);
        console.error("DEBUG: Error stack:", error.stack);
        throw error;
    }
}
```

2. Modify the URL handling part to look like this:

```javascript
async function loadModel(modelInfo = {}) {
    console.log("DEBUG: loadModel called with modelInfo:", JSON.stringify(modelInfo));
    emoMap = modelInfo["emotionMap"];

    if (window.model2) {
        app.stage.removeChild(window.model2);
        window.model2.destroy({ children: true, texture: true, baseTexture: true });
        window.model2 = null;
        model2 = null;
    }

    const options = {
        autoInteract: false,
        autoUpdate: true,
    };

    // Make sure the URL is valid - FIX THE PATH RESOLUTION HERE
    let modelUrl = modelInfo.url;
    console.log("DEBUG: Original model URL:", modelUrl);
    
    // CRITICAL FIX: Better path handling
    // Don't convert to file:/// URL which causes path issues
    // Just use relative paths which work better with Electron
    if (modelUrl) {
        // Clean up any leading slashes that might cause path resolution issues
        modelUrl = modelUrl.replace(/^\/+/, '');
        console.log("DEBUG: Using model URL:", modelUrl);
    }

    try {
        console.log("DEBUG: Attempting to load model from:", modelUrl);
        const models = await Promise.all([
            live2d.Live2DModel.from(modelUrl, options),
        ]);

        // ...rest of function should remain the same...
```

Only change the URL handling part - keep the rest of the function exactly as it is.

## Step 4: Save and Test

1. Save the file after making these changes
2. Restart your Electron app
3. Check if the Live2D model loads correctly now

## Verifying the Fix

When the app loads:

1. You should see log messages in the console like:
   ```
   DEBUG: Using direct path to default model: static/desktop/models/default/default.model3.json
   DEBUG: Original model URL: static/desktop/models/default/default.model3.json
   DEBUG: Using model URL: static/desktop/models/default/default.model3.json
   ```

2. The model should load and appear on screen

3. You should NOT see errors like:
   ```
   GET file:///live2d-models/elaina/elaina.model3.json net::ERR_FILE_NOT_FOUND
   ```

## If You Still Have Issues

If the model still doesn't load after applying these fixes:

1. Check the console for new errors
2. Verify that the model files actually exist at `static/desktop/models/default/default.model3.json`
3. Try using the standalone debug page from the `live2d-debug-tool.md` document to test model loading independently
4. Consider implementing the complete minimal version from the `live2d-minimal-implementation.md` document

## Additional Notes

- The key issue was that the path resolution was using `file:///` URLs which were causing problems
- The fix directly uses relative paths which Electron handles better
- We bypass the complex resolution chain that was failing
- This fix addresses model loading but there are other issues noted in the console logs that might need attention later