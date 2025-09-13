# Live2D Refactoring Implementation Guide

This document provides detailed instructions for refactoring the Live2D integration to meet the following requirements:
1. Auto-initialize the Live2D model when the Electron app loads
2. Ensure the model is separate from the LLM
3. Create a clean pipeline where STT input flows to LLM and then the system feeds back TTS output

## 1. Modifying `live2d.js`

Replace the current `live2d.js` with the following implementation:

```javascript
/**
 * Enhanced Live2D Module
 * Auto-initializes and provides a clean interface independent of LLM
 */
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
        // Keep existing makeDraggable implementation
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
        // Keep existing setupMouseEvents implementation
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

/**
 * Enhanced model configuration loading - completely independent of WebSocket
 */
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
        // Otherwise try to resolve it using the models API
        else if (defaultModel.conf) {
          try {
            modelPath = await window.models.resolvePath(defaultModel);
            if (!modelPath) {
              // Fallback to default path based on model directory
              modelPath = `${defaultModel.dir}/default.model3.json`;
            }
          } catch (e) {
            console.warn("Failed to resolve model path:", e);
            // Fallback path
            modelPath = `${defaultModel.dir}/default.model3.json`;
          }
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
  
  // Fallback to default config with hardcoded path as last resort
  console.warn("No model found, using fallback config");
  
  // Try multiple possible locations
  const possiblePaths = [
    "static/desktop/models/default/default.model3.json",
    "desktop/models/default/default.model3.json", 
    "models/default/default.model3.json"
  ];
  
  for (const path of possiblePaths) {
    try {
      return {
        url: pathToFileURL(path),
        kScale: 0.15,
        initialXshift: 0,
        initialYshift: 0,
        emotionMap: {}
      };
    } catch (e) {
      console.warn(`Tried path ${path}, but failed:`, e);
    }
  }
  
  // Ultimate fallback
  return {
    url: "live2d-models/elaina/elaina.model3.json",
    kScale: 0.15,
    initialXshift: 0,
    initialYshift: 0,
    emotionMap: {}
  };
}

/**
 * Enhanced bootLive2D with retries and better error handling
 * Completely independent of WebSocket connections
 */
async function bootLive2D(retryCount = 3, retryDelay = 1000) {
  console.log("Booting Live2D model");
  console.log("DEBUG: Starting Live2D initialization process");
  try {
    console.log("DEBUG: Starting Live2D initialization in bootLive2D()");
    await window.live2dModule.init();
    console.log("DEBUG: window.live2dModule.init() completed successfully");
    
    // Get model config using our enhanced system
    console.log("DEBUG: Getting model config");
    const modelConfig = await getDefaultModelConfig();
    console.log("Loading Live2D model with config:", modelConfig);
    
    if (!modelConfig.url) {
      console.error("DEBUG: Model URL is undefined or empty");
      document.getElementById("message").textContent = "Error: Invalid model URL";
      
      if (retryCount > 0) {
        console.log(`Retrying in ${retryDelay}ms... (${retryCount} attempts left)`);
        return new Promise(resolve => {
          setTimeout(() => resolve(bootLive2D(retryCount - 1, retryDelay * 1.5)), retryDelay);
        });
      }
      
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
    
    if (retryCount > 0) {
      console.log(`Retrying in ${retryDelay}ms... (${retryCount} attempts left)`);
      return new Promise(resolve => {
        setTimeout(() => resolve(bootLive2D(retryCount - 1, retryDelay * 1.5)), retryDelay);
      });
    }
    
    return false;
  }
}

/**
 * Expose a global Live2D controller API that other modules can use
 * This is key for the separation between Live2D and LLM
 */
window.live2dController = {
  // Control mouth movement (used by TTS module)
  setMouth: (mouthY) => {
    if (window.model2 && window.model2.internalModel.coreModel) {
      if (typeof window.model2.internalModel.coreModel.setParameterValueById === 'function') {
        window.model2.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', mouthY);
      } else {
        window.model2.internalModel.coreModel.setParamFloat('PARAM_MOUTH_OPEN_Y', mouthY);
      }
    }
  },
  
  // Set expression (used for emotional responses)
  setExpression: (expressionIndex) => {
    expressionIndex = parseInt(expressionIndex);
    if (window.model2 && window.model2.internalModel.motionManager.expressionManager) {
      window.model2.internalModel.motionManager.expressionManager.setExpression(expressionIndex);
      console.info(`>> [x] -> Expression set to: (${expressionIndex})`);
    }
  },
  
  // Reset to idle state
  resetToIdle: () => {
    window.live2dController.setExpression(0);
    window.live2dController.setMouth(0);
  },
  
  // Animation sequence player
  animate: (animationData) => {
    if (!window.model2 || !animationData) return;
    
    // Process animation sequence with mouth movements
    if (animationData.mouthData && Array.isArray(animationData.mouthData)) {
      let index = 0;
      const interval = setInterval(() => {
        if (index >= animationData.mouthData.length) {
          clearInterval(interval);
          window.live2dController.setMouth(0); // Reset mouth
          return;
        }
        window.live2dController.setMouth(animationData.mouthData[index]);
        index++;
      }, 33); // ~30fps
    }
    
    // Process expression changes
    if (animationData.expressions && Array.isArray(animationData.expressions)) {
      animationData.expressions.forEach(exp => {
        if (exp.time && exp.id !== undefined) {
          setTimeout(() => {
            window.live2dController.setExpression(exp.id);
          }, exp.time);
        }
      });
    }
  },
  
  // Load a new model
  loadModel: async (modelConfig) => {
    return await window.live2dModule.loadModel(modelConfig);
  }
};

// Initialize Live2D on page load - high priority, independent of other services
document.addEventListener('DOMContentLoaded', async () => {
  console.log("Initializing Live2D model on page load - high priority");
  setTimeout(async () => {
    await bootLive2D();
  }, 0);
});

// Backup initialization if DOMContentLoaded already fired
if (document.readyState === 'complete' || document.readyState === 'interactive') {
  console.log("Document already loaded - initializing Live2D model now");
  setTimeout(async () => {
    await bootLive2D();
  }, 0);
}

// Map original functions to controller for backward compatibility
window.setExpression = window.live2dController.setExpression;
window.setMouth = window.live2dController.setMouth;
```

## 2. Modifying `websocket.js` 

Update the WebSocket message handling to ensure proper separation between model and LLM:

```javascript
// Modify the handleMessage function in websocket.js
function handleMessage(message) {
    console.log("Received Message: ", message);
    try {
        switch (message.type) {
            case "full-text":
                document.getElementById("message").textContent = message.text;
                console.log("full-text: ", message.text);
                // Force a UI update
                setTimeout(() => {
                    // Try to ensure the message is displayed
                    if (document.getElementById("message").textContent === "Thinking...") {
                        console.log("Message still showing 'Thinking...', forcing update");
                        document.getElementById("message").textContent = message.text || "Ready";
                    }
                }, 1000);
                break;
            case "control":
                switch (message.text) {
                    case "start-mic":
                        window.start_mic();
                        break;
                    case "stop-mic":
                        window.stop_mic();
                        break;
                    case "conversation-chain-start":
                        setState("thinking-speaking");
                        window.fullResponse = "";
                        window.audioTaskQueue = new TaskQueue(20);
                        // Update the message to show we're starting a conversation
                        document.getElementById("message").textContent = "Listening...";
                        break;
                    case "conversation-chain-end":
                        setState("idle");
                        window.live2dController.resetToIdle(); // Use our new controller API
                        // Force update the message to show we're done
                        document.getElementById("message").textContent = "Ready";
                        console.log("Conversation chain ended, updating message to 'Ready'");
                        if (!window.voiceInterruptionOn) {
                            window.start_mic();
                        }
                        break;
                }
                break;
            case "expression":
                window.live2dController.setExpression(message.text); // Use our new controller API
                break;
            case "mouth":
                window.live2dController.setMouth(Number(message.text)); // Use our new controller API
                break;
            case "audio":
                if (window.state == "interrupted") {
                    console.log("Audio playback intercepted. Sentence:", message.text);
                } else {
                    // Update the message text to show what the VTuber is saying
                    if (message.text) {
                        document.getElementById("message").textContent = message.text;
                        console.log("Updating message with audio text:", message.text);
                    }
                    
                    // Create animation data for Live2D
                    const animationData = {
                        mouthData: generateMouthData(message.audio), // This would be a function to analyze audio
                        expressions: message.expressions
                    };
                    
                    // Use our controller to animate the model
                    window.live2dController.animate(animationData);
                    
                    window.addAudioTask(message.audio, message.instrument, message.volumes, message.slice_length, message.text, message.expressions);
                }
                break;
            case "set-model":
                // Use our new controller API to load the model
                if (window.live2dController) {
                    console.log("Updating Live2D model with new configuration from WebSocket");
                    try {
                        // Try to parse the model config if it's a string
                        const modelConfig = typeof message.text === 'string' ? 
                            JSON.parse(message.text) : message.text;
                        
                        window.live2dController.loadModel(modelConfig).catch(error => {
                            console.error("Failed to load Live2D model:", error);
                        });
                    } catch (error) {
                        console.error("Error parsing model config:", error);
                        console.error("Raw model config:", message.text);
                    }
                } else {
                    console.error("Live2D controller not properly initialized");
                    // Boot Live2D as a fallback
                    if (window.bootLive2D) {
                        console.log("Attempting to initialize Live2D model using bootLive2D");
                        window.bootLive2D().catch(error => {
                            console.error("Failed to boot Live2D model:", error);
                        });
                    }
                }
                break;
            // Other cases remain unchanged...
        }
    } catch (error) {
        console.error("Error handling message:", error);
        console.error("Message that caused the error:", message);
    }
}

// Helper function to generate mouth animation data from audio
// This is a placeholder - real implementation would analyze audio frequency/volume
function generateMouthData(audioBase64) {
    // In a real implementation, this would analyze the audio
    // For now, just generate some simple mouth movements
    const mouthData = [];
    const duration = estimateAudioDuration(audioBase64);
    const framesCount = Math.floor(duration * 30); // 30fps
    
    for (let i = 0; i < framesCount; i++) {
        // Simple sine wave pattern for mouth movement
        const value = Math.sin(i * 0.2) * 0.5 + 0.5;
        mouthData.push(value);
    }
    
    return mouthData;
}

// Estimate audio duration from base64 data size (rough approximation)
function estimateAudioDuration(audioBase64) {
    // WAV 16-bit mono @ 22050Hz is about 44KB per second
    const bytes = atob(audioBase64).length;
    return bytes / 44000; // Approximate seconds
}
```

## 3. Modifying `electron.js`

Update the STT processing to properly separate it from the Live2D model:

```javascript
// Update the logSTTResult function in electron.js
window.logSTTResult = function(text) {
    console.log(`[STT] Transcription: "${text}"`);
    
    // Send to main process for logging in terminal
    if (window.electronAPI) {
        window.electronAPI.logTranscription(text);
    }
    
    // Update path ping
    updatePathPing('stt', true);
    
    // If we have text, try to send it to Claude
    if (text && text.trim().length > 0) {
        // Update path ping
        updatePathPing('stt-to-claude', 'pending');
        
        // Try to send to Claude via WebSocket if available
        if (window.ws && window.ws.readyState === WebSocket.OPEN) {
            try {
                window.ws.send(JSON.stringify({ 
                    type: "transcription", 
                    text: text 
                }));
                console.log("[STT] Sent transcription to WebSocket");
                updatePathPing('stt-to-claude', true);
            } catch (error) {
                console.error("[STT] Failed to send transcription to WebSocket:", error);
                updatePathPing('stt-to-claude', false);
                
                // Fallback to direct Claude API
                tryDirectClaudeAPI(text);
            }
        } else {
            console.log("[STT] WebSocket not available, using direct Claude API");
            updatePathPing('stt-to-claude', 'skipped');
            
            // Use direct Claude API
            tryDirectClaudeAPI(text);
        }
    }
};

// Update the audio processing to use the new Live2D controller API
async function generateAndPlaySpeech(text) {
    try {
        console.log("Generating speech for:", text);
        document.getElementById("message").textContent = text;
        
        // Update path ping
        updatePathPing('tts-generation', 'pending');
        
        const speechData = await window.api.generateSpeech(text);
        console.log("Speech generated, playing audio...");
        updatePathPing('tts-generation', true);
        
        // Update path ping
        updatePathPing('audio-playback', 'pending');
        
        // Generate animation data for the Live2D model
        const animationData = {
            mouthData: generateMouthData(speechData.base64),
            expressions: [] // Default empty expressions
        };
        
        // Animate the Live2D model independently of the LLM
        window.live2dController.animate(animationData);
        
        await window.addAudioTask(speechData.base64, null, null, null, text, null);
        console.log("Audio task added to queue");
        updatePathPing('audio-playback', true);
    } catch (error) {
        console.error("Error generating or playing speech:", error);
        updatePathPing('tts-generation', false);
        updatePathPing('audio-playback', false);
    }
}

// Helper function to generate mouth animation data
function generateMouthData(audioBase64) {
    // In a real implementation, this would analyze the audio
    // For now, just generate some simple mouth movements
    const mouthData = [];
    const duration = estimateAudioDuration(audioBase64);
    const framesCount = Math.floor(duration * 30); // 30fps
    
    for (let i = 0; i < framesCount; i++) {
        // Simple sine wave pattern for mouth movement
        const value = Math.sin(i * 0.2) * 0.5 + 0.5;
        mouthData.push(value);
    }
    
    return mouthData;
}

// Estimate audio duration from base64 data size (rough approximation)
function estimateAudioDuration(audioBase64) {
    // WAV 16-bit mono @ 22050Hz is about 44KB per second
    const bytes = atob(audioBase64).length;
    return bytes / 44000; // Approximate seconds
}
```

## 4. Testing the Implementation

After implementing these changes, you should test the application to ensure:

1. Live2D model loads immediately when the app starts
2. The model loads successfully even if WebSocket fails or LLM is unavailable
3. STT properly sends text to LLM
4. TTS output properly animates the Live2D model
5. The separation is clean with no direct dependencies between model and LLM

## 5. Advanced Audio Analysis for Better Mouth Movement

For a more accurate mouth animation, consider implementing a more sophisticated audio analysis:

```javascript
// Enhanced mouth movement generation based on audio amplitude analysis
function generateMouthDataFromAudio(audioBase64) {
    // Convert base64 to array buffer
    const binaryString = atob(audioBase64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    
    // Convert to audio buffer (would require Web Audio API)
    // This is a simplified example - real implementation would need more robust audio processing
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    return audioContext.decodeAudioData(bytes.buffer).then(audioBuffer => {
        // Get audio channel data
        const channelData = audioBuffer.getChannelData(0);
        const frameSize = Math.floor(audioBuffer.sampleRate / 30); // 30fps
        const mouthData = [];
        
        // Process in frames
        for (let i = 0; i < channelData.length; i += frameSize) {
            // Calculate RMS amplitude for this frame
            let sum = 0;
            for (let j = 0; j < frameSize && i + j < channelData.length; j++) {
                sum += channelData[i + j] * channelData[i + j];
            }
            const rms = Math.sqrt(sum / frameSize);
            
            // Map RMS to mouth openness (0-1 range)
            const mouthValue = Math.min(1, rms * 5); // Scaling factor may need adjustment
            mouthData.push(mouthValue);
        }
        
        return mouthData;
    });
}
```

This is more advanced and may require further adaptation to work within the context of the application, but it provides a more accurate mouth movement based on actual audio analysis.