let micStateBeforeConfigSwitch = null;
window.state = "idle"; // idle, thinking-speaking, interrupted
window.voiceInterruptionOn = false;
window.fullResponse = ""; // full response from the server in one conversation chain

function setState(newState) {
    window.state = newState;
    console.log(`State updated to: ${window.state}`);
}
window.setState = setState;

// Define the chunk size for audio data
const chunkSize = 16000; // 1 second of audio at 16kHz

async function sendAudioPartition(audio) {
    try {
        let clipboardData = await window.electronAPI.getClipboardContent();
        
        for (let index = 0; index < audio.length; index += chunkSize) {
            const endIndex = Math.min(index + chunkSize, audio.length);
            const chunk = audio.slice(index, endIndex);
            
            const safeClipboardData = {
                text: clipboardData?.text || '',
                image: clipboardData?.image || null
            };
            
            window.ws.send(JSON.stringify({ 
                type: "mic-audio-data", 
                audio: chunk,
                clipboardData: safeClipboardData
            }));
        }
        
        window.ws.send(JSON.stringify({ 
            type: "mic-audio-end",
            clipboardData: {
                text: clipboardData?.text || '',
                image: clipboardData?.image || null
            }
        }));
    } catch (error) {
        console.error('Error sending audio partition:', error);
    }
}
window.sendAudioPartition = sendAudioPartition;

window.ws = null;

// Track WebSocket connection attempts
let wsConnectionAttempts = 0;
const MAX_WS_CONNECTION_ATTEMPTS = 3;
let wsServerAvailable = true;

function connectWebSocket() {
    return new Promise((resolve, reject) => {
        try {
            // Check if we've exceeded the maximum number of attempts or if server is marked as unavailable
            if (wsConnectionAttempts >= MAX_WS_CONNECTION_ATTEMPTS || !wsServerAvailable) {
                if (wsServerAvailable) {
                    console.warn(`Maximum WebSocket connection attempts (${MAX_WS_CONNECTION_ATTEMPTS}) reached. Disabling WebSocket functionality.`);
                    document.getElementById("message").textContent = "WebSocket server not available. Some features will be limited.";
                    wsServerAvailable = false;
                }
                reject(new Error("WebSocket server not available"));
                return;
            }
            
            wsConnectionAttempts++;
            console.log(`Attempting to connect to WebSocket at ws://127.0.0.1:1018/client-ws (attempt ${wsConnectionAttempts}/${MAX_WS_CONNECTION_ATTEMPTS})`);
            window.ws = new WebSocket("ws://127.0.0.1:1018/client-ws");

            window.ws.onopen = function () {
                setState("idle");
                console.log("Connected to WebSocket successfully");
                wsConnectionAttempts = 0; // Reset counter on success
                wsServerAvailable = true;
                
                // Fetch configurations immediately after connection
                setTimeout(() => {
                    fetchConfigurations();
                }, 500);
                
                resolve();
            };

            window.ws.onclose = function (event) {
                setState("idle");
                console.log("Disconnected from WebSocket. Code:", event.code, "Reason:", event.reason);
                if (window.audioTaskQueue) {
                    window.audioTaskQueue.clearQueue();
                }
                
                // Try to reconnect after a delay if not a normal closure and we haven't exceeded max attempts
                if (event.code !== 1000 && wsConnectionAttempts < MAX_WS_CONNECTION_ATTEMPTS && wsServerAvailable) {
                    console.log(`Abnormal closure. Will attempt to reconnect in 5 seconds... (attempt ${wsConnectionAttempts}/${MAX_WS_CONNECTION_ATTEMPTS})`);
                    setTimeout(() => {
                        if (window.reconnectWebSocket) {
                            window.reconnectWebSocket();
                        }
                    }, 5000);
                }
            };

            window.ws.onmessage = function (event) {
                try {
                    const data = JSON.parse(event.data);
                    console.log("Received message type:", data.type);
                    handleMessage(data);
                } catch (error) {
                    console.error("Error parsing WebSocket message:", error);
                    console.error("Raw message:", event.data);
                }
            };

            window.ws.onerror = function (error) {
                // Only log detailed error on first attempt to reduce console spam
                if (wsConnectionAttempts === 1) {
                    console.error("WebSocket error:", error);
                } else {
                    console.log("WebSocket connection failed");
                }
                
                // If we've reached max attempts, mark server as unavailable
                if (wsConnectionAttempts >= MAX_WS_CONNECTION_ATTEMPTS) {
                    wsServerAvailable = false;
                    document.getElementById("message").textContent = "WebSocket server not available. Some features will be limited.";
                }
                
                reject(error);
            };
        } catch (error) {
            console.error("Error creating WebSocket connection:", error);
            reject(error);
        }
    });
}

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
                        setExpression(0);
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
                setExpression(message.text);
                break;
            case "mouth":
                setMouth(Number(message.text));
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
                    
                    window.addAudioTask(message.audio, message.instrument, message.volumes, message.slice_length, message.text, message.expressions);
                    window.setExpression(0);
                    
                    // Force audio playback using standard Audio API as a backup
                    try {
                        console.log("Attempting direct audio playback");
                        const audio = new Audio("data:audio/wav;base64," + message.audio);
                        audio.play().catch(error => {
                            console.error("Direct audio play error:", error);
                        });
                    } catch (error) {
                        console.error("Error in direct audio playback:", error);
                    }
                }
                break;
            case "set-model":
                // The model should already be initialized on page load
                // This is just for updating the model if needed
                if (window.live2dModule && window.live2dModule.loadModel) {
                    console.log("Updating Live2D model with new configuration from WebSocket");
                    try {
                        // Try to parse the model config if it's a string
                        const modelConfig = typeof message.text === 'string' ? 
                            JSON.parse(message.text) : message.text;
                        
                        window.live2dModule.loadModel(modelConfig).catch(error => {
                            console.error("Failed to load Live2D model:", error);
                        });
                    } catch (error) {
                        console.error("Error parsing model config:", error);
                        console.error("Raw model config:", message.text);
                    }
                } else {
                    console.error("Live2D module not properly initialized");
                    // Try to initialize the model using our new bootLive2D function
                    if (window.bootLive2D) {
                        console.log("Attempting to initialize Live2D model using bootLive2D");
                        window.bootLive2D().catch(error => {
                            console.error("Failed to boot Live2D model:", error);
                        });
                    }
                }
                break;
            case "listExpressions":
                console.log(listSupportedExpressions());
                break;
            case "config-files":
                console.log("Received config files:", message.files);
                if (Array.isArray(message.files) && message.files.length > 0) {
                    console.log("Sending config files to main process:", message.files);
                    window.electronAPI.sendConfigFiles(message.files);
                } else {
                    console.error("No config files received or invalid format");
                    // Try to fetch configurations again after a delay
                    setTimeout(() => {
                        console.log("Retrying fetch configurations due to empty response");
                        fetchConfigurations();
                    }, 3000);
                }
                break;
            case "config-switched":
                console.log(message.message);
                document.getElementById("message").textContent = "Configuration switched successfully!";
                setState("idle");

                if (micStateBeforeConfigSwitch) {
                    start_mic();
                }
                micStateBeforeConfigSwitch = null;  // reset the state
                break;        
            default:
                console.error("Unknown message type: " + message.type);
                console.log(message);
        }
    } catch (error) {
        console.error("Error handling message:", error);
        console.error("Message that caused the error:", message);
    }
}

function fetchConfigurations() {
    console.log("Attempting to fetch configurations...");
    console.log("WebSocket state:", window.ws ? ["CONNECTING", "OPEN", "CLOSING", "CLOSED"][window.ws.readyState] : "undefined");
    
    if (window.ws && window.ws.readyState === WebSocket.OPEN) {
        try {
            window.ws.send(JSON.stringify({ type: "fetch-configs" }));
            console.log("Fetching configurations request sent");
        } catch (error) {
            console.error("Error sending fetch configurations request:", error);
        }
    } else {
        console.error("WebSocket is not open. Cannot fetch configurations.");
        console.log("Current WebSocket state:", window.ws ? ["CONNECTING", "OPEN", "CLOSING", "CLOSED"][window.ws.readyState] : "undefined");
        
        // Try to reconnect and then fetch configurations
        console.log("Attempting to reconnect before fetching configurations...");
        connectWebSocket().then(() => {
            if (window.ws && window.ws.readyState === WebSocket.OPEN) {
                console.log("Successfully reconnected. Fetching configurations after delay...");
                setTimeout(() => {
                    try {
                        window.ws.send(JSON.stringify({ type: "fetch-configs" }));
                        console.log("Fetching configurations after reconnect");
                    } catch (error) {
                        console.error("Error sending fetch configurations request after reconnect:", error);
                    }
                }, 1000);
            } else {
                console.error("WebSocket still not open after reconnect attempt");
            }
        }).catch(error => {
            console.error("Failed to reconnect:", error);
        });
    }
}

function switchConfig(configFile) {
    setState("switching-config");
    document.getElementById("message").textContent = "Switching configuration...";
    
    micStateBeforeConfigSwitch = micToggleState;
    if (micToggleState) {
        stop_mic();
    }
    window.interrupt();
    window.ws.send(JSON.stringify({ type: "switch-config", file: configFile }));
}

window.handleMessage = handleMessage;
window.switchConfig = switchConfig;
window.fetchConfigurations = fetchConfigurations;

async function initialize() {
    try {
        // Check if we should use the local WebSocket
        if (window.electronAPI) {
            const flags = await window.electronAPI.getFeatureFlags();
            console.log("Feature flags:", flags);
            
            // Only connect to WebSocket if explicitly enabled
            // This decouples Live2D initialization from WebSocket
            const useLocalWS = flags.useLocalWS || false;
            
            if (useLocalWS) {
                console.log("Initializing local WebSocket connection...");
                try {
                    await connectWebSocket();
                    console.log("WebSocket connection initialized successfully");
                    
                    // Fetch configurations with a slight delay to ensure connection is stable
                    setTimeout(() => {
                        console.log("Fetching configurations after initialization...");
                        fetchConfigurations();
                    }, 1000);
                } catch (error) {
                    console.error("Failed to connect to WebSocket:", error);
                    console.log("Will continue without WebSocket connection");
                }
            } else {
                console.log("Local WebSocket disabled - skipping connection");
            }
        } else {
            console.error("electronAPI not available, cannot check feature flags");
        }
    } catch (error) {
        console.error("Failed to initialize:", error);
    }
}

// Initialize with a slight delay to ensure electronAPI is available
setTimeout(() => {
    initialize();
}, 500);

window.connectWebSocket = connectWebSocket;
