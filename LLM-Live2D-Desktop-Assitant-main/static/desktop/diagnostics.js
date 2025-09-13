/**
 * Simple diagnostics module for the Live2D Desktop Assistant
 */

// Show a message in the UI
function showMessage(message, isError = false) {
    console.log(`Diagnostic message: ${message}`);
    
    // Update the message element if it exists
    const messageElement = document.getElementById('message');
    if (messageElement) {
        messageElement.textContent = message;
        messageElement.classList.remove('hidden');
        
        if (isError) {
            messageElement.style.backgroundColor = 'rgba(255, 0, 0, 0.7)';
        } else {
            messageElement.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        }
        
        // Hide the message after 5 seconds
        setTimeout(() => {
            messageElement.classList.add('hidden');
        }, 5000);
    }
}

// Log model initialization
function logModelInit(success) {
    if (success) {
        showMessage('Live2D model loaded successfully');
    } else {
        showMessage('Failed to load Live2D model', true);
    }
}

// Log STT status
function logSTT(text) {
    console.log(`STT: ${text}`);
    showMessage(`Heard: ${text}`);
    
    // Send to main process for logging
    if (window.api && window.api.logTranscription) {
        window.api.logTranscription(text);
    }
}

// Log TTS status
function logTTS(text) {
    console.log(`TTS: ${text}`);
}

// Export functions
window.diagnostics = {
    showMessage,
    logModelInit,
    logSTT,
    logTTS
};

// Update model status when Live2D model is loaded
const originalBootLive2D = window.bootLive2D;
if (originalBootLive2D) {
    window.bootLive2D = async function() {
        try {
            const result = await originalBootLive2D();
            logModelInit(result);
            return result;
        } catch (error) {
            console.error('Error loading Live2D model:', error);
            logModelInit(false);
            return false;
        }
    };
}

// Hook into the STT system
const originalLogSTTResult = window.logSTTResult;
if (originalLogSTTResult) {
    window.logSTTResult = function(text) {
        logSTT(text);
        if (originalLogSTTResult) {
            originalLogSTTResult(text);
        }
    };
}
