/**
 * Script to obtain and set up Porcupine wake word files
 * This script helps download or generate the missing English wake word file
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const WAKE_WORD_CONFIG = {
    chinese: {
        filename: '伊蕾娜_zh_wasm_v3_0_0.ppn',
        exists: true,
        path: 'static/desktop/伊蕾娜_zh_wasm_v3_0_0.ppn'
    },
    english: {
        filename: 'Elaina_en_wasm_v3_0_0.ppn',
        exists: false,
        path: 'static/desktop/Elaina_en_wasm_v3_0_0.ppn',
        alternativeNames: [
            'elaina_en_wasm_v3_0_0.ppn',
            'computer_en_wasm_v3_0_0.ppn',
            'hey_elaina_en_wasm_v3_0_0.ppn'
        ]
    }
};

// Porcupine Console information
const PORCUPINE_INFO = {
    consoleUrl: 'https://console.picovoice.ai/',
    accessKey: '/7gDUCElrddYzUegKQSEoe/ZQjH+sKU1KjcEnANpHdYQeLhc1WXrHQ==',
    instructions: `
To obtain the English wake word file:

1. Go to Porcupine Console: https://console.picovoice.ai/
2. Sign in or create an account (free tier available)
3. Create a new wake word with the following settings:
   - Wake phrase: "Elaina" or "Hey Elaina"
   - Platform: Web (WASM)
   - Language: English
4. Train the model (usually takes a few minutes)
5. Download the .ppn file
6. Rename it to: Elaina_en_wasm_v3_0_0.ppn
7. Place it in: LLM-Live2D-Desktop-Assitant-main/static/desktop/

Alternative: Use a pre-built wake word like "Computer" or "Jarvis"
- These are available in the Porcupine GitHub repository
`
};

// Check existing files
function checkExistingFiles() {
    console.log('🔍 Checking for wake word files...\n');
    
    const projectRoot = path.join(__dirname, '..');
    
    // Check Chinese wake word
    const chinesePath = path.join(projectRoot, WAKE_WORD_CONFIG.chinese.path);
    if (fs.existsSync(chinesePath)) {
        const stats = fs.statSync(chinesePath);
        console.log(`✅ Chinese wake word found: ${WAKE_WORD_CONFIG.chinese.filename}`);
        console.log(`   Size: ${stats.size} bytes`);
        console.log(`   Path: ${chinesePath}\n`);
    } else {
        console.log(`❌ Chinese wake word missing: ${WAKE_WORD_CONFIG.chinese.filename}\n`);
    }
    
    // Check English wake word
    const englishPath = path.join(projectRoot, WAKE_WORD_CONFIG.english.path);
    if (fs.existsSync(englishPath)) {
        const stats = fs.statSync(englishPath);
        console.log(`✅ English wake word found: ${WAKE_WORD_CONFIG.english.filename}`);
        console.log(`   Size: ${stats.size} bytes`);
        console.log(`   Path: ${englishPath}\n`);
    } else {
        console.log(`❌ English wake word missing: ${WAKE_WORD_CONFIG.english.filename}`);
        console.log(`   Expected path: ${englishPath}\n`);
        
        // Check for alternative names
        console.log('   Checking for alternative filenames...');
        const desktopDir = path.join(projectRoot, 'static/desktop');
        let foundAlternative = false;
        
        for (const altName of WAKE_WORD_CONFIG.english.alternativeNames) {
            const altPath = path.join(desktopDir, altName);
            if (fs.existsSync(altPath)) {
                console.log(`   📌 Found alternative: ${altName}`);
                console.log(`      You can rename this to: ${WAKE_WORD_CONFIG.english.filename}`);
                foundAlternative = true;
            }
        }
        
        if (!foundAlternative) {
            console.log('   No alternative files found.\n');
        }
    }
}

// Create a fallback wake word configuration
function createFallbackConfig() {
    console.log('\n📝 Creating fallback configuration...\n');
    
    const projectRoot = path.join(__dirname, '..');
    const configPath = path.join(projectRoot, 'static/desktop/wake_word_config.json');
    
    const config = {
        wakeWords: {
            chinese: {
                enabled: true,
                file: '伊蕾娜_zh_wasm_v3_0_0.ppn',
                label: '伊蕾娜',
                language: 'zh',
                paramsFile: 'porcupine_params_zh.pv'
            },
            english: {
                enabled: false,
                file: 'Elaina_en_wasm_v3_0_0.ppn',
                label: 'Elaina',
                language: 'en',
                paramsFile: 'porcupine_params.pv',
                fallbackWords: ['Computer', 'Jarvis', 'Hey Assistant']
            }
        },
        accessKey: PORCUPINE_INFO.accessKey,
        sensitivity: 0.5
    };
    
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    console.log(`✅ Created wake word configuration: ${configPath}`);
    console.log('   This config will allow the app to work with just the Chinese wake word.\n');
}

// Create a JavaScript module for wake word handling
function createWakeWordModule() {
    console.log('📦 Creating wake word JavaScript module...\n');
    
    const projectRoot = path.join(__dirname, '..');
    const modulePath = path.join(projectRoot, 'static/desktop/wake-word.js');
    
    const moduleContent = `/**
 * Wake Word Detection Module
 * Handles Porcupine wake word detection with fallback support
 */

class WakeWordDetector {
    constructor() {
        this.porcupine = null;
        this.isListening = false;
        this.config = null;
        this.accessKey = "${PORCUPINE_INFO.accessKey}";
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
                    const checkResponse = await fetch(\`desktop/\${this.config.wakeWords.chinese.file}\`, { method: 'HEAD' });
                    if (checkResponse.ok) {
                        availableKeywords.push({
                            label: this.config.wakeWords.chinese.label,
                            publicPath: \`desktop/\${this.config.wakeWords.chinese.file}\`
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
                    const checkResponse = await fetch(\`desktop/\${this.config.wakeWords.english.file}\`, { method: 'HEAD' });
                    if (checkResponse.ok) {
                        availableKeywords.push({
                            label: this.config.wakeWords.english.label,
                            publicPath: \`desktop/\${this.config.wakeWords.english.file}\`
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
                modelPath = \`desktop/\${this.config.wakeWords.chinese.paramsFile}\`;
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
        console.log(\`Wake word detected: \${detection.label}\`);
        
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
`;
    
    fs.writeFileSync(modulePath, moduleContent);
    console.log(`✅ Created wake word module: ${modulePath}\n`);
}

// Main execution
function main() {
    console.log('========================================');
    console.log('  Porcupine Wake Word Setup Assistant');
    console.log('========================================\n');
    
    // Check existing files
    checkExistingFiles();
    
    // Create fallback configuration
    createFallbackConfig();
    
    // Create wake word module
    createWakeWordModule();
    
    // Display instructions
    console.log('========================================');
    console.log('  Instructions to Complete Setup');
    console.log('========================================');
    console.log(PORCUPINE_INFO.instructions);
    
    console.log('\n🎯 Quick Fix (Works with Chinese wake word only):');
    console.log('   The system is now configured to work with just the Chinese wake word.');
    console.log('   You can say "伊蕾娜" (Yī lěi nà) to activate the assistant.\n');
    
    console.log('📌 To add English wake word support:');
    console.log('   1. Follow the instructions above to get the English .ppn file');
    console.log('   2. Place it in: static/desktop/Elaina_en_wasm_v3_0_0.ppn');
    console.log('   3. Update wake_word_config.json to enable English wake word\n');
    
    console.log('✅ Setup script completed!');
}

// Run the script
main();