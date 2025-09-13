// Initialize audio task queue if not already initialized
if (!window.audioTaskQueue) {
    window.audioTaskQueue = new TaskQueue(20);
}

// Handle direct Claude API calls
async function askClaudeDirectly(text) {
    try {
        console.log("Asking Claude directly via IPC:", text);
        setState("thinking-speaking");
        document.getElementById("message").textContent = "Thinking...";
        
        // Update path ping
        updatePathPing('claude-response', 'pending');
        
        const reply = await window.api.askClaude(text);
        console.log("Claude reply received:", reply);
        updatePathPing('claude-response', true);
        
        // Generate speech for the reply
        await generateAndPlaySpeech(reply);
        
        setState("idle");
        document.getElementById("message").textContent = "Ready";
        return reply;
    } catch (error) {
        console.error("Error asking Claude:", error);
        document.getElementById("message").textContent = "Error: " + error.message;
        setState("idle");
        updatePathPing('claude-response', false);
        throw error;
    }
}

// Generate speech and play it
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
        
        await window.addAudioTask(speechData.base64, null, null, null, text, null);
        console.log("Audio task added to queue");
        updatePathPing('audio-playback', true);
    } catch (error) {
        console.error("Error generating or playing speech:", error);
        updatePathPing('tts-generation', false);
        updatePathPing('audio-playback', false);
    }
}

// Expose functions to window
window.askClaudeDirectly = askClaudeDirectly;
window.generateAndPlaySpeech = generateAndPlaySpeech;

// Handle UI events
window.electronAPI.onToggleSubtitles((isChecked) => {
    const messageDiv = document.getElementById('message');
    if (isChecked) {
        messageDiv.classList.remove('hidden');
    } else {
        messageDiv.classList.add('hidden');
    }
});

window.electronAPI.onToggleWakeUp((isChecked) => {
    window.wakeWordDetectionOn = isChecked;
    if (isChecked) {
        window.start_wake_word_detection();
    } else {
        window.stop_wake_word_detection();
    }
});

window.electronAPI.onToggleMicrophone((isChecked) => {
    if (isChecked) {
        window.start_mic();
    } else {
        window.stop_mic();
    }
});

window.electronAPI.onToggleInterruption((isChecked) => {
    window.voiceInterruptionOn = isChecked;
});

window.electronAPI.onSwitchConfig((configFile) => {
   window.switchConfig(configFile);
});

window.electronAPI.setSensitivity((event, value) => {
    const sensitivityInput = document.getElementById('speechProbThreshold');
    if (sensitivityInput) {
        sensitivityInput.value = Math.round(value * 100);
        window.updateSensitivity(sensitivityInput.value);
    }
});

let isMouseOverModel = false;

// Add right-click event listener to show context menu
document.addEventListener('contextmenu', (event) => {
    event.preventDefault();
    window.electronAPI.showContextMenu(event.clientX, event.clientY);
});

// Enable mouse events for the test panel and model
document.addEventListener('mousemove', (event) => {
    const testPanel = document.getElementById('test-panel');
    const liveStage = document.getElementById('live2d-stage');
    
    // Check if mouse is over test panel or canvas
    const elementAtPoint = document.elementFromPoint(event.clientX, event.clientY);
    const isOverTestPanel = testPanel && testPanel.contains(elementAtPoint);
    
    // Check if mouse is over the Live2D model or its container
    const isOverLive2D = elementAtPoint && 
                         (elementAtPoint.id === 'live2d-canvas' || 
                          (liveStage && liveStage.contains(elementAtPoint)));
    
    // Check if model is being dragged
    const isModelDragging = window.model2 && window.model2.dragging;
    
    // Only ignore mouse events if not over test panel, not over canvas, and not dragging
    if (isOverTestPanel || isOverLive2D || isModelDragging) {
        window.electronAPI.setIgnoreMouseEvents(false);
    } else {
        window.electronAPI.setIgnoreMouseEvents(true);
    }
});

// Add a status indicator for draggable model
function addDraggableIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'draggable-indicator';
    indicator.textContent = 'Model is draggable';
    indicator.style.position = 'absolute';
    indicator.style.bottom = '10px';
    indicator.style.right = '10px';
    indicator.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    indicator.style.color = 'white';
    indicator.style.padding = '5px 10px';
    indicator.style.borderRadius = '5px';
    indicator.style.fontSize = '12px';
    indicator.style.zIndex = '1000';
    indicator.style.opacity = '0.7';
    document.body.appendChild(indicator);
    
    // Fade out after 5 seconds
    setTimeout(() => {
        indicator.style.transition = 'opacity 1s ease';
        indicator.style.opacity = '0';
        
        // Remove after fade out
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.parentNode.removeChild(indicator);
            }
        }, 1000);
    }, 5000);
}

const canvas = document.getElementById('live2d-canvas');
if (canvas) {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
}

// Microphone device handling
async function initializeMicrophoneDevices() {
    try {
        // Request microphone permission to get device labels
        await navigator.mediaDevices.getUserMedia({ audio: true });
        
        const devices = await navigator.mediaDevices.enumerateDevices();
        const micDevices = devices.filter(device => device.kind === 'audioinput');
        
        console.log("Found microphone devices:", micDevices);
        
        // Send the devices to the main process
        if (window.electronAPI && window.electronAPI.setMicrophoneDevices) {
            window.electronAPI.setMicrophoneDevices(micDevices.map(device => ({
                id: device.deviceId,
                name: device.label || `Microphone ${device.deviceId.slice(0, 5)}...`
            })));
        } else {
            console.error("electronAPI.setMicrophoneDevices is not available");
        }
    } catch (error) {
        console.error('Error enumerating microphone devices:', error);
    }
}

// Check health status
async function checkHealth() {
    try {
        const health = await window.api.getHealth();
        console.log("Health check result:", health);
        return health;
    } catch (error) {
        console.error("Health check failed:", error);
        return { status: 'error', error: error.message };
    }
}

// Add STT logging
function setupSTTLogging() {
    // Store the original start_mic function if it exists
    const originalStartMic = window.start_mic;
    if (originalStartMic) {
        window.start_mic = function() {
            console.log("[STT] Starting microphone...");
            return originalStartMic.apply(this, arguments);
        };
    }
    
    // Store the original stop_mic function if it exists
    const originalStopMic = window.stop_mic;
    if (originalStopMic) {
        window.stop_mic = function() {
            console.log("[STT] Stopping microphone...");
            return originalStopMic.apply(this, arguments);
        };
    }
    
    // Create a global function to log STT results
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
    
    console.log("[STT] Logging setup complete");
}

// Try to use direct Claude API
async function tryDirectClaudeAPI(text) {
    updatePathPing('direct-claude-api', 'pending');
    try {
        console.log("[Claude] Sending direct API request:", text);
        await askClaudeDirectly(text);
        updatePathPing('direct-claude-api', true);
    } catch (error) {
        console.error("[Claude] Direct API request failed:", error);
        updatePathPing('direct-claude-api', false);
    }
}

// Path ping system to trace data flow
const pathStatus = {
    'stt': null,
    'stt-to-claude': null,
    'claude-response': null,
    'tts-generation': null,
    'audio-playback': null,
    'direct-claude-api': null
};

function updatePathPing(path, status) {
    pathStatus[path] = status;
    console.log(`[PathPing] ${path}: ${status}`);
    
    // Update UI if path ping element exists
    updatePathPingUI();
}

function updatePathPingUI() {
    const container = document.getElementById('path-ping-container');
    if (!container) return;
    
    // Clear existing content
    container.innerHTML = '';
    
    // Add header
    const header = document.createElement('div');
    header.textContent = 'Path Status:';
    header.style.fontWeight = 'bold';
    container.appendChild(header);
    
    // Add status for each path
    for (const [path, status] of Object.entries(pathStatus)) {
        const item = document.createElement('div');
        item.textContent = `${path}: `;
        
        const statusSpan = document.createElement('span');
        statusSpan.textContent = status === null ? 'not started' : status;
        
        // Set color based on status
        if (status === true) {
            statusSpan.style.color = 'green';
        } else if (status === false) {
            statusSpan.style.color = 'red';
        } else if (status === 'pending') {
            statusSpan.style.color = 'orange';
        } else if (status === 'skipped') {
            statusSpan.style.color = 'blue';
        } else {
            statusSpan.style.color = 'gray';
        }
        
        item.appendChild(statusSpan);
        container.appendChild(item);
    }
}

// Create path ping UI
function createPathPingUI() {
    const container = document.createElement('div');
    container.id = 'path-ping-container';
    container.style.position = 'absolute';
    container.style.top = '30px';
    container.style.right = '10px';
    container.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
    container.style.color = 'white';
    container.style.padding = '10px';
    container.style.borderRadius = '5px';
    container.style.fontSize = '12px';
    container.style.zIndex = '1000';
    document.body.appendChild(container);
    
    // Initial update
    updatePathPingUI();
}

// Populate the "Switch configuration" dropdown with available models
async function populateModelDropdown() {
    try {
        console.log("Populating model dropdown...");
        
        // Get the list of available models
        const models = await window.models.list();
        console.log("Available models:", models);
        
        if (!models || models.length === 0) {
            console.warn("No models found");
            return;
        }
        
        // Send the model names to the main process for the context menu
        const modelNames = models.map(model => model.name);
        window.electronAPI.sendConfigFiles(modelNames);
        
        // Create a select element for the UI if needed
        const existingSelect = document.getElementById('switch-config');
        if (existingSelect) {
            // Clear existing options
            existingSelect.innerHTML = '';
            
            // Add options for each model
            models.forEach((model, index) => {
                const option = document.createElement('option');
                option.value = index.toString();
                option.textContent = model.name;
                existingSelect.appendChild(option);
            });
            
            // Store models in a global variable for reference
            window._models = models;
            
            // Add change event listener
            existingSelect.addEventListener('change', async () => {
                const selectedIndex = parseInt(existingSelect.value);
                const selectedModel = models[selectedIndex];
                if (selectedModel) {
                    await loadSelectedModel(selectedModel);
                }
            });
            
            console.log("Model dropdown populated successfully");
        } else {
            console.log("No select element found with id 'switch-config'");
        }
    } catch (error) {
        console.error("Error populating model dropdown:", error);
    }
}

// Load the selected model
async function loadSelectedModel(model) {
    try {
        console.log(`Loading model: ${model.name}`);
        
        let model3Path;
        
        // If we have a direct model3 path, use it
        if (model.model3) {
            model3Path = model.model3;
        } 
        // Otherwise try to resolve it from conf.yml
        else if (model.conf) {
            model3Path = await window.models.resolvePath(model);
        }
        
        if (!model3Path) {
            console.error(`Could not resolve model3 path for ${model.name}`);
            return;
        }
        
        console.log(`Resolved model3 path: ${model3Path}`);
        
        // Create model config for Live2D
        const modelConfig = {
            url: model3Path, // Use relative path instead of file:// URL
            kScale: 0.15,
            initialXshift: 0,
            initialYshift: 0,
            emotionMap: {}
        };
        
        // Load the model with retry mechanism
        let attempts = 0;
        const maxAttempts = 3;
        let success = false;
        
        while (attempts < maxAttempts && !success) {
            attempts++;
            try {
                await window.live2dModule.loadModel(modelConfig);
                console.log(`Model ${model.name} loaded successfully on attempt ${attempts}`);
                success = true;
            } catch (error) {
                console.error(`Error loading model ${model.name} (attempt ${attempts}/${maxAttempts}):`, error);
                if (attempts < maxAttempts) {
                    console.log(`Retrying model load in 500ms...`);
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
            }
        }
        
        if (!success) {
            console.error(`Failed to load model ${model.name} after ${maxAttempts} attempts`);
        }
    } catch (error) {
        console.error(`Error in loadSelectedModel for ${model.name}:`, error);
    }
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

// Initialize when the page loads
window.addEventListener('DOMContentLoaded', async () => {
    console.log("DOM content loaded, initializing...");
    
    // Initialize microphone devices
    setTimeout(() => {
        initializeMicrophoneDevices();
    }, 1000);
    
    // Setup STT logging
    setupSTTLogging();
    
    // Create path ping UI
    createPathPingUI();
    
    // Show draggable indicator
    setTimeout(() => {
        addDraggableIndicator();
    }, 2000);
    
    // Populate model dropdown
    setTimeout(() => {
        populateModelDropdown();
    }, 1500);
    
    // Check health status
    try {
        const health = await checkHealth();
        console.log(`Cloud service health: ${health.status}`);
        
        // Add a health indicator to the UI
        const healthIndicator = document.createElement('div');
        healthIndicator.id = 'health-indicator';
        healthIndicator.style.position = 'absolute';
        healthIndicator.style.top = '10px';
        healthIndicator.style.right = '10px';
        healthIndicator.style.width = '10px';
        healthIndicator.style.height = '10px';
        healthIndicator.style.borderRadius = '50%';
        healthIndicator.style.backgroundColor = health.status === 'ok' ? '#00ff00' : '#ff0000';
        document.body.appendChild(healthIndicator);
    } catch (error) {
        console.error("Failed to check health:", error);
    }
});

// Expose health check to window
window.checkHealth = checkHealth;
