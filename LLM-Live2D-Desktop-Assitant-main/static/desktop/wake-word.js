/**
 * Wake Word Detection Module
 * Handles Porcupine wake word detection with fallback support
 */

class WakeWordDetector {
    constructor() {
        this.porcupine = null;
        this.isListening = false;
        this.config = null;
        this.accessKey = "/7gDUCElrddYzUegKQSEoe/ZQjH+sKU1KjcEnANpHdYQeLhc1WXrHQ==";
    }
    
    async initialize() {
        try {
            // Load configuration
            const response = await fetch('desktop/wake_word_config.json');
            this.config = await response.json();
            
            // Check which wake words are available
            const availableKeywords = [];
            
            // Check Chinese wake word
            if (this.config.wakeWords.chinese.enabled) {
                try {
                    const checkResponse = await fetch(`desktop/${this.config.wakeWords.chinese.file}`, { method: 'HEAD' });
                    if (checkResponse.ok) {
                        availableKeywords.push({
                            label: this.config.wakeWords.chinese.label,
                            publicPath: `desktop/${this.config.wakeWords.chinese.file}`
                        });
                        console.log('✅ Chinese wake word available:', this.config.wakeWords.chinese.label);
                    }
                } catch (e) {
                    console.warn('Chinese wake word file not found');
                }
            }
            
            // Check English wake word
            if (this.config.wakeWords.english.enabled) {
                try {
                    const checkResponse = await fetch(`desktop/${this.config.wakeWords.english.file}`, { method: 'HEAD' });
                    if (checkResponse.ok) {
                        availableKeywords.push({
                            label: this.config.wakeWords.english.label,
                            publicPath: `desktop/${this.config.wakeWords.english.file}`
                        });
                        console.log('✅ English wake word available:', this.config.wakeWords.english.label);
                    }
                } catch (e) {
                    console.warn('English wake word file not found, will work with Chinese only');
                }
            }
            
            if (availableKeywords.length === 0) {
                throw new Error('No wake word files available');
            }
            
            // Determine which parameter file to use
            let modelPath = 'desktop/porcupine_params.pv'; // Default English
            if (availableKeywords.length === 1 && availableKeywords[0].label === this.config.wakeWords.chinese.label) {
                modelPath = `desktop/${this.config.wakeWords.chinese.paramsFile}`;
            }
            
            // Initialize Porcupine
            this.porcupine = await PorcupineWeb.PorcupineWorker.create(
                this.accessKey,
                availableKeywords,
                this.onDetection.bind(this),
                modelPath,
                { sensitivity: this.config.sensitivity }
            );
            
            console.log('✅ Wake word detector initialized with keywords:', availableKeywords.map(k => k.label));
            return true;
            
        } catch (error) {
            console.error('Failed to initialize wake word detector:', error);
            return false;
        }
    }
    
    async start() {
        if (!this.porcupine) {
            const initialized = await this.initialize();
            if (!initialized) return false;
        }
        
        if (!this.isListening && window.WebVoiceProcessor) {
            await window.WebVoiceProcessor.WebVoiceProcessor.subscribe(this.porcupine);
            this.isListening = true;
            console.log('🎤 Wake word detection started');
            return true;
        }
        return false;
    }
    
    async stop() {
        if (this.isListening && this.porcupine && window.WebVoiceProcessor) {
            await window.WebVoiceProcessor.WebVoiceProcessor.unsubscribe(this.porcupine);
            this.isListening = false;
            console.log('🔇 Wake word detection stopped');
        }
    }
    
    async terminate() {
        await this.stop();
        if (this.porcupine) {
            await this.porcupine.terminate();
            this.porcupine = null;
        }
    }
    
    onDetection(detection) {
        console.log(`Wake word detected: ${detection.label}`);
        
        // Trigger the main application's wake word handler
        if (window.onWakeWordDetected) {
            window.onWakeWordDetected(detection);
        }
        
        // Also dispatch a custom event
        window.dispatchEvent(new CustomEvent('wakeword', { 
            detail: { 
                label: detection.label,
                timestamp: Date.now()
            } 
        }));
    }
}

// Export for use in other modules
window.WakeWordDetector = WakeWordDetector;

// Auto-initialize if needed
if (window.autoInitWakeWord) {
    const detector = new WakeWordDetector();
    window.wakeWordDetector = detector;
    detector.initialize().then(success => {
        if (success && window.autoStartWakeWord) {
            detector.start();
        }
    });
}
