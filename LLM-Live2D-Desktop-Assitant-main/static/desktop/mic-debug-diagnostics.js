// Microphone Debug Diagnostics
// This file adds comprehensive logging to identify the mic start/stop loop issue

console.log('[MIC DEBUG] Loading microphone diagnostics...');

// Track mic state changes
let micStateHistory = [];
let lastMicAction = null;
let micActionCount = 0;
let startTime = Date.now();

function logMicAction(action, source, details = {}) {
    const timestamp = Date.now();
    const timeSinceStart = timestamp - startTime;
    micActionCount++;
    
    const logEntry = {
        action,
        source,
        timestamp,
        timeSinceStart,
        count: micActionCount,
        details,
        stackTrace: new Error().stack.split('\n').slice(2, 5).join('\n')
    };
    
    micStateHistory.push(logEntry);
    
    console.log(`[MIC DEBUG ${micActionCount}] ${action.toUpperCase()} from ${source} at +${timeSinceStart}ms`, details);
    
    // Keep only last 20 entries
    if (micStateHistory.length > 20) {
        micStateHistory.shift();
    }
    
    // Detect rapid cycling
    if (micActionCount > 5) {
        const recentActions = micStateHistory.slice(-5);
        const timeSpan = recentActions[4].timestamp - recentActions[0].timestamp;
        if (timeSpan < 5000) { // 5 actions in less than 5 seconds
            console.error('[MIC DEBUG] RAPID CYCLING DETECTED!', {
                actionsInLast5Seconds: recentActions.length,
                timeSpan,
                recentActions: recentActions.map(a => `${a.action}(${a.source})`)
            });
        }
    }
    
    lastMicAction = logEntry;
}

// Override start_mic function
if (window.start_mic) {
    const originalStartMic = window.start_mic;
    window.start_mic = function(...args) {
        logMicAction('start', 'function_call', {
            args,
            micToggleState: window.micToggleState,
            vadExists: !!window.myvad,
            wakeWordDetectionOn: window.wakeWordDetectionOn
        });
        return originalStartMic.apply(this, args);
    };
}

// Override stop_mic function
if (window.stop_mic) {
    const originalStopMic = window.stop_mic;
    window.stop_mic = function(...args) {
        logMicAction('stop', 'function_call', {
            args,
            micToggleState: window.micToggleState,
            vadExists: !!window.myvad,
            wakeWordDetectionOn: window.wakeWordDetectionOn
        });
        return originalStopMic.apply(this, args);
    };
}

// Monitor WebSocket messages
if (window.ws) {
    const originalOnMessage = window.ws.onmessage;
    window.ws.onmessage = function(event) {
        try {
            const message = JSON.parse(event.data);
            if (message.type === 'control' && message.text === 'start-mic') {
                logMicAction('start', 'websocket_control', {
                    message,
                    wsReadyState: window.ws.readyState,
                    wsUrl: window.ws.url
                });
            }
        } catch (e) {
            // Ignore parsing errors
        }
        
        if (originalOnMessage) {
            return originalOnMessage.apply(this, arguments);
        }
    };
}

// Monitor VAD events
if (window.myvad) {
    console.log('[MIC DEBUG] VAD instance exists, monitoring events...');
} else {
    console.log('[MIC DEBUG] No VAD instance found yet, will monitor when created...');
}

// Monitor timeout events
const originalSetTimeout = window.setTimeout;
window.setTimeout = function(callback, delay, ...args) {
    if (callback.toString().includes('No speech detected') || 
        callback.toString().includes('stop_mic')) {
        console.log('[MIC DEBUG] Timeout set for mic stop:', {
            delay,
            callbackPreview: callback.toString().substring(0, 100)
        });
    }
    return originalSetTimeout.call(this, callback, delay, ...args);
};

// Add global diagnostic functions
window.getMicDiagnostics = function() {
    return {
        history: micStateHistory,
        currentState: {
            micToggleState: window.micToggleState,
            vadExists: !!window.myvad,
            wakeWordDetectionOn: window.wakeWordDetectionOn,
            wsConnected: window.ws && window.ws.readyState === WebSocket.OPEN,
            lastAction: lastMicAction
        },
        stats: {
            totalActions: micActionCount,
            runtimeMs: Date.now() - startTime
        }
    };
};

window.logMicState = function() {
    console.log('[MIC DEBUG] Current State:', window.getMicDiagnostics());
};

// Auto-log state every 10 seconds if there's activity
setInterval(() => {
    if (micActionCount > 0) {
        const diagnostics = window.getMicDiagnostics();
        if (diagnostics.history.length > 0) {
            const lastActionTime = diagnostics.history[diagnostics.history.length - 1].timestamp;
            const timeSinceLastAction = Date.now() - lastActionTime;
            
            if (timeSinceLastAction < 30000) { // Activity in last 30 seconds
                console.log('[MIC DEBUG] Periodic State Check:', {
                    totalActions: micActionCount,
                    lastActionAgo: timeSinceLastAction + 'ms',
                    currentState: diagnostics.currentState
                });
            }
        }
    }
}, 10000);

console.log('[MIC DEBUG] Diagnostics loaded. Use window.getMicDiagnostics() or window.logMicState() for details.');