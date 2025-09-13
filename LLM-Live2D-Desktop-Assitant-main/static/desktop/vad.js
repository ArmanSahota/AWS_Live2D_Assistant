window.myvad = null;
window.previousTriggeredProbability = 0;
window.wakeWordDetectionOn = false;
window.speechProbThreshold = 0.9;
window.selectedMicrophoneId = null;

// Load the previously selected microphone device ID if available
async function loadSelectedMicrophoneId() {
    try {
        const devices = await window.electronAPI.getMicrophoneDevices();
        if (devices && devices.length > 0) {
            // Use the first available device as default if none is selected
            window.selectedMicrophoneId = devices[0].id;
            updateMicrophoneDisplay(devices[0].name);
        }
    } catch (error) {
        console.error("Error loading microphone devices:", error);
    }
}

// Update the microphone display
function updateMicrophoneDisplay(micName) {
    const micInfoElement = document.getElementById('mic-info');
    if (micInfoElement) {
        micInfoElement.textContent = `Microphone: ${micName}`;
        micInfoElement.classList.remove('hidden');
    }
}

// Initialize microphone selection
loadSelectedMicrophoneId();

// Handle microphone selection from the menu
window.electronAPI.onSelectMicrophone(async (deviceId) => {
    console.log("Selected microphone device:", deviceId);
    window.selectedMicrophoneId = deviceId;
    window.electronAPI.setMicrophoneDevice(deviceId);
    
    // Get the device name to display
    try {
        const devices = await window.electronAPI.getMicrophoneDevices();
        const selectedDevice = devices.find(device => device.id === deviceId);
        if (selectedDevice) {
            updateMicrophoneDisplay(selectedDevice.name);
        }
    } catch (error) {
        console.error("Error getting microphone device name:", error);
    }
    
    // Restart the microphone if it's currently active
    if (window.micToggleState) {
        stop_mic().then(() => {
            start_mic();
        });
    }
});

porcupine = null;
isWaitingForWakeWord = false;
noSpeechTimeout = null;

async function init_vad() {
    const vadOptions = {
        preSpeechPadFrames: 10,
        positiveSpeechThreshold: window.speechProbThreshold,
        onSpeechStart: () => {
            console.log("Speech start detected: " + window.previousTriggeredProbability);
            if (window.state === "thinking-speaking") {
                window.interrupt();
            } else {
                console.log("Not interrupted. Just normal conversation");
            }
            resetNoSpeechTimeout();
        },
        onFrameProcessed: (probs) => {
            if (probs["isSpeech"] > window.previousTriggeredProbability) {
                window.previousTriggeredProbability = probs["isSpeech"];
                resetNoSpeechTimeout();
            }
        },
        onVADMisfire: () => {
            console.log("VAD Misfire. The LLM can't hear you.");
            if (window.state === "interrupted") {
                window.setState("idle");
            }
            document.getElementById("message").textContent = "The LLM can't hear you.";
        },
        onSpeechEnd: (audio) => {
            window.audioTaskQueue.clearQueue();
            if (!window.voiceInterruptionOn) {
                window.stop_mic();
            }
            if (window.ws && window.ws.readyState === WebSocket.OPEN) {
                window.sendAudioPartition(audio);
            }
            resetNoSpeechTimeout();
        }
    };
    
    // Add the selected microphone device ID if available
    if (window.selectedMicrophoneId) {
        vadOptions.deviceId = window.selectedMicrophoneId;
    }
    
    window.myvad = await vad.MicVAD.new(vadOptions);
}

async function start_mic() {
    if (isWaitingForWakeWord) {
        await stop_wake_word_detection();
    }

    try {
        console.log("Mic start");
        if (window.myvad == null) {
            await init_vad();
        }
        await window.myvad.start();
        window.electronAPI.updateMenuChecked("Microphone", true);
        window.micToggleState = true;
        resetNoSpeechTimeout();
    } catch (error) {
        console.error("Failed to start microphone:", error);
        window.micToggleState = false;
        window.electronAPI.updateMenuChecked("Microphone", false);
    }
}

window.start_mic = start_mic;

async function stop_mic() {
    console.log("Mic stop");
    
    if (window.myvad) {
        window.myvad.pause();
    }
    window.electronAPI.updateMenuChecked("Microphone", false);
    clearNoSpeechTimeout();
    window.micToggleState = false;
    if (window.wakeWordDetectionOn)
        await start_wake_word_detection();
}

window.stop_mic = stop_mic;

function interrupt() {
    console.log("Interrupting conversation chain");
    console.log("Sending: " + JSON.stringify({ type: "interrupt-signal", text: window.fullResponse }));
    if (window.ws && window.ws.readyState === WebSocket.OPEN) {
        window.ws.send(JSON.stringify({ type: "interrupt-signal", text: window.fullResponse }));
    }
    setState("interrupted");
    if (window.model2 && typeof window.model2.stopSpeaking === 'function') {
        window.model2.stopSpeaking();
    }
    if (window.audioTaskQueue && typeof window.audioTaskQueue.clearQueue === 'function') {
        window.audioTaskQueue.clearQueue();
    }
    resetNoSpeechTimeout();
    console.log("Interrupted!!!!");
}

window.interrupt = interrupt;

async function start_wake_word_detection() {
    if (isWaitingForWakeWord) {
        console.log("Already waiting for wake word.");
        return;
    }

    // Check if required libraries are available
    if (!window.WebVoiceProcessor || !window.PorcupineWeb) {
        console.error("Wake word detection libraries not available. Skipping wake word detection.");
        return;
    }

    if (window.WebVoiceProcessor.WebVoiceProcessor && 
        window.WebVoiceProcessor.WebVoiceProcessor.isRecording && 
        porcupine) {
        try {
            await window.WebVoiceProcessor.WebVoiceProcessor.unsubscribe(porcupine);
            await porcupine.terminate();
        } catch (err) {
            console.error("Error cleaning up previous wake word detection:", err);
        }
    }

    console.log("Starting wake word detection...");
    isWaitingForWakeWord = true;
    
    accessKey = "/7gDUCElrddYzUegKQSEoe/ZQjH+sKU1KjcEnANpHdYQeLhc1WXrHQ=="
    try {
        // First check if the files actually exist before trying to load them
        const keywords = [];
        const chineseWakeWordFile = "desktop/伊蕾娜_zh_wasm_v3_0_0.ppn";
        const englishWakeWordFile = "desktop/Elaina_en_wasm_v3_0_0.ppn";
        const chineseParamsFile = "desktop/porcupine_params_zh.pv";
        const englishParamsFile = "desktop/porcupine_params.pv";
        
        // Check Chinese wake word availability
        let chineseAvailable = false;
        try {
            // Try to fetch the file to see if it exists
            const chineseFileCheck = await fetch(chineseWakeWordFile, { method: 'HEAD' })
                .catch(() => ({ ok: false }));
                
            if (chineseFileCheck.ok) {
                console.log("Chinese wake word file found");
                chineseAvailable = true;
                keywords.push({
                    label: "伊蕾娜",
                    publicPath: chineseWakeWordFile
                });
            }
        } catch (e) {
            console.log("Error checking Chinese wake word file:", e);
        }

        // Check English wake word availability if window.englishWakeWordAvailable is true
        // (This flag was set in desktop.html based on file availability)
        let englishAvailable = false;
        try {
            if (window.englishWakeWordAvailable !== false) {
                const englishFileCheck = await fetch(englishWakeWordFile, { method: 'HEAD' })
                    .catch(() => ({ ok: false }));
                    
                if (englishFileCheck.ok) {
                    console.log("English wake word file found");
                    englishAvailable = true;
                    keywords.push({
                        label: "Elaina",
                        publicPath: englishWakeWordFile
                    });
                }
            }
        } catch (e) {
            console.log("Error checking English wake word file:", e);
        }
        
        // If no wake words are available, we can't continue
        if (keywords.length === 0) {
            console.error("No wake word files available");
            isWaitingForWakeWord = false;
            document.getElementById("message").textContent = "Wake word detection unavailable";
            return;
        }
        
        // Choose the appropriate params file based on which keywords are available
        let paramsPath;
        if (chineseAvailable && englishAvailable) {
            // Both are available, prioritize English
            paramsPath = englishParamsFile;
        } else if (chineseAvailable) {
            paramsPath = chineseParamsFile;
        } else if (englishAvailable) {
            paramsPath = englishParamsFile;
        }
        
        console.log(`Creating Porcupine with ${keywords.length} keywords and params: ${paramsPath}`);
        
        // Create the Porcupine worker with all available keywords
        porcupine = await PorcupineWeb.PorcupineWorker.create(
            accessKey,
            keywords,
            keywordDetectionCallback,
            {
                publicPath: paramsPath,
                forceWrite: true,
            }
        );
        
        // Subscribe to the voice processor
        if (porcupine && window.WebVoiceProcessor.WebVoiceProcessor) {
            await window.WebVoiceProcessor.WebVoiceProcessor.subscribe(porcupine);
            console.log("Wake word detection started successfully with keywords:", keywords.map(k => k.label).join(", "));
        } else {
            throw new Error("Porcupine or WebVoiceProcessor not available");
        }
    } catch (err) {
        console.error("Error starting wake word detection:", err);
        isWaitingForWakeWord = false;
    }
}

async function stop_wake_word_detection() {
    if (!isWaitingForWakeWord) return;
    console.log("Stopping wake word detection...");
    if (porcupine) {
        await window.WebVoiceProcessor.WebVoiceProcessor.unsubscribe(porcupine);
        await porcupine.terminate();
        porcupine = null;
    }
    isWaitingForWakeWord = false;
    console.log("Wake word detection stopped.");
}

function keywordDetectionCallback(detection) {
    console.log(`Porcupine detected keyword: ${detection.label}`);
    // Handle both Chinese and English wake words
    if (detection.label === "伊蕾娜" || detection.label === "Elaina") {
        console.log("Wake word detected, activating microphone");
        window.start_mic();
    }
}

function resetNoSpeechTimeout() {
    if (window.wakeWordDetectionOn === false) return;
    clearNoSpeechTimeout();
    noSpeechTimeout = setTimeout(() => {
        console.log("No speech detected for 15 seconds, stopping mic.");
        window.stop_mic();
    }, 15000);
}

window.resetNoSpeechTimeout = resetNoSpeechTimeout;

function clearNoSpeechTimeout() {
    if (noSpeechTimeout) {
        clearTimeout(noSpeechTimeout);
        noSpeechTimeout = null;
    }
}

window.addEventListener("beforeunload", async () => {
    if (window.myvad) {
        window.myvad.release();
        window.myvad = null;
    }
    if (porcupine) {
        await stop_wake_word_detection();
    }
});

window.updateSensitivity = async function(value) {
    value = Math.max(1, Math.min(100, value));
    window.speechProbThreshold = value / 100;
    
    if (window.myvad) {
        const micWasActive = window.WebVoiceProcessor.WebVoiceProcessor.isRecording;
        if (micWasActive) {
            await window.myvad.pause();
        }
        await init_vad();
        if (micWasActive) {
            await window.myvad.start();
        }
    }
    
    const sensitivityInput = document.getElementById('speechProbThreshold');
    if (sensitivityInput && sensitivityInput.value !== value.toString()) {
        sensitivityInput.value = value;
    }
    window.electronAPI.updateSensitivity(value / 100);
};

window.electronAPI.setSensitivity((event, value) => {
    const sensitivityInput = document.getElementById('speechProbThreshold');
    if (sensitivityInput) {
        sensitivityInput.value = Math.round(value * 100);
        window.updateSensitivity(sensitivityInput.value);
    }
});

document.getElementById('speechProbThreshold').addEventListener('change', function() {
    window.updateSensitivity(this.value);
});
