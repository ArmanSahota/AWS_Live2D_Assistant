// Using audioChunkSize instead of chunkSize to avoid conflict with websocket.js
const audioChunkSize = 4096;

async function addAudioTask(audio_base64, instrument_base64, volumes, slice_length, text = null, expression_list = null) {
    console.log(`1. Adding audio task ${text} to queue`);
    
    if (window.state === "interrupted") {
        console.log("Skipping audio task due to interrupted state");
        return;
    }
    
    window.audioTaskQueue.addTask(() => {
        return new Promise((resolve, reject) => {
            playAudioLipSync(audio_base64, instrument_base64, volumes, slice_length, text, expression_list, onComplete=resolve);
        }).catch(error => {
            console.log("Audio task error:", error);
        });
    });
}
window.addAudioTask = addAudioTask;

async function getAudioLength(audio_base64) {
    return new Promise((resolve) => {
        const audio = new Audio("data:audio/wav;base64," + audio_base64);
        audio.onloadedmetadata = () => {
            const audioDur = audio.duration * 1000;
            resolve(audioDur);
        };
    });
}

function playAudioLipSync(audio_base64, instrument_base64, volumes, slice_length, text = null, expression_list = null, onComplete) {
    if (window.state === "interrupted") {
        console.error("Audio playback blocked. State:", window.state);
        onComplete();
        return;
    }

    // ENHANCED SUBTITLE DEBUG: Comprehensive logging
    console.log("[SUBTITLE DEBUG] ========== SUBTITLE DIAGNOSTIC START ==========");
    console.log("[SUBTITLE DEBUG] playAudioLipSync called with text:", text);
    console.log("[SUBTITLE DEBUG] Text type:", typeof text);
    console.log("[SUBTITLE DEBUG] Text length:", text ? text.length : 0);
    
    const messageElement = document.getElementById("message");
    console.log("[SUBTITLE DEBUG] Message element found:", !!messageElement);
    
    if (messageElement) {
        const computedStyle = window.getComputedStyle(messageElement);
        console.log("[SUBTITLE DEBUG] Element details:");
        console.log("  - ID:", messageElement.id);
        console.log("  - Classes:", messageElement.className);
        console.log("  - Current text content:", messageElement.textContent);
        console.log("  - Display style:", computedStyle.display);
        console.log("  - Visibility:", computedStyle.visibility);
        console.log("  - Opacity:", computedStyle.opacity);
        console.log("  - Z-index:", computedStyle.zIndex);
        console.log("  - Position:", computedStyle.position);
        console.log("  - Hidden class present:", messageElement.classList.contains('hidden'));
        
        // Check parent visibility
        let parent = messageElement.parentElement;
        if (parent) {
            const parentStyle = window.getComputedStyle(parent);
            console.log("[SUBTITLE DEBUG] Parent element:");
            console.log("  - ID:", parent.id);
            console.log("  - Display:", parentStyle.display);
            console.log("  - Visibility:", parentStyle.visibility);
        }
    } else {
        console.error("[SUBTITLE DEBUG] ERROR: Message element not found in DOM!");
    }

    window.fullResponse += text;
    if (text) {
        if (messageElement) {
            const oldText = messageElement.textContent;
            messageElement.textContent = text;
            console.log("[SUBTITLE DEBUG] Text updated:");
            console.log("  - Old text:", oldText);
            console.log("  - New text:", text);
            console.log("  - Verification:", messageElement.textContent === text);
            
            // Force style recalculation
            messageElement.offsetHeight; // Trigger reflow
            
            // Check final visibility
            const finalStyle = window.getComputedStyle(messageElement);
            console.log("[SUBTITLE DEBUG] After update:");
            console.log("  - Display:", finalStyle.display);
            console.log("  - Is visible:", finalStyle.display !== 'none' && finalStyle.visibility !== 'hidden');
        } else {
            console.error("[SUBTITLE DEBUG] Cannot set text - element not found!");
        }
    } else {
        console.log("[SUBTITLE DEBUG] No text provided, skipping subtitle update");
    }
    console.log("[SUBTITLE DEBUG] ========== SUBTITLE DIAGNOSTIC END ==========");

    if (instrument_base64 != "None" && instrument_base64) {
        try {
            const instrumentAudio = new Audio("data:audio/mp3;base64," + instrument_base64);
            instrumentAudio.play().catch(error => {
                console.log("Instrument audio failed, trying WAV format");
                const wavAudio = new Audio("data:audio/wav;base64," + instrument_base64);
                wavAudio.play().catch(err => {
                    console.error("Failed to play instrument audio in any format:", err);
                });
            });
        } catch (error) {
            console.error("Error creating instrument audio:", error);
        }
    }

    const displayExpression = expression_list ? expression_list[0] : null;
    console.log("Start playing audio: ", text);
    
    // Check if audio_base64 is valid
    if (!audio_base64 || audio_base64 === "ZHVtbXkgYXVkaW8=" || audio_base64.length < 100) {
        console.log("Invalid or dummy audio data detected, skipping playback");
        // Just call onComplete without trying to play audio
        setTimeout(onComplete, 500);
        return;
    }
    
    // Enhanced fallback audio playback with format detection
    const playFallbackAudio = () => {
        console.log("Using enhanced fallback audio playback");
        
        // Try different audio formats
        const tryPlayAudio = (format) => {
            return new Promise((resolve, reject) => {
                const audio = new Audio(`data:audio/${format};base64,` + audio_base64);
                
                audio.onended = () => {
                    console.log(`${format} audio playback complete`);
                    resolve(true);
                };
                
                audio.onerror = (error) => {
                    console.log(`${format} audio format failed:`, error);
                    reject(error);
                };
                
                audio.play().catch(error => {
                    console.log(`${format} audio play error:`, error);
                    reject(error);
                });
            });
        };
        
        // Try mp3 first, then wav, then other formats
        tryPlayAudio("mp3")
            .catch(() => tryPlayAudio("wav"))
            .catch(() => tryPlayAudio("mpeg"))
            .catch(() => tryPlayAudio("aac"))
            .catch(() => {
                console.error("All audio formats failed");
                // Create a simple audio beep as final fallback
                try {
                    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                    const oscillator = audioCtx.createOscillator();
                    oscillator.type = 'sine';
                    oscillator.frequency.setValueAtTime(440, audioCtx.currentTime); // 440 Hz = A4
                    oscillator.connect(audioCtx.destination);
                    oscillator.start();
                    setTimeout(() => {
                        oscillator.stop();
                    }, 500);
                    console.log("Playing beep sound as final fallback");
                } catch (e) {
                    console.error("Even beep audio failed:", e);
                }
            })
            .finally(() => {
                // Always call onComplete even if all formats fail
                setTimeout(onComplete, 500);
            });
    };
    
    // Check if model2 exists and has speak function
    if (!window.model2) {
        console.error("model2 is not available for audio playback");
        playFallbackAudio();
        return;
    }
    
    try {
        if (typeof window.model2.speak !== 'function') {
            console.error("model2.speak is not a function");
            playFallbackAudio();
            return;
        }
        
        // Try multiple audio formats with the model2.speak function
        const tryModelFormats = ["mp3", "wav", "mpeg"];
        let formatIndex = 0;
        
        const tryNextFormat = () => {
            if (formatIndex >= tryModelFormats.length) {
                console.error("All formats failed with model2.speak");
                playFallbackAudio();
                return;
            }
            
            const format = tryModelFormats[formatIndex++];
            console.log(`Trying model2.speak with ${format} format`);
            
            window.model2.speak(`data:audio/${format};base64,` + audio_base64, {
                expression: displayExpression,
                resetExpression: true,
                onFinish: () => {
                    console.log("Voiceline is over");
                    onComplete();
                },
                onError: (error) => {
                    console.error(`Audio playback error with ${format}:`, error);
                    tryNextFormat();
                }
            });
        };
        
        tryNextFormat();
    } catch (error) {
        console.error("Speak function error:", error);
        playFallbackAudio();
    }
}
window.playAudioLipSync = playAudioLipSync;
