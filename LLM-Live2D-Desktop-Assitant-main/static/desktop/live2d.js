var app;
var modelInfo, emoMap;
window.model2 = null; // Expose model2 to the global window object

window.live2dModule = (function () {
    const live2d = PIXI.live2d;

    async function init() {
        app = new PIXI.Application({
            view: document.getElementById("live2d-canvas"),
            autoStart: true,
            resizeTo: document.getElementById("live2d-stage"),
            transparent: true,
            backgroundAlpha: 0,
        });

        console.log("Live2D app initialized with canvas:", document.getElementById("live2d-canvas"));
        console.log("Live2D stage element:", document.getElementById("live2d-stage"));
        
        // await loadModel();
    }

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
            autoHitTest: false,
            autoFocus: false,
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
        
        // Add a base URL to ensure the model is loaded from the correct location
        // This is critical for Electron to resolve the path correctly
        if (!modelUrl.startsWith('http') && !modelUrl.startsWith('file:')) {
            const baseUrl = window.location.href.substring(0, window.location.href.lastIndexOf('/') + 1);
            modelUrl = new URL(modelUrl, baseUrl).href;
            
            // Fix duplicate 'static' in path if present
            modelUrl = modelUrl.replace(/\/static\/static\//g, '/static/');
            modelUrl = modelUrl.replace(/\\static\\static\\/g, '\\static\\');
            
            // Also check for file:// URLs with duplicate static
            modelUrl = modelUrl.replace(/file:\/\/.*\/static\/static\//g, (match) => {
                return match.replace('/static/static/', '/static/');
            });
            console.log("DEBUG: Resolved model URL with base:", modelUrl);
        }
    }

        try {
            console.log("DEBUG: Attempting to load model from:", modelUrl);
            const models = await Promise.all([
                live2d.Live2DModel.from(modelUrl, options),
            ]);

            models.forEach((model) => {
                app.stage.addChild(model);

                const vw = app.view.width;
                const vh = app.view.height;
                const naturalW = model.width || 1;
                const naturalH = model.height || 1;
                
                // Scale to fit with 10% margin
                const scale = Math.min(vw / naturalW, vh / naturalH) * 0.9;
                model.scale.set(scale);
                
                // Set center anchor
                model.anchor.set(0.5, 0.5);
                model.position.set(vw / 2, vh / 2);

                makeDraggable(model);
                setupMouseEvents(model);
            });

            window.model2 = models[0]; // Assign to window.model2 instead of local model2
            model2 = window.model2; // Keep local reference for compatibility

            if (!modelInfo.initialXshift) modelInfo.initialXshift = 0;
            if (!modelInfo.initialYshift) modelInfo.initialYshift = 0;

            // Position adjustments are now handled by the anchor and position settings above
            // We'll keep the shift values for minor adjustments if needed
            if (modelInfo.initialXshift) {
                model2.x += modelInfo.initialXshift;
            }
            if (modelInfo.initialYshift) {
                model2.y += modelInfo.initialYshift;
            }

            model2.internalModel.eyeBlink = null;
            console.log("DEBUG: Model loaded successfully");
            return models[0];
        } catch (error) {
            console.error("DEBUG: Error loading model:", error);
            console.error("DEBUG: Error stack:", error.stack);
            throw error;
        }
    }

    function makeDraggable(model) {
        model.interactive = true;
        model.buttonMode = true;
        
        // Add a cursor style to indicate the model is draggable
        model.cursor = 'grab';
        
        // Store original alpha to restore after dragging
        const originalAlpha = model.alpha;
        
        model.on("pointerdown", (e) => {
            if (e.data.button !== 0) return; // Only left mouse button
            
            // Change cursor style when dragging
            model.cursor = 'grabbing';
            
            // Make model slightly transparent while dragging
            model.alpha = 0.8;
            
            model.dragging = true;
            model._pointerX = e.data.global.x - model.x;
            model._pointerY = e.data.global.y - model.y;
            
            // Bring model to front while dragging
            if (model.parent) {
                const index = model.parent.children.indexOf(model);
                if (index !== model.parent.children.length - 1) {
                    model.parent.addChildAt(model, model.parent.children.length - 1);
                }
            }
            
            // Prevent default to avoid text selection
            e.stopPropagation();
        });

        model.on("pointermove", (e) => {
            if (model.dragging) {
                // Calculate new position without boundaries
                const newX = e.data.global.x - model._pointerX;
                const newY = e.data.global.y - model._pointerY;
                
                // Set position without boundaries - allow dragging anywhere
                model.position.x = newX;
                model.position.y = newY;
            }
        });

        model.on("pointerupoutside", () => {
            model.dragging = false;
            model.cursor = 'grab';
            model.alpha = originalAlpha;
        });
        
        model.on("pointerup", () => {
            model.dragging = false;
            model.cursor = 'grab';
            model.alpha = originalAlpha;
        });
    }

    function setupMouseEvents(model) {
        // Add a tooltip to indicate the model is draggable
        const tooltip = document.createElement('div');
        tooltip.textContent = 'Drag me!';
        tooltip.style.position = 'absolute';
        tooltip.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        tooltip.style.color = 'white';
        tooltip.style.padding = '5px 10px';
        tooltip.style.borderRadius = '5px';
        tooltip.style.fontSize = '12px';
        tooltip.style.zIndex = '1000';
        tooltip.style.pointerEvents = 'none';
        tooltip.style.opacity = '0';
        tooltip.style.transition = 'opacity 0.3s ease';
        document.body.appendChild(tooltip);
        
        // Show tooltip on hover
        model.on("pointerover", (e) => {
            const stage = document.getElementById("live2d-stage");
            const stageRect = stage.getBoundingClientRect();
            
            tooltip.style.left = `${e.data.global.x}px`;
            tooltip.style.top = `${e.data.global.y - 30}px`;
            tooltip.style.opacity = '1';
            
            // Ensure we can interact with the model
            window.electronAPI.setIgnoreMouseEvents(false);
        });

        model.on("pointermove", (e) => {
            if (!model.dragging) {
                tooltip.style.left = `${e.data.global.x}px`;
                tooltip.style.top = `${e.data.global.y - 30}px`;
            } else {
                // Hide tooltip while dragging
                tooltip.style.opacity = '0';
            }
        });

        model.on("pointerout", () => {
            // Hide tooltip
            tooltip.style.opacity = '0';
            
            // Only ignore mouse events if we're not dragging
            if (!model.dragging) {
                window.electronAPI.setIgnoreMouseEvents(true);
            }
        });
        
        // Handle right-click for context menu
        model.on("rightdown", (e) => {
            const x = e.data.originalEvent.clientX;
            const y = e.data.originalEvent.clientY;
            window.electronAPI.showContextMenu(x, y);
            e.stopPropagation();
        });
    }

    return {
        init,
        loadModel
    };
})();

// Helper function to convert file:// URLs to paths
function fileURLToPath(url) {
  if (url.startsWith('file://')) {
    // Remove file:// prefix and decode URI components
    return decodeURIComponent(url.substring(url.startsWith('file:///') ? 8 : 7));
  }
  return url;
}

// Helper function to convert paths to file:// URLs
function pathToFileURL(path) {
  // Ensure path uses forward slashes
  const normalizedPath = path.replace(/\\/g, '/');
  
  // Add file:// prefix (with triple slash for absolute paths)
  if (normalizedPath.match(/^[A-Za-z]:/)) {
    // Windows path with drive letter
    return `file:///${normalizedPath}`;
  } else if (normalizedPath.startsWith('/')) {
    // Unix absolute path
    return `file://${normalizedPath}`;
  } else {
    // Relative path
    return `file:///${normalizedPath}`;
  }
}

// Helper function to join paths
function joinPath(...parts) {
  return parts.join('/').replace(/\/+/g, '/');
}

// Fixed model configuration loading that uses correct paths
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

// Boot Live2D independently of WebSocket connection
async function bootLive2D() {
  console.log("Booting Live2D model");
  console.log("DEBUG: Starting Live2D initialization process");
  try {
    console.log("DEBUG: Starting Live2D initialization in bootLive2D()");
    await window.live2dModule.init();
    console.log("DEBUG: window.live2dModule.init() completed successfully");
    
    // Get model config using our new system
    console.log("DEBUG: Getting model config");
    const modelConfig = await getDefaultModelConfig();
    console.log("Loading Live2D model with config:", modelConfig);
    
    if (!modelConfig.url) {
      console.error("DEBUG: Model URL is undefined or empty");
      document.getElementById("message").textContent = "Error: Invalid model URL";
      return false;
    }
    
    console.log("DEBUG: About to call window.live2dModule.loadModel()");
    await window.live2dModule.loadModel(modelConfig);
    console.log("Live2D model loaded successfully");
    
    // Set initial state
    document.getElementById("message").textContent = "Ready";
    return true;
  } catch (error) {
    console.error("Failed to initialize Live2D model:", error);
    console.error("DEBUG: Error stack:", error.stack);
    console.error("DEBUG: Error occurred during Live2D initialization");
    document.getElementById("message").textContent = "Error loading model";
    return false;
  }
}

// Initialize Live2D on page load - no longer depends on WebSocket
window.addEventListener('DOMContentLoaded', async () => {
  console.log("Initializing Live2D model on page load");
  await bootLive2D();
});

function setExpression(expressionIndex) {
  expressionIndex = parseInt(expressionIndex);
  if (window.model2 && window.model2.internalModel.motionManager.expressionManager) {
      window.model2.internalModel.motionManager.expressionManager.setExpression(expressionIndex);
      console.info(`>> [x] -> Expression set to: (${expressionIndex})`);
  }
}

function setMouth(mouthY) {
  if (window.model2 && window.model2.internalModel.coreModel) {
      if (typeof window.model2.internalModel.coreModel.setParameterValueById === 'function') {
          window.model2.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', mouthY);
      } else {
          window.model2.internalModel.coreModel.setParamFloat('PARAM_MOUTH_OPEN_Y', mouthY);
      }
  }
}

window.setExpression = setExpression;
window.setMouth = setMouth;
