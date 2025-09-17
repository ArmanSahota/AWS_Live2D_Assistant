// WebSocket connection handler with dynamic port detection
let ws = null;
let reconnectTimer = null;
let isReconnecting = false;

// Try multiple ports to find the server
const POSSIBLE_PORTS = [1018, 1025, 1026, 1027, 1028, 1029, 1030];
let currentPortIndex = 0;

async function findServerPort() {
    for (const port of POSSIBLE_PORTS) {
        try {
            const response = await fetch(`http://localhost:${port}/health`, {
                method: 'GET',
                timeout: 1000
            }).catch(() => null);
            
            if (response && response.ok) {
                console.log(`Found server on port ${port}`);
                return port;
            }
        } catch (e) {
            // Continue to next port
        }
    }
    
    // Default to 1029 if no port found (based on server output)
    console.log('No server found, defaulting to port 1029');
    return 1029;
}

async function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        return;
    }
    
    const port = await findServerPort();
    const wsUrl = `ws://localhost:${port}/client-ws`;
    
    console.log(`Connecting to WebSocket at ${wsUrl}`);
    
    try {
        ws = new WebSocket(wsUrl);
        
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
            
        case 'control':
            // Handle control messages
            if (data.text === 'start-mic') {
                console.log('[STT DEBUG] Received start-mic command from server');
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
