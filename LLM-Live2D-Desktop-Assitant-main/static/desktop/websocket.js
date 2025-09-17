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
            // Display subtitles
            if (window.displaySubtitles) {
                window.displaySubtitles(data.text);
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
                if (window.startMicrophone) {
                    window.startMicrophone();
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

// Export functions for global use
window.wsConnection = {
    connect: connectWebSocket,
    sendAudioData: sendAudioData,
    sendAudioEnd: sendAudioEnd,
    sendTextInput: sendTextInput,
    getState: () => ws ? ws.readyState : WebSocket.CLOSED
};
