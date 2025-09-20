// WebSocket connection handler with direct port from main process
let ws = null;
let reconnectTimer = null;
let isReconnecting = false;
let detectedPort = null;

// WEBSOCKET PORT FIX: Get port directly from main process
// Fallback ports if we can't get the port from the main process
const POSSIBLE_PORTS = [1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027, 1028, 1029, 1030];

// Listen for backend port detection from main process
if (window.electronAPI && window.electronAPI.onBackendPortDetected) {
    window.electronAPI.onBackendPortDetected((port) => {
        console.log(`[WEBSOCKET PORT FIX] Received backend port from main process: ${port}`);
        detectedPort = port;
        
        // If we're already connected to a different port, reconnect to the correct one
        if (ws && ws.readyState === WebSocket.OPEN && ws._port !== port) {
            console.log(`[WEBSOCKET PORT FIX] Reconnecting to newly detected port: ${port}`);
            ws.close();
            connectWebSocket();
        }
    });
}

async function getServerPort() {
    // SIMPLIFIED PORT DISCOVERY: More reliable and deterministic approach
    
    // Priority 1: Get port from main process (most reliable)
    if (window.electronAPI && window.electronAPI.getBackendPort) {
        try {
            const port = await Promise.race([
                window.electronAPI.getBackendPort(),
                new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), 2000))
            ]);
            if (port && port > 0) {
                console.log(`[WEBSOCKET SIMPLIFIED] Using port from main process: ${port}`);
                detectedPort = port;
                return port;
            }
        } catch (e) {
            console.log(`[WEBSOCKET SIMPLIFIED] Main process port failed: ${e.message}`);
        }
    }
    
    // Priority 2: Use previously detected port
    if (detectedPort && detectedPort > 0) {
        console.log(`[WEBSOCKET SIMPLIFIED] Using cached port: ${detectedPort}`);
        return detectedPort;
    }
    
    // Priority 3: Quick port file check (with timeout)
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 1000);
        
        const response = await fetch('/server_port.txt', {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        
        if (response.ok) {
            const portText = await response.text();
            const port = parseInt(portText.trim());
            if (!isNaN(port) && port > 0) {
                console.log(`[WEBSOCKET SIMPLIFIED] Found port from file: ${port}`);
                detectedPort = port;
                return port;
            }
        }
    } catch (e) {
        console.log(`[WEBSOCKET SIMPLIFIED] Port file check failed: ${e.message}`);
    }
    
    // Priority 4: Fast port discovery (limited attempts)
    console.log('[WEBSOCKET SIMPLIFIED] Starting fast port discovery...');
    const quickPorts = [8002, 1018, 1019, 1020]; // Check port 8002 first (current server port)
    
    for (const port of quickPorts) {
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 500); // Faster timeout
            
            const response = await fetch(`http://localhost:${port}/health`, {
                method: 'GET',
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            
            if (response.ok) {
                console.log(`[WEBSOCKET SIMPLIFIED] Found server on port ${port}`);
                detectedPort = port;
                return port;
            }
        } catch (e) {
            // Continue to next port
        }
    }
    
    // Default fallback
    console.log('[WEBSOCKET SIMPLIFIED] Using default port 1018');
    detectedPort = 1018;
    return 1018;
}

async function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log('[WEBSOCKET PORT FIX] WebSocket already connected');
        return;
    }
    
    console.log('[WEBSOCKET PORT FIX] Starting WebSocket connection process...');
    const port = await getServerPort();
    const wsUrl = `ws://localhost:${port}/client-ws`;
    
    console.log(`[WEBSOCKET PORT FIX] Attempting WebSocket connection to ${wsUrl}`);
    
    try {
        ws = new WebSocket(wsUrl);
        ws._port = port; // Store the port we're connected to
        
        ws.onopen = () => {
            console.log('WebSocket connected successfully');
            isReconnecting = false;
            
            // Make ws globally available
            window.ws = ws;
            
            // Update UI status
            if (window.updateConnectionStatus) {
                window.updateConnectionStatus('connected');
            }
            
            // Send initial configuration
            ws.send(JSON.stringify({
                type: 'config',
                data: {
                    useLocalSTT: true,
                    useLocalTTS: true
                }
            }));
        };
        
        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (e) {
                console.error('Error parsing WebSocket message:', e);
            }
        };
        
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (window.updateConnectionStatus) {
                window.updateConnectionStatus('error');
            }
        };
        
        ws.onclose = () => {
            console.log('WebSocket disconnected');
            if (window.updateConnectionStatus) {
                window.updateConnectionStatus('disconnected');
            }
            
            // Attempt to reconnect after 3 seconds
            if (!isReconnecting) {
                isReconnecting = true;
                reconnectTimer = setTimeout(() => {
                    console.log('Attempting to reconnect...');
                    connectWebSocket();
                }, 3000);
            }
        };
        
    } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        
        // Retry connection after 5 seconds
        setTimeout(connectWebSocket, 5000);
    }
}

function handleWebSocketMessage(data) {
    console.log('Received WebSocket message:', data.type);
    
    switch(data.type) {
        case 'full-text':
            console.log('[SUBTITLE DEBUG] Received full-text message via WebSocket:', data.text);
            // Display subtitles
            if (window.displaySubtitles) {
                console.log('[SUBTITLE DEBUG] Calling window.displaySubtitles function');
                window.displaySubtitles(data.text);
            } else {
                console.log('[SUBTITLE DEBUG] window.displaySubtitles function not found!');
                // Fallback: directly update the message element
                const messageElement = document.getElementById('message');
                if (messageElement) {
                    console.log('[SUBTITLE DEBUG] Using fallback - directly updating message element');
                    messageElement.textContent = data.text;
                    messageElement.classList.remove('hidden'); // Ensure it's visible
                } else {
                    console.error('[SUBTITLE DEBUG] Message element not found for fallback!');
                }
            }
            break;
            
        case 'audio-data':
            // Play audio response
            if (window.playAudioResponse) {
                window.playAudioResponse(data);
            }
            break;
            
        case 'audio-payload':
            // Handle audio payload from backend (EdgeTTS)
            console.log('[AUDIO DEBUG] Received audio-payload message');
            console.log('[AUDIO DEBUG] Payload contains:', {
                hasAudio: !!data.audio,
                hasVolumes: !!data.volumes,
                hasText: !!data.text,
                hasExpression: !!data.expression_list,
                format: data.format
            });
            
            // Call the audio task handler
            if (window.addAudioTask && data.audio) {
                console.log('[AUDIO DEBUG] Adding audio task with text:', data.text);
                window.addAudioTask(
                    data.audio,
                    data.instrument || "None",
                    data.volumes || [],
                    data.slice_length || 0.1,
                    data.text || null,
                    data.expression_list || null
                );
            } else {
                console.error('[AUDIO DEBUG] Missing addAudioTask function or audio data');
            }
            break;
            
        case 'control':
            // Handle control messages with state checking and rate limiting
            if (data.text === 'start-mic') {
                console.log('[STT DEBUG] Received start-mic command from server');
                
                // Initialize rate limiting variables if not exists
                if (!window.lastMicStartCommand) {
                    window.lastMicStartCommand = 0;
                    window.micStartCommandCount = 0;
                }
                
                const now = Date.now();
                const timeSinceLastCommand = now - window.lastMicStartCommand;
                
                // Rate limiting: ignore if less than 2 seconds since last command
                if (timeSinceLastCommand < 2000) {
                    console.log('[STT DEBUG] Ignoring start-mic command - rate limited (last command ' + timeSinceLastCommand + 'ms ago)');
                    return;
                }
                
                // State checking: don't start if already active
                if (window.micToggleState === true) {
                    console.log('[STT DEBUG] Ignoring start-mic command - microphone already active');
                    return;
                }
                
                // Check if VAD is already running
                if (window.myvad && window.myvad.listening) {
                    console.log('[STT DEBUG] Ignoring start-mic command - VAD already listening');
                    return;
                }
                
                // Update rate limiting tracking
                window.lastMicStartCommand = now;
                window.micStartCommandCount++;
                
                console.log('[STT DEBUG] Processing start-mic command (count: ' + window.micStartCommandCount + ')');
                
                if (window.start_mic) {
                    console.log('[STT DEBUG] Calling start_mic function');
                    window.start_mic();
                } else if (window.startMicrophone) {
                    console.log('[STT DEBUG] Calling startMicrophone function');
                    window.startMicrophone();
                } else {
                    console.error('[STT DEBUG] No microphone start function found!');
                }
            }
            break;
            
        case 'set-model':
            // Update Live2D model
            if (window.updateLive2DModel) {
                window.updateLive2DModel(data.text);
            }
            break;
            
        case 'error':
            console.error('Server error:', data.message);
            if (window.showError) {
                window.showError(data.message);
            }
            break;
    }
}

function sendAudioData(audioData) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'mic-audio-data',
            audio: audioData
        }));
    }
}

function sendAudioEnd() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'mic-audio-end'
        }));
    }
}

function sendTextInput(text) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: 'text-input',
            text: text
        }));
        console.log('Sent text input:', text);
    } else {
        console.error('WebSocket not connected');
    }
}

// Initialize WebSocket connection when page loads
document.addEventListener('DOMContentLoaded', () => {
    connectWebSocket();
});

// Function to send audio data in chunks (missing function that VAD calls)
const chunkSize = 4096;
async function sendAudioPartition(audio) {
    console.log('[STT DEBUG] sendAudioPartition called with audio length:', audio ? audio.length : 0);
    
    if (!ws || ws.readyState !== WebSocket.OPEN) {
        console.error('[STT DEBUG] WebSocket not connected, cannot send audio');
        return;
    }
    
    if (!audio || audio.length === 0) {
        console.error('[STT DEBUG] No audio data to send');
        return;
    }
    
    // Log audio characteristics for debugging
    const audioMin = Math.min(...audio);
    const audioMax = Math.max(...audio);
    console.log(`[STT DEBUG] Audio amplitude range: ${audioMin.toFixed(4)} to ${audioMax.toFixed(4)}`);
    
    // Send audio in chunks
    let chunksSent = 0;
    for (let index = 0; index < audio.length; index += chunkSize) {
        const endIndex = Math.min(index + chunkSize, audio.length);
        const chunk = audio.slice(index, endIndex);
        
        // Convert to object format expected by server
        const chunkObject = {};
        for (let i = 0; i < chunk.length; i++) {
            chunkObject[i] = chunk[i];
        }
        
        ws.send(JSON.stringify({ 
            type: "mic-audio-data", 
            audio: chunkObject 
        }));
        chunksSent++;
    }
    
    console.log(`[STT DEBUG] Sent ${chunksSent} audio chunks`);
    
    // Send end signal
    ws.send(JSON.stringify({ type: "mic-audio-end" }));
    console.log('[STT DEBUG] Sent mic-audio-end signal');
}

// Make sendAudioPartition available globally
window.sendAudioPartition = sendAudioPartition;
// Make ws available globally for other scripts
window.ws = ws;

// Export functions for global use
window.wsConnection = {
    connect: connectWebSocket,
    sendAudioData: sendAudioData,
    sendAudioEnd: sendAudioEnd,
    sendTextInput: sendTextInput,
    sendAudioPartition: sendAudioPartition,
    getState: () => ws ? ws.readyState : WebSocket.CLOSED
};
